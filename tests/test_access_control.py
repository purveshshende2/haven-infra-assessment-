"""Unit tests for landlord-scoped screening report access.

Coverage focuses on the authorization boundary, not the seeded records:

* same landlord account -> allowed
* different landlord account -> denied, even with a valid tenant/report reference
* missing, unassigned, or unknown ownership data -> denied (fail closed)
"""
from dataclasses import replace

import pytest

from app.access_control import can_access_screening_report
from app.models import Property, PropertyManager, ScreeningReport, Tenant
from app.seed_data import (
    PROPERTIES,
    PROPERTY_MANAGERS,
    SCREENING_REPORTS,
    TENANTS,
)


def _by_id(records, record_id):
    return next(record for record in records if record.id == record_id)


@pytest.fixture
def pm_001():
    return _by_id(PROPERTY_MANAGERS, "pm-001")


@pytest.fixture
def pm_002():
    return _by_id(PROPERTY_MANAGERS, "pm-002")


@pytest.fixture
def rep_001():
    return _by_id(SCREENING_REPORTS, "rep-001")


@pytest.fixture
def rep_002():
    return _by_id(SCREENING_REPORTS, "rep-002")


class TestSameLandlordAccount:
    @pytest.mark.parametrize(
        ("manager_id", "report_id"),
        [("pm-001", "rep-001"), ("pm-002", "rep-002")],
    )
    def test_same_account_allows_access(self, manager_id, report_id):
        actor = _by_id(PROPERTY_MANAGERS, manager_id)
        report = _by_id(SCREENING_REPORTS, report_id)

        assert (
            can_access_screening_report(
                actor,
                report,
                properties=PROPERTIES,
                tenants=TENANTS,
            )
            is True
        )

    def test_every_seeded_manager_can_read_own_tenant_report(self):
        for actor in PROPERTY_MANAGERS:
            own_property_ids = {
                prop.id
                for prop in PROPERTIES
                if prop.landlord_account_id == actor.landlord_account_id
            }
            own_tenant_ids = {
                tenant.id
                for tenant in TENANTS
                if tenant.property_id in own_property_ids
            }
            own_reports = [
                report
                for report in SCREENING_REPORTS
                if report.tenant_id in own_tenant_ids
            ]

            assert own_reports, f"{actor.id} should have at least one report"
            for report in own_reports:
                assert can_access_screening_report(
                    actor,
                    report,
                    properties=PROPERTIES,
                    tenants=TENANTS,
                )


class TestCrossLandlordAccount:
    @pytest.mark.parametrize(
        ("manager_id", "report_id"),
        [("pm-001", "rep-002"), ("pm-002", "rep-001")],
    )
    def test_cross_account_denies_access(self, manager_id, report_id):
        actor = _by_id(PROPERTY_MANAGERS, manager_id)
        report = _by_id(SCREENING_REPORTS, report_id)

        assert (
            can_access_screening_report(
                actor,
                report,
                properties=PROPERTIES,
                tenants=TENANTS,
            )
            is False
        )

    def test_cross_account_denied_with_valid_tenant_reference(self, pm_001, rep_002):
        """A valid tenant/report reference must not bypass the landlord boundary."""
        assert rep_002.tenant_id == "ten-002"
        assert can_access_screening_report(
            pm_001,
            rep_002,
            properties=PROPERTIES,
            tenants=TENANTS,
        ) is False

    def test_cross_account_denied_when_report_tenant_is_forged(
        self, pm_001, rep_001
    ):
        """A report whose tenant_id was pointed at another landlord is denied."""
        forged_report = replace(rep_001, tenant_id="ten-002")

        assert can_access_screening_report(
            pm_001,
            forged_report,
            properties=PROPERTIES,
            tenants=TENANTS,
        ) is False

    def test_every_cross_account_pair_is_denied(self):
        for actor in PROPERTY_MANAGERS:
            for report in SCREENING_REPORTS:
                tenant = _by_id(TENANTS, report.tenant_id)
                prop = _by_id(PROPERTIES, tenant.property_id)

                if prop.landlord_account_id == actor.landlord_account_id:
                    continue

                assert can_access_screening_report(
                    actor,
                    report,
                    properties=PROPERTIES,
                    tenants=TENANTS,
                ) is False


