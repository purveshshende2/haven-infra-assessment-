# Terminal Log

This file records the verification commands and their exact terminal output. ANSI colour was
disabled for Terraform commands with `-no-color` so the log is readable. Nothing in this file is
hand-edited output: each block is the captured stdout/stderr of the command shown above it.

## Environment

```console
$ ./venv/bin/python --version
Python 3.13.5

$ ./venv/bin/pytest --version
pytest 9.2.0

$ terraform version
Terraform v1.12.2
on darwin_arm64
+ provider registry.terraform.io/hashicorp/aws v5.100.0

Your version of Terraform is out of date! The latest version
is 1.17.2. You can update by downloading from https://developer.hashicorp.com/terraform/install
```

## 1. Terraform initialization

```console
$ cd terraform
$ terraform init -input=false -no-color
Initializing the backend...
Initializing provider plugins...
- Reusing previous version of hashicorp/aws from the dependency lock file
- Using previously-installed hashicorp/aws v5.100.0

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.
```
Exit code: `0`.

## 2. Terraform plan

```console
$ terraform plan -input=false -no-color -out=tfplan
aws_s3_bucket.landlord_media[0]: Refreshing state... [id=haven-media-la-001]
aws_s3_bucket.landlord_media[2]: Refreshing state... [id=haven-media-la-003]
aws_s3_bucket.landlord_media[1]: Refreshing state... [id=haven-media-la-002]
aws_s3_bucket.landlord_media[3]: Refreshing state... [id=haven-media-la-004]

Terraform used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # aws_s3_bucket.landlord_media[0] will be created
  + resource "aws_s3_bucket" "landlord_media" {
      + acceleration_status         = (known after apply)
      + acl                         = (known after apply)
      + arn                         = (known after apply)
      + bucket                      = "haven-media-la-001"
      + bucket_domain_name          = (known after apply)
      + bucket_prefix               = (known after apply)
      + bucket_regional_domain_name = (known after apply)
      + force_destroy               = false
      + hosted_zone_id              = (known after apply)
      + id                          = (known after apply)
      + object_lock_enabled         = (known after apply)
      + policy                      = (known after apply)
      + region                      = (known after apply)
      + request_payer               = (known after apply)
      + tags                        = {
          + "landlord_account_id" = "la-001"
        }
      + tags_all                    = {
          + "landlord_account_id" = "la-001"
        }
      + website_domain              = (known after apply)
      + website_endpoint            = (known after apply)

      + cors_rule (known after apply)

      + grant (known after apply)

      + lifecycle_rule (known after apply)

      + logging (known after apply)

      + object_lock_configuration (known after apply)

      + replication_configuration (known after apply)

      + server_side_encryption_configuration (known after apply)

      + versioning (known after apply)

      + website (known after apply)
    }

  # aws_s3_bucket.landlord_media[1] will be created
  + resource "aws_s3_bucket" "landlord_media" {
      + acceleration_status         = (known after apply)
      + acl                         = (known after apply)
      + arn                         = (known after apply)
      + bucket                      = "haven-media-la-002"
      + bucket_domain_name          = (known after apply)
      + bucket_prefix               = (known after apply)
      + bucket_regional_domain_name = (known after apply)
      + force_destroy               = false
      + hosted_zone_id              = (known after apply)
      + id                          = (known after apply)
      + object_lock_enabled         = (known after apply)
      + policy                      = (known after apply)
      + region                      = (known after apply)
      + request_payer               = (known after apply)
      + tags                        = {
          + "landlord_account_id" = "la-002"
        }
      + tags_all                    = {
          + "landlord_account_id" = "la-002"
        }
      + website_domain              = (known after apply)
      + website_endpoint            = (known after apply)

      + cors_rule (known after apply)

      + grant (known after apply)

      + lifecycle_rule (known after apply)

      + logging (known after apply)

      + object_lock_configuration (known after apply)

      + replication_configuration (known after apply)

      + server_side_encryption_configuration (known after apply)

      + versioning (known after apply)

      + website (known after apply)
    }

  # aws_s3_bucket.landlord_media[2] will be created
  + resource "aws_s3_bucket" "landlord_media" {
      + acceleration_status         = (known after apply)
      + acl                         = (known after apply)
      + arn                         = (known after apply)
      + bucket                      = "haven-media-la-003"
      + bucket_domain_name          = (known after apply)
      + bucket_prefix               = (known after apply)
      + bucket_regional_domain_name = (known after apply)
      + force_destroy               = false
      + hosted_zone_id              = (known after apply)
      + id                          = (known after apply)
      + object_lock_enabled         = (known after apply)
      + policy                      = (known after apply)
      + region                      = (known after apply)
      + request_payer               = (known after apply)
      + tags                        = {
          + "landlord_account_id" = "la-003"
        }
      + tags_all                    = {
          + "landlord_account_id" = "la-003"
        }
      + website_domain              = (known after apply)
      + website_endpoint            = (known after apply)

      + cors_rule (known after apply)

      + grant (known after apply)

      + lifecycle_rule (known after apply)

      + logging (known after apply)

      + object_lock_configuration (known after apply)

      + replication_configuration (known after apply)

      + server_side_encryption_configuration (known after apply)

      + versioning (known after apply)

      + website (known after apply)
    }

  # aws_s3_bucket.landlord_media[3] will be created
  + resource "aws_s3_bucket" "landlord_media" {
      + acceleration_status         = (known after apply)
      + acl                         = (known after apply)
      + arn                         = (known after apply)
      + bucket                      = "haven-media-la-004"
      + bucket_domain_name          = (known after apply)
      + bucket_prefix               = (known after apply)
      + bucket_regional_domain_name = (known after apply)
      + force_destroy               = false
      + hosted_zone_id              = (known after apply)
      + id                          = (known after apply)
      + object_lock_enabled         = (known after apply)
      + policy                      = (known after apply)
      + region                      = (known after apply)
      + request_payer               = (known after apply)
      + tags                        = {
          + "landlord_account_id" = "la-004"
        }
      + tags_all                    = {
          + "landlord_account_id" = "la-004"
        }
      + website_domain              = (known after apply)
      + website_endpoint            = (known after apply)

      + cors_rule (known after apply)

      + grant (known after apply)

      + lifecycle_rule (known after apply)

      + logging (known after apply)

      + object_lock_configuration (known after apply)

      + replication_configuration (known after apply)

      + server_side_encryption_configuration (known after apply)

      + versioning (known after apply)

      + website (known after apply)
    }

  # aws_s3_bucket.listing_media will be created
  + resource "aws_s3_bucket" "listing_media" {
      + acceleration_status         = (known after apply)
      + acl                         = (known after apply)
      + arn                         = (known after apply)
      + bucket                      = "haven-listing-media"
      + bucket_domain_name          = (known after apply)
      + bucket_prefix               = (known after apply)
      + bucket_regional_domain_name = (known after apply)
      + force_destroy               = false
      + hosted_zone_id              = (known after apply)
      + id                          = (known after apply)
      + object_lock_enabled         = (known after apply)
      + policy                      = (known after apply)
      + region                      = (known after apply)
      + request_payer               = (known after apply)
      + tags_all                    = (known after apply)
      + website_domain              = (known after apply)
      + website_endpoint            = (known after apply)

      + cors_rule (known after apply)

      + grant (known after apply)

      + lifecycle_rule (known after apply)

      + logging (known after apply)

      + object_lock_configuration (known after apply)

      + replication_configuration (known after apply)

      + server_side_encryption_configuration (known after apply)

      + versioning (known after apply)

      + website (known after apply)
    }

  # aws_s3_bucket_lifecycle_configuration.listing_media_archive will be created
  + resource "aws_s3_bucket_lifecycle_configuration" "listing_media_archive" {
      + bucket                                 = (known after apply)
      + expected_bucket_owner                  = (known after apply)
      + id                                     = (known after apply)
      + transition_default_minimum_object_size = "all_storage_classes_128K"

      + rule {
          + id     = "archive-sold-listing-photos"
          + status = "Enabled"
            # (1 unchanged attribute hidden)

          + filter {
                # (1 unchanged attribute hidden)
            }

          + transition {
              + days          = 30
              + storage_class = "GLACIER"
            }
        }
    }

Plan: 6 to add, 0 to change, 0 to destroy.

─────────────────────────────────────────────────────────────────────────────

Saved the plan to: tfplan

To perform exactly these actions, run the following command to apply:
    terraform apply "tfplan"
```
Exit code: `0`.

