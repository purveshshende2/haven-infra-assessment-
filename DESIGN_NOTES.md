# Design Notes

## B2 — the exact idempotency key

**The key is `resource_changes[].address` — the Terraform resource instance address, for example
`aws_s3_bucket.landlord_media[0]` or `aws_lambda_function.mls_feed_sync`.**

`collect_violations()` keeps a local `set[str]` of these addresses, adds an address only when the
resource is managed, has a `create`/`update`/replace action, is taggable, and lacks the
`landlord_account_id` tag, and then returns `sorted(violations)`. The address is unique per
resource instance (including `count` indexes and `for_each` keys), so duplicate entries for the
same resource collapse to one line and two different instances never collapse together.

Nothing is persisted between runs: no cache, no database, no counter, no timestamp. The plan
file is read-only input, the dedup set is local memory, and the output is sorted. Therefore the
**idempotency** guarantee is:

> Running `python scripts/cost_tag_check.py <plan.json>` twice against an unchanged plan produces
> byte-for-byte identical output and the same exit code, with no duplicated violation lines and
> no side effects on the plan or repository.

The terminal log demonstrates this with two consecutive runs whose outputs have the same SHA-256
hash (`358c630e...`). The unit test `test_fixture_rerun_is_idempotent` asserts the same property,
and `test_output_order_does_not_depend_on_input_order` proves the sort makes the result stable
even if the plan lists resources in a different order.

### Why this key rather than the alternatives

| Candidate | Why it was not used |
|---|---|
| Bucket name / function name | Not every resource has one, and a name can change independently of identity. |
| `type` + `name` | Not unique for `count`/`for_each` instances, and collides across modules. |
| Resource type alone | Would incorrectly merge every bucket into one violation. |
| File path or run timestamp | Not stable across reruns; would break idempotency. |
| `resource_changes` list position | Changes when unrelated resources are added or reordered. |

The address is Terraform's own stable identity for a resource instance, which is exactly what a
deduplication key needs.

## B2 — access control decisions

### The boundary is the landlord account, not the tenant reference

The authoritative chain is `ScreeningReport -> Tenant -> Property -> LandlordAccount`. The
implementation resolves the report's `tenant_id` against the supplied tenant records, then
resolves that tenant's `property_id` against the supplied property records, and only then
compares the property's `landlord_account_id` with the actor's `landlord_account_id`.

A caller can pass a perfectly valid report ID and a perfectly valid tenant ID and still be
denied if the tenant's property belongs to another landlord. The report/tenant reference is
never treated as proof of ownership.

**Alternative considered:** trust the `tenant_id` on the report and compare it with a
tenant-to-manager mapping. Rejected because the report's tenant reference is data supplied by
the caller; the property-to-landlord edge is the ownership boundary the README defines.

### Fail closed

`None` actors/reports, blank or whitespace landlord account IDs, missing tenant records,
tenants without a property, missing property records, and unassigned property landlord IDs all
return `False`. Unknown reports (a report whose tenant cannot be resolved) also return `False`.
This is deliberate: a missing ownership link must never be interpreted as "no restriction".

**Alternative considered:** raising an exception for malformed records. Rejected for this
authorization check because an exception can fail open if a caller catches it broadly; returning
`False` keeps the default deny.

## B2 — cost tag check decisions

### `landlord_account_id` is required, `tenant_id` is not enough

The README identifies `LandlordAccount` as the billing unit. A resource tagged only with
`tenant_id` fails the check, because tenant costs cannot be rolled up to the landlord account
without a separate lookup and because the assignment explicitly calls out that resources are
tagged with the wrong field today. A resource with both tags passes as long as
`landlord_account_id` is non-empty.

### Effective tags: `tags` and `tags_all`

The check inspects both `tags` and `tags_all`. `tags_all` is the provider's effective tag set and
includes provider-level `default_tags`, so a landlord tag supplied through provider defaults is
accepted. Values that are `None`, empty, or whitespace-only do not count.