class TestFailClosed:
    def test_none_actor_denied(self, rep_001):
        assert (
            can_access_screening_report(
                None,
                rep_001,
                properties=PROPERTIES,
                tenants=TENANTS,
            )
            is False
        )

    def test_none_report_denied(self, pm_001):
        assert (
            can_access_screening_report(
                pm_001,
                None,
                properties=PROPERTIES,
                tenants=TENANTS,
            )
            is False
        )

    @pytest.mark.parametrize("landlord_account_id", ["", "   ", None])
    def test_missing_actor_landlord_account_denied(
        self, pm_001, rep_001, landlord_account_id
    ):
        actor = replace(pm_001, landlord_account_id=landlord_account_id)

        assert can_access_screening_report(
            actor,
            rep_001,
            properties=PROPERTIES,
            tenants=TENANTS,
        ) is False

    @pytest.mark.parametrize("tenant_id", ["", "   ", None])
    def test_missing_report_tenant_id_denied(self, pm_001, rep_001, tenant_id):
        report = replace(rep_001, tenant_id=tenant_id)

        assert can_access_screening_report(
            pm_001,
            report,
            properties=PROPERTIES,
            tenants=TENANTS,
        ) is False

    def test_unknown_report_tenant_denied(self, pm_001, rep_001):
        report = replace(rep_001, tenant_id="ten-does-not-exist")

        assert can_access_screening_report(
            pm_001,
            report,
            properties=PROPERTIES,
            tenants=TENANTS,
        ) is False

    def test_unknown_tenant_list_denied(self, pm_001, rep_001):
        assert can_access_screening_report(
            pm_001,
            rep_001,
            properties=PROPERTIES,
            tenants=[],
        ) is False

    def test_none_tenant_list_denied(self, pm_001, rep_001):
        assert can_access_screening_report(
            pm_001,
            rep_001,
            properties=PROPERTIES,
            tenants=None,
        ) is False

    @pytest.mark.parametrize("property_id", ["", "   ", None])
    def test_tenant_without_property_denied(self, pm_001, rep_001, property_id):
        tenant = replace(_by_id(TENANTS, "ten-001"), property_id=property_id)

        assert can_access_screening_report(
            pm_001,
            rep_001,
            properties=PROPERTIES,
            tenants=[tenant],
        ) is False

    def test_unknown_property_denied(self, pm_001, rep_001):
        assert can_access_screening_report(
            pm_001,
            rep_001,
            properties=[],
            tenants=TENANTS,
        ) is False

    def test_none_property_list_denied(self, pm_001, rep_001):
        assert can_access_screening_report(
            pm_001,
            rep_001,
            properties=None,
            tenants=TENANTS,
        ) is False

    @pytest.mark.parametrize("landlord_account_id", ["", "   ", None])
    def test_unassigned_property_landlord_account_denied(
        self, pm_001, landlord_account_id
    ):
        prop = Property(
            id="prop-unassigned",
            landlord_account_id=landlord_account_id,
            address="1 Unassigned Way",
        )
        tenant = Tenant(
            id="ten-unassigned",
            name="Unassigned Tenant",
            property_id=prop.id,
        )
        report = ScreeningReport(
            id="rep-unassigned",
            tenant_id=tenant.id,
            ssn_last4="0000",
            credit_score=700,
        )

        assert can_access_screening_report(
            pm_001,
            report,
            properties=[prop],
            tenants=[tenant],
        ) is False

    def test_actor_landlord_account_must_match_property(self, pm_001, rep_001):
        actor = replace(pm_001, landlord_account_id="la-does-not-exist")

        assert can_access_screening_report(
            actor,
            rep_001,
            properties=PROPERTIES,
            tenants=TENANTS,
        ) is False

    def test_report_tenant_must_resolve_to_a_property(self, pm_001):
        prop = Property(
            id="prop-orphan",
            landlord_account_id="la-001",
            address="2 Orphan Way",
        )
        tenant = Tenant(id="ten-orphan", name="Orphan", property_id="prop-missing")
        report = ScreeningReport(
            id="rep-orphan",
            tenant_id=tenant.id,
            ssn_last4="0000",
            credit_score=700,
        )

        assert can_access_screening_report(
            pm_001,
            report,
            properties=[prop],
            tenants=[tenant],
        ) is False

    def test_empty_records_deny_access(self, pm_001, rep_001):
        assert can_access_screening_report(
            pm_001,
            rep_001,
            properties=[],
            tenants=[],
        ) is False
