"""Unit tests for the generic, idempotent landlord billing-tag check.

The tests use synthetic plans written to ``tmp_path`` for edge cases and the
shared read-only ``fixtures/plan.json`` for the happy-path/mixed fixture. They
do not modify the fixture, seed data, or any Terraform state.
"""
import json
import runpy
import sys
from pathlib import Path

import pytest

from scripts.cost_tag_check import (
    REQUIRED_TAG,
    _after,
    _after_unknown,
    check_plan,
    collect_violations,
    has_required_tag,
    is_taggable,
    main,
    resource_address,
)

FIXTURE_PLAN = Path(__file__).resolve().parents[1] / "fixtures" / "plan.json"
_UNSET = object()


def _change(
    address=None,
    *,
    actions=("create",),
    after=_UNSET,
    after_unknown=None,
    mode="managed",
    resource_type="aws_s3_bucket",
    name="example",
    change_body=_UNSET,
):
    if change_body is _UNSET:
        body = {"actions": list(actions)}
        if after is not _UNSET:
            body["after"] = after
        if after_unknown is not None:
            body["after_unknown"] = after_unknown
        change_body = body

    result = {
        "mode": mode,
        "type": resource_type,
        "name": name,
        "change": change_body,
    }
    if address is not None:
        result["address"] = address
    return result


def _write_plan(tmp_path, changes, filename="plan.json"):
    path = tmp_path / filename
    path.write_text(
        json.dumps(
            {
                "format_version": "1.2",
                "resource_changes": changes,
            }
        ),
        encoding="utf-8",
    )
    return path


def _output_lines(capsys):
    return [
        line
        for line in capsys.readouterr().out.splitlines()
        if line.strip()
    ]


class TestFixturePlan:
    def test_fixture_flags_only_missing_landlord_tags(self, capsys):
        exit_code = check_plan(FIXTURE_PLAN)

        assert exit_code == 1
        lines = _output_lines(capsys)
        assert lines == [
            "Missing 'landlord_account_id' tag on resource: "
            "aws_lambda_function.mls_feed_sync",
            "Missing 'landlord_account_id' tag on resource: "
            "aws_s3_bucket.listing_media",
        ]

    def test_fixture_does_not_flag_passing_or_skipped_resources(self, capsys):
        check_plan(FIXTURE_PLAN)
        output = capsys.readouterr().out

        # Passing resources.
        assert "aws_s3_bucket.landlord_media[0]" not in output
        assert "aws_lambda_function.screening_report_export" not in output
        # Non-action / removed resources.
        assert "aws_s3_bucket.archive_media" not in output
        assert "aws_s3_bucket.decommissioned_media" not in output

    def test_fixture_violations_are_deduplicated(self, capsys):
        check_plan(FIXTURE_PLAN)
        lines = _output_lines(capsys)

        assert len(lines) == len(set(lines)) == 2

    def test_fixture_rerun_is_idempotent(self, capsys):
        first_exit = check_plan(FIXTURE_PLAN)
        first_output = capsys.readouterr().out

        second_exit = check_plan(FIXTURE_PLAN)
        second_output = capsys.readouterr().out

        assert first_exit == second_exit == 1
        assert first_output == second_output


class TestTenantOnlyTagFailure:
    @pytest.mark.parametrize(
        "resource_type",
        [
            "aws_s3_bucket",
            "aws_lambda_function",
            "aws_db_instance",
            "aws_unknown_future_resource",
        ],
    )
    def test_tenant_only_tag_fails_for_any_resource_type(
        self, tmp_path, capsys, resource_type
    ):
        address = f"{resource_type}.example"
        plan_path = _write_plan(
            tmp_path,
            [
                _change(
                    address,
                    resource_type=resource_type,
                    after={"tags": {"tenant_id": "ten-001"}},
                )
            ],
        )

        assert check_plan(plan_path) == 1
        assert _output_lines(capsys) == [
            f"Missing '{REQUIRED_TAG}' tag on resource: {address}"
        ]

    def test_tenant_tag_does_not_satisfy_landlord_tag(self, capsys):
        assert (
            has_required_tag(
                {"tags": {"tenant_id": "ten-001"}, "tags_all": {"tenant_id": "ten-001"}}
            )
            is False
        )

    def test_landlord_tag_alongside_tenant_tag_passes(self, capsys):
        assert (
            has_required_tag(
                {
                    "tags": {
                        "tenant_id": "ten-001",
                        "landlord_account_id": "la-001",
                    }
                }
            )
            is True
        )


