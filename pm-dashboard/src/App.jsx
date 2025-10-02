import React, { useEffect, useMemo, useState } from "react";
import "./App.css";

// === CONFIG ===
const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

// --- helpers ---
async function api(path, opts = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.status !== 204 ? res.json() : null;
}

function StatusBadge({ s }) {
  const map = {
    todo: { label: "Todo", color: "#64748b", bg: "#eef2ff" },
    in_progress: { label: "In Progress", color: "#0ea5e9", bg: "#e0f2fe" },
    done: { label: "Done", color: "#16a34a", bg: "#dcfce7" },
    blocked: { label: "Blocked", color: "#dc2626", bg: "#fee2e2" },
  }[s] || { label: s, color: "#64748b", bg: "#eef2ff" };

  return (
    <span
      className="badge"
      style={{ color: map.color, background: map.bg, borderColor: `${map.color}40` }}
    >
      {map.label}
    </span>
  );
}

function percentDone(tasks) {
  if (!tasks?.length) return 0;
  const done = tasks.filter((t) => t.status === "done").length;
  return Math.round((done / tasks.length) * 100);
}

function dueSoonCount(tasks) {
  const now = new Date();
  const soon = new Date(now.getTime() + 86_400_000);
  return tasks.filter(
    (t) => t.due_at && new Date(t.due_at) >= now && new Date(t.due_at) <= soon && t.status !== "done"
  ).length;
}

function formatDateTime(dt) {
  if (!dt) return "—";
  try {
    const d = new Date(dt);
    return d.toLocaleString();
  } catch {
    return dt;
  }
}

// Simple title suggester from description
function suggestTitle(desc) {
  if (!desc) return "New Task";
  const d = desc.toLowerCase();
  if (d.includes("endpoint")) return "Draft API endpoints – tasks";
  if (d.includes("schema")) return "Define DB schema – tasks";
  if (d.includes("reminder") || d.includes("cron")) return "Implement reminder scheduler";
  if (d.includes("slack")) return "Wire Slack notifications";
  if (d.includes("teams")) return "Wire Teams notifications (Graph)";
  if (d.includes("react") || d.includes("ui")) return "Build React dashboard MVP";
  const pretty = desc.trim();
  return pretty.length > 50 ? pretty.slice(0, 50) + "…" : pretty.charAt(0).toUpperCase() + pretty.slice(1);
}

