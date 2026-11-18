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
