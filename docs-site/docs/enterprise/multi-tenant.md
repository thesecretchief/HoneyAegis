# Multi-Tenant Isolation

HoneyAegis provides complete tenant isolation for MSP deployments.

## How It Works

- Every database table has a `tenant_id` column
- JWT tokens include the tenant context
- All queries are scoped to the authenticated user's tenant
- Cross-tenant access is prevented at the query level

## Tenant Setup

1. Create a tenant via the API
2. Assign users to the tenant
3. Register sensors under the tenant
4. Configure branding (logo, colors, display name)

## Client Portals

Each tenant gets a view-only portal at `/client/{tenant-slug}`:

- No authentication required (identified by slug)
- Read-only access to attack sessions and stats
- Auto-refreshes every 30 seconds
- Branded with tenant colors and logo

## Branding

Per-tenant branding includes:
- Display name
- Logo URL
- Primary color
- Custom client portal URL

See the [MSP guide](https://github.com/thesecretchief/HoneyAegis/blob/main/docs/msp-guide.md) for detailed setup instructions.
