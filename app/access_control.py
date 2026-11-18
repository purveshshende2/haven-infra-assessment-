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

    tenants_by_id = {tenant.id: tenant for tenant in tenants or []}
    tenant = tenants_by_id.get(tenant_id)
    if tenant is None:
        return False

    property_id = (tenant.property_id or "").strip()
    if not property_id:
        return False

    properties_by_id = {prop.id: prop for prop in properties or []}
    prop = properties_by_id.get(property_id)
    if prop is None:
        return False

    property_landlord_id = (prop.landlord_account_id or "").strip()
    if not property_landlord_id:
        return False

    return actor_landlord_id == property_landlord_id
