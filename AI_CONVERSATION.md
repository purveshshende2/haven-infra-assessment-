# AI Conversation Record — Haven Infrastructure Assessment

## Context

| Item | Value |
|---|---|
| Date | 2026-11-19 |
| Agent | OpenCode / DeepSeek V4.1 Flash Free |
| Repository | `purveshshende2/haven-infra-assessment-` |
| Tasks | B0 (count trap), B1 (Glacier cost), B2 (access control + cost tagging) |
| Constraints | Do not modify `app/seed_data.py`, `app/models.py`, `fixtures/plan.json`, or `terraform/terraform.tfstate`; do not squash/amend/`rebase -i`; separate commits per milestone; no hardcoded resource names in the tag check |

This record is a faithful summary of the prompts, the initial checks, the generated code, and the
verification output. The full terminal output is in `TERMINAL_LOG.md`; the written answers are in
`B0.md` and `B1.md`; the design decisions are in `DESIGN_NOTES.md`.

## User prompt (key requirements, preserved)

The user asked to complete the Haven infrastructure assessment end-to-end, including
implementation, full unit-test coverage, verification runs, documentation, and incremental Git
commits, with these strict rules:

> - Never modify app seed, app seed data.py, or any existing seed data fixtures.
> - Never squash commits, `git rebase -i`, or `git commit amend` across milestone. It is forbidden.
> - Make sure to make separate clean commits at each milestone below.
> - Do not hardcode specific resource names in the cost tagging check.
> - execute these steps in the order:
>   1. Inspect and resolve imports or typos. Read README.md, models.py, seed_data.py,
>      script-cost_tag_check.py, existing test, and all TF files. Fix any circular imports
>      (example via type checking) or clean module structure, typos, Python path issues in the
>      existing code or test runner without touching the seed data.
>   2. Read or create B0.md and explain what `terraform plan` outputs when a landlord account is
>      removed from the middle of a `count`-indexed S3 bucket list (index shifting forcing
>      replacement/recreation of subsequent buckets and destruction of the last index), why it is
>      dangerous (data loss especially with `force_destroy = true`, apply failures on non-empty
>      buckets, and cross-tenant IAM or output misrouting), and the fix (keying with `for_each`
>      using the immutable `landlord_account_id`).
>   3. Read B1.md and solve the S3 Glacier early deletion cost question, explaining the impact of
>      archiving on day 30 and deleting on day 40 under the 90-day minimum storage duration
>      (charging prorated storage for the remaining 80 days).
>   4. Implement `can_access_screening_report` matching the existing function signature in
>      `app/` so a property manager can only view screening reports for tenants under their own
>      `landlord_account_id` and never across different landlord accounts even if a valid ID or
>      tenant reference is passed. Add tests for same account allowed, cross account denied, and
>      missing/unassigned landlord account ID or unknown report denied. Run `pytest -v` and commit.
>   5. Implement a generic, idempotent `scripts/cost_tag_check.py` and tests covering tenant-only
>      tags (fails), `landlord_account_id` (passes), and null/non-taggable resources (handled
>      cleanly). Run `terraform init`, `terraform plan -out=tfplan`, and
>      `terraform show -json tfplan > tfplan.json`; verify the check against `tfplan.json`; run
>      `pytest -v`; commit.
>   6. Create `DESIGN_NOTES.md` stating the exact key used to guarantee idempotency (using the
>      word "idempotency"), `TERMINAL_LOG.md` with the exact init/plan/pytest/cost-check output,
>      and `AI_CONVERSATION.md` with prompts, outputs, initial checks, and generated code; make a
>      final documentation commit.

The user also supplied the original assignment text, including the B0/B1 questions, the B2
"must work" criteria, and the instruction to record what was learned from the README before
writing code.

## Initial checks (HKS)

The first pass inspected the repository before changing anything:

1. **Repository shape** — `app/` contains the frozen domain dataclasses and seed data; `scripts/`
   contains the tag-check stub; `tests/` contains the access-control and tag-check stubs;
   `terraform/` contains `main.tf` (B0), `lifecycle.tf` (B1), `provider.tf`, `variables.tf`, and a
   deliberately checked-in `terraform.tfstate` with four landlord media buckets.