class TestLandlordTagPasses:
    @pytest.mark.parametrize("tag_attribute", ["tags", "tags_all"])
    def test_landlord_tag_in_either_attribute_passes(
        self, tmp_path, capsys, tag_attribute
    ):
        plan_path = _write_plan(
            tmp_path,
            [_change("aws_s3_bucket.example", after={tag_attribute: {REQUIRED_TAG: "la-001"}})],
        )

        assert check_plan(plan_path) == 0
        assert _output_lines(capsys) == [
            "All created/updated taggable resources have 'landlord_account_id'."
        ]

    def test_provider_default_tag_in_tags_all_passes(self, tmp_path):
        plan_path = _write_plan(
            tmp_path,
            [
                _change(
                    "aws_s3_bucket.example",
                    after={
                        "tags": {"tenant_id": "ten-001"},
                        "tags_all": {REQUIRED_TAG: "la-001"},
                    },
                )
            ],
        )

        assert check_plan(plan_path) == 0

    @pytest.mark.parametrize("value", ["la-001", "la-002", "la-999"])
    def test_any_non_empty_landlord_id_passes(self, value):
        assert has_required_tag({"tags": {REQUIRED_TAG: value}}) is True


class TestNullAndMissingTags:
    @pytest.mark.parametrize(
        "after",
        [
            {"tags": None},
            {"tags": None, "tags_all": None},
            {"tags": {}},
            {"tags": {"landlord_account_id": None}},
            {"tags": {"landlord_account_id": ""}},
            {"tags": {"landlord_account_id": "   "}},
            {"tags": {"tenant_id": "ten-001"}},
        ],
    )
    def test_null_empty_or_tenant_only_tags_fail_cleanly(
        self, tmp_path, capsys, after
    ):
        plan_path = _write_plan(
            tmp_path,
            [_change("aws_s3_bucket.example", after=after)],
        )

        assert check_plan(plan_path) == 1
        assert "Missing 'landlord_account_id' tag" in capsys.readouterr().out

    def test_unknown_tags_fail_closed(self, tmp_path, capsys):
        plan_path = _write_plan(
            tmp_path,
            [
                _change(
                    "aws_s3_bucket.example",
                    after={"tags": None},
                    after_unknown={"tags": True},
                )
            ],
        )

        assert check_plan(plan_path) == 1
        assert "aws_s3_bucket.example" in capsys.readouterr().out

    def test_non_taggable_resource_is_skipped_cleanly(self, tmp_path, capsys):
        plan_path = _write_plan(
            tmp_path,
            [
                _change(
                    "aws_s3_bucket_lifecycle_configuration.example",
                    resource_type="aws_s3_bucket_lifecycle_configuration",
                    after={"bucket": "haven-listing-media", "rule": []},
                )
            ],
        )

        assert check_plan(plan_path) == 0
        assert "Missing" not in capsys.readouterr().out

    def test_taggable_detection_uses_tags_or_tags_all_only(self):
        assert is_taggable({"tags": None}, {}) is True
        assert is_taggable({}, {"tags_all": True}) is True
        assert is_taggable({"bucket": "x"}, {}) is False

    def test_non_mapping_tag_attribute_does_not_crash(self):
        assert has_required_tag({"tags": "not-a-map"}) is False
        assert has_required_tag({"tags": "not-a-map", "tags_all": {}}) is False