> **Why the plan shows the seeded buckets as creates:** the provider is configured with dummy
> credentials and this command performs the default refresh. The seeded state is present, but a
> refresh against a non-existent AWS account cannot confirm the objects, so Terraform plans them
> as creates. This does not change the checked-in `terraform.tfstate`. The B0-specific
> `-refresh=false` reproduction, which diffs directly against the seeded state and exposes the
> index shift, is documented in `B0.md`.

## 3. Export the plan as JSON

```console
$ terraform show -json tfplan > tfplan.json
```
Exit code: `0`. The command writes JSON to the file and has no stdout. The generated file has
`6` entries in `resource_changes`:

```text
aws_s3_bucket.landlord_media[0]                              ["create"]
aws_s3_bucket.landlord_media[1]                              ["create"]
aws_s3_bucket.landlord_media[2]                              ["create"]
aws_s3_bucket.landlord_media[3]                              ["create"]
aws_s3_bucket.listing_media                                   ["create"]
aws_s3_bucket_lifecycle_configuration.listing_media_archive  ["create"]
```

## 4. Cost-tag check, run 1

```console
$ cd ..
$ ./venv/bin/python scripts/cost_tag_check.py terraform/tfplan.json
Missing 'landlord_account_id' tag on resource: aws_s3_bucket.listing_media
```
Exit code: `1`. The check found a real violation: the shared `listing_media` bucket has no
`landlord_account_id` tag. The four `landlord_media` buckets pass; the non-taggable lifecycle
configuration is skipped.

