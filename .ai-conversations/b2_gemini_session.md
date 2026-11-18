## AI Prompts Used

The following prompts were used to assist with implementation, testing, and troubleshooting during this assessment:

1. **Tenant-Scoped Access Control & Cost Tagging Check (B2)**
   > "I'm working on the Haven infra repo based on the README domain model and existing codebase. Help me implement two things in Python:
   > 1) An access check (`can_access_screening_report`) ensuring a `PropertyManager` can only view screening reports under their own `landlord_account_id` (failing closed when records are missing), with unit tests for same-account allow and cross-account deny using `app/seed_data.py`.
   > 2) A generic, idempotent cost-tagging check (`scripts/cost_tag_check.py`) on `terraform show -json` plan output that inspects created/updated taggable resources and fails with a non-zero exit code if any taggable resource is missing `landlord_account_id`."

2. **S3 Glacier Lifecycle Cost Analysis (B1)**
   > "Reason through the S3 Glacier cost gotcha in `terraform/lifecycle.tf`: sold listings' photos archive to Glacier 30 days after upload, and a seller requests deletion on day 40 with immediate deletion. What does that cost given Glacier's minimum storage duration, and what changes should be made to the lifecycle configuration?"

3. **Python Test & Plan Script Troubleshooting**
   > "Debug `ImportError` circular imports when running `unittest` on `app/access_control.py` and `app/seed_data.py`, and refine `scripts/cost_tag_check.py` so non-taggable resources (such as `aws_s3_bucket_lifecycle_configuration`) and non-create/update actions are skipped cleanly."