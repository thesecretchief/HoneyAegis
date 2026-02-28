# SSO / OIDC Integration

HoneyAegis supports Single Sign-On via OpenID Connect for enterprise deployments.

## Supported Providers

| Provider | Template | Status |
|---|---|---|
| Keycloak | `keycloak` | Stub (ready for configuration) |
| Okta | `okta` | Stub (ready for configuration) |
| Azure AD | `azure_ad` | Stub (ready for configuration) |
| Google Workspace | `google` | Stub (ready for configuration) |

## Configuration

### 1. Check Available Templates

```bash
GET /api/v1/sso/templates
# Response: {"templates": ["azure_ad", "google", "keycloak", "okta"]}
```

### 2. Configure a Provider

```bash
POST /api/v1/sso/configure
{
  "template": "keycloak",
  "name": "Corporate SSO",
  "client_id": "honeyaegis",
  "client_secret": "your-client-secret",
  "issuer_url": "https://keycloak.example.com/realms/honeyaegis"
}
```

### 3. Check Status

```bash
GET /api/v1/sso/status
```

## OIDC → RBAC Role Mapping

OIDC group claims are mapped to HoneyAegis roles:

| OIDC Group | HoneyAegis Role |
|---|---|
| `honeyaegis-superadmins` | Super Admin |
| `honeyaegis-admins` | Admin |
| `honeyaegis-analysts` | Analyst |
| (default) | Viewer |

Configure custom group mappings in your IdP to control access levels.

## Security Notes

- SSO is currently a stub — token exchange requires a real IdP
- State parameters use `secrets.token_urlsafe(32)` for CSRF protection
- OIDC subjects are hashed before internal storage
