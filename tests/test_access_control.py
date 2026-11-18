import unittest
from app.access_control import can_access_screening_report
from app.seed_data import PROPERTIES, PROPERTY_MANAGERS, SCREENING_REPORTS, TENANTS


def _by_id(records, record_id: str):
    return next(r for r in records if r.id == record_id)


class TestAccessControl(unittest.TestCase):
    def test_same_account_allows_access(self):
        pm_001 = _by_id(PROPERTY_MANAGERS, "pm-001")
        pm_002 = _by_id(PROPERTY_MANAGERS, "pm-002")
        rep_001 = _by_id(SCREENING_REPORTS, "rep-001")
        rep_002 = _by_id(SCREENING_REPORTS, "rep-002")

        self.assertTrue(can_access_screening_report(pm_001, rep_001, properties=PROPERTIES, tenants=TENANTS))
        self.assertTrue(can_access_screening_report(pm_002, rep_002, properties=PROPERTIES, tenants=TENANTS))

    def test_cross_account_denies_access(self):
        pm_001 = _by_id(PROPERTY_MANAGERS, "pm-001")
        pm_002 = _by_id(PROPERTY_MANAGERS, "pm-002")
        rep_001 = _by_id(SCREENING_REPORTS, "rep-001")
        rep_002 = _by_id(SCREENING_REPORTS, "rep-002")

        self.assertFalse(can_access_screening_report(pm_001, rep_002, properties=PROPERTIES, tenants=TENANTS))
        self.assertFalse(can_access_screening_report(pm_002, rep_001, properties=PROPERTIES, tenants=TENANTS))

    def test_fail_closed_when_missing(self):
        pm_001 = _by_id(PROPERTY_MANAGERS, "pm-001")
        rep_001 = _by_id(SCREENING_REPORTS, "rep-001")

        self.assertFalse(can_access_screening_report(pm_001, rep_001, properties=PROPERTIES, tenants=[]))
        self.assertFalse(can_access_screening_report(pm_001, rep_001, properties=[], tenants=TENANTS))


if __name__ == "__main__":
    unittest.main()
