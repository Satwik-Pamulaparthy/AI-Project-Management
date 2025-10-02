from sqlalchemy import select
from src.db import async_session
from src.models import Task
from collections import Counter

async def project_progress(project_id: int) -> dict:
    """Compute a naive progress metric from local tasks (no external tools yet)."""
    async with async_session() as session:
        res = await session.execute(select(Task).where(Task.project_id == project_id))
        tasks = res.scalars().all()
        if not tasks:
            return {"percent": 0, "counts": {}}
        counts = Counter(t.status for t in tasks)
        done = counts.get("done", 0)
        pct = int(round(done / len(tasks) * 100))
        return {"percent": pct, "counts": dict(counts), "total": len(tasks)}