class TestActionFiltering:
    @pytest.mark.parametrize(
        "actions",
        [
            ["delete"],
            ["no-op"],
            ["read"],
        ],
    )
    def test_non_create_update_actions_are_skipped(self, tmp_path, actions):
        plan_path = _write_plan(
            tmp_path,
            [
                _change(
                    "aws_s3_bucket.example",
                    actions=actions,
                    after={"tags": {"tenant_id": "ten-001"}},
                )
            ],
        )

        assert check_plan(plan_path) == 0

    @pytest.mark.parametrize(
        "actions",
        [
            ["create"],
            ["update"],
            ["delete", "create"],
            ["create", "delete"],
        ],
    )
    def test_create_update_and_replace_are_checked(self, tmp_path, actions):
        plan_path = _write_plan(
            tmp_path,
            [
                _change(
                    "aws_s3_bucket.example",
                    actions=actions,
                    after={"tags": {"tenant_id": "ten-001"}},
                )
            ],
        )

        assert check_plan(plan_path) == 1

    def test_delete_without_after_is_skipped(self, tmp_path):
        plan_path = _write_plan(
            tmp_path,
            [
                _change(
                    "aws_s3_bucket.example",
                    actions=["delete"],
                    after=None,
                )
            ],
        )

        assert check_plan(plan_path) == 0

    def test_data_source_is_skipped(self, tmp_path):
        plan_path = _write_plan(
            tmp_path,
            [
                _change(
                    "data.aws_s3_bucket.example",
                    mode="data",
                    after={"tags": {}},
                )
            ],
        )

        assert check_plan(plan_path) == 0

    def test_missing_mode_defaults_to_managed(self):
        plan = {
            "resource_changes": [
                {
                    "address": "aws_s3_bucket.example",
                    "change": {
                        "actions": ["create"],
                        "after": {"tags": {"tenant_id": "ten-001"}},
                    },
                }
            ]
        }

        assert collect_violations(plan) == ["aws_s3_bucket.example"]

    def test_change_body_none_is_skipped(self):
        plan = {
            "resource_changes": [
                {
                    "address": "aws_s3_bucket.example",
                    "mode": "managed",
                    "change": None,
                }
            ]
        }

        assert collect_violations(plan) == []

    def test_missing_actions_is_skipped(self):
        plan = {
            "resource_changes": [
                {
                    "address": "aws_s3_bucket.example",
                    "mode": "managed",
                    "change": {"after": {"tags": {}}},
                }
            ]
        }

        assert collect_violations(plan) == []

    def test_non_list_actions_is_skipped(self):
        plan = {
            "resource_changes": [
                {
                    "address": "aws_s3_bucket.example",
                    "mode": "managed",
                    "change": {"actions": "create", "after": {"tags": {}}},
                }
            ]
        }

        assert collect_violations(plan) == []

    def test_non_mapping_after_is_skipped(self):
        plan = {
            "resource_changes": [
                {
                    "address": "aws_s3_bucket.example",
                    "mode": "managed",
                    "change": {"actions": ["create"], "after": "broken"},
                }
            ]
        }

        assert collect_violations(plan) == []

    def test_non_mapping_after_unknown_is_tolerated(self):
        plan = {
            "resource_changes": [
                {
                    "address": "aws_s3_bucket.example",
                    "mode": "managed",
                    "change": {
                        "actions": ["create"],
                        "after": {"tags": {REQUIRED_TAG: "la-001"}},
                        "after_unknown": "broken",
                    },
                }
            ]
        }

        assert collect_violations(plan) == []

    def test_after_helpers_tolerate_non_mapping_change_body(self):
        assert _after({"change": None}) is None
        assert _after({"change": "broken"}) is None
        assert _after_unknown({"change": None}) == {}
        assert _after_unknown({"change": "broken"}) == {}


class TestPlanShape:
    def test_empty_plan_passes(self, tmp_path, capsys):
        plan_path = _write_plan(tmp_path, [])

        assert check_plan(plan_path) == 0
        assert "All created/updated taggable resources" in capsys.readouterr().out

    def test_null_resource_changes_passes(self, tmp_path):
        path = tmp_path / "plan.json"
        path.write_text(json.dumps({"resource_changes": None}), encoding="utf-8")

        assert check_plan(path) == 0

    def test_non_list_resource_changes_passes(self, tmp_path):
        path = tmp_path / "plan.json"
        path.write_text(json.dumps({"resource_changes": "broken"}), encoding="utf-8")

        assert check_plan(path) == 0

    def test_non_dict_change_entries_are_skipped(self, tmp_path):
        plan_path = _write_plan(tmp_path, ["not-a-change", 42, None])

        assert check_plan(plan_path) == 0

    def test_pathlib_path_is_accepted(self, tmp_path):
        plan_path = _write_plan(
            tmp_path,
            [_change("aws_s3_bucket.example", after={"tags": {REQUIRED_TAG: "la-001"}})],
        )

        assert check_plan(Path(plan_path)) == 0


