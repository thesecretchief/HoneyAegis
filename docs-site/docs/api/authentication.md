# Authentication API

HoneyAegis uses JWT (JSON Web Tokens) for API authentication. All API endpoints except `/api/v1/auth/login` require a valid Bearer token.

## Endpoints

### Login

```
POST /api/v1/auth/login
```

Authenticate with email and password to receive a JWT access token.

**Request:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@honeyaegis.local",
    "password": "your-password"
  }'
```

**Response:**

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
        "id": "usr_abc123",
        "email": "admin@honeyaegis.local",
        "role": "admin",
        "tenant_id": "ten_default"
    }
}
```

### Refresh Token

```
POST /api/v1/auth/refresh
```

Exchange a valid token for a new one with a fresh expiry.

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Authorization: Bearer $TOKEN"
```

### Get Current User

```
GET /api/v1/auth/me
```

Returns the authenticated user's profile.

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**

```json
{
    "id": "usr_abc123",
    "email": "admin@honeyaegis.local",
    "role": "admin",
    "tenant_id": "ten_default",
    "created_at": "2026-01-15T10:00:00Z",
    "last_login": "2026-02-28T08:30:00Z"
}
```

### Change Password

```
PUT /api/v1/auth/password
```

```bash
curl -X PUT http://localhost:8000/api/v1/auth/password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "old-password",
    "new_password": "new-secure-password"
  }'
```

## Using Tokens

Include the token in the `Authorization` header for all API requests:

```bash
curl http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

## Token Configuration

| Variable | Default | Description |
|---|---|---|
| `JWT_SECRET_KEY` | (required) | Signing secret (64+ characters) |
| `JWT_ALGORITHM` | `HS256` | Signing algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token lifetime |

## Error Responses

| Status | Code | Description |
|---|---|---|
| `401` | `invalid_credentials` | Wrong email or password |
| `401` | `token_expired` | Token has expired, refresh or re-login |
| `401` | `token_invalid` | Token is malformed or tampered |
| `403` | `insufficient_permissions` | User role lacks required permission |
| `429` | `rate_limited` | Too many authentication attempts |

## Rate Limits

Authentication endpoints have stricter rate limits to prevent brute-force attacks:

- **Login:** 10 requests per burst, 5 per second sustained
- **Refresh:** 20 requests per burst, 10 per second sustained

## Related Pages

- [RBAC](../enterprise/rbac.md) -- Role-based access control
- [SSO / OIDC](../enterprise/sso.md) -- Single sign-on integration
- [Security Model](../architecture/security-model.md) -- Authentication architecture
