from app.models import PropertyManager, ScreeningReport, Property, Tenant

def can_access_screening_report(
    actor: PropertyManager,
    report: ScreeningReport,
    *,
    properties: list[Property],
    tenants: list[Tenant],
) -> bool:
    if not actor or not report or not actor.landlord_account_id or not report.tenant_id:
        return False

    tenants_by_id = {tenant.id: tenant for tenant in tenants}
    tenant = tenants_by_id.get(report.tenant_id)
    if tenant is None or not tenant.property_id:
        return False

    properties_by_id = {prop.id: prop for prop in properties}
    prop = properties_by_id.get(tenant.property_id)
    if prop is None or not prop.landlord_account_id:
        return False

    return actor.landlord_account_id == prop.landlord_account_id
