/**
 * Task Manager Dashboard Card for Home Assistant Lovelace
 * Type: custom:task-manager-card
 */

const CARD_VERSION = "1.0.18";

class TaskManagerCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._currentFilter = "all";
    this._tasks = [];
    this._users = [];
  }

  _escape(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  static getStubConfig() {
    return {
      title: "Task Manager",
      default_filter: "all",
      show_add: true,
      show_completed: true,
      show_assignee: true,
      show_priority: true,
      max_items: 20,
    };
  }

  static async getConfigElement() {
    return document.createElement("task-manager-card-editor");
  }

  setConfig(config) {
    this._config = {
      title: "Task Manager",
      default_filter: "all",
      show_add: true,
      show_completed: true,
      show_assignee: true,
      show_priority: true,
      max_items: 20,
      ...config,
    };
    if (!this._currentFilter || this._currentFilter === "all") {
      this._currentFilter = this._config.default_filter || "all";
    }
    this._render();
  }

  set hass(hass) {
    const oldHass = this._hass;
    this._hass = hass;

    if (!oldHass || this._hasDataChanged(oldHass, hass)) {
      this._fetchTasks();
    }
  }

  connectedCallback() {
    if (this._hass) {
      this._fetchTasks();
    }
  }

  _hasDataChanged(oldHass, newHass) {
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
      if (res) {
        if (Array.isArray(res.tasks)) this._tasks = res.tasks;
        if (Array.isArray(res.users)) this._users = res.users;
        this._render();
      }
    } catch (err) {
      console.debug("TaskManagerCard: Error querying task_manager/get_data", err);
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

    if (this._currentFilter === "inactive") {
      list = list.filter(t => t.is_active === false);
    } else if (this._currentFilter === "today") {
      list = list.filter(t => t.is_active !== false && t.status === "pending" && t.due_date === todayStr);
    } else if (this._currentFilter === "due_soon") {
      list = list.filter(t => {
        if (t.is_active === false || t.status !== "pending" || !t.due_date) return false;
        const dsDays = (t.due_soon_days !== undefined && t.due_soon_days > 0) ? t.due_soon_days : 7;
        const soonDate = new Date();
        soonDate.setDate(soonDate.getDate() + dsDays);
        const soonStr = soonDate.toISOString().slice(0, 10);
        return t.due_date <= soonStr;
      });
    } else if (this._currentFilter === "overdue") {
      list = list.filter(t => t.is_active !== false && t.status === "pending" && t.due_date && t.due_date < todayStr);
    } else if (this._currentFilter === "completed") {
      list = list.filter(t => t.status === "completed");
    } else {
      // all: show active pending
      list = list.filter(t => t.is_active !== false && t.status === "pending");
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

  _isGerman() {
    const lang = (this._hass && (this._hass.language || (this._hass.locale && this._hass.locale.language))) || "en";
    return lang.startsWith("de");
  }

  _render() {
    if (!this.shadowRoot) return;

    const de = this._isGerman();
    const todayStr = new Date().toISOString().slice(0, 10);
    const tasks = this._getFilteredTasks();
    const overdueCount = this._tasks.filter(t => t.status === "pending" && t.due_date && t.due_date < todayStr).length;
    const pausedCount = this._tasks.filter(t => t.is_active === false).length;

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
          box-sizing: border-box;
          overflow: hidden;
        }
        .header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 12px;
        }
        .title {
          font-size: 17px;
          font-weight: 700;
          display: flex;
          align-items: center;
          gap: 8px;
          color: var(--primary-text-color, inherit);
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
          padding: 6px 12px;
          border-radius: 16px;
          font-size: 12px;
          font-weight: 600;
          cursor: pointer;
          white-space: nowrap;
          transition: all 0.15s ease;
          display: flex;
          align-items: center;
          gap: 4px;
        }
        .filter-chip:hover {
          background: var(--secondary-background-color, rgba(127,127,127,0.2));
        }
        .filter-chip.active {
          background: var(--primary-color, #2563eb);
          color: #ffffff;
        }
        .add-row {
          display: flex;
          gap: 8px;
          margin-bottom: 14px;
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
          box-sizing: border-box;
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
          display: flex;
          align-items: center;
          justify-content: center;
          transition: opacity 0.15s ease;
        }
        .add-btn:active {
          opacity: 0.8;
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
          padding: 9px 12px;
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
          transition: all 0.15s ease;
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
          color: var(--primary-text-color, inherit);
        }
        .task-title.done {
          text-decoration: line-through;
          opacity: 0.6;
        }
        .task-meta {
          display: flex;
          gap: 6px;
          flex-wrap: wrap;
          margin-top: 4px;
          font-size: 11px;
        }
        .badge {
          padding: 2px 6px;
          border-radius: 4px;
          font-weight: 600;
          font-size: 10px;
          display: inline-flex;
          align-items: center;
          gap: 2px;
        }
        .badge-overdue {
          background: rgba(239, 68, 68, 0.15);
          color: var(--error-color, #ef4444);
        }
        .badge-due-today {
          background: rgba(245, 158, 11, 0.15);
          color: var(--warning-color, #d97706);
        }
        .badge-date {
          background: var(--secondary-background-color, rgba(127, 127, 127, 0.12));
          color: var(--secondary-text-color, #64748b);
        }
        .badge-p1 { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
        .badge-p2 { background: rgba(249, 115, 22, 0.2); color: #f97316; }
        .badge-p3 { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
        .badge-p4 { background: rgba(100, 116, 139, 0.2); color: #64748b; }
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
            <span>${this._config.title || (de ? "Aufgaben & Chores" : "Task Manager")}</span>
          </div>
          <div style="font-size:12px; font-weight:600; color:var(--secondary-text-color, #64748b);">
            ${tasks.length} ${de ? (tasks.length === 1 ? "Aufgabe" : "Aufgaben") : (tasks.length === 1 ? "task" : "tasks")}
          </div>
        </div>

        <div class="filter-row">
          <button class="filter-chip ${this._currentFilter === "all" ? "active" : ""}" data-filter="all">${de ? "Alle" : "All"}</button>
          <button class="filter-chip ${this._currentFilter === "today" ? "active" : ""}" data-filter="today">🔥 ${de ? "Heute" : "Today"}</button>
          <button class="filter-chip ${this._currentFilter === "due_soon" ? "active" : ""}" data-filter="due_soon">⏳ ${de ? "Bald fällig" : "Due Soon"}</button>
          ${overdueCount > 0 ? `
            <button class="filter-chip ${this._currentFilter === "overdue" ? "active" : ""}" data-filter="overdue">⚠️ ${de ? "Überfällig" : "Overdue"} (${overdueCount})</button>
          ` : ""}
          ${pausedCount > 0 ? `
            <button class="filter-chip ${this._currentFilter === "inactive" ? "active" : ""}" data-filter="inactive">⏸️ ${de ? "Pausiert" : "Paused"} (${pausedCount})</button>
          ` : ""}
          <button class="filter-chip ${this._currentFilter === "completed" ? "active" : ""}" data-filter="completed">✓ ${de ? "Erledigt" : "Done"}</button>
        </div>

        ${this._config.show_add ? `
          <div class="add-row">
            <input type="text" class="add-input" id="card-add-input" placeholder="${de ? "Neue Aufgabe hinzufügen..." : "Add a new task..."}">
            <button class="add-btn" id="card-add-btn" title="${de ? "Hinzufügen" : "Add"}">+</button>
          </div>
        ` : ""}

        <div class="task-list">
          ${tasks.length === 0 ? `
            <div class="empty-state">🎉 ${de ? "Keine offenen Aufgaben in dieser Ansicht" : "No open tasks in this view"}</div>
          ` : tasks.map(t => {
            const isDone = t.status === "completed";
            const isOverdue = !isDone && t.due_date && t.due_date < todayStr;
            const isToday = !isDone && t.due_date === todayStr;

            let assigneeName = t.current_assignee;
            if (assigneeName && Array.isArray(this._users)) {
              const u = this._users.find(x => x.id === assigneeName);
              if (u && u.name) assigneeName = u.name;
            }

            return `
              <div class="task-item">
                <button class="task-check ${isDone ? "checked" : ""}" data-id="${t.id}" data-action="${isDone ? "reset" : "complete"}" title="${isDone ? (de ? "Wiedereröffnen" : "Reopen") : (de ? "Erledigen" : "Complete")}">
                  ✓
                </button>
                <div class="task-content">
                  <div class="task-title ${isDone ? "done" : ""}">${t.title || (de ? "Aufgabe" : "Task")}</div>
                  <div class="task-meta">
                    ${t.is_active === false ? `
                      <span class="badge" style="background:rgba(100,116,139,0.15); color:#64748b;">⏸️ ${de ? "Pausiert" : "Paused"}</span>
                    ` : ""}
                    ${t.due_date ? `
                      <span class="badge ${t.due_date >= "2099-01-01" && t.linked_thing_id ? "badge-date" : isOverdue ? "badge-overdue" : isToday ? "badge-due-today" : "badge-date"}">
                        ${t.due_date >= "2099-01-01" && t.linked_thing_id ? `⚡ ${de ? "Wartet auf Schwellwert" : "Waiting for threshold"}` : `${isOverdue ? (de ? "⚠️ Überfällig: " : "⚠️ Overdue: ") : isToday ? (de ? "🔥 Heute" : "🔥 Today") : "📅 "} ${t.due_date}`}
                      </span>
                    ` : ""}
                    ${this._config.show_priority && t.priority && t.priority !== "none" ? `
                      <span class="badge badge-${t.priority}">${t.priority.toUpperCase()}</span>
                    ` : ""}
                    ${this._config.show_assignee && assigneeName ? `
                      <span class="badge badge-date">👤 ${assigneeName}</span>
                    ` : ""}
                    ${t.times_completed > 0 ? `
                      <span class="badge" style="background:rgba(16,185,129,0.12); color:#10b981;">🔁 ${t.times_completed}x</span>
                    ` : ""}
                    ${t.dependencies && t.dependencies.length > 0 ? `
                      <span class="badge" style="background:rgba(234,179,8,0.15); color:#ca8a04;">🔗 ${t.dependencies.length} ${de ? "Abh." : "deps"}</span>
                    ` : ""}
                    ${t.task_type === "reading" ? `
                      <span class="badge" style="background:rgba(6,182,212,0.15); color:#0891b2;">📟 ${t.last_reading_value !== undefined && t.last_reading_value !== null ? `${t.last_reading_value} ${t.reading_unit || ""}` : (de ? "Zählerablesung" : "Reading")}</span>
                    ` : ""}
                    ${t.consumed_parts && t.consumed_parts.length > 0 ? `
                      <span class="badge" style="background:rgba(249,115,22,0.15); color:#ea580c;">📦 ${t.consumed_parts.length} ${de ? "Teile" : "parts"}</span>
                    ` : ""}
                    ${t.tags && t.tags.length > 0 ? t.tags.map(tg => `
                      <span class="badge" style="background:rgba(139,92,246,0.12); color:#8b5cf6;">🏷️ ${this._escape(tg)}</span>
                    `).join("") : ""}
                  </div>
                </div>
                ${!isDone ? `
                  <button class="task-skip-btn" data-id="${t.id}" title="${de ? "Überspringen" : "Skip"}" style="background:transparent; border:none; color:var(--secondary-text-color, #64748b); cursor:pointer; font-size:14px; padding:4px 6px; border-radius:4px;" onmouseover="this.style.color='var(--primary-color, #2563eb)'" onmouseout="this.style.color='var(--secondary-text-color, #64748b)'">
                    ⏭️
                  </button>
                ` : ""}
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

    // Skip Task
    root.querySelectorAll(".task-skip-btn").forEach(btn => {
      btn.addEventListener("click", async () => {
        const taskId = btn.getAttribute("data-id");
        if (taskId && this._hass) {
          try {
            await this._hass.callWS({ type: "task_manager/skip_task", task_id: taskId });
          } catch (e) {
            await this._hass.callService("task_manager", "skip_task", { task_id: taskId });
          }
          await this._fetchTasks();
        }
      });
    });

    // Complete / Reset
    root.querySelectorAll(".task-check").forEach(btn => {
      btn.addEventListener("click", async () => {
        const taskId = btn.getAttribute("data-id");
        const action = btn.getAttribute("data-action");
        if (taskId && this._hass) {
          try {
            if (action === "complete") {
              await this._hass.callWS({ type: "task_manager/complete_task", task_id: taskId });
            } else {
              await this._hass.callWS({ type: "task_manager/reset_task", task_id: taskId });
            }
          } catch (e) {
            // Service fallback
            const srv = action === "complete" ? "complete_task" : "reopen_task";
            await this._hass.callService("task_manager", srv, { task_id: taskId });
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
      try {
        await this._hass.callWS({
          type: "task_manager/save_task",
          task: { title: title, due_date: new Date().toISOString().slice(0, 10) }
        });
      } catch (e) {
        await this._hass.callService("task_manager", "create_task", {
          title: title,
          due_date: new Date().toISOString().slice(0, 10)
        });
      }
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

class TaskManagerCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
  }

  setConfig(config) {
    this._config = { ...config };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
  }

  _valueChanged(ev) {
    if (!this._config || !ev.target) return;
    const target = ev.target;
    const configValue = target.configValue;
    if (!configValue) return;

    let value = target.value;
    if (target.type === "checkbox") {
      value = target.checked;
    } else if (target.type === "number") {
      value = parseInt(target.value, 10);
    }

    this._config = {
      ...this._config,
      [configValue]: value,
    };

    const event = new CustomEvent("config-changed", {
      detail: { config: this._config },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }

  _render() {
    if (!this.shadowRoot) return;

    this.shadowRoot.innerHTML = `
      <style>
        .card-config {
          display: flex;
          flex-direction: column;
          gap: 12px;
          padding: 8px 0;
          font-family: var(--paper-font-body1_-_font-family);
        }
        .form-row {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .form-row label {
          font-size: 13px;
          font-weight: 600;
          color: var(--primary-text-color, inherit);
        }
        .form-row input[type="text"],
        .form-row input[type="number"],
        .form-row select {
          padding: 8px 10px;
          border-radius: 6px;
          border: 1px solid var(--divider-color, rgba(127,127,127,0.3));
          background: var(--card-background-color, #ffffff);
          color: var(--primary-text-color, inherit);
          font-size: 13px;
        }
        .toggle-row {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
        }
      </style>

      <div class="card-config">
        <div class="form-row">
          <label>Title</label>
          <input type="text" .configValue="${"title"}" id="ed-title" value="${this._config.title || "Task Manager"}">
        </div>

        <div class="form-row">
          <label>Default Filter</label>
          <select .configValue="${"default_filter"}" id="ed-filter">
            <option value="all" ${this._config.default_filter === "all" ? "selected" : ""}>All</option>
            <option value="today" ${this._config.default_filter === "today" ? "selected" : ""}>Today</option>
            <option value="due_soon" ${this._config.default_filter === "due_soon" ? "selected" : ""}>Due Soon</option>
            <option value="overdue" ${this._config.default_filter === "overdue" ? "selected" : ""}>Overdue</option>
            <option value="completed" ${this._config.default_filter === "completed" ? "selected" : ""}>Completed</option>
          </select>
        </div>

        <div class="form-row">
          <label>Max Tasks to Display</label>
          <input type="number" .configValue="${"max_items"}" id="ed-max" value="${this._config.max_items || 20}" min="1" max="100">
        </div>

        <label class="toggle-row">
          <input type="checkbox" .configValue="${"show_add"}" id="ed-add" ${this._config.show_add !== false ? "checked" : ""}>
          <span>Show Quick Add Input Row</span>
        </label>

        <label class="toggle-row">
          <input type="checkbox" .configValue="${"show_priority"}" id="ed-prio" ${this._config.show_priority !== false ? "checked" : ""}>
          <span>Show Priority Badges</span>
        </label>

        <label class="toggle-row">
          <input type="checkbox" .configValue="${"show_assignee"}" id="ed-assignee" ${this._config.show_assignee !== false ? "checked" : ""}>
          <span>Show Assigned Member</span>
        </label>
      </div>
    `;

    const inputs = this.shadowRoot.querySelectorAll("input, select");
    inputs.forEach(input => {
      input.addEventListener("change", (e) => this._valueChanged(e));
      input.addEventListener("input", (e) => this._valueChanged(e));
    });
  }
}

// Resilient Custom Element Registration (immediate + polling fallback for scoped registries)
const _registerCustomCardElements = () => {
  if (!customElements.get("task-manager-card")) {
    try {
      customElements.define("task-manager-card", TaskManagerCard);
    } catch (_) {}
  }
  if (!customElements.get("task-manager-card-editor")) {
    try {
      customElements.define("task-manager-card-editor", TaskManagerCardEditor);
    } catch (_) {}
  }
};

_registerCustomCardElements();

let _regAttempts = 0;
const _checkRegistryPoll = () => {
  _registerCustomCardElements();
  _regAttempts++;
  if (_regAttempts < 40) {
    setTimeout(_checkRegistryPoll, 100);
  }
};
_checkRegistryPoll();

// Register with Lovelace Card Picker modal
window.customCards = window.customCards || [];
if (!window.customCards.some(c => c.type === "task-manager-card")) {
  window.customCards.push({
    type: "task-manager-card",
    name: "Task Manager Card",
    description: "Display, filter, complete, and add chores and tasks on your Lovelace dashboard.",
    preview: true,
    documentationURL: "https://github.com/vitals5/ha-task-manager",
  });
}
