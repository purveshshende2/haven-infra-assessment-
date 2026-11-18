import json
import sys


REQUIRED_TAG = "landlord_account_id"


def check_plan(plan_path: str) -> int:
    with open(plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)

    violations: list[str] = []
    seen: set[str] = set()

    for rc in plan.get("resource_changes", []):
        if rc.get("mode", "managed") != "managed":
            continue

        change = rc.get("change") or {}
        actions = set(change.get("actions") or [])

        # Only check resources being created or updated (skip no-op, read, delete)
        if not actions.intersection({"create", "update"}):
            continue

        after = change.get("after")
        if not isinstance(after, dict):
            continue

        # Skip non-taggable resources (neither `tags` nor `tags_all` in resource schema)
        after_unknown = change.get("after_unknown") or {}
        if not any(k in after or k in after_unknown for k in ("tags", "tags_all")):
            continue

        # Check both `tags` and `tags_all` for a non-empty `landlord_account_id`
        has_valid_tag = False
        for key in ("tags", "tags_all"):
            tag_map = after.get(key)
            if isinstance(tag_map, dict):
                val = tag_map.get(REQUIRED_TAG)
                if val is not None and str(val).strip() != "":
                    has_valid_tag = True
                    break

        if not has_valid_tag:
            addr = rc.get("address", "<unknown>")
            if addr not in seen:
                seen.add(addr)
                violations.append(addr)

    if violations:
        for addr in violations:
            print(f"Missing '{REQUIRED_TAG}' tag on resource: {addr}")
        return 1

    print(f"All created/updated taggable resources have '{REQUIRED_TAG}'.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/cost_tag_check.py <plan.json>", file=sys.stderr)
        sys.exit(2)
    sys.exit(check_plan(sys.argv[1]))