## 5. Cost-tag check, run 2 (idempotency)

```console
$ ./venv/bin/python scripts/cost_tag_check.py terraform/tfplan.json
Missing 'landlord_account_id' tag on resource: aws_s3_bucket.listing_media
```
Exit code: `1`. The output is byte-for-byte identical to run 1. The two captured output files
hash to the same SHA-256:

```text
358c630ef833fb00fe563198fa1a8ab8b0f22fb6bfaf5e6468760804fe189be9  run1
358c630ef833fb00fe563198fa1a8ab8b0f22fb6bfaf5e6468760804fe189be9  run2
```

The key that makes this idempotent is `resource_changes[].address`, documented in
`DESIGN_NOTES.md`.

## 6. Cost-tag check control run (detected violation corrected)

To prove the same plan passes once the missing tag is supplied, a temporary copy of the plan was
made with `landlord_account_id = "la-001"` added to `aws_s3_bucket.listing_media`. This copy is
not committed; it is a control run only.

```console
$ ./venv/bin/python scripts/cost_tag_check.py /tmp/haven_tfplan_fixed.json
All created/updated taggable resources have 'landlord_account_id'.
```
Exit code: `0`.

## 7. Access-control tests (B2 part 1)

```console
$ ./venv/bin/pytest tests/test_access_control.py -v
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-9.2.0, pluggy-1.7.0 -- /Users/purveshparasramshende/project-folder/haven-infra-assessment-/venv/bin/python3.13
cachedir: .pytest_cache
rootdir: /Users/purveshparasramshende/project-folder/haven-infra-assessment-
configfile: pytest.ini
collecting ... collected 30 items

tests/test_access_control.py::TestSameLandlordAccount::test_same_account_allows_access[pm-001-rep-001] PASSED [  3%]
tests/test_access_control.py::TestSameLandlordAccount::test_same_account_allows_access[pm-002-rep-002] PASSED [  6%]
tests/test_access_control.py::TestSameLandlordAccount::test_every_seeded_manager_can_read_own_tenant_report PASSED [ 10%]
tests/test_access_control.py::TestCrossLandlordAccount::test_cross_account_denies_access[pm-001-rep-002] PASSED [ 13%]
tests/test_access_control.py::TestCrossLandlordAccount::test_cross_account_denies_access[pm-002-rep-001] PASSED [ 16%]
tests/test_access_control.py::TestCrossLandlordAccount::test_cross_account_denied_with_valid_tenant_reference PASSED [ 20%]
tests/test_access_control.py::TestCrossLandlordAccount::test_cross_account_denied_when_report_tenant_is_forged PASSED [ 23%]
tests/test_access_control.py::TestCrossLandlordAccount::test_every_cross_account_pair_is_denied PASSED [ 26%]
tests/test_access_control.py::TestFailClosed::test_none_actor_denied PASSED [ 30%]
tests/test_access_control.py::TestFailClosed::test_none_report_denied PASSED [ 33%]
tests/test_access_control.py::TestFailClosed::test_missing_actor_landlord_account_denied[] PASSED [ 36%]
tests/test_access_control.py::TestFailClosed::test_missing_actor_landlord_account_denied[   ] PASSED [ 40%]
tests/test_access_control.py::TestFailClosed::test_missing_actor_landlord_account_denied[None] PASSED [ 43%]
tests/test_access_control.py::TestFailClosed::test_missing_report_tenant_id_denied[] PASSED [ 46%]
tests/test_access_control.py::TestFailClosed::test_missing_report_tenant_id_denied[   ] PASSED [ 50%]
tests/test_access_control.py::TestFailClosed::test_missing_report_tenant_id_denied[None] PASSED [ 53%]
tests/test_access_control.py::TestFailClosed::test_unknown_report_tenant_denied PASSED [ 56%]
tests/test_access_control.py::TestFailClosed::test_unknown_tenant_list_denied PASSED [ 60%]
tests/test_access_control.py::TestFailClosed::test_none_tenant_list_denied PASSED [ 63%]
tests/test_access_control.py::TestFailClosed::test_tenant_without_property_denied[] PASSED [ 66%]
tests/test_access_control.py::TestFailClosed::test_tenant_without_property_denied[   ] PASSED [ 70%]
tests/test_access_control.py::TestFailClosed::test_tenant_without_property_denied[None] PASSED [ 73%]
tests/test_access_control.py::TestFailClosed::test_unknown_property_denied PASSED [ 76%]
tests/test_access_control.py::TestFailClosed::test_none_property_list_denied PASSED [ 80%]
tests/test_access_control.py::TestFailClosed::test_unassigned_property_landlord_account_denied[] PASSED [ 83%]
tests/test_access_control.py::TestFailClosed::test_unassigned_property_landlord_account_denied[   ] PASSED [ 86%]
tests/test_access_control.py::TestFailClosed::test_unassigned_property_landlord_account_denied[None] PASSED [ 90%]
tests/test_access_control.py::TestFailClosed::test_actor_landlord_account_must_match_property PASSED [ 93%]
tests/test_access_control.py::TestFailClosed::test_report_tenant_must_resolve_to_a_property PASSED [ 96%]
tests/test_access_control.py::TestFailClosed::test_empty_records_deny_access PASSED [100%]

============================== 30 passed in 0.03s ==============================
```
Exit code: `0`. **30 passed.**