2. **Imports** — no true circular import existed. `app/access_control.py` imported
   `app.models` at runtime even though the names were only needed for type annotations. It was
   changed to `from __future__ import annotations` plus `TYPE_CHECKING` imports, keeping the
   module tree clean and avoiding unnecessary runtime coupling.
3. **Python path / test runner** — pytest worked from the repository root, but there was no
   explicit configuration. Added `pytest.ini` with `testpaths = tests` and `pythonpath = .` so
   the suite is reproducible from the root without manual `PYTHONPATH` edits.
4. **Baseline tests** — `pytest -v` collected 3 tests and all 3 passed before the new work.
5. **Generated artifacts** — `tfplan`, `terraform/tfplan.json`, and the root `tfplan.json` were
   tracked. They were removed from Git tracking and added to `.gitignore`; `terraform.tfstate`
   was left untouched because the README says it is intentionally checked in.
6. **Terraform** — `terraform init` succeeded offline with the dummy provider credentials.
   `terraform plan -refresh=false -var='landlord_accounts=["la-001","la-003","la-004"]'`
   reproduced the B0 count cascade: `[1]` and `[2]` replaced, `[3]` destroyed.
7. **Seed data** — `app/seed_data.py` and `app/models.py` were read but never edited;
   `fixtures/plan.json` and `terraform/terraform.tfstate` were never edited.

### What the README changed about the implementation

The README's domain model is the key: **`LandlordAccount` is the billing unit**, not
`Tenant`/`tenant_id`. A `PropertyManager` is scoped to exactly one `LandlordAccount`, and the
ownership path for a screening report is `ScreeningReport -> Tenant -> Property ->
LandlordAccount`. That directly determined two design choices:

* The access check resolves the report's tenant to its property and compares
  `property.landlord_account_id` with `actor.landlord_account_id`; a valid tenant/report
  reference alone is never enough.
* The tag check requires `landlord_account_id` on every taggable create/update, and a resource
  tagged only with `tenant_id` fails. It also checks `tags_all` so provider default tags count.

## Milestones and generated outputs

### Milestone 1 — inspection and hygiene

Commit: `e3dfeb8 chore: inspect repository and fix module and import hygiene`

* Added `pytest.ini`.
* Added `TYPE_CHECKING` imports and a clear module docstring to `app/access_control.py`.
* Added the module docstring to `scripts/cost_tag_check.py`.
* Removed generated plan artifacts from tracking and ignored them.
* Re-ran `pytest -v`: 3 passed.

### B0 — the `count` trap

Commit: `f5ee2e8 docs: answer B0 terraform count index shifting question`

Answer in `B0.md`: removing `la-002` from the middle of the list shifts `la-003` to index 1 and
`la-004` to index 2, so Terraform replaces `[1]` and `[2]` and destroys `[3]`. With
`force_destroy = true` that is permanent data loss; with the default `false` it fails on
non-empty buckets and leaves a half-applied state. Positional addresses also let IAM policies,
outputs, and app configuration follow the index to the wrong landlord, which is a cross-tenant
exposure. The fix is `for_each` keyed by the immutable `landlord_account_id`, with `moved` blocks
or `terraform state mv` to migrate the existing state safely.

### B1 — the Glacier cost gotcha

Commit: `e9ab50d docs: answer B1 glacier early deletion cost question`

Answer in `B1.md`: a day-30 transition and day-40 deletion means 10 days in Glacier Flexible
Retrieval, so the 90-day minimum leaves 80 days billable. The early deletion fee is prorated for
those 80 days; transition requests, 40 KB of per-object overhead, and restore costs are also
already spent. The redesign delays the Glacier transition until after the deletion window (for
example day 90), keeps the 30–90 day window in a class without a 90-day minimum, filters out
objects under 128 KB, and makes deletion a workflow that checks the object's age/class rather
than deleting blindly.

### B2 part 1 — landlord-scoped access

Commit: `9ce5689 feat: implement landlord-scoped screening report access and unit tests`