**Alternative considered:** check only `tags`. Rejected because it would reject a correctly
defaulted provider configuration and produce false positives.

### Generic taggability detection, no resource names

The check does not contain a list of Terraform resource types. It treats a resource as taggable
when the planned object (`after`) or its unknown-value map (`after_unknown`) contains a `tags` or
`tags_all` attribute. A lifecycle configuration or IAM policy attachment with neither attribute
is skipped cleanly. This is what makes the check generic and future-proof: a new resource type
with a tag surface is covered automatically.

**Alternative considered:** hardcode a list of known taggable types. Rejected because the
assignment explicitly forbids hardcoding resource names and because the list would drift.

### Only planned changes are checked

The check considers managed resources with a `create`, `update`, or replace action. It skips
`delete`, `no-op`, and `read` actions, data sources, null `after` blocks, and malformed entries.
There is no planned object to tag on a delete, and a no-op resource is already in state; checking
it would produce noise unrelated to the change being reviewed.

### Unknown tag values fail closed

If the plan says the tag value is unknown (`after_unknown["tags"] = true`), the checker cannot
prove that `landlord_account_id` is present. It reports a violation rather than assuming success.
This is consistent with the access-control fail-closed choice.

### Real plan finding

The real `terraform plan` for this repository surfaces a true positive:
`aws_s3_bucket.listing_media` has no `landlord_account_id` tag. That bucket is shared across
landlords, so assigning it a single landlord ID would be semantically wrong. The correct
remediation is architectural: split listing media into per-landlord buckets using the B0
`for_each` keyed by `landlord_account_id`, or assign the shared bucket to an explicit platform
cost center with a documented exception. Weakening the check to ignore it would hide the
modeling problem the assessment is asking us to catch. The unit tests and the control run in
`TERMINAL_LOG.md` prove the check passes once a landlord tag is present.

## B0 — `count` versus `for_each`

The fix is `for_each` keyed by the immutable `landlord_account_id`, not by list position. The
key is stable when an account is added or removed, so only the affected bucket is planned for
destruction. Retained buckets keep their addresses, names, tags, policies, and objects.

**Alternative considered:** keep `count` and use `terraform state mv` after every list edit.
Rejected because it is an operational workaround, not a design fix; a future editor will still
cause the same cascade. The migration still uses `moved` blocks or `state mv` once, but the
steady state is keyed and safe.

The `force_destroy` default is left `false`. Turning it on to make apply succeed converts a
failed destroy into permanent data loss. For production buckets, `prevent_destroy` is a useful
second guardrail.

## B1 — Glacier lifecycle

The lifecycle is redesigned to delay the Glacier transition until after the period in which a
seller can request deletion. A day-40 deletion then occurs while the object is in a class with no
90-day minimum, so there is no early deletion fee. The alternative — keep the 30-day transition
and accept the prorated fee — is rejected because the fee is predictable waste and the transition
request plus 40 KB overhead have already been paid.

**Alternative considered:** move everything to Glacier Deep Archive immediately for the lowest
storage rate. Rejected because Deep Archive has a 180-day minimum, is not real-time readable, and
turns a day-40 deletion into a 170-day penalty. Standard-IA and Intelligent-Tiering are
appropriate for the 30–90 day window, subject to their own minimums and per-object fees.

## Test strategy decisions

* Access-control tests use the seeded accounts for the allowed/denied matrix, then construct
  edge cases with `dataclasses.replace()` and small in-memory records so no seed fixture is
  modified.
* Cost-tag tests use `tmp_path` for synthetic plans and the shared read-only
  `fixtures/plan.json` for the mixed fixture. This follows the test stub's instruction and avoids
  editing the fixture.
* Coverage is measured with `coverage run --source=app,scripts -m pytest`; the reported line
  coverage is 100% for `app/access_control.py` and `scripts/cost_tag_check.py`.