class TestAddressAndDedup:
    def test_address_fallback_is_stable(self):
        change = {"type": "aws_s3_bucket", "name": "example"}
        assert resource_address(change) == "aws_s3_bucket.example"
        assert resource_address(change) == resource_address(change)

    def test_blank_address_uses_fallback(self):
        change = {
            "address": "   ",
            "type": "aws_lambda_function",
            "name": "example",
        }
        assert resource_address(change) == "aws_lambda_function.example"

    def test_violations_are_sorted_and_deduplicated(self, tmp_path, capsys):
        plan_path = _write_plan(
            tmp_path,
            [
                _change("aws_s3_bucket.z", after={"tags": {}}),
                _change("aws_s3_bucket.a", after={"tags": {}}),
                _change("aws_s3_bucket.z", after={"tags": {}}),
            ],
        )

        assert check_plan(plan_path) == 1
        lines = _output_lines(capsys)
        assert lines == [
            "Missing 'landlord_account_id' tag on resource: aws_s3_bucket.a",
            "Missing 'landlord_account_id' tag on resource: aws_s3_bucket.z",
        ]

    def test_output_order_does_not_depend_on_input_order(self, tmp_path, capsys):
        changes = [
            _change("aws_s3_bucket.z", after={"tags": {}}),
            _change("aws_s3_bucket.a", after={"tags": {}}),
        ]
        forward = _write_plan(tmp_path, changes, "forward.json")
        reverse = _write_plan(tmp_path, list(reversed(changes)), "reverse.json")

        check_plan(forward)
        forward_output = capsys.readouterr().out

        check_plan(reverse)
        reverse_output = capsys.readouterr().out

        assert forward_output == reverse_output


class TestCli:
    def test_main_returns_zero_for_clean_plan(self, tmp_path):
        plan_path = _write_plan(
            tmp_path,
            [_change("aws_s3_bucket.example", after={"tags": {REQUIRED_TAG: "la-001"}})],
        )

        assert main([str(plan_path)]) == 0

    def test_main_returns_one_for_violation(self, tmp_path):
        plan_path = _write_plan(
            tmp_path,
            [_change("aws_s3_bucket.example", after={"tags": {"tenant_id": "ten-001"}})],
        )

        assert main([str(plan_path)]) == 1

    def test_missing_file_returns_two(self, tmp_path, capsys):
        missing = tmp_path / "missing.json"

        assert main([str(missing)]) == 2
        assert "error:" in capsys.readouterr().err

    def test_invalid_json_returns_two(self, tmp_path, capsys):
        bad = tmp_path / "bad.json"
        bad.write_text("{not-json", encoding="utf-8")

        assert main([str(bad)]) == 2
        assert "error:" in capsys.readouterr().err

    def test_non_object_json_returns_two(self, tmp_path, capsys):
        bad = tmp_path / "list.json"
        bad.write_text("[]", encoding="utf-8")

        assert main([str(bad)]) == 2
        assert "must be an object" in capsys.readouterr().err

    def test_module_entrypoint_exits_with_check_code(self, tmp_path, monkeypatch):
        plan_path = _write_plan(
            tmp_path,
            [_change("aws_s3_bucket.example", after={"tags": {REQUIRED_TAG: "la-001"}})],
        )
        monkeypatch.setattr(
            sys,
            "argv",
            ["cost_tag_check.py", str(plan_path)],
        )
        monkeypatch.delitem(sys.modules, "scripts.cost_tag_check", raising=False)

        with pytest.raises(SystemExit) as excinfo:
            runpy.run_module("scripts.cost_tag_check", run_name="__main__")

        assert excinfo.value.code == 0