`app/access_control.py` was implemented with fail-closed behavior and 30 tests in
`tests/test_access_control.py`. The tests cover:

* same `landlord_account_id` -> `True` (both seeded managers);
* cross-account report -> `False` (both directions), including a valid foreign tenant reference
  and a forged `tenant_id`;
* missing actor, missing report, blank/whitespace/`None` landlord account ID, unassigned property
  landlord ID, unknown tenant, unknown property, empty lists, and unknown report tenant -> all
  `False`;
* an exhaustive cross-account pair loop over the seed data.

### B2 part 2 — generic cost-tag check

Commit: `f7d7723 feat: add generic idempotent landlord cost tag check and tests`

`scripts/cost_tag_check.py` was implemented with:

* no hardcoded resource names or resource-type allowlist;
* taggability inferred from the presence of `tags`/`tags_all` in `after` or `after_unknown`;
* managed create/update/replace actions only; delete/no-op/read/data sources skipped;
* `landlord_account_id` required in either `tags` or `tags_all`, non-empty;
* unknown tags fail closed;
* dedup by `resource_changes[].address` and sorted output;
* exit codes `0` (clean), `1` (violations), `2` (usage/read/JSON error).

The 58 tests in `tests/test_cost_tag_check.py` cover the mixed fixture, tenant-only tags across
multiple resource types, landlord tags in either attribute, null/empty tags, non-taggable
resources, action filtering, malformed plan shapes, dedup/sort behavior, CLI exit codes, and
the module entrypoint. Measured coverage is 100% for both B2 modules.

### Verification

`terraform init`, `terraform plan -out=tfplan`, and
`terraform show -json tfplan > tfplan.json` all exited 0. The cost check was run twice against
the real plan; both runs produced the same one-line violation and exit code 1, with identical
SHA-256 output hashes. The real plan correctly flags `aws_s3_bucket.listing_media`, which is a
shared bucket with no landlord tag; the four `landlord_media` buckets pass and the lifecycle
configuration is skipped as non-taggable. A control run with that tag added exits 0.

`pytest -v` reports **88 passed**. `coverage report -m` reports **100%** for
`app/access_control.py` and `scripts/cost_tag_check.py` (and 100% total for `app/` + `scripts/`).

## Generated code

### `app/access_control.py`

```python
"""Landlord-scoped access checks for Haven screening reports.

The authoritative ownership chain is:

    ScreeningReport -> Tenant -> Property -> LandlordAccount

A ``PropertyManager`` is scoped to exactly one ``LandlordAccount``. Access is
therefore decided by resolving the report's tenant to its property and
comparing the property's landlord account with the manager's landlord account.
A caller-supplied tenant or report reference alone is never sufficient.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Property, PropertyManager, ScreeningReport, Tenant


def can_access_screening_report(
    actor: PropertyManager,
    report: ScreeningReport,
    *,
    properties: list[Property],
    tenants: list[Tenant],
) -> bool:
    """Return ``True`` only when ``actor`` and ``report`` share a landlord account.

    The function fails closed: missing actors, reports, tenant links, property
    links, blank landlord account IDs, or unknown tenant/property records all
    return ``False``.
    """
    if not actor or not report:
        return False

    actor_landlord_id = (actor.landlord_account_id or "").strip()
    tenant_id = (report.tenant_id or "").strip()
    if not actor_landlord_id or not tenant_id:
        return False

    # Resolve the report's tenant and property from server-side records. Never
    # trust an ID supplied alongside the report without checking the hierarchy.
    tenants_by_id = {
        (tenant.id or "").strip(): tenant for tenant in tenants or []
    }
    tenant = tenants_by_id.get(tenant_id)
    if tenant is None:
        return False

    property_id = (tenant.property_id or "").strip()
    if not property_id:
        return False

    properties_by_id = {
        (prop.id or "").strip(): prop for prop in properties or []
    }
    prop = properties_by_id.get(property_id)
    if prop is None:
        return False

    property_landlord_id = (prop.landlord_account_id or "").strip()
    if not property_landlord_id:
        return False

    return actor_landlord_id == property_landlord_id
```

