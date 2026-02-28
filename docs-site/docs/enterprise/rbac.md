# Role-Based Access Control (RBAC)

HoneyAegis provides fine-grained RBAC for enterprise deployments.

## Roles

| Role | Description | Use Case |
|---|---|---|
| **Super Admin** | Full system access, all permissions | Platform owner |
| **Admin** | Tenant management, user management, config | Security team lead |
| **Analyst** | Read/write sessions, alerts, tokens, reports | SOC analyst |
| **Viewer** | Read-only access to all data | Executive, auditor |

## Permissions

Permissions are granular and role-based. Each role inherits permissions from the role below it.

### Viewer Permissions
- `sessions:read`, `alerts:read`, `sensors:read`, `tokens:read`
- `webhooks:read`, `config:read`, `reports:read`, `plugins:read`
- `intel:read`, `sandbox:read`, `billing:read`

### Analyst Permissions (includes Viewer)
- `sessions:export`, `alerts:manage`, `tokens:manage`
- `reports:generate`, `intel:manage`, `sandbox:submit`

### Admin Permissions (includes Analyst)
- `sensors:manage`, `webhooks:manage`, `config:manage`
- `users:read`, `users:manage`, `tenants:read`
- `plugins:manage`, `audit:read`, `billing:manage`

### Super Admin Permissions
- All permissions including `system:admin`, `tenants:manage`

## API Endpoints

```
GET    /api/v1/rbac/roles                  # List all roles
GET    /api/v1/rbac/roles/{role_name}      # Get role details
POST   /api/v1/rbac/check                  # Check permission
GET    /api/v1/rbac/permissions            # List all permissions
```

## Example: Check Permission

```bash
curl -X POST http://localhost:8000/api/v1/rbac/check \
  -H "Content-Type: application/json" \
  -d '{"role": "analyst", "permission": "sessions:export"}'

# Response: {"role": "analyst", "permission": "sessions:export", "allowed": true}
```