## 8. Cost-tag tests (B2 part 2)

```console
$ ./venv/bin/pytest tests/test_cost_tag_check.py -v
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-9.2.0, pluggy-1.7.0 -- /Users/purveshparasramshende/project-folder/haven-infra-assessment-/venv/bin/python3.13
cachedir: .pytest_cache
rootdir: /Users/purveshparasramshende/project-folder/haven-infra-assessment-
configfile: pytest.ini
collecting ... collected 58 items

tests/test_cost_tag_check.py::TestFixturePlan::test_fixture_flags_only_missing_landlord_tags PASSED [  1%]
tests/test_cost_tag_check.py::TestFixturePlan::test_fixture_does_not_flag_passing_or_skipped_resources PASSED [  3%]
tests/test_cost_tag_check.py::TestFixturePlan::test_fixture_violations_are_deduplicated PASSED [  5%]
tests/test_cost_tag_check.py::TestFixturePlan::test_fixture_rerun_is_idempotent PASSED [  6%]
tests/test_cost_tag_check.py::TestTenantOnlyTagFailure::test_tenant_only_tag_fails_for_any_resource_type[aws_s3_bucket] PASSED [  8%]
tests/test_cost_tag_check.py::TestTenantOnlyTagFailure::test_tenant_only_tag_fails_for_any_resource_type[aws_lambda_function] PASSED [ 10%]
tests/test_cost_tag_check.py::TestTenantOnlyTagFailure::test_tenant_only_tag_fails_for_any_resource_type[aws_db_instance] PASSED [ 12%]
tests/test_cost_tag_check.py::TestTenantOnlyTagFailure::test_tenant_only_tag_fails_for_any_resource_type[aws_unknown_future_resource] PASSED [ 13%]
tests/test_cost_tag_check.py::TestTenantOnlyTagFailure::test_tenant_tag_does_not_satisfy_landlord_tag PASSED [ 15%]
tests/test_cost_tag_check.py::TestTenantOnlyTagFailure::test_landlord_tag_alongside_tenant_tag_passes PASSED [ 17%]
tests/test_cost_tag_check.py::TestLandlordTagPasses::test_landlord_tag_in_either_attribute_passes[tags] PASSED [ 18%]
tests/test_cost_tag_check.py::TestLandlordTagPasses::test_landlord_tag_in_either_attribute_passes[tags_all] PASSED [ 20%]
tests/test_cost_tag_check.py::TestLandlordTagPasses::test_provider_default_tag_in_tags_all_passes PASSED [ 22%]
tests/test_cost_tag_check.py::TestLandlordTagPasses::test_any_non_empty_landlord_id_passes[la-001] PASSED [ 24%]
tests/test_cost_tag_check.py::TestLandlordTagPasses::test_any_non_empty_landlord_id_passes[la-002] PASSED [ 25%]
tests/test_cost_tag_check.py::TestLandlordTagPasses::test_any_non_empty_landlord_id_passes[la-999] PASSED [ 27%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_null_empty_or_tenant_only_tags_fail_cleanly[after0] PASSED [ 29%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_null_empty_or_tenant_only_tags_fail_cleanly[after1] PASSED [ 31%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_null_empty_or_tenant_only_tags_fail_cleanly[after2] PASSED [ 32%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_null_empty_or_tenant_only_tags_fail_cleanly[after3] PASSED [ 34%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_null_empty_or_tenant_only_tags_fail_cleanly[after4] PASSED [ 36%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_null_empty_or_tenant_only_tags_fail_cleanly[after5] PASSED [ 37%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_null_empty_or_tenant_only_tags_fail_cleanly[after6] PASSED [ 39%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_unknown_tags_fail_closed PASSED [ 41%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_non_taggable_resource_is_skipped_cleanly PASSED [ 43%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_taggable_detection_uses_tags_or_tags_all_only PASSED [ 44%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_non_mapping_tag_attribute_does_not_crash PASSED [ 46%]
tests/test_cost_tag_check.py::TestActionFiltering::test_non_create_update_actions_are_skipped[actions0] PASSED [ 48%]
tests/test_cost_tag_check.py::TestActionFiltering::test_non_create_update_actions_are_skipped[actions1] PASSED [ 50%]
tests/test_cost_tag_check.py::TestActionFiltering::test_non_create_update_actions_are_skipped[actions2] PASSED [ 51%]
tests/test_cost_tag_check.py::TestActionFiltering::test_create_update_and_replace_are_checked[actions0] PASSED [ 53%]
tests/test_cost_tag_check.py::TestActionFiltering::test_create_update_and_replace_are_checked[actions1] PASSED [ 55%]
tests/test_cost_tag_check.py::TestActionFiltering::test_create_update_and_replace_are_checked[actions2] PASSED [ 56%]
tests/test_cost_tag_check.py::TestActionFiltering::test_create_update_and_replace_are_checked[actions3] PASSED [ 58%]
tests/test_cost_tag_check.py::TestActionFiltering::test_delete_without_after_is_skipped PASSED [ 60%]
tests/test_cost_tag_check.py::TestActionFiltering::test_data_source_is_skipped PASSED [ 62%]
tests/test_cost_tag_check.py::TestActionFiltering::test_missing_mode_defaults_to_managed PASSED [ 63%]
tests/test_cost_tag_check.py::TestActionFiltering::test_change_body_none_is_skipped PASSED [ 65%]
tests/test_cost_tag_check.py::TestActionFiltering::test_missing_actions_is_skipped PASSED [ 67%]
tests/test_cost_tag_check.py::TestActionFiltering::test_non_list_actions_is_skipped PASSED [ 68%]
tests/test_cost_tag_check.py::TestActionFiltering::test_non_mapping_after_is_skipped PASSED [ 70%]
tests/test_cost_tag_check.py::TestActionFiltering::test_non_mapping_after_unknown_is_tolerated PASSED [ 72%]
tests/test_cost_tag_check.py::TestActionFiltering::test_after_helpers_tolerate_non_mapping_change_body PASSED [ 74%]
tests/test_cost_tag_check.py::TestPlanShape::test_empty_plan_passes PASSED [ 75%]
tests/test_cost_tag_check.py::TestPlanShape::test_null_resource_changes_passes PASSED [ 77%]
tests/test_cost_tag_check.py::TestPlanShape::test_non_list_resource_changes_passes PASSED [ 79%]
tests/test_cost_tag_check.py::TestPlanShape::test_non_dict_change_entries_are_skipped PASSED [ 81%]
tests/test_cost_tag_check.py::TestPlanShape::test_pathlib_path_is_accepted PASSED [ 82%]
tests/test_cost_tag_check.py::TestAddressAndDedup::test_address_fallback_is_stable PASSED [ 84%]
tests/test_cost_tag_check.py::TestAddressAndDedup::test_blank_address_uses_fallback PASSED [ 86%]
tests/test_cost_tag_check.py::TestAddressAndDedup::test_violations_are_sorted_and_deduplicated PASSED [ 87%]
tests/test_cost_tag_check.py::TestAddressAndDedup::test_output_order_does_not_depend_on_input_order PASSED [ 89%]
tests/test_cost_tag_check.py::TestCli::test_main_returns_zero_for_clean_plan PASSED [ 91%]
tests/test_cost_tag_check.py::TestCli::test_main_returns_one_for_violation PASSED [ 93%]
tests/test_cost_tag_check.py::TestCli::test_missing_file_returns_two PASSED [ 94%]
tests/test_cost_tag_check.py::TestCli::test_invalid_json_returns_two PASSED [ 96%]
tests/test_cost_tag_check.py::TestCli::test_non_object_json_returns_two PASSED [ 98%]
tests/test_cost_tag_check.py::TestCli::test_module_entrypoint_exits_with_check_code PASSED [100%]

============================== 58 passed in 0.06s ==============================
```
Exit code: `0`. **58 passed.**

