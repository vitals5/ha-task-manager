/**
 * Task Manager Dashboard Card for Home Assistant Lovelace
 * Type: custom:task-manager-card
 */

class TaskManagerCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._currentFilter = "all";
    this._tasks = [];
  }

  setConfig(config) {
    this._config = {
      title: "Task Manager",
      show_add: true,
      show_completed: true,
      show_assignee: true,
      show_priority: true,
      max_items: 20,
      default_filter: "all",
      ...config,
    };
    this._currentFilter = this._config.default_filter || "all";
    this._render();
  }

  set hass(hass) {
    const oldHass = this._hass;
    this._hass = hass;

    // Check if we need to reload tasks
    if (!oldHass || this._hasDataChanged(oldHass, hass)) {
      this._fetchTasks();
    }
  }

  _hasDataChanged(oldHass, newHass) {
    // Check if sensor or todo states changed
    const sOld = oldHass.states["sensor.task_manager_pending_tasks"];
    const sNew = newHass.states["sensor.task_manager_pending_tasks"];
    if (sOld !== sNew) return true;

    const bOld = oldHass.states["binary_sensor.task_manager_overdue"];
    const bNew = newHass.states["binary_sensor.task_manager_overdue"];
    if (bOld !== bNew) return true;

    return false;
  }

  async _fetchTasks() {
    if (!this._hass) return;
    try {
      const res = await this._hass.callWS({ type: "task_manager/get_data" });
      if (res && res.tasks) {
        this._tasks = res.tasks;
        this._render();
      }
    } catch (err) {
      // Fallback: try reading from todo entity if WS is busy
      console.debug("TaskManagerCard: fetch error", err);
    }
  }

  getCardSize() {
    return 4;
  }

  _getFilteredTasks() {
    const todayStr = new Date().toISOString().slice(0, 10);
    const soonDate = new Date();
    soonDate.setDate(soonDate.getDate() + 7);
    const soonStr = soonDate.toISOString().slice(0, 10);

    let list = [...this._tasks];

    if (this._currentFilter === "today") {
      list = list.filter(t => t.status === "pending" && t.due_date === todayStr);
    } else if (this._currentFilter === "due_soon") {
      list = list.filter(t => t.status === "pending" && t.due_date && t.due_date <= soonStr);
    } else if (this._currentFilter === "overdue") {
      list = list.filter(t => t.status === "pending" && t.due_date && t.due_date < todayStr);
    } else if (this._currentFilter === "completed") {
      list = list.filter(t => t.status === "completed");
    } else {
      // all: show pending
      list = list.filter(t => t.status === "pending");
    }

    // Sort: overdue first, then due_date, then priority
    const pOrder = { p1: 1, p2: 2, p3: 3, p4: 4, none: 5 };
    list.sort((a, b) => {
      if (a.due_date !== b.due_date) {
        return (a.due_date || "9999") < (b.due_date || "9999") ? -1 : 1;
      }
      return (pOrder[a.priority] || 5) - (pOrder[b.priority] || 5);
    });

    if (this._config.max_items && this._config.max_items > 0) {
      list = list.slice(0, this._config.max_items);
    }

    return list;
  }

  _render() {
    if (!this.shadowRoot) return;

    const todayStr = new Date().toISOString().slice(0, 10);
    const tasks = this._getFilteredTasks();
    const overdueCount = this._tasks.filter(t => t.status === "pending" && t.due_date && t.due_date < todayStr).length;

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
        }
        ha-card {
          padding: 16px;
          background: var(--ha-card-background, var(--card-background-color, #ffffff));
          color: var(--primary-text-color, #1e293b);
          border-radius: var(--ha-card-border-radius, 12px);
          box-shadow: var(--ha-card-box-shadow, none);
          border: var(--ha-card-border-width, 1px) solid var(--ha-card-border-color, var(--divider-color, rgba(127,127,127,0.15)));
        }
        .header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 12px;
        }
        .title {
          font-size: 18px;
          font-weight: 700;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .filter-row {
          display: flex;
          gap: 6px;
          overflow-x: auto;
          padding-bottom: 6px;
          margin-bottom: 12px;
          scrollbar-width: none;
        }
        .filter-row::-webkit-scrollbar {
          display: none;
        }
        .filter-chip {
          border: none;
          background: var(--secondary-background-color, rgba(127,127,127,0.12));
          color: var(--secondary-text-color, #64748b);
          padding: 5px 10px;
          border-radius: 16px;
          font-size: 12px;
          font-weight: 600;
          cursor: pointer;
          white-space: nowrap;
          transition: all 0.15s ease;
        }
        .filter-chip.active {
          background: var(--primary-color, #2563eb);
          color: #ffffff;
        }
        .add-row {
          display: flex;
          gap: 6px;
          margin-bottom: 12px;
        }
        .add-input {
          flex: 1;
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127,127,127,0.25)));
          border-radius: 8px;
          padding: 8px 12px;
          font-size: 13px;
          background: var(--card-background-color, #ffffff);
          color: var(--primary-text-color, inherit);
          outline: none;
        }
        .add-input:focus {
          border-color: var(--primary-color, #2563eb);
        }
        .add-btn {
          background: var(--primary-color, #2563eb);
          color: #ffffff;
          border: none;
          border-radius: 8px;
          padding: 0 14px;
          font-size: 18px;
          font-weight: 700;
          cursor: pointer;
        }
        .task-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .task-item {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 8px 10px;
          border-radius: 8px;
          background: var(--secondary-background-color, rgba(127,127,127,0.06));
          border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127,127,127,0.12)));
          transition: background 0.15s ease;
        }
        .task-item:hover {
          background: var(--secondary-background-color, rgba(127,127,127,0.12));
        }
        .task-check {
          width: 22px;
          height: 22px;
          border-radius: 6px;
          border: 1.5px solid var(--ha-card-border-color, #94a3b8);
          background: transparent;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 13px;
          color: transparent;
          flex-shrink: 0;
          padding: 0;
        }
        .task-check.checked {
          background: var(--success-color, #10b981);
          border-color: var(--success-color, #10b981);
          color: #ffffff;
        }
        .task-content {
          flex: 1;
          min-width: 0;
        }
        .task-title {
          font-size: 14px;
          font-weight: 500;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .task-title.done {
          text-decoration: line-through;
          opacity: 0.6;
        }
        .task-meta {
          display: flex;
          gap: 6px;
          flex-wrap: wrap;
          margin-top: 3px;
          font-size: 11px;
        }
        .badge {
          padding: 1px 6px;
          border-radius: 4px;
          font-weight: 600;
          font-size: 10px;
        }
        .badge-overdue {
          background: rgba(239, 68, 68, 0.15);
          color: #ef4444;
        }
        .badge-due-today {
          background: rgba(245, 158, 11, 0.15);
          color: #d97706;
        }
        .badge-date {
          background: rgba(127, 127, 127, 0.12);
          color: var(--secondary-text-color, #64748b);
        }
        .badge-p1 { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
        .badge-p2 { background: rgba(249, 115, 22, 0.2); color: #f97316; }
        .badge-p3 { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
        .empty-state {
          text-align: center;
          padding: 24px 8px;
          color: var(--secondary-text-color, #64748b);
          font-size: 13px;
        }
      </style>

      <ha-card>
        <div class="header">
          <div class="title">
            <span>📋</span>
            <span>${this._config.title || "Tasks"}</span>
          </div>
          <div style="font-size:12px; font-weight:600; color:var(--secondary-text-color, #64748b);">
            ${tasks.length} ${tasks.length === 1 ? "task" : "tasks"}
          </div>
        </div>

        <div class="filter-row">
          <button class="filter-chip ${this._currentFilter === "all" ? "active" : ""}" data-filter="all">All</button>
          <button class="filter-chip ${this._currentFilter === "today" ? "active" : ""}" data-filter="today">🔥 Today</button>
          <button class="filter-chip ${this._currentFilter === "due_soon" ? "active" : ""}" data-filter="due_soon">⏳ Due Soon</button>
          ${overdueCount > 0 ? `
            <button class="filter-chip ${this._currentFilter === "overdue" ? "active" : ""}" data-filter="overdue">⚠️ Overdue (${overdueCount})</button>
          ` : ""}
          <button class="filter-chip ${this._currentFilter === "completed" ? "active" : ""}" data-filter="completed">✓ Done</button>
        </div>

        ${this._config.show_add ? `
          <div class="add-row">
            <input type="text" class="add-input" id="card-add-input" placeholder="Add a task...">
            <button class="add-btn" id="card-add-btn">+</button>
          </div>
        ` : ""}

        <div class="task-list">
          ${tasks.length === 0 ? `
            <div class="empty-state">🎉 No tasks in this view</div>
          ` : tasks.map(t => {
            const isDone = t.status === "completed";
            const isOverdue = !isDone && t.due_date && t.due_date < todayStr;
            const isToday = !isDone && t.due_date === todayStr;

            return `
              <div class="task-item">
                <button class="task-check ${isDone ? "checked" : ""}" data-id="${t.id}" data-action="${isDone ? "reset" : "complete"}">
                  ✓
                </button>
                <div class="task-content">
                  <div class="task-title ${isDone ? "done" : ""}">${t.title || "Untitled Task"}</div>
                  <div class="task-meta">
                    ${t.due_date ? `
                      <span class="badge ${isOverdue ? "badge-overdue" : isToday ? "badge-due-today" : "badge-date"}">
                        ${isOverdue ? "⚠️ Overdue: " : isToday ? "🔥 Today: " : "📅 "} ${t.due_date}
                      </span>
                    ` : ""}
                    ${this._config.show_priority && t.priority && t.priority !== "none" ? `
                      <span class="badge badge-${t.priority}">${t.priority.toUpperCase()}</span>
                    ` : ""}
                    ${this._config.show_assignee && t.current_assignee ? `
                      <span class="badge badge-date">👤 ${t.current_assignee}</span>
                    ` : ""}
                  </div>
                </div>
              </div>
            `;
          }).join("")}
        </div>
      </ha-card>
    `;

    this._attachEvents();
  }

  _attachEvents() {
    const root = this.shadowRoot;
    if (!root) return;

    // Filters
    root.querySelectorAll(".filter-chip").forEach(btn => {
      btn.addEventListener("click", () => {
        this._currentFilter = btn.getAttribute("data-filter") || "all";
        this._render();
      });
    });

    // Complete / Reset
    root.querySelectorAll(".task-check").forEach(btn => {
      btn.addEventListener("click", async () => {
        const taskId = btn.getAttribute("data-id");
        const action = btn.getAttribute("data-action");
        if (taskId && this._hass) {
          if (action === "complete") {
            await this._hass.callWS({ type: "task_manager/complete_task", task_id: taskId });
          } else {
            await this._hass.callWS({ type: "task_manager/reset_task", task_id: taskId });
          }
          await this._fetchTasks();
        }
      });
    });

    // Add Task
    const addInput = root.getElementById("card-add-input");
    const addBtn = root.getElementById("card-add-btn");
    const handleAdd = async () => {
      if (!addInput || !this._hass) return;
      const title = addInput.value.trim();
      if (!title) return;
      addInput.value = "";
      await this._hass.callWS({
        type: "task_manager/save_task",
        task: { title: title, due_date: new Date().toISOString().slice(0, 10) }
      });
      await this._fetchTasks();
    };

    if (addBtn) addBtn.addEventListener("click", handleAdd);
    if (addInput) {
      addInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") handleAdd();
      });
    }
  }
}

customElements.define("task-manager-card", TaskManagerCard);

// Register with Lovelace Card Picker
window.customCards = window.customCards || [];
window.customCards.push({
  type: "task-manager-card",
  name: "Task Manager Card",
  description: "Display, filter, complete, and add chores and tasks on your Lovelace dashboard.",
  preview: true,
  documentationURL: "https://github.com/vitals5/ha-task-manager",
});