### `scripts/cost_tag_check.py`

```python
"""Fail a Terraform plan when a taggable resource lacks the billing tag.

Haven's billing unit is ``landlord_account_id``. Resources are commonly tagged
with ``tenant_id`` instead, which does not roll up to a landlord account and
therefore cannot support chargeback.

The check is intentionally resource-agnostic: it never names a Terraform
resource type. It detects taggable resources from the plan itself by looking
for the presence of a ``tags`` or ``tags_all`` attribute, so new resource types
are covered automatically.

Idempotency
-----------
The deduplication key is the Terraform resource instance address
(``resource_changes[].address``), for example
``aws_s3_bucket.landlord_media[0]``. That address is unique and stable for a
given plan. ``check_plan`` keeps the set only in local memory, sorts the
violations before printing, and writes nothing, so rerunning it against an
unchanged plan produces byte-for-byte identical output and the same exit code.

Exit codes: ``0`` = no violations, ``1`` = violations, ``2`` = usage/read error.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

REQUIRED_TAG = "landlord_account_id"
TAG_ATTRIBUTES = ("tags", "tags_all")
CHECKED_ACTIONS = frozenset({"create", "update"})


def load_plan(plan_path: str | Path) -> Mapping[str, Any]:
    """Load and validate the top-level shape of a ``terraform show -json`` file."""
    with open(plan_path, "r", encoding="utf-8") as plan_file:
        plan = json.load(plan_file)

    if not isinstance(plan, dict):
        raise ValueError("Terraform plan JSON must be an object at the top level")
    return plan


def iter_resource_changes(plan: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    """Yield well-formed entries from ``resource_changes``, tolerating nulls."""
    changes = plan.get("resource_changes")
    if not isinstance(changes, list):
        return

    for change in changes:
        if isinstance(change, dict):
            yield change


def resource_address(change: Mapping[str, Any]) -> str:
    """Return the stable Terraform address used as the idempotency/dedup key."""
    address = change.get("address")
    if isinstance(address, str) and address.strip():
        return address.strip()

    # Address is normally always present. This fallback keeps output stable for
    # malformed or older plan fixtures without inventing a random identifier.
    resource_type = change.get("type", "<unknown>")
    resource_name = change.get("name", "<unknown>")
    return f"{resource_type}.{resource_name}"


def _actions(change: Mapping[str, Any]) -> set[str]:
    change_body = change.get("change")
    if not isinstance(change_body, Mapping):
        return set()
    actions = change_body.get("actions")
    if not isinstance(actions, list):
        return set()
    return {str(action) for action in actions}


def _after(change: Mapping[str, Any]) -> Mapping[str, Any] | None:
    change_body = change.get("change")
    if not isinstance(change_body, Mapping):
        return None
    after = change_body.get("after")
    return after if isinstance(after, Mapping) else None


def _after_unknown(change: Mapping[str, Any]) -> Mapping[str, Any]:
    change_body = change.get("change")
    if not isinstance(change_body, Mapping):
        return {}
    after_unknown = change_body.get("after_unknown")
    return after_unknown if isinstance(after_unknown, Mapping) else {}


def is_taggable(after: Mapping[str, Any], after_unknown: Mapping[str, Any]) -> bool:
    """Infer taggability without a hardcoded list of resource types.

    Terraform emits a ``tags`` and/or ``tags_all`` attribute for resources that
    support tagging. If neither attribute is present in the known or unknown
    portions of the planned object, the resource has no tag surface to check.
    """
    return any(
        attribute in after or attribute in after_unknown
        for attribute in TAG_ATTRIBUTES
    )


def has_required_tag(after: Mapping[str, Any]) -> bool:
    """Return True when a non-empty landlord account tag is present.

    Both ``tags`` and ``tags_all`` are inspected so provider-level default tags
    (which appear in ``tags_all``) count as effective billing tags. Values that
    are missing, null, empty, or whitespace-only do not count.
    """
    for attribute in TAG_ATTRIBUTES:
        tag_map = after.get(attribute)
        if not isinstance(tag_map, Mapping):
            continue
        value = tag_map.get(REQUIRED_TAG)
        if value is not None and str(value).strip():
            return True
    return False


def collect_violations(plan: Mapping[str, Any]) -> list[str]:
    """Return sorted, de-duplicated addresses of violating resources.

    Only managed resources with a create/update/replace action are checked.
    Delete, no-op, read, and data-source entries have no planned object to
    validate and are skipped. The dedup key is the Terraform resource address.
    """
    violations: set[str] = set()

    for change in iter_resource_changes(plan):
        if change.get("mode", "managed") != "managed":
            continue

        if not _actions(change) & CHECKED_ACTIONS:
            continue

        after = _after(change)
        if after is None:
            # A delete/replace action without a planned object has nothing to
            # validate. Replacements normally do include an ``after`` object.
            continue

        after_unknown = _after_unknown(change)
        if not is_taggable(after, after_unknown):
            # Non-taggable resource (for example a lifecycle configuration or
            # an IAM policy attachment). There is no tag surface to check.
            continue

        if not has_required_tag(after):
            violations.add(resource_address(change))

    return sorted(violations)


def check_plan(plan_path: str | Path) -> int:
    """Check one plan file and return the process exit code."""
    plan = load_plan(plan_path)
    violations = collect_violations(plan)

    if violations:
        for address in violations:
            print(f"Missing '{REQUIRED_TAG}' tag on resource: {address}")
        return 1

    print(f"All created/updated taggable resources have '{REQUIRED_TAG}'.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail when a created/updated taggable resource in a Terraform plan "
            f"is missing the '{REQUIRED_TAG}' billing tag."
        )
    )
    parser.add_argument(
        "plan",
        help="Path to JSON output from `terraform show -json <planfile>`.",
    )
    args = parser.parse_args(argv)

    try:
        return check_plan(args.plan)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
```