## 9. Full test suite

```console
$ ./venv/bin/pytest -v
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-9.2.0, pluggy-1.7.0 -- /Users/purveshparasramshende/project-folder/haven-infra-assessment-/venv/bin/python3.13
cachedir: .pytest_cache
rootdir: /Users/purveshparasramshende/project-folder/haven-infra-assessment-
configfile: pytest.ini
testpaths: tests
collecting ... collected 88 items

tests/test_access_control.py::TestSameLandlordAccount::test_same_account_allows_access[pm-001-rep-001] PASSED [  1%]
tests/test_access_control.py::TestSameLandlordAccount::test_same_account_allows_access[pm-002-rep-002] PASSED [  2%]
tests/test_access_control.py::TestSameLandlordAccount::test_every_seeded_manager_can_read_own_tenant_report PASSED [  3%]
tests/test_access_control.py::TestCrossLandlordAccount::test_cross_account_denies_access[pm-001-rep-002] PASSED [  4%]
tests/test_access_control.py::TestCrossLandlordAccount::test_cross_account_denies_access[pm-002-rep-001] PASSED [  5%]
tests/test_access_control.py::TestCrossLandlordAccount::test_cross_account_denied_with_valid_tenant_reference PASSED [  6%]
tests/test_access_control.py::TestCrossLandlordAccount::test_cross_account_denied_when_report_tenant_is_forged PASSED [  7%]
tests/test_access_control.py::TestCrossLandlordAccount::test_every_cross_account_pair_is_denied PASSED [  9%]
tests/test_access_control.py::TestFailClosed::test_none_actor_denied PASSED [ 10%]
tests/test_access_control.py::TestFailClosed::test_none_report_denied PASSED [ 11%]
tests/test_access_control.py::TestFailClosed::test_missing_actor_landlord_account_denied[] PASSED [ 12%]
tests/test_access_control.py::TestFailClosed::test_missing_actor_landlord_account_denied[   ] PASSED [ 13%]
tests/test_access_control.py::TestFailClosed::test_missing_actor_landlord_account_denied[None] PASSED [ 14%]
tests/test_access_control.py::TestFailClosed::test_missing_report_tenant_id_denied[] PASSED [ 15%]
tests/test_access_control.py::TestFailClosed::test_missing_report_tenant_id_denied[   ] PASSED [ 17%]
tests/test_access_control.py::TestFailClosed::test_missing_report_tenant_id_denied[None] PASSED [ 18%]
tests/test_access_control.py::TestFailClosed::test_unknown_report_tenant_denied PASSED [ 19%]
tests/test_access_control.py::TestFailClosed::test_unknown_tenant_list_denied PASSED [ 20%]
tests/test_access_control.py::TestFailClosed::test_none_tenant_list_denied PASSED [ 21%]
tests/test_access_control.py::TestFailClosed::test_tenant_without_property_denied[] PASSED [ 22%]
tests/test_access_control.py::TestFailClosed::test_tenant_without_property_denied[   ] PASSED [ 23%]
tests/test_access_control.py::TestFailClosed::test_tenant_without_property_denied[None] PASSED [ 25%]
tests/test_access_control.py::TestFailClosed::test_unknown_property_denied PASSED [ 26%]
tests/test_access_control.py::TestFailClosed::test_none_property_list_denied PASSED [ 27%]
tests/test_access_control.py::TestFailClosed::test_unassigned_property_landlord_account_denied[] PASSED [ 28%]
tests/test_access_control.py::TestFailClosed::test_unassigned_property_landlord_account_denied[   ] PASSED [ 29%]
tests/test_access_control.py::TestFailClosed::test_unassigned_property_landlord_account_denied[None] PASSED [ 30%]
tests/test_access_control.py::TestFailClosed::test_actor_landlord_account_must_match_property PASSED [ 31%]
tests/test_access_control.py::TestFailClosed::test_report_tenant_must_resolve_to_a_property PASSED [ 32%]
tests/test_access_control.py::TestFailClosed::test_empty_records_deny_access PASSED [ 34%]
tests/test_cost_tag_check.py::TestFixturePlan::test_fixture_flags_only_missing_landlord_tags PASSED [ 35%]
tests/test_cost_tag_check.py::TestFixturePlan::test_fixture_does_not_flag_passing_or_skipped_resources PASSED [ 36%]
tests/test_cost_tag_check.py::TestFixturePlan::test_fixture_violations_are_deduplicated PASSED [ 37%]
tests/test_cost_tag_check.py::TestFixturePlan::test_fixture_rerun_is_idempotent PASSED [ 38%]
tests/test_cost_tag_check.py::TestTenantOnlyTagFailure::test_tenant_only_tag_fails_for_any_resource_type[aws_s3_bucket] PASSED [ 39%]
tests/test_cost_tag_check.py::TestTenantOnlyTagFailure::test_tenant_only_tag_fails_for_any_resource_type[aws_lambda_function] PASSED [ 40%]
tests/test_cost_tag_check.py::TestTenantOnlyTagFailure::test_tenant_only_tag_fails_for_any_resource_type[aws_db_instance] PASSED [ 42%]
tests/test_cost_tag_check.py::TestTenantOnlyTagFailure::test_tenant_only_tag_fails_for_any_resource_type[aws_unknown_future_resource] PASSED [ 43%]
tests/test_cost_tag_check.py::TestTenantOnlyTagFailure::test_tenant_tag_does_not_satisfy_landlord_tag PASSED [ 44%]
tests/test_cost_tag_check.py::TestTenantOnlyTagFailure::test_landlord_tag_alongside_tenant_tag_passes PASSED [ 45%]
tests/test_cost_tag_check.py::TestLandlordTagPasses::test_landlord_tag_in_either_attribute_passes[tags] PASSED [ 46%]
tests/test_cost_tag_check.py::TestLandlordTagPasses::test_landlord_tag_in_either_attribute_passes[tags_all] PASSED [ 47%]
tests/test_cost_tag_check.py::TestLandlordTagPasses::test_provider_default_tag_in_tags_all_passes PASSED [ 48%]
tests/test_cost_tag_check.py::TestLandlordTagPasses::test_any_non_empty_landlord_id_passes[la-001] PASSED [ 50%]
tests/test_cost_tag_check.py::TestLandlordTagPasses::test_any_non_empty_landlord_id_passes[la-002] PASSED [ 51%]
tests/test_cost_tag_check.py::TestLandlordTagPasses::test_any_non_empty_landlord_id_passes[la-999] PASSED [ 52%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_null_empty_or_tenant_only_tags_fail_cleanly[after0] PASSED [ 53%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_null_empty_or_tenant_only_tags_fail_cleanly[after1] PASSED [ 54%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_null_empty_or_tenant_only_tags_fail_cleanly[after2] PASSED [ 55%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_null_empty_or_tenant_only_tags_fail_cleanly[after3] PASSED [ 56%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_null_empty_or_tenant_only_tags_fail_cleanly[after4] PASSED [ 57%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_null_empty_or_tenant_only_tags_fail_cleanly[after5] PASSED [ 59%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_null_empty_or_tenant_only_tags_fail_cleanly[after6] PASSED [ 60%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_unknown_tags_fail_closed PASSED [ 61%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_non_taggable_resource_is_skipped_cleanly PASSED [ 62%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_taggable_detection_uses_tags_or_tags_all_only PASSED [ 63%]
tests/test_cost_tag_check.py::TestNullAndMissingTags::test_non_mapping_tag_attribute_does_not_crash PASSED [ 64%]
tests/test_cost_tag_check.py::TestActionFiltering::test_non_create_update_actions_are_skipped[actions0] PASSED [ 65%]
tests/test_cost_tag_check.py::TestActionFiltering::test_non_create_update_actions_are_skipped[actions1] PASSED [ 67%]
tests/test_cost_tag_check.py::TestActionFiltering::test_non_create_update_actions_are_skipped[actions2] PASSED [ 68%]
tests/test_cost_tag_check.py::TestActionFiltering::test_create_update_and_replace_are_checked[actions0] PASSED [ 69%]
tests/test_cost_tag_check.py::TestActionFiltering::test_create_update_and_replace_are_checked[actions1] PASSED [ 70%]
tests/test_cost_tag_check.py::TestActionFiltering::test_create_update_and_replace_are_checked[actions2] PASSED [ 71%]
tests/test_cost_tag_check.py::TestActionFiltering::test_create_update_and_replace_are_checked[actions3] PASSED [ 72%]
tests/test_cost_tag_check.py::TestActionFiltering::test_delete_without_after_is_skipped PASSED [ 73%]
tests/test_cost_tag_check.py::TestActionFiltering::test_data_source_is_skipped PASSED [ 75%]
tests/test_cost_tag_check.py::TestActionFiltering::test_missing_mode_defaults_to_managed PASSED [ 76%]
tests/test_cost_tag_check.py::TestActionFiltering::test_change_body_none_is_skipped PASSED [ 77%]
tests/test_cost_tag_check.py::TestActionFiltering::test_missing_actions_is_skipped PASSED [ 78%]
tests/test_cost_tag_check.py::TestActionFiltering::test_non_list_actions_is_skipped PASSED [ 79%]
tests/test_cost_tag_check.py::TestActionFiltering::test_non_mapping_after_is_skipped PASSED [ 80%]
tests/test_cost_tag_check.py::TestActionFiltering::test_non_mapping_after_unknown_is_tolerated PASSED [ 81%]
tests/test_cost_tag_check.py::TestActionFiltering::test_after_helpers_tolerate_non_mapping_change_body PASSED [ 82%]
tests/test_cost_tag_check.py::TestPlanShape::test_empty_plan_passes PASSED [ 84%]
tests/test_cost_tag_check.py::TestPlanShape::test_null_resource_changes_passes PASSED [ 85%]
tests/test_cost_tag_check.py::TestPlanShape::test_non_list_resource_changes_passes PASSED [ 86%]
tests/test_cost_tag_check.py::TestPlanShape::test_non_dict_change_entries_are_skipped PASSED [ 87%]
tests/test_cost_tag_check.py::TestPlanShape::test_pathlib_path_is_accepted PASSED [ 88%]
tests/test_cost_tag_check.py::TestAddressAndDedup::test_address_fallback_is_stable PASSED [ 89%]
tests/test_cost_tag_check.py::TestAddressAndDedup::test_blank_address_uses_fallback PASSED [ 90%]
tests/test_cost_tag_check.py::TestAddressAndDedup::test_violations_are_sorted_and_deduplicated PASSED [ 92%]
tests/test_cost_tag_check.py::TestAddressAndDedup::test_output_order_does_not_depend_on_input_order PASSED [ 93%]
tests/test_cost_tag_check.py::TestCli::test_main_returns_zero_for_clean_plan PASSED [ 94%]
tests/test_cost_tag_check.py::TestCli::test_main_returns_one_for_violation PASSED [ 95%]
tests/test_cost_tag_check.py::TestCli::test_missing_file_returns_two PASSED [ 96%]
tests/test_cost_tag_check.py::TestCli::test_invalid_json_returns_two PASSED [ 97%]
tests/test_cost_tag_check.py::TestCli::test_non_object_json_returns_two PASSED [ 98%]
tests/test_cost_tag_check.py::TestCli::test_module_entrypoint_exits_with_check_code PASSED [100%]

============================== 88 passed in 0.08s ==============================
```
Exit code: `0`. **88 passed.**

## 10. Coverage

```console
$ ./venv/bin/python -m coverage run --source=app,scripts -m pytest -q
$ ./venv/bin/python -m coverage report -m
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
app/__init__.py                 0      0   100%
app/access_control.py          24      0   100%
app/models.py                  26      0   100%
app/seed_data.py                6      0   100%
scripts/cost_tag_check.py      97      0   100%
---------------------------------------------------------
TOTAL                         153      0   100%
```
The two B2 modules are at **100% line coverage**; the total across `app/` and `scripts/` is also
100%.

## 11. Commit history produced by this work

```console
$ git log --oneline -7
02fb993 docs: refine B1 glacier pricing and lifecycle guidance
f7d7723 feat: add generic idempotent landlord cost tag check and tests
9ce5689 feat: implement landlord-scoped screening report access and unit tests
e9ab50d docs: answer B1 glacier early deletion cost question
f5ee2e8 docs: answer B0 terraform count index shifting question
e3dfeb8 chore: inspect repository and fix module and import hygiene
cdd0128 feat: complete B2 implementation and add documentation files
```

The final documentation commit is added after this file. No commit was squashed, amended, or
rebased.
