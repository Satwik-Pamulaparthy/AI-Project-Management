import re
from src.schemas import TaskCreate, TaskUpdate
from src.services import tasks as task_service
from datetime import datetime, timedelta
from dateutil import parser

async def route_intent(text: str) -> str:
    t = text.lower().strip()

    # Assign intent: "assign @alice to <title> due <date>"
    m = re.search(r"assign\s+@(?P<user>\w+)\s+to\s+'?(?P<title>[^']+?)'?\s+due\s+(?P<due>.+)$", t)
    if m:
        # For demo, we don't resolve users; create bare task on project 1.
        due_raw = m.group('due')
        try:
            due_at = parser.parse(due_raw)
        except Exception:
            return "Couldn't parse due date. Try formats like 'tomorrow 5pm' or '2025-10-05 17:00'."
        data = TaskCreate(project_id=1, title=m.group('title'), due_at=due_at)
        task = await task_service.create_task(data)
        return f"Created task #{task.id}: '{task.title}' due {due_at}."

    # Status intent: "status project <id>"
    m = re.search(r"status\s+project\s+(?P<pid>\d+)", t)
    if m:
        from src.services.progress import project_progress
        pid = int(m.group('pid'))
        prog = await project_progress(pid)
        return f"Project {pid} progress: {prog.get('percent', 0)}% (counts={prog.get('counts', {})})."

    # Update intent: "mark task <id> done"
    m = re.search(r"mark\s+task\s+(?P<tid>\d+)\s+(?P<status>done|blocked|in_progress)", t)
    if m:
        tid = int(m.group('tid'))
        upd = TaskUpdate(status=m.group('status'))
        task = await task_service.update_task(tid, upd)
        return f"Task #{task.id} marked {task.status}."

    return "I can help with: assign, status project <id>, mark task <id> done/blocked/in_progress."