export default function App() {
  const [loading, setLoading] = useState(true);
  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [activeTab, setActiveTab] = useState("all");
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");

  // Create Task form state
  const [form, setForm] = useState({
    project_id: 1,
    title: "",
    description: "",
    assignee_id: "",
    priority: 3,
    due_at: "",
  });

  // Auto-suggest title from description (only when title is empty)
  useEffect(() => {
    if (!form.title && form.description.trim()) {
      setForm((f) => ({ ...f, title: suggestTitle(f.description) }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form.description]);

  // Load data
  async function load() {
    try {
      setLoading(true);
      const [ts, ps] = await Promise.all([api("/tasks"), api("/projects").catch(() => [])]);
      setTasks(ts);
      setProjects(ps || []);
      setError("");
    } catch (e) {
      console.error(e);
      setError("Failed to load from API. Is the backend running and CORS enabled?");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const filtered = useMemo(() => {
    if (activeTab === "all") return tasks;
    if (activeTab === "due-soon") {
      const now = new Date();
      const soon = new Date(now.getTime() + 86_400_000);
      return tasks.filter(
        (t) => t.due_at && new Date(t.due_at) >= now && new Date(t.due_at) <= soon && t.status !== "done"
      );
    }
    if (activeTab === "overdue") {
      const now = new Date();
      return tasks.filter((t) => t.due_at && new Date(t.due_at) < now && t.status !== "done");
    }
    return tasks.filter((t) => t.status === activeTab);
  }, [tasks, activeTab]);

  async function createTask(ev) {
    ev.preventDefault();
    try {
      const payload = {
        ...form,
        assignee_id:
          form.assignee_id?.toString().trim() === "" ? null : Number(form.assignee_id),
        priority: Number(form.priority),
      };
      const t = await api("/tasks", { method: "POST", body: JSON.stringify(payload) });
      setTasks((prev) => [t, ...prev]);
      setForm((f) => ({ ...f, title: "", description: "", due_at: "" }));
      ping("Task created");
    } catch (e) {
      console.error(e);
      ping("Failed to create task", true);
    }
  }

  async function updateStatus(id, status) {
    try {
      const t = await api(`/tasks/${id}`, { method: "PATCH", body: JSON.stringify({ status }) });
      setTasks((prev) => prev.map((x) => (x.id === id ? t : x)));
      ping(`Marked #${id} ${status.replace("_", " ")}`);
    } catch (e) {
      console.error(e);
      ping("Failed to update status", true);
    }
  }

  function ping(msg, danger = false) {
    setToast(msg + (danger ? " ❌" : " ✅"));
    setTimeout(() => setToast(""), 1800);
  }

  // Allow Cmd/Ctrl+Enter to submit the form
  function onFormKeyDown(e) {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      createTask(e);
    }
  }

  return (
    <div className="page">
      {/* gradient backdrop */}
      <div className="backdrop" />

      {/* sticky header */}
      <header className="header">
        <div className="brand">
          <div className="logo-dot" />
          <h1>AI Project Management Dashboard</h1>
        </div>
        <div className="header-actions">
          <button className="btn ghost" onClick={load} disabled={loading}>
            🔄 Refresh
          </button>
          <span className="muted">API: {API_BASE}</span>
        </div>
      </header>

      <main className="content">
        {/* Summary cards */}
        <section className="grid4">
          <div className="card lift">
            <div className="card-title">Total</div>
            <div className="kpi">{tasks.length}</div>
          </div>

          <div className="card lift">
            <div className="card-title">Done</div>
            <div className="kpi">{tasks.filter((t) => t.status === "done").length}</div>
          </div>

          <div className="card lift">
            <div className="card-title">Progress</div>
            <div className="progress">
              <div className="progress-bar" style={{ width: `${percentDone(tasks)}%` }} />
            </div>
            <div className="muted small">{percentDone(tasks)}% complete</div>
          </div>

          <div className="card lift">
            <div className="card-title">Due in 24h</div>
            <div className="kpi">{dueSoonCount(tasks)}</div>
          </div>
        </section>

        {/* Create Task */}
        <section className="card lift">
          <div className="card-title">New Task</div>
          <form className="form-grid" onSubmit={createTask} onKeyDown={onFormKeyDown}>
            <div>
              <label>Project</label>
              <select
                value={String(form.project_id)}
                onChange={(e) => setForm((f) => ({ ...f, project_id: Number(e.target.value) }))}
              >
                {(projects.length ? projects : [{ id: 1, name: "Demo Project" }]).map((p) => (
                  <option key={p.id} value={String(p.id)}>
                    {p.name || `Project ${p.id}`}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label>Title</label>
              <div style={{ display: "flex", gap: 8 }}>
                <input
                  value={form.title}
                  onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
                  required
                  placeholder="e.g., Draft API endpoints – tasks"
                  style={{ flex: 1 }}
                />
                <button
                  type="button"
                  className="btn ghost"
                  onClick={() =>
                    setForm((f) => ({ ...f, title: suggestTitle(f.description || "") }))
                  }
                >
                  Suggest
                </button>
              </div>
            </div>

            <div>
              <label>Assignee ID (optional)</label>
              <input
                value={form.assignee_id}
                onChange={(e) => setForm((f) => ({ ...f, assignee_id: e.target.value }))}
                placeholder="1"
              />
            </div>

            <div className="col-span-2">
              <label>Description</label>
              <textarea
                rows={2}
                value={form.description}
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                placeholder="Endpoints, payloads, acceptance criteria…"
              />
            </div>

            <div>
              <label>Priority</label>
              <select
                value={String(form.priority)}
                onChange={(e) => setForm((f) => ({ ...f, priority: Number(e.target.value) }))}
              >
                {[1, 2, 3, 4, 5].map((p) => (
                  <option key={p} value={String(p)}>
                    {p}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label>Due at</label>
              <input
                type="datetime-local"
                value={form.due_at}
                onChange={(e) =>
                  setForm((f) => ({
                    ...f,
                    due_at: e.target.value
                      ? new Date(e.target.value).toISOString()
                      : "",
                  }))
                }
              />
            </div>

            <div className="col-span-2 actions">
              <button className="btn primary" type="submit" disabled={loading}>
                ➕ Create Task
              </button>
              {loading && <span className="muted">Loading…</span>}
              {error && <span className="danger">{error}</span>}
            </div>
          </form>
        </section>

        {/* Filter tabs */}
        <section className="card lift">
          <div className="tabs">
            {["all", "todo", "in_progress", "done", "blocked", "due-soon", "overdue"].map((tab) => (
              <button
                key={tab}
                className={`pill ${activeTab === tab ? "active" : ""}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab}
              </button>
            ))}
          </div>
        </section>

        {/* Task list */}
        <section className="card lift">
          <div className="card-title">Tasks</div>
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Status</th>
                  <th>Priority</th>
                  <th>Due</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((t) => (
                  <tr key={t.id}>
                    <td className="mono">#{t.id}</td>
                    <td>
                      <div className="strong">{t.title}</div>
                      <div className="muted ellipsis">{t.description || ""}</div>
                    </td>
                    <td>
                      <StatusBadge s={t.status} />
                    </td>
                    <td>{t.priority}</td>
                    <td>{formatDateTime(t.due_at)}</td>
                    <td>
                      <div className="row-actions">
                        <button className="btn ghost" onClick={() => updateStatus(t.id, "in_progress")}>
                          In&nbsp;Progress
                        </button>
                        <button className="btn ghost" onClick={() => updateStatus(t.id, "blocked")}>
                          Blocked
                        </button>
                        <button className="btn primary" onClick={() => updateStatus(t.id, "done")}>
                          Done
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!filtered.length && <div className="empty">No tasks found.</div>}
          </div>
        </section>
      </main>

      {/* toasts */}
      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}
