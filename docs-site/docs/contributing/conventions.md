# Code Conventions

Standards and practices for contributing to HoneyAegis. All pull requests are expected to follow these conventions.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
feat: add threat intel lookup API
fix: resolve WebSocket reconnection on timeout
docs: update deployment matrix for Proxmox
test: add RBAC permission edge cases
chore: bump FastAPI to 0.115.6
refactor: extract GeoIP enrichment into service class
```

| Prefix | Use Case |
|---|---|
| `feat:` | New feature or capability |
| `fix:` | Bug fix |
| `docs:` | Documentation changes only |
| `test:` | Adding or updating tests |
| `chore:` | Build, CI, dependency updates |
| `refactor:` | Code restructuring without behavior change |
| `perf:` | Performance improvement |

## Python (Backend)

### Required Practices

- **Type hints** on all function signatures and return types
- **Async by default** for all database and I/O operations
- **Structured logging** using the `logging` module; never use `print()`
- **Pydantic models** for all request/response schemas
- **Tests** for all new features and bug fixes

### Style

```python
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.session import SessionResponse

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionResponse:
    """Retrieve a session by ID, scoped to the user's tenant."""
    session = await db.get(Session, session_id)
    if not session or session.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse.model_validate(session)
```

## TypeScript (Frontend)

### Required Practices

- **Strict mode** enabled in `tsconfig.json`
- **Server components** preferred where possible (Next.js App Router)
- **Tailwind CSS** for all styling; no CSS modules or styled-components
- **ESLint** with zero warnings policy

### Style

```typescript
interface SessionCardProps {
    session: Session;
    onSelect: (id: string) => void;
}

export function SessionCard({ session, onSelect }: SessionCardProps) {
    return (
        <div
            className="rounded-lg border border-border p-4 hover:bg-muted/50 cursor-pointer"
            onClick={() => onSelect(session.id)}
        >
            <h3 className="font-semibold">{session.src_ip}</h3>
            <p className="text-sm text-muted-foreground">
                {session.protocol.toUpperCase()} - Risk: {session.risk_score}/10
            </p>
        </div>
    );
}
```

## File Organization

| Type | Location |
|---|---|
| API endpoints | `backend/app/api/` |
| Business logic | `backend/app/services/` |
| Database models | `backend/app/models/` |
| Request/response schemas | `backend/app/schemas/` |
| Background tasks | `backend/app/workers/` |
| Core utilities | `backend/app/core/` |
| Frontend pages | `frontend/src/app/` |
| React components | `frontend/src/components/` |
| Honeypot configs | `honeypots/<service>/` |
| Database migrations | `db/migrations/` and `backend/alembic/` |
| Scripts | `scripts/` |

## Pull Request Checklist

Every PR must satisfy the following before merge:

- [ ] Tests added and passing (`pytest` / `npm test`)
- [ ] Linting passes with zero warnings
- [ ] Documentation updated (if user-facing changes)
- [ ] CHANGELOG.md updated with the change
- [ ] No secrets or credentials committed
- [ ] Commit messages follow Conventional Commits format
- [ ] PR description explains the "why" not just the "what"

## Branch Naming

```
feat/add-mqtt-honeypot
fix/websocket-reconnection
docs/update-api-reference
chore/bump-dependencies
```

## Related Pages

- [Development Setup](setup.md) -- Local environment setup
- [Changelog](changelog.md) -- Release history
- [Architecture Overview](../architecture/overview.md) -- Codebase structure