### Representative tests

The access-control test file is organized around the authorization boundary:

```python
class TestSameLandlordAccount:
    @pytest.mark.parametrize(
        ("manager_id", "report_id"),
        [("pm-001", "rep-001"), ("pm-002", "rep-002")],
    )
    def test_same_account_allows_access(self, manager_id, report_id):
        ...

class TestCrossLandlordAccount:
    def test_cross_account_denied_with_valid_tenant_reference(self, pm_001, rep_002):
        assert can_access_screening_report(
            pm_001, rep_002, properties=PROPERTIES, tenants=TENANTS
        ) is False

class TestFailClosed:
    @pytest.mark.parametrize("landlord_account_id", ["", "   ", None])
    def test_missing_actor_landlord_account_denied(self, pm_001, rep_001, landlord_account_id):
        ...
```

The cost-tag tests use `tmp_path` for synthetic plans and the shared read-only fixture for the
mixed case:

```python
def test_tenant_only_tag_fails_for_any_resource_type(tmp_path, capsys, resource_type):
    ...

def test_null_empty_or_tenant_only_tags_fail_cleanly(tmp_path, capsys, after):
    ...

def test_fixture_rerun_is_idempotent(capsys):
    first_exit = check_plan(FIXTURE_PLAN)
    first_output = capsys.readouterr().out
    second_exit = check_plan(FIXTURE_PLAN)
    second_output = capsys.readouterr().out
    assert first_exit == second_exit == 1
    assert first_output == second_output
```

## Commit history

```text
e3dfeb8 chore: inspect repository and fix module and import hygiene
f5ee2e8 docs: answer B0 terraform count index shifting question
e9ab50d docs: answer B1 glacier early deletion cost question
9ce5689 feat: implement landlord-scoped screening report access and unit tests
f7d7723 feat: add generic idempotent landlord cost tag check and tests
02fb993 docs: refine B1 glacier pricing and lifecycle guidance
```

The documentation commit for `DESIGN_NOTES.md`, `TERMINAL_LOG.md`, and this file is made after
this content is written. No commit was squashed, amended, or rebased. `app/seed_data.py`,
`app/models.py`, `fixtures/plan.json`, and `terraform/terraform.tfstate` are unchanged from the
starter repository.
