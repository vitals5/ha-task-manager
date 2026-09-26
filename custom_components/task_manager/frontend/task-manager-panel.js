/**
 * Task Manager Custom Sidebar Panel for Home Assistant
 *
 * Features:
 * - Tasks & Chores Management (Due date, priority P1-P4, recurring cadences)
 * - Subtasks with smart automatic reset on recurring chore completion
 * - Assignee rotation (Round-Robin, Least Completed, Random)
 * - Gamification (Points, streaks, leaderboards, achievement badges, confetti)
 * - "Things" tracking (appliances, filters, meters, counters with auto-tasks)
 * - Calendar view
 * - Mount / Tablet Kiosk mode with large touch targets and quick user switcher
 * - Full Administration: Users, Labels, Things, Preferences, Backup & Restore
 */

(function () {
  const I18N = {
    en: {
      appName: "Task Manager",
      chores: "Tasks & Chores",
      calendar: "Calendar",
      things: "Things",
      leaderboard: "Leaderboard",
      settings: "Settings",
      mountMode: "Tablet Mode",
      exitMountMode: "Standard View",
      addTask: "New Chore",
      addThing: "New Thing",
      addUser: "New Member",
      addLabel: "New Label",
      all: "All",
      today: "Today",
      upcoming: "Upcoming",
      overdue: "Overdue",
      completed: "Completed",
      searchPlaceholder: "Search tasks or chores...",
      noTasks: "No tasks found in this view.",
      noThings: "No tracked things yet. Add items like water filters, vacuum bins, or coffee machines!",
      priority: "Priority",
      due: "Due",
      assignee: "Assignee",
      rotation: "Rotation",
      subtasks: "Subtasks",
      points: "Points",
      linkedThing: "Linked Thing",
      save: "Save",
      cancel: "Cancel",
      delete: "Delete",
      edit: "Edit",
      reset: "Reset",
      undo: "Undo",
      recurrence: "Recurrence",
      none: "None",
      daily: "Daily",
      weekly: "Weekly",
      monthly: "Monthly",
      yearly: "Yearly",
      customDays: "Custom Days",
      streak: "Streak",
      completedChores: "Completed",
      exportBackup: "Export Backup (JSON)",
      importBackup: "Import Backup",
      confirmDelete: "Are you sure you want to delete this?",
      soundEnabled: "Completion Sounds",
      confettiEnabled: "Celebration Confetti",
      gamificationEnabled: "Gamification & Points",
      defaultPoints: "Default Points per Task",
      firstDayOfWeek: "First Day of Week",
      monday: "Monday",
      sunday: "Sunday",
      recentActivity: "Recent Activity",
      autoTask: "Auto-creates task when limit reached",
      statusNormal: "Normal",
      statusWarning: "Nearing limit",
      statusAlert: "Limit reached!",
      menuToggle: "Toggle sidebar",
    },
    de: {
      appName: "Task Manager",
      chores: "Aufgaben & Chores",
      calendar: "Kalender",
      things: "Things",
      leaderboard: "Bestenliste",
      settings: "Einstellungen",
      mountMode: "Tablet-Modus",
      exitMountMode: "Standardansicht",
      addTask: "Neue Aufgabe",
      addThing: "Neues Thing",
      addUser: "Neues Mitglied",
      addLabel: "Neues Label",
      all: "Alle",
      today: "Heute",
      upcoming: "Demnächst",
      overdue: "Überfällig",
      completed: "Erledigt",
      searchPlaceholder: "Aufgaben durchsuchen...",
      noTasks: "Keine Aufgaben in dieser Ansicht.",
      noThings: "Noch keine Things hinterlegt. Erfasse Haushaltsgeräte wie Wasserfilter, Staubsauger oder Kaffeemaschine!",
      priority: "Priorität",
      due: "Fällig",
      assignee: "Zuständig",
      rotation: "Rotation",
      subtasks: "Teilaufgaben",
      points: "Punkte",
      linkedThing: "Verknüpftes Thing",
      save: "Speichern",
      cancel: "Abbrechen",
      delete: "Löschen",
      edit: "Bearbeiten",
      reset: "Zurücksetzen",
      undo: "Wiederherstellen",
      recurrence: "Wiederholung",
      none: "Keine",
      daily: "Täglich",
      weekly: "Wöchentlich",
      monthly: "Monatlich",
      yearly: "Jährlich",
      customDays: "Benutzerdefiniert",
      streak: "Serie",
      completedChores: "Erledigt",
      exportBackup: "Backup exportieren (JSON)",
      importBackup: "Backup importieren",
      confirmDelete: "Möchtest du dies wirklich löschen?",
      soundEnabled: "Erledigungs-Sounds",
      confettiEnabled: "Konfetti-Effekt",
      gamificationEnabled: "Gamification & Punkte",
      defaultPoints: "Standard-Punkte pro Aufgabe",
      firstDayOfWeek: "Erster Wochentag",
      monday: "Montag",
      sunday: "Sonntag",
      recentActivity: "Letzte Aktivitäten",
      autoTask: "Erstellt automatisch Aufgabe bei Erreichen",
      statusNormal: "Normal",
      statusWarning: "Bald fällig",
      statusAlert: "Limit erreicht!",
      menuToggle: "Seitenleiste ein-/ausblenden",
    }
  };

  class TaskManagerPanel extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: "open" });
      this._hass = null;
      this._data = {
        tasks: [],
        things: [],
        users: [],
        labels: [],
        settings: {},
        activity_log: []
      };
      this._currentTab = "chores";
      this._filterStatus = "all";
      this._filterAssignee = "all";
      this._filterLabel = "all";
      this._filterPriority = "all";
      this._searchQuery = "";
      this._activeUser = null;
      this._modalState = null;
      this._calendarDate = new Date();
      this._calendarSelectedDay = null;
      this._tabletMode = false;
      this._audioCtx = null;
    }

    connectedCallback() {
      this._onResize = () => this._updateSidebarVisibility();
      window.addEventListener("resize", this._onResize);
      this._updateSidebarVisibility();
    }

    disconnectedCallback() {
      if (this._onResize) {
        window.removeEventListener("resize", this._onResize);
      }
    }

    _isSidebarHidden() {
      if (!this._hass) return true;
      if (window.innerWidth < 870) {
        return true;
      }
      const docked = this._hass.dockedSidebar;
      if (docked === "docked") {
        return false;
      }
      if (docked === "hidden" || docked === "undocked") {
        return true;
      }
      if (docked === "auto") {
        try {
          const ha = document.querySelector("home-assistant");
          const main = ha && ha.shadowRoot && ha.shadowRoot.querySelector("home-assistant-main");
          if (main && main.shadowRoot) {
            const sidebar = main.shadowRoot.querySelector("ha-sidebar");
            if (sidebar) {
              const rect = sidebar.getBoundingClientRect();
              if (rect.width > 50 && sidebar.offsetParent !== null) {
                return false;
              }
            }
          }
        } catch (e) {}
        return true;
      }
      return true;
    }

    _updateSidebarVisibility() {
      const isHidden = this._isSidebarHidden();
      const menuBtn = this.shadowRoot && this.shadowRoot.getElementById("menu-toggle-btn");
      if (menuBtn) {
        menuBtn.style.display = isHidden ? "inline-flex" : "none";
      }
    }

    set hass(hass) {
      const isFirst = !this._hass;
      const prevDocked = this._hass ? this._hass.dockedSidebar : null;
      this._hass = hass;
      if (isFirst) {
        this._initAudio();
        this._fetchData();
      }
      if (prevDocked !== (hass && hass.dockedSidebar)) {
        this._updateSidebarVisibility();
      }
    }

    get lang() {
      const l = (this._hass && (this._hass.language || (this._hass.locale && this._hass.locale.language))) || "en";
      return l.startsWith("de") ? "de" : "en";
    }

    t(key) {
      return (I18N[this.lang] && I18N[this.lang][key]) || I18N.en[key] || key;
    }

    _initAudio() {
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {
          this._audioCtx = new AudioContext();
        }
      } catch (e) {
        // audio optional
      }
    }

    _playSuccessSound() {
      if (!this._data.settings.sound_enabled || !this._audioCtx) return;
      try {
        if (this._audioCtx.state === "suspended") {
          this._audioCtx.resume();
        }
        const osc = this._audioCtx.createOscillator();
        const gain = this._audioCtx.createGain();
        osc.type = "sine";
        osc.connect(gain);
        gain.connect(this._audioCtx.destination);

        const now = this._audioCtx.currentTime;
        osc.frequency.setValueAtTime(587.33, now); // D5
        osc.frequency.exponentialRampToValueAtTime(880.0, now + 0.12); // A5
        gain.gain.setValueAtTime(0.18, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);

        osc.start(now);
        osc.stop(now + 0.35);
      } catch (e) {}
    }

    _triggerConfetti() {
      if (!this._data.settings.confetti_enabled) return;
      const canvas = this.shadowRoot.getElementById("confetti-canvas");
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;

      const particles = [];
      const colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];

      for (let i = 0; i < 70; i++) {
        particles.push({
          x: canvas.width / 2 + (Math.random() * 200 - 100),
          y: canvas.height / 3 + (Math.random() * 100 - 50),
          vx: (Math.random() - 0.5) * 14,
          vy: Math.random() * -12 - 4,
          color: colors[Math.floor(Math.random() * colors.length)],
          size: Math.random() * 8 + 4,
          rot: Math.random() * 360,
          vrot: (Math.random() - 0.5) * 15,
          alpha: 1
        });
      }

      let animId;
      const render = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        let alive = false;
        for (const p of particles) {
          p.x += p.vx;
          p.y += p.vy;
          p.vy += 0.45; // gravity
          p.rot += p.vrot;
          p.alpha -= 0.015;

          if (p.alpha > 0) {
            alive = true;
            ctx.save();
            ctx.globalAlpha = p.alpha;
            ctx.translate(p.x, p.y);
            ctx.rotate((p.rot * Math.PI) / 180);
            ctx.fillStyle = p.color;
            ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.7);
            ctx.restore();
          }
        }
        if (alive) {
          animId = requestAnimationFrame(render);
        } else {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          cancelAnimationFrame(animId);
        }
      };
      render();
    }

    async _fetchData() {
      if (!this._hass) return;
      try {
        const res = await this._hass.callWS({ type: "task_manager/get_data" });
        if (res) {
          this._data = res;
          if (this._data.settings && this._data.settings.tablet_mount_mode && !this._tabletMode) {
            this._tabletMode = true;
          }
          if (!this._activeUser && this._data.users && this._data.users.length > 0) {
            this._activeUser = this._data.users[0].id;
          }
          this._render();
        }
      } catch (err) {
        console.error("Task Manager: Failed to load data", err);
      }
    }

    async _callWS(type, payload = {}) {
      if (!this._hass) return;
      try {
        const res = await this._hass.callWS({ type, ...payload });
        if (res && res.data) {
          this._data = res.data;
          this._render();
        } else {
          await this._fetchData();
        }
        return res;
      } catch (err) {
        console.error(`Task Manager: Error calling ${type}`, err);
        alert(`Error: ${err.message || err}`);
      }
    }

    async completeTask(taskId) {
      this._playSuccessSound();
      this._triggerConfetti();
      await this._callWS("task_manager/complete_task", {
        task_id: taskId,
        user_id: this._activeUser
      });
    }

    async resetTask(taskId) {
      await this._callWS("task_manager/reset_task", { task_id: taskId });
    }

    async deleteTask(taskId) {
      if (confirm(this.t("confirmDelete"))) {
        await this._callWS("task_manager/delete_task", { task_id: taskId });
      }
    }

    async toggleSubtask(taskId, subtaskId, currentState) {
      await this._callWS("task_manager/update_subtask", {
        task_id: taskId,
        subtask_id: subtaskId,
        completed: !currentState
      });
    }

    async updateThingValue(thingId, delta = null, reset = false, value = null) {
      await this._callWS("task_manager/update_thing_value", {
        thing_id: thingId,
        delta: delta,
        reset: reset,
        value: value
      });
    }

    async deleteThing(thingId) {
      if (confirm(this.t("confirmDelete"))) {
        await this._callWS("task_manager/delete_thing", { thing_id: thingId });
      }
    }

    async deleteUser(userId) {
      if (confirm(this.t("confirmDelete"))) {
        await this._callWS("task_manager/delete_user", { user_id: userId });
        if (this._activeUser === userId) {
          this._activeUser = this._data.users[0] ? this._data.users[0].id : null;
        }
      }
    }

    async deleteLabel(labelId) {
      if (confirm(this.t("confirmDelete"))) {
        await this._callWS("task_manager/delete_label", { label_id: labelId });
      }
    }

    _exportBackup() {
      const jsonStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this._data, null, 2));
      const downloadAnchor = document.createElement("a");
      downloadAnchor.setAttribute("href", jsonStr);
      downloadAnchor.setAttribute("download", `task_manager_backup_${new Date().toISOString().slice(0, 10)}.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    }

    async _importBackup(fileInput) {
      const file = fileInput.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const parsed = JSON.parse(e.target.result);
          await this._callWS("task_manager/import_data", { data: parsed });
          alert("Backup imported successfully!");
        } catch (err) {
          alert("Failed to parse JSON backup file: " + err);
        }
      };
      reader.readAsText(file);
    }

    // Modal helpers
    openTaskModal(task = null) {
      this._modalState = { type: "task", task: task || this._getNewTaskTemplate() };
      this._render();
    }

    openThingModal(thing = null) {
      this._modalState = { type: "thing", thing: thing || this._getNewThingTemplate() };
      this._render();
    }

    openUserModal(user = null) {
      this._modalState = { type: "user", user: user || this._getNewUserTemplate() };
      this._render();
    }

    openLabelModal(label = null) {
      this._modalState = { type: "label", label: label || this._getNewLabelTemplate() };
      this._render();
    }

    closeModal() {
      this._modalState = null;
      this._render();
    }

    _getNewTaskTemplate() {
      const today = new Date().toISOString().slice(0, 10);
      return {
        id: "",
        title: "",
        description: "",
        due_date: today,
        due_time: "",
        priority: "none",
        assignees: this._activeUser ? [this._activeUser] : [],
        current_assignee: this._activeUser || "",
        rotation_mode: "none",
        labels: [],
        recurrence: {
          enabled: false,
          type: "none",
          interval: 1,
          days_of_week: [],
          based_on: "due_date"
        },
        subtasks: [],
        points: this._data.settings.default_points || 10,
        linked_thing_id: "",
        thing_action: "reset"
      };
    }

    _getNewThingTemplate() {
      return {
        id: "",
        name: "",
        category: "General",
        icon: "mdi:chart-arc",
        current_value: 0,
        target_value: 30,
        unit: "days",
        auto_task_creation: true,
        auto_task_title: ""
      };
    }

    _getNewUserTemplate() {
      return {
        id: "",
        name: "",
        color: "#3b82f6",
        avatar: "mdi:account",
        points: 0,
        streak: 0
      };
    }

    _getNewLabelTemplate() {
      return {
        id: "",
        name: "",
        color: "#10b981",
        icon: "mdi:tag"
      };
    }

    _getFilteredTasks() {
      let tasks = [...this._data.tasks];
      const todayStr = new Date().toISOString().slice(0, 10);

      // Search filter
      if (this._searchQuery.trim()) {
        const q = this._searchQuery.toLowerCase();
        tasks = tasks.filter(t => (t.title && t.title.toLowerCase().includes(q)) || (t.description && t.description.toLowerCase().includes(q)));
      }

      // Status filter
      if (this._filterStatus === "today") {
        tasks = tasks.filter(t => t.status === "pending" && t.due_date === todayStr);
      } else if (this._filterStatus === "upcoming") {
        tasks = tasks.filter(t => t.status === "pending" && t.due_date > todayStr);
      } else if (this._filterStatus === "overdue") {
        tasks = tasks.filter(t => t.status === "pending" && t.due_date && t.due_date < todayStr);
      } else if (this._filterStatus === "completed") {
        tasks = tasks.filter(t => t.status === "completed");
      } else {
        // 'all' shows pending first, completed can be toggled
        tasks = tasks.filter(t => t.status === "pending");
      }

      // Assignee filter
      if (this._filterAssignee !== "all") {
        tasks = tasks.filter(t => t.current_assignee === this._filterAssignee || (t.assignees && t.assignees.includes(this._filterAssignee)));
      }

      // Label filter
      if (this._filterLabel !== "all") {
        tasks = tasks.filter(t => t.labels && t.labels.includes(this._filterLabel));
      }

      // Priority filter
      if (this._filterPriority !== "all") {
        tasks = tasks.filter(t => t.priority === this._filterPriority);
      }

      // Sort: overdue first, then by due date, then priority
      tasks.sort((a, b) => {
        const pOrder = { p1: 1, p2: 2, p3: 3, p4: 4, none: 5 };
        if (a.due_date !== b.due_date) {
          return (a.due_date || "") < (b.due_date || "") ? -1 : 1;
        }
        return (pOrder[a.priority] || 5) - (pOrder[b.priority] || 5);
      });

      return tasks;
    }

    _render() {
      const todayStr = new Date().toISOString().slice(0, 10);
      const pendingCount = this._data.tasks.filter(t => t.status === "pending").length;
      const todayCount = this._data.tasks.filter(t => t.status === "pending" && t.due_date === todayStr).length;
      const overdueCount = this._data.tasks.filter(t => t.status === "pending" && t.due_date && t.due_date < todayStr).length;

      this.shadowRoot.innerHTML = `
        <style>
          :host {
            display: flex;
            flex-direction: column;
            height: 100%;
            width: 100%;
            background-color: var(--primary-background-color, #f8fafc);
            color: var(--primary-text-color, #0f172a);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            box-sizing: border-box;
            overflow: hidden;
            position: relative;
          }

          * {
            box-sizing: border-box;
          }

          /* Header bar */
          .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 24px;
            background: var(--card-background-color, #ffffff);
            border-bottom: 1px solid var(--divider-color, #e2e8f0);
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
            flex-shrink: 0;
            gap: 16px;
          }

          .header-left {
            display: flex;
            align-items: center;
            gap: 12px;
          }

          .menu-btn {
            background: var(--card-background-color, #ffffff);
            border: 1px solid var(--divider-color, #e2e8f0);
            color: var(--primary-text-color, #0f172a);
            width: 38px;
            height: 38px;
            min-width: 38px;
            border-radius: 10px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.15s ease;
            padding: 0;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
          }

          .menu-btn:hover {
            background: var(--secondary-background-color, #f1f5f9);
            border-color: #2563eb;
            color: #2563eb;
            transform: translateY(-1px);
            box-shadow: 0 2px 6px rgba(37, 99, 235, 0.15);
          }

          .menu-btn:active {
            transform: translateY(0);
          }

          .menu-btn svg {
            display: block;
            pointer-events: none;
          }

          @media (max-width: 870px) {
            .menu-btn {
              display: inline-flex !important;
            }
          }

          .brand {
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
            color: inherit;
          }

          .brand-logo {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-weight: 700;
            font-size: 20px;
            box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25);
          }

          .brand-title {
            font-size: 19px;
            font-weight: 700;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 8px;
          }

          .status-badge {
            font-size: 12px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 9999px;
            background: #dbeafe;
            color: #1d4ed8;
          }

          .header-actions {
            display: flex;
            align-items: center;
            gap: 12px;
          }

          .user-select {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            background: var(--secondary-background-color, #f1f5f9);
            border: 1px solid var(--divider-color, #e2e8f0);
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
          }

          .user-avatar {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 12px;
            font-weight: 600;
          }

          .btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 600;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            transition: all 0.15s ease;
          }

          .btn-primary {
            background: #2563eb;
            color: #ffffff;
            box-shadow: 0 2px 6px rgba(37, 99, 235, 0.3);
          }

          .btn-primary:hover {
            background: #1d4ed8;
            transform: translateY(-1px);
          }

          .btn-secondary {
            background: var(--secondary-background-color, #f1f5f9);
            color: var(--primary-text-color, #334155);
            border: 1px solid var(--divider-color, #cbd5e1);
          }

          .btn-secondary:hover {
            background: #e2e8f0;
          }

          /* Tab navigation */
          .nav-tabs {
            display: flex;
            gap: 6px;
            padding: 10px 24px;
            background: var(--card-background-color, #ffffff);
            border-bottom: 1px solid var(--divider-color, #e2e8f0);
            overflow-x: auto;
          }

          .nav-tab {
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            color: var(--secondary-text-color, #64748b);
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s ease;
            white-space: nowrap;
          }

          .nav-tab:hover {
            background: var(--secondary-background-color, #f8fafc);
            color: var(--primary-text-color, #0f172a);
          }

          .nav-tab.active {
            background: #eff6ff;
            color: #2563eb;
          }

          .badge-pill {
            font-size: 11px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 999px;
            background: #e2e8f0;
            color: #475569;
          }

          .nav-tab.active .badge-pill {
            background: #2563eb;
            color: #ffffff;
          }

          /* Main body */
          .content-area {
            flex: 1;
            overflow-y: auto;
            padding: 20px 24px;
          }

          /* Filters toolbar */
          .toolbar {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 18px;
          }

          .filter-pills {
            display: flex;
            gap: 6px;
            overflow-x: auto;
          }

          .filter-pill {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            background: var(--card-background-color, #ffffff);
            border: 1px solid var(--divider-color, #e2e8f0);
            color: var(--secondary-text-color, #64748b);
            cursor: pointer;
          }

          .filter-pill.active {
            background: #2563eb;
            color: #ffffff;
            border-color: #2563eb;
          }

          .filter-selects {
            display: flex;
            gap: 8px;
          }

          .select-input, .text-input {
            padding: 6px 12px;
            border-radius: 8px;
            border: 1px solid var(--divider-color, #cbd5e1);
            background: var(--card-background-color, #ffffff);
            color: inherit;
            font-size: 13px;
            outline: none;
          }

          /* Tasks list */
          .task-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 14px;
          }

          .task-card {
            background: var(--card-background-color, #ffffff);
            border-radius: 14px;
            border: 1px solid var(--divider-color, #e2e8f0);
            box-shadow: 0 1px 4px rgba(0,0,0,0.03);
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            position: relative;
          }

          .task-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.06);
          }

          .task-card.priority-p1 { border-left: 5px solid #ef4444; }
          .task-card.priority-p2 { border-left: 5px solid #f97316; }
          .task-card.priority-p3 { border-left: 5px solid #3b82f6; }
          .task-card.priority-p4 { border-left: 5px solid #94a3b8; }
          .task-card.completed-task { opacity: 0.7; }

          .task-top {
            display: flex;
            align-items: flex-start;
            gap: 12px;
          }

          .check-btn {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            border: 2px solid #cbd5e1;
            background: transparent;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            color: transparent;
            transition: all 0.2s ease;
            margin-top: 2px;
          }

          .check-btn:hover {
            border-color: #10b981;
            background: #ecfdf5;
            color: #10b981;
          }

          .completed-task .check-btn {
            background: #10b981;
            border-color: #10b981;
            color: #ffffff;
          }

          .task-info {
            flex: 1;
            min-width: 0;
          }

          .task-title {
            font-size: 15px;
            font-weight: 600;
            line-height: 1.3;
            margin: 0 0 4px 0;
            word-break: break-word;
          }

          .completed-task .task-title {
            text-decoration: line-through;
            color: #94a3b8;
          }

          .task-desc {
            font-size: 13px;
            color: var(--secondary-text-color, #64748b);
            margin: 0;
            line-height: 1.4;
          }

          .task-meta {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 6px;
            margin-top: 4px;
          }

          .meta-chip {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 11px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
            background: var(--secondary-background-color, #f1f5f9);
            color: var(--secondary-text-color, #475569);
          }

          .meta-chip.overdue { background: #fee2e2; color: #dc2626; }
          .meta-chip.due-today { background: #fef3c7; color: #d97706; }
          .meta-chip.priority-p1 { background: #fee2e2; color: #b91c1c; }
          .meta-chip.priority-p2 { background: #ffedd5; color: #c2410c; }
          .meta-chip.priority-p3 { background: #dbeafe; color: #1d4ed8; }

          /* Subtasks checklist */
          .subtasks-box {
            background: var(--secondary-background-color, #f8fafc);
            border-radius: 8px;
            padding: 8px 12px;
            margin-top: 4px;
          }

          .subtask-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            padding: 3px 0;
          }

          .subtask-item input {
            cursor: pointer;
          }

          .subtask-title.done {
            text-decoration: line-through;
            color: #94a3b8;
          }

          .task-bottom {
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-top: 1px solid var(--divider-color, #f1f5f9);
            padding-top: 8px;
            margin-top: 4px;
          }

          .assignee-badge {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            font-weight: 500;
          }

          /* Things grid */
          .things-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 16px;
          }

          .thing-card {
            background: var(--card-background-color, #ffffff);
            border-radius: 14px;
            border: 1px solid var(--divider-color, #e2e8f0);
            box-shadow: 0 1px 4px rgba(0,0,0,0.03);
            padding: 18px;
            display: flex;
            flex-direction: column;
            gap: 14px;
          }

          .thing-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
          }

          .thing-title-group {
            display: flex;
            align-items: center;
            gap: 10px;
          }

          .thing-icon {
            width: 38px;
            height: 38px;
            border-radius: 10px;
            background: #eff6ff;
            color: #2563eb;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: bold;
          }

          .progress-bar-bg {
            width: 100%;
            height: 10px;
            background: #e2e8f0;
            border-radius: 999px;
            overflow: hidden;
            margin: 6px 0;
          }

          .progress-bar-fill {
            height: 100%;
            border-radius: 999px;
            transition: width 0.3s ease;
          }

          .fill-green { background: #10b981; }
          .fill-amber { background: #f59e0b; }
          .fill-red { background: #ef4444; }

          .thing-actions {
            display: flex;
            gap: 8px;
          }

          /* Leaderboard */
          .leaderboard-cards {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
          }

          .leaderboard-card {
            background: var(--card-background-color, #ffffff);
            border-radius: 14px;
            border: 1px solid var(--divider-color, #e2e8f0);
            padding: 20px;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
          }

          .rank-badge {
            font-size: 24px;
          }

          .points-huge {
            font-size: 32px;
            font-weight: 800;
            color: #2563eb;
            margin: 4px 0;
          }

          /* Activity log */
          .activity-timeline {
            background: var(--card-background-color, #ffffff);
            border-radius: 14px;
            border: 1px solid var(--divider-color, #e2e8f0);
            padding: 16px;
          }

          .activity-row {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 0;
            border-bottom: 1px solid var(--divider-color, #f1f5f9);
            font-size: 13px;
          }

          /* Calendar View */
          .calendar-box {
            background: var(--card-background-color, #ffffff);
            border-radius: 14px;
            border: 1px solid var(--divider-color, #e2e8f0);
            padding: 20px;
            max-width: 900px;
            margin: 0 auto;
          }

          .calendar-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
          }

          .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 8px;
          }

          .cal-day-header {
            text-align: center;
            font-size: 12px;
            font-weight: 700;
            color: var(--secondary-text-color, #64748b);
            padding: 6px 0;
          }

          .cal-cell {
            min-height: 80px;
            background: var(--secondary-background-color, #f8fafc);
            border-radius: 8px;
            padding: 6px;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            gap: 4px;
            border: 1px solid transparent;
          }

          .cal-cell:hover {
            border-color: #2563eb;
          }

          .cal-cell.today {
            background: #eff6ff;
            border-color: #93c5fd;
          }

          .cal-cell.selected {
            border-color: #2563eb;
            box-shadow: 0 0 0 2px #2563eb;
          }

          .cal-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
          }

          /* Modal dialog */
          .modal-backdrop {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(4px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            padding: 16px;
          }

          .modal-window {
            background: var(--card-background-color, #ffffff);
            border-radius: 16px;
            max-width: 580px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
          }

          .form-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
          }

          .form-label {
            font-size: 13px;
            font-weight: 600;
            color: var(--secondary-text-color, #475569);
          }

          .modal-footer {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 12px;
          }

          /* Confetti canvas */
          #confetti-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 9999;
          }

          /* Tablet Kiosk mount mode */
          :host(.tablet-mode) .header {
            padding: 18px 30px;
          }
          :host(.tablet-mode) .brand-title {
            font-size: 24px;
          }
          :host(.tablet-mode) .btn {
            padding: 12px 22px;
            font-size: 16px;
          }
          :host(.tablet-mode) .task-card {
            padding: 20px;
          }
          :host(.tablet-mode) .check-btn {
            width: 36px;
            height: 36px;
          }
        </style>

        <canvas id="confetti-canvas"></canvas>

        <!-- Top Header -->
        <header class="header">
          <div class="header-left">
            <button class="menu-btn" id="menu-toggle-btn" aria-label="${this.t("menuToggle")}" title="${this.t("menuToggle")}">
              <svg viewBox="0 0 24 24" width="22" height="22" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
                <line x1="3" y1="6" x2="21" y2="6"></line>
                <line x1="3" y1="12" x2="21" y2="12"></line>
                <line x1="3" y1="18" x2="21" y2="18"></line>
              </svg>
            </button>
            <div class="brand">
              <div class="brand-logo">✓</div>
              <div>
                <div class="brand-title">
                  ${this.t("appName")}
                  <span class="status-badge">${pendingCount} ${this.t("chores").toLowerCase()}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="header-actions">
            <!-- Active user switcher -->
            ${this._renderUserSelector()}

            <!-- Tablet mode toggle -->
            <button class="btn btn-secondary" id="btn-toggle-mount">
              ${this._tabletMode ? "📱 " + this.t("exitMountMode") : "📺 " + this.t("mountMode")}
            </button>

            <!-- Add Task CTA -->
            <button class="btn btn-primary" id="btn-add-task">
              + ${this.t("addTask")}
            </button>
          </div>
        </header>

        <!-- Tabs Bar -->
        <nav class="nav-tabs">
          <div class="nav-tab ${this._currentTab === "chores" ? "active" : ""}" data-tab="chores">
            📋 ${this.t("chores")} <span class="badge-pill">${pendingCount}</span>
          </div>
          <div class="nav-tab ${this._currentTab === "calendar" ? "active" : ""}" data-tab="calendar">
            📅 ${this.t("calendar")}
          </div>
          <div class="nav-tab ${this._currentTab === "things" ? "active" : ""}" data-tab="things">
            ⚙️ ${this.t("things")} <span class="badge-pill">${this._data.things.length}</span>
          </div>
          <div class="nav-tab ${this._currentTab === "leaderboard" ? "active" : ""}" data-tab="leaderboard">
            🏆 ${this.t("leaderboard")}
          </div>
          <div class="nav-tab ${this._currentTab === "settings" ? "active" : ""}" data-tab="settings">
            🛠️ ${this.t("settings")}
          </div>
        </nav>

        <!-- Content Area -->
        <main class="content-area">
          ${this._renderTabContent()}
        </main>

        <!-- Modals -->
        ${this._renderModal()}
      `;

      this._attachEventListeners();
      this._updateSidebarVisibility();
    }

    _renderUserSelector() {
      if (!this._data.users || this._data.users.length === 0) return "";
      const currentUser = this._data.users.find(u => u.id === this._activeUser) || this._data.users[0];

      return `
        <select class="user-select" id="header-user-select" title="Active Member">
          ${this._data.users.map(u => `
            <option value="${u.id}" ${u.id === this._activeUser ? "selected" : ""}>
              👤 ${u.name} (${u.points || 0} pts)
            </option>
          `).join("")}
        </select>
      `;
    }

    _renderTabContent() {
      switch (this._currentTab) {
        case "chores":
          return this._renderChoresView();
        case "calendar":
          return this._renderCalendarView();
        case "things":
          return this._renderThingsView();
        case "leaderboard":
          return this._renderLeaderboardView();
        case "settings":
          return this._renderSettingsView();
        default:
          return "";
      }
    }

    // ================= VIEW: CHORES =================
    _renderChoresView() {
      const tasks = this._getFilteredTasks();
      const todayStr = new Date().toISOString().slice(0, 10);
      const overdueCount = this._data.tasks.filter(t => t.status === "pending" && t.due_date && t.due_date < todayStr).length;

      return `
        <div class="toolbar">
          <div class="filter-pills">
            <button class="filter-pill ${this._filterStatus === "all" ? "active" : ""}" data-status="all">${this.t("all")}</button>
            <button class="filter-pill ${this._filterStatus === "today" ? "active" : ""}" data-status="today">🔥 ${this.t("today")}</button>
            <button class="filter-pill ${this._filterStatus === "upcoming" ? "active" : ""}" data-status="upcoming">${this.t("upcoming")}</button>
            <button class="filter-pill ${this._filterStatus === "overdue" ? "active" : ""}" data-status="overdue">
              ⚠️ ${this.t("overdue")} ${overdueCount > 0 ? `(${overdueCount})` : ""}
            </button>
            <button class="filter-pill ${this._filterStatus === "completed" ? "active" : ""}" data-status="completed">✓ ${this.t("completed")}</button>
          </div>

          <div class="filter-selects">
            <input type="text" class="text-input" id="search-input" placeholder="${this.t("searchPlaceholder")}" value="${this._searchQuery}">

            <select class="select-input" id="filter-assignee">
              <option value="all">${this.t("assignee")}: ${this.t("all")}</option>
              ${this._data.users.map(u => `<option value="${u.id}" ${this._filterAssignee === u.id ? "selected" : ""}>${u.name}</option>`).join("")}
            </select>

            <select class="select-input" id="filter-label">
              <option value="all">Label: ${this.t("all")}</option>
              ${this._data.labels.map(l => `<option value="${l.id}" ${this._filterLabel === l.id ? "selected" : ""}>${l.name}</option>`).join("")}
            </select>
          </div>
        </div>

        ${tasks.length === 0 ? `
          <div style="text-align: center; padding: 48px; color: var(--secondary-text-color, #64748b);">
            <div style="font-size: 40px; margin-bottom: 12px;">🎉</div>
            <div style="font-size: 16px; font-weight: 600;">${this.t("noTasks")}</div>
          </div>
        ` : `
          <div class="task-grid">
            ${tasks.map(t => this._renderTaskCard(t, todayStr)).join("")}
          </div>
        `}
      `;
    }

    _renderTaskCard(task, todayStr) {
      const isCompleted = task.status === "completed";
      const isOverdue = !isCompleted && task.due_date && task.due_date < todayStr;
      const isToday = !isCompleted && task.due_date === todayStr;

      const assigneeUser = this._data.users.find(u => u.id === task.current_assignee);
      const linkedThing = task.linked_thing_id ? this._data.things.find(th => th.id === task.linked_thing_id) : null;

      const subtasks = task.subtasks || [];
      const completedSubtasks = subtasks.filter(st => st.completed).length;

      return `
        <div class="task-card priority-${task.priority} ${isCompleted ? "completed-task" : ""}">
          <div class="task-top">
            <button class="check-btn" data-complete-task="${task.id}" title="${isCompleted ? this.t("reset") : "Done!"}">
              ✓
            </button>
            <div class="task-info">
              <div class="task-title">${this._escape(task.title)}</div>
              ${task.description ? `<p class="task-desc">${this._escape(task.description)}</p>` : ""}

              <div class="task-meta">
                ${task.due_date ? `
                  <span class="meta-chip ${isOverdue ? "overdue" : isToday ? "due-today" : ""}">
                    📅 ${task.due_date} ${task.due_time || ""}
                  </span>
                ` : ""}

                ${task.priority && task.priority !== "none" ? `
                  <span class="meta-chip priority-${task.priority}">
                    ${task.priority.toUpperCase()}
                  </span>
                ` : ""}

                ${task.recurrence && task.recurrence.enabled ? `
                  <span class="meta-chip">
                    🔄 ${this.t(task.recurrence.type)} ${task.recurrence.interval > 1 ? `(${task.recurrence.interval})` : ""}
                  </span>
                ` : ""}

                ${task.points ? `
                  <span class="meta-chip" style="background: #fef3c7; color: #b45309;">
                    ⭐ +${task.points} pts
                  </span>
                ` : ""}

                ${linkedThing ? `
                  <span class="meta-chip" style="background: #e0f2fe; color: #0369a1;">
                    ⚙️ ${this._escape(linkedThing.name)}
                  </span>
                ` : ""}

                ${task.labels && task.labels.map(lId => {
                  const lbl = this._data.labels.find(l => l.id === lId);
                  return lbl ? `<span class="meta-chip" style="background:${lbl.color}15; color:${lbl.color};">${this._escape(lbl.name)}</span>` : "";
                }).join("")}
              </div>
            </div>
          </div>

          ${subtasks.length > 0 ? `
            <div class="subtasks-box">
              <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 4px; display:flex; justify-content:space-between;">
                <span>${this.t("subtasks")} (${completedSubtasks}/${subtasks.length})</span>
                ${task.recurrence && task.recurrence.enabled ? `<span>🔄 auto-resets</span>` : ""}
              </div>
              ${subtasks.map(st => `
                <label class="subtask-item">
                  <input type="checkbox" data-subtask-task="${task.id}" data-subtask-id="${st.id}" ${st.completed ? "checked" : ""}>
                  <span class="subtask-title ${st.completed ? "done" : ""}">${this._escape(st.title)}</span>
                </label>
              `).join("")}
            </div>
          ` : ""}

          <div class="task-bottom">
            <div class="assignee-badge">
              ${assigneeUser ? `
                <div class="user-avatar" style="background:${assigneeUser.color}; width:20px; height:20px; font-size:10px;">
                  ${assigneeUser.name.slice(0, 1).toUpperCase()}
                </div>
                <span>${this._escape(assigneeUser.name)}</span>
                ${task.rotation_mode && task.rotation_mode !== "none" ? `<span title="Rotation: ${task.rotation_mode}">🔄</span>` : ""}
              ` : `<span style="color:#94a3b8;">${this.t("none")}</span>`}
            </div>

            <div style="display:flex; gap:6px;">
              <button class="btn btn-secondary" style="padding:4px 8px; font-size:12px;" data-edit-task="${task.id}">✏️</button>
              <button class="btn btn-secondary" style="padding:4px 8px; font-size:12px; color:#ef4444;" data-delete-task="${task.id}">🗑️</button>
            </div>
          </div>
        </div>
      `;
    }

    // ================= VIEW: CALENDAR =================
    _renderCalendarView() {
      const year = this._calendarDate.getFullYear();
      const month = this._calendarDate.getMonth();
      const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

      const firstDay = new Date(year, month, 1);
      const lastDay = new Date(year, month + 1, 0);

      // Start day offset (Monday = 0)
      let startOffset = firstDay.getDay() - 1;
      if (startOffset < 0) startOffset = 6;

      const daysInMonth = lastDay.getDate();
      const todayStr = new Date().toISOString().slice(0, 10);

      // Build task map for this month
      const taskMap = {};
      this._data.tasks.forEach(t => {
        if (t.due_date && t.status === "pending") {
          taskMap[t.due_date] = taskMap[t.due_date] || [];
          taskMap[t.due_date].push(t);
        }
      });

      const dayCells = [];
      for (let i = 0; i < startOffset; i++) {
        dayCells.push(`<div class="cal-cell" style="opacity:0.3;"></div>`);
      }

      for (let d = 1; d <= daysInMonth; d++) {
        const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
        const dayTasks = taskMap[dateStr] || [];
        const isToday = dateStr === todayStr;
        const isSelected = dateStr === this._calendarSelectedDay;

        dayCells.push(`
          <div class="cal-cell ${isToday ? "today" : ""} ${isSelected ? "selected" : ""}" data-cal-date="${dateStr}">
            <div style="font-size:12px; font-weight:700;">${d}</div>
            <div style="display:flex; flex-direction:column; gap:2px;">
              ${dayTasks.slice(0, 3).map(t => `
                <div style="font-size:10px; padding:2px 4px; border-radius:3px; background:#eff6ff; color:#1d4ed8; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                  ${this._escape(t.title)}
                </div>
              `).join("")}
              ${dayTasks.length > 3 ? `<div style="font-size:9px; color:#64748b;">+${dayTasks.length - 3} more</div>` : ""}
            </div>
          </div>
        `);
      }

      return `
        <div class="calendar-box">
          <div class="calendar-header">
            <h2 style="margin:0; font-size:18px;">${monthNames[month]} ${year}</h2>
            <div style="display:flex; gap:8px;">
              <button class="btn btn-secondary" id="cal-prev">◀</button>
              <button class="btn btn-secondary" id="cal-today">${this.t("today")}</button>
              <button class="btn btn-secondary" id="cal-next">▶</button>
            </div>
          </div>

          <div class="calendar-grid">
            <div class="cal-day-header">Mon</div>
            <div class="cal-day-header">Tue</div>
            <div class="cal-day-header">Wed</div>
            <div class="cal-day-header">Thu</div>
            <div class="cal-day-header">Fri</div>
            <div class="cal-day-header">Sat</div>
            <div class="cal-day-header">Sun</div>
            ${dayCells.join("")}
          </div>

          ${this._calendarSelectedDay ? `
            <div style="margin-top:20px; border-top:1px solid #e2e8f0; padding-top:16px;">
              <h3 style="margin:0 0 12px 0;">Chores due on ${this._calendarSelectedDay}:</h3>
              <div class="task-grid">
                ${(taskMap[this._calendarSelectedDay] || []).map(t => this._renderTaskCard(t, todayStr)).join("")}
                ${(taskMap[this._calendarSelectedDay] || []).length === 0 ? `<p style="color:#64748b;">No chores due on this date.</p>` : ""}
              </div>
            </div>
          ` : ""}
        </div>
      `;
    }

    // ================= VIEW: THINGS =================
    _renderThingsView() {
      return `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
          <div>
            <h2 style="margin:0 0 4px 0; font-size:20px;">${this.t("things")}</h2>
            <p style="margin:0; font-size:13px; color:var(--secondary-text-color, #64748b);">
              Track appliances, filter lifespans, and supplies. Connected chores auto-reset these meters!
            </p>
          </div>
          <button class="btn btn-primary" id="btn-add-thing">+ ${this.t("addThing")}</button>
        </div>

        ${this._data.things.length === 0 ? `
          <div style="text-align: center; padding: 48px; color: #64748b;">
            <div style="font-size: 40px; margin-bottom: 12px;">⚙️</div>
            <div>${this.t("noThings")}</div>
          </div>
        ` : `
          <div class="things-grid">
            ${this._data.things.map(th => this._renderThingCard(th)).join("")}
          </div>
        `}
      `;
    }

    _renderThingCard(thing) {
      const cur = parseFloat(thing.current_value) || 0;
      const target = parseFloat(thing.target_value) || 100;
      const pct = Math.min(100, Math.round((cur / target) * 100));

      let fillColor = "fill-green";
      let statusText = this.t("statusNormal");
      if (pct >= 100) {
        fillColor = "fill-red";
        statusText = this.t("statusAlert");
      } else if (pct >= 75) {
        fillColor = "fill-amber";
        statusText = this.t("statusWarning");
      }

      return `
        <div class="thing-card">
          <div class="thing-header">
            <div class="thing-title-group">
              <div class="thing-icon">⚙️</div>
              <div>
                <div style="font-weight:700; font-size:15px;">${this._escape(thing.name)}</div>
                <div style="font-size:12px; color:#64748b;">${this._escape(thing.category || "General")}</div>
              </div>
            </div>
            <div style="display:flex; gap:4px;">
              <button class="btn btn-secondary" style="padding:4px 6px; font-size:11px;" data-edit-thing="${thing.id}">✏️</button>
              <button class="btn btn-secondary" style="padding:4px 6px; font-size:11px; color:#ef4444;" data-delete-thing="${thing.id}">🗑️</button>
            </div>
          </div>

          <div>
            <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600;">
              <span>${cur} / ${target} ${this._escape(thing.unit || "")}</span>
              <span>${pct}%</span>
            </div>
            <div class="progress-bar-bg">
              <div class="progress-bar-fill ${fillColor}" style="width: ${pct}%;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:11px; color:#64748b; margin-top:2px;">
              <span>${statusText}</span>
              ${thing.last_reset ? `<span>Last reset: ${thing.last_reset.slice(0, 10)}</span>` : ""}
            </div>
          </div>

          <div class="thing-actions">
            <button class="btn btn-secondary" style="flex:1;" data-thing-delta="${thing.id}" data-delta="1">+1</button>
            <button class="btn btn-secondary" style="flex:1;" data-thing-delta="${thing.id}" data-delta="-1">-1</button>
            <button class="btn btn-primary" style="flex:1;" data-thing-reset="${thing.id}">↺ ${this.t("reset")}</button>
          </div>
        </div>
      `;
    }

    // ================= VIEW: LEADERBOARD =================
    _renderLeaderboardView() {
      const sortedUsers = [...this._data.users].sort((a, b) => (b.points || 0) - (a.points || 0));

      return `
        <div style="max-width: 900px; margin: 0 auto;">
          <h2 style="margin: 0 0 18px 0; font-size: 20px;">🏆 ${this.t("leaderboard")} & Streaks</h2>

          <div class="leaderboard-cards">
            ${sortedUsers.map((u, index) => `
              <div class="leaderboard-card">
                <div class="rank-badge">${index === 0 ? "🥇" : index === 1 ? "🥈" : index === 2 ? "🥉" : "⭐"}</div>
                <div class="user-avatar" style="background:${u.color}; width:48px; height:48px; font-size:20px;">
                  ${u.name.slice(0, 1).toUpperCase()}
                </div>
                <div style="font-weight:700; font-size:16px;">${this._escape(u.name)}</div>
                <div class="points-huge">${u.points || 0} <span style="font-size:14px; font-weight:500;">pts</span></div>
                <div style="display:flex; gap:12px; font-size:12px; color:#64748b;">
                  <span>🔥 ${u.streak || 0} day streak</span>
                  <span>✓ ${u.completed_count || 0} tasks done</span>
                </div>
              </div>
            `).join("")}
          </div>

          <h3 style="margin: 24px 0 12px 0; font-size: 16px;">📜 ${this.t("recentActivity")}</h3>
          <div class="activity-timeline">
            ${this._data.activity_log && this._data.activity_log.length > 0 ? (
              this._data.activity_log.slice(-15).reverse().map(act => `
                <div class="activity-row">
                  <div style="font-size:16px;">
                    ${act.action === "task_completed" ? "✅" : act.action === "task_created" ? "📝" : "⚙️"}
                  </div>
                  <div style="flex:1;">
                    <strong>${this._escape(act.title || act.name || act.action)}</strong>
                    ${act.user_id ? `<span> by ${this._getUserName(act.user_id)}</span>` : ""}
                    ${act.points ? `<span style="color:#d97706; font-weight:600;"> (+${act.points} pts)</span>` : ""}
                  </div>
                  <div style="font-size:11px; color:#64748b;">
                    ${act.timestamp ? act.timestamp.slice(11, 16) : ""}
                  </div>
                </div>
              `).join("")
            ) : `<p style="color:#64748b; font-size:13px;">No recent activity yet.</p>`}
          </div>
        </div>
      `;
    }

    _getUserName(userId) {
      const u = this._data.users.find(user => user.id === userId);
      return u ? u.name : userId;
    }

    // ================= VIEW: SETTINGS =================
    _renderSettingsView() {
      const s = this._data.settings || {};

      return `
        <div style="max-width: 800px; margin: 0 auto; display: flex; flex-direction: column; gap: 24px;">
          <!-- Members Management -->
          <div style="background:var(--card-background-color, #ffffff); border-radius:14px; border:1px solid #e2e8f0; padding:20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
              <h3 style="margin:0; font-size:16px;">👥 Household Members</h3>
              <button class="btn btn-secondary" id="btn-add-user">+ ${this.t("addUser")}</button>
            </div>
            <div style="display:flex; flex-direction:column; gap:8px;">
              ${this._data.users.map(u => `
                <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 12px; background:#f8fafc; border-radius:8px;">
                  <div style="display:flex; align-items:center; gap:10px;">
                    <div class="user-avatar" style="background:${u.color}; width:28px; height:28px;">
                      ${u.name.slice(0, 1).toUpperCase()}
                    </div>
                    <strong>${this._escape(u.name)}</strong>
                    <span style="font-size:12px; color:#64748b;">(${u.points || 0} pts)</span>
                  </div>
                  <div style="display:flex; gap:6px;">
                    <button class="btn btn-secondary" style="padding:4px 8px; font-size:11px;" data-edit-user="${u.id}">✏️</button>
                    <button class="btn btn-secondary" style="padding:4px 8px; font-size:11px; color:#ef4444;" data-delete-user="${u.id}">🗑️</button>
                  </div>
                </div>
              `).join("")}
            </div>
          </div>

          <!-- Labels Management -->
          <div style="background:var(--card-background-color, #ffffff); border-radius:14px; border:1px solid #e2e8f0; padding:20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
              <h3 style="margin:0; font-size:16px;">🏷️ Labels & Categories</h3>
              <button class="btn btn-secondary" id="btn-add-label">+ ${this.t("addLabel")}</button>
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:8px;">
              ${this._data.labels.map(l => `
                <div style="display:flex; align-items:center; gap:6px; padding:4px 10px; border-radius:20px; background:${l.color}18; color:${l.color}; font-size:13px; font-weight:600;">
                  <span>${this._escape(l.name)}</span>
                  <button style="border:none; background:transparent; cursor:pointer; color:inherit; font-size:12px;" data-edit-label="${l.id}">✏️</button>
                  <button style="border:none; background:transparent; cursor:pointer; color:inherit; font-size:12px;" data-delete-label="${l.id}">×</button>
                </div>
              `).join("")}
            </div>
          </div>

          <!-- System Preferences -->
          <div style="background:var(--card-background-color, #ffffff); border-radius:14px; border:1px solid #e2e8f0; padding:20px;">
            <h3 style="margin:0 0 16px 0; font-size:16px;">⚙️ Preferences</h3>
            <div style="display:flex; flex-direction:column; gap:12px;">
              <label style="display:flex; align-items:center; gap:10px; font-size:14px; cursor:pointer;">
                <input type="checkbox" id="pref-gamification" ${s.gamification_enabled ? "checked" : ""}>
                <span>${this.t("gamificationEnabled")}</span>
              </label>

              <label style="display:flex; align-items:center; gap:10px; font-size:14px; cursor:pointer;">
                <input type="checkbox" id="pref-sounds" ${s.sound_enabled ? "checked" : ""}>
                <span>${this.t("soundEnabled")}</span>
              </label>

              <label style="display:flex; align-items:center; gap:10px; font-size:14px; cursor:pointer;">
                <input type="checkbox" id="pref-confetti" ${s.confetti_enabled ? "checked" : ""}>
                <span>${this.t("confettiEnabled")}</span>
              </label>

              <div class="form-group" style="max-width:240px; margin-top:8px;">
                <label class="form-label">${this.t("defaultPoints")}</label>
                <input type="number" class="text-input" id="pref-default-points" value="${s.default_points || 10}">
              </div>

              <button class="btn btn-primary" style="align-self:flex-start; margin-top:10px;" id="btn-save-prefs">
                ${this.t("save")}
              </button>
            </div>
          </div>

          <!-- Backup & Restore -->
          <div style="background:var(--card-background-color, #ffffff); border-radius:14px; border:1px solid #e2e8f0; padding:20px;">
            <h3 style="margin:0 0 12px 0; font-size:16px;">💾 Data Backup & Restore</h3>
            <p style="font-size:13px; color:#64748b; margin-top:0;">Download a complete JSON export of all your tasks, things, users, and history, or restore from a backup.</p>
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
              <button class="btn btn-secondary" id="btn-export-backup">📥 ${this.t("exportBackup")}</button>
              <label class="btn btn-secondary" style="cursor:pointer;">
                📤 ${this.t("importBackup")}
                <input type="file" id="input-import-backup" accept=".json" style="display:none;">
              </label>
            </div>
          </div>
        </div>
      `;
    }

    // ================= MODALS =================
    _renderModal() {
      if (!this._modalState) return "";
      const { type } = this._modalState;

      if (type === "task") return this._renderTaskModal();
      if (type === "thing") return this._renderThingModal();
      if (type === "user") return this._renderUserModal();
      if (type === "label") return this._renderLabelModal();
      return "";
    }

    _renderTaskModal() {
      const task = this._modalState.task;
      const rec = task.recurrence || {};
      const subtasks = task.subtasks || [];

      return `
        <div class="modal-backdrop" id="modal-backdrop">
          <div class="modal-window">
            <h2 style="margin:0 0 12px 0; font-size:18px;">
              ${task.id ? this.t("edit") : this.t("addTask")}
            </h2>

            <div class="form-group">
              <label class="form-label">Title *</label>
              <input type="text" class="text-input" id="m-task-title" value="${this._escape(task.title)}" placeholder="e.g. Clean kitchen counters">
            </div>

            <div class="form-group">
              <label class="form-label">Description</label>
              <textarea class="text-input" id="m-task-desc" rows="2" placeholder="Optional notes...">${this._escape(task.description)}</textarea>
            </div>

            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
              <div class="form-group">
                <label class="form-label">${this.t("due")} Date</label>
                <input type="date" class="text-input" id="m-task-date" value="${task.due_date || ""}">
              </div>
              <div class="form-group">
                <label class="form-label">${this.t("due")} Time</label>
                <input type="time" class="text-input" id="m-task-time" value="${task.due_time || ""}">
              </div>
            </div>

            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
              <div class="form-group">
                <label class="form-label">${this.t("priority")}</label>
                <select class="select-input" id="m-task-priority">
                  <option value="none" ${task.priority === "none" ? "selected" : ""}>None</option>
                  <option value="p1" ${task.priority === "p1" ? "selected" : ""}>P1 (Urgent - Red)</option>
                  <option value="p2" ${task.priority === "p2" ? "selected" : ""}>P2 (High - Orange)</option>
                  <option value="p3" ${task.priority === "p3" ? "selected" : ""}>P3 (Medium - Blue)</option>
                  <option value="p4" ${task.priority === "p4" ? "selected" : ""}>P4 (Low - Gray)</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">${this.t("points")} Reward</label>
                <input type="number" class="text-input" id="m-task-points" value="${task.points || 10}">
              </div>
            </div>

            <!-- Assignee & Rotation -->
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
              <div class="form-group">
                <label class="form-label">${this.t("assignee")}</label>
                <select class="select-input" id="m-task-assignee">
                  <option value="">None</option>
                  ${this._data.users.map(u => `
                    <option value="${u.id}" ${u.id === task.current_assignee ? "selected" : ""}>${u.name}</option>
                  `).join("")}
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">${this.t("rotation")}</label>
                <select class="select-input" id="m-task-rotation">
                  <option value="none" ${task.rotation_mode === "none" ? "selected" : ""}>None (Fixed)</option>
                  <option value="round_robin" ${task.rotation_mode === "round_robin" ? "selected" : ""}>Round-Robin</option>
                  <option value="least_completed" ${task.rotation_mode === "least_completed" ? "selected" : ""}>Least Completed</option>
                  <option value="random" ${task.rotation_mode === "random" ? "selected" : ""}>Random</option>
                </select>
              </div>
            </div>

            <!-- Recurrence -->
            <div style="border:1px solid #e2e8f0; border-radius:10px; padding:12px;">
              <label style="display:flex; align-items:center; gap:8px; font-weight:600; font-size:14px; cursor:pointer;">
                <input type="checkbox" id="m-task-rec-enable" ${rec.enabled ? "checked" : ""}>
                <span>${this.t("recurrence")} (Smart Schedule)</span>
              </label>

              <div id="m-rec-fields" style="display:${rec.enabled ? "grid" : "none"}; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px;">
                <div class="form-group">
                  <label class="form-label">Type</label>
                  <select class="select-input" id="m-task-rec-type">
                    <option value="daily" ${rec.type === "daily" ? "selected" : ""}>Daily</option>
                    <option value="weekly" ${rec.type === "weekly" ? "selected" : ""}>Weekly</option>
                    <option value="monthly" ${rec.type === "monthly" ? "selected" : ""}>Monthly</option>
                    <option value="yearly" ${rec.type === "yearly" ? "selected" : ""}>Yearly</option>
                    <option value="custom_days" ${rec.type === "custom_days" ? "selected" : ""}>Every X Days</option>
                  </select>
                </div>

                <div class="form-group">
                  <label class="form-label">Interval</label>
                  <input type="number" class="text-input" id="m-task-rec-interval" value="${rec.interval || 1}" min="1">
                </div>

                <div class="form-group" style="grid-column: span 2;">
                  <label class="form-label">Recurrence Cadence</label>
                  <select class="select-input" id="m-task-rec-based">
                    <option value="due_date" ${rec.based_on === "due_date" ? "selected" : ""}>From Scheduled Due Date (Fixed Cadence)</option>
                    <option value="completion_date" ${rec.based_on === "completion_date" ? "selected" : ""}>From Actual Completion Date (Adaptive)</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Subtasks Checklist -->
            <div class="form-group">
              <label class="form-label">${this.t("subtasks")} (Automatically resets on completion!)</label>
              <div id="subtasks-container" style="display:flex; flex-direction:column; gap:6px;">
                ${subtasks.map((st, i) => `
                  <div style="display:flex; gap:6px;">
                    <input type="text" class="text-input m-subtask-input" value="${this._escape(st.title)}" style="flex:1;">
                    <button class="btn btn-secondary btn-del-subtask" data-index="${i}">×</button>
                  </div>
                `).join("")}
              </div>
              <button class="btn btn-secondary" style="align-self:flex-start; margin-top:6px; font-size:12px;" id="btn-add-subtask-row">
                + Add Subtask Step
              </button>
            </div>

            <!-- Linked Thing -->
            <div class="form-group">
              <label class="form-label">${this.t("linkedThing")}</label>
              <select class="select-input" id="m-task-linked-thing">
                <option value="">None</option>
                ${this._data.things.map(th => `
                  <option value="${th.id}" ${th.id === task.linked_thing_id ? "selected" : ""}>
                    ${th.name} (${th.current_value}/${th.target_value} ${th.unit})
                  </option>
                `).join("")}
              </select>
            </div>

            <div class="modal-footer">
              <button class="btn btn-secondary" id="modal-cancel">${this.t("cancel")}</button>
              <button class="btn btn-primary" id="modal-save-task">${this.t("save")}</button>
            </div>
          </div>
        </div>
      `;
    }

    _renderThingModal() {
      const thing = this._modalState.thing;
      return `
        <div class="modal-backdrop" id="modal-backdrop">
          <div class="modal-window">
            <h2 style="margin:0 0 12px 0; font-size:18px;">
              ${thing.id ? this.t("edit") : this.t("addThing")}
            </h2>

            <div class="form-group">
              <label class="form-label">Name *</label>
              <input type="text" class="text-input" id="m-thing-name" value="${this._escape(thing.name)}" placeholder="e.g. Robot Vacuum Dustbin">
            </div>

            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
              <div class="form-group">
                <label class="form-label">Category</label>
                <input type="text" class="text-input" id="m-thing-category" value="${this._escape(thing.category)}" placeholder="Kitchen, Living room...">
              </div>
              <div class="form-group">
                <label class="form-label">Unit of measurement</label>
                <input type="text" class="text-input" id="m-thing-unit" value="${this._escape(thing.unit)}" placeholder="days, runs, hours, L...">
              </div>
            </div>

            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
              <div class="form-group">
                <label class="form-label">Current Value</label>
                <input type="number" class="text-input" id="m-thing-current" value="${thing.current_value || 0}">
              </div>
              <div class="form-group">
                <label class="form-label">Target / Max Limit</label>
                <input type="number" class="text-input" id="m-thing-target" value="${thing.target_value || 30}">
              </div>
            </div>

            <div class="form-group">
              <label style="display:flex; align-items:center; gap:8px; font-size:13px; font-weight:600; cursor:pointer;">
                <input type="checkbox" id="m-thing-auto-task" ${thing.auto_task_creation ? "checked" : ""}>
                <span>${this.t("autoTask")}</span>
              </label>
            </div>

            <div class="form-group">
              <label class="form-label">Auto-Generated Task Title</label>
              <input type="text" class="text-input" id="m-thing-task-title" value="${this._escape(thing.auto_task_title || "")}" placeholder="e.g. Empty Robot Vacuum Dustbin">
            </div>

            <div class="modal-footer">
              <button class="btn btn-secondary" id="modal-cancel">${this.t("cancel")}</button>
              <button class="btn btn-primary" id="modal-save-thing">${this.t("save")}</button>
            </div>
          </div>
        </div>
      `;
    }

    _renderUserModal() {
      const user = this._modalState.user;
      return `
        <div class="modal-backdrop" id="modal-backdrop">
          <div class="modal-window">
            <h2 style="margin:0 0 12px 0; font-size:18px;">
              ${user.id ? this.t("edit") : this.t("addUser")}
            </h2>

            <div class="form-group">
              <label class="form-label">Member Name *</label>
              <input type="text" class="text-input" id="m-user-name" value="${this._escape(user.name)}" placeholder="e.g. Alex">
            </div>

            <div class="form-group">
              <label class="form-label">Color Theme</label>
              <input type="color" id="m-user-color" value="${user.color || "#3b82f6"}" style="width:60px; height:36px; border:none; border-radius:6px; cursor:pointer;">
            </div>

            <div class="form-group">
              <label class="form-label">Points</label>
              <input type="number" class="text-input" id="m-user-points" value="${user.points || 0}">
            </div>

            <div class="modal-footer">
              <button class="btn btn-secondary" id="modal-cancel">${this.t("cancel")}</button>
              <button class="btn btn-primary" id="modal-save-user">${this.t("save")}</button>
            </div>
          </div>
        </div>
      `;
    }

    _renderLabelModal() {
      const label = this._modalState.label;
      return `
        <div class="modal-backdrop" id="modal-backdrop">
          <div class="modal-window">
            <h2 style="margin:0 0 12px 0; font-size:18px;">
              ${label.id ? this.t("edit") : this.t("addLabel")}
            </h2>

            <div class="form-group">
              <label class="form-label">Label Name *</label>
              <input type="text" class="text-input" id="m-label-name" value="${this._escape(label.name)}" placeholder="e.g. Garden">
            </div>

            <div class="form-group">
              <label class="form-label">Color</label>
              <input type="color" id="m-label-color" value="${label.color || "#10b981"}" style="width:60px; height:36px; border:none; border-radius:6px; cursor:pointer;">
            </div>

            <div class="modal-footer">
              <button class="btn btn-secondary" id="modal-cancel">${this.t("cancel")}</button>
              <button class="btn btn-primary" id="modal-save-label">${this.t("save")}</button>
            </div>
          </div>
        </div>
      `;
    }

    // ================= EVENT ATTACHMENT =================
    _attachEventListeners() {
      const root = this.shadowRoot;

      // Hamburger Menu Toggle (opens/closes Home Assistant sidebar)
      const menuToggleBtn = root.getElementById("menu-toggle-btn");
      if (menuToggleBtn) {
        menuToggleBtn.addEventListener("click", (e) => {
          e.preventDefault();
          e.stopPropagation();
          const event = new CustomEvent("hass-toggle-menu", {
            bubbles: true,
            composed: true,
            detail: { open: true },
          });
          this.dispatchEvent(event);
          window.dispatchEvent(event);
          try {
            const ha = document.querySelector("home-assistant");
            const main = ha && ha.shadowRoot && ha.shadowRoot.querySelector("home-assistant-main");
            if (main) {
              main.dispatchEvent(new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true, detail: { open: true } }));
            }
          } catch (err) {}
          if (window.parent && window.parent !== window) {
            try {
              window.parent.dispatchEvent(new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true, detail: { open: true } }));
            } catch (err) {}
          }
        });
      }

      // Nav Tabs
      root.querySelectorAll(".nav-tab").forEach(tab => {
        tab.addEventListener("click", () => {
          this._currentTab = tab.getAttribute("data-tab");
          this._render();
        });
      });

      // Filter pills
      root.querySelectorAll(".filter-pill").forEach(pill => {
        pill.addEventListener("click", () => {
          this._filterStatus = pill.getAttribute("data-status");
          this._render();
        });
      });

      // Search
      const searchInput = root.getElementById("search-input");
      if (searchInput) {
        searchInput.addEventListener("input", (e) => {
          this._searchQuery = e.target.value;
          this._render();
        });
      }

      // Assignee Filter
      const assigneeFilter = root.getElementById("filter-assignee");
      if (assigneeFilter) {
        assigneeFilter.addEventListener("change", (e) => {
          this._filterAssignee = e.target.value;
          this._render();
        });
      }

      // Label Filter
      const labelFilter = root.getElementById("filter-label");
      if (labelFilter) {
        labelFilter.addEventListener("change", (e) => {
          this._filterLabel = e.target.value;
          this._render();
        });
      }

      // Active User Header Select
      const headerUserSelect = root.getElementById("header-user-select");
      if (headerUserSelect) {
        headerUserSelect.addEventListener("change", (e) => {
          this._activeUser = e.target.value;
          this._render();
        });
      }

      // Tablet / Mount Mode toggle
      const btnMount = root.getElementById("btn-toggle-mount");
      if (btnMount) {
        btnMount.addEventListener("click", () => {
          this._tabletMode = !this._tabletMode;
          if (this._tabletMode) {
            this.classList.add("tablet-mode");
          } else {
            this.classList.remove("tablet-mode");
          }
          this._render();
        });
      }

      // Add Task Button
      const btnAddTask = root.getElementById("btn-add-task");
      if (btnAddTask) {
        btnAddTask.addEventListener("click", () => this.openTaskModal());
      }

      // Add Thing Button
      const btnAddThing = root.getElementById("btn-add-thing");
      if (btnAddThing) {
        btnAddThing.addEventListener("click", () => this.openThingModal());
      }

      // Add User Button
      const btnAddUser = root.getElementById("btn-add-user");
      if (btnAddUser) {
        btnAddUser.addEventListener("click", () => this.openUserModal());
      }

      // Add Label Button
      const btnAddLabel = root.getElementById("btn-add-label");
      if (btnAddLabel) {
        btnAddLabel.addEventListener("click", () => this.openLabelModal());
      }

      // Task complete toggle
      root.querySelectorAll("[data-complete-task]").forEach(btn => {
        btn.addEventListener("click", (e) => {
          const tId = btn.getAttribute("data-complete-task");
          const task = this._data.tasks.find(t => t.id === tId);
          if (task && task.status === "completed") {
            this.resetTask(tId);
          } else {
            this.completeTask(tId);
          }
        });
      });

      // Task Subtask Toggle
      root.querySelectorAll("[data-subtask-task]").forEach(cb => {
        cb.addEventListener("change", (e) => {
          const tId = cb.getAttribute("data-subtask-task");
          const stId = cb.getAttribute("data-subtask-id");
          this.toggleSubtask(tId, stId, !cb.checked);
        });
      });

      // Task Edit / Delete
      root.querySelectorAll("[data-edit-task]").forEach(btn => {
        btn.addEventListener("click", () => {
          const t = this._data.tasks.find(x => x.id === btn.getAttribute("data-edit-task"));
          if (t) this.openTaskModal(t);
        });
      });

      root.querySelectorAll("[data-delete-task]").forEach(btn => {
        btn.addEventListener("click", () => this.deleteTask(btn.getAttribute("data-delete-task")));
      });

      // Thing actions
      root.querySelectorAll("[data-thing-delta]").forEach(btn => {
        btn.addEventListener("click", () => {
          const id = btn.getAttribute("data-thing-delta");
          const delta = parseFloat(btn.getAttribute("data-delta"));
          this.updateThingValue(id, delta);
        });
      });

      root.querySelectorAll("[data-thing-reset]").forEach(btn => {
        btn.addEventListener("click", () => {
          const id = btn.getAttribute("data-thing-reset");
          this.updateThingValue(id, null, true);
        });
      });

      root.querySelectorAll("[data-edit-thing]").forEach(btn => {
        btn.addEventListener("click", () => {
          const th = this._data.things.find(x => x.id === btn.getAttribute("data-edit-thing"));
          if (th) this.openThingModal(th);
        });
      });

      root.querySelectorAll("[data-delete-thing]").forEach(btn => {
        btn.addEventListener("click", () => this.deleteThing(btn.getAttribute("data-delete-thing")));
      });

      // User actions
      root.querySelectorAll("[data-edit-user]").forEach(btn => {
        btn.addEventListener("click", () => {
          const u = this._data.users.find(x => x.id === btn.getAttribute("data-edit-user"));
          if (u) this.openUserModal(u);
        });
      });

      root.querySelectorAll("[data-delete-user]").forEach(btn => {
        btn.addEventListener("click", () => this.deleteUser(btn.getAttribute("data-delete-user")));
      });

      // Label actions
      root.querySelectorAll("[data-edit-label]").forEach(btn => {
        btn.addEventListener("click", () => {
          const l = this._data.labels.find(x => x.id === btn.getAttribute("data-edit-label"));
          if (l) this.openLabelModal(l);
        });
      });

      root.querySelectorAll("[data-delete-label]").forEach(btn => {
        btn.addEventListener("click", () => this.deleteLabel(btn.getAttribute("data-delete-label")));
      });

      // Calendar controls
      const calPrev = root.getElementById("cal-prev");
      if (calPrev) {
        calPrev.addEventListener("click", () => {
          this._calendarDate.setMonth(this._calendarDate.getMonth() - 1);
          this._render();
        });
      }
      const calNext = root.getElementById("cal-next");
      if (calNext) {
        calNext.addEventListener("click", () => {
          this._calendarDate.setMonth(this._calendarDate.getMonth() + 1);
          this._render();
        });
      }
      const calToday = root.getElementById("cal-today");
      if (calToday) {
        calToday.addEventListener("click", () => {
          this._calendarDate = new Date();
          this._calendarSelectedDay = new Date().toISOString().slice(0, 10);
          this._render();
        });
      }
      root.querySelectorAll("[data-cal-date]").forEach(cell => {
        cell.addEventListener("click", () => {
          this._calendarSelectedDay = cell.getAttribute("data-cal-date");
          this._render();
        });
      });

      // Backup & Settings
      const btnExport = root.getElementById("btn-export-backup");
      if (btnExport) btnExport.addEventListener("click", () => this._exportBackup());

      const inputImport = root.getElementById("input-import-backup");
      if (inputImport) {
        inputImport.addEventListener("change", (e) => this._importBackup(e.target));
      }

      const btnSavePrefs = root.getElementById("btn-save-prefs");
      if (btnSavePrefs) {
        btnSavePrefs.addEventListener("click", async () => {
          const newPrefs = {
            gamification_enabled: root.getElementById("pref-gamification").checked,
            sound_enabled: root.getElementById("pref-sounds").checked,
            confetti_enabled: root.getElementById("pref-confetti").checked,
            default_points: parseInt(root.getElementById("pref-default-points").value, 10) || 10
          };
          await this._callWS("task_manager/update_settings", { settings: newPrefs });
          alert("Preferences saved!");
        });
      }

      // Modal Events
      const modalCancel = root.getElementById("modal-cancel");
      if (modalCancel) modalCancel.addEventListener("click", () => this.closeModal());

      const modalBackdrop = root.getElementById("modal-backdrop");
      if (modalBackdrop) {
        modalBackdrop.addEventListener("click", (e) => {
          if (e.target === modalBackdrop) this.closeModal();
        });
      }

      // Modal Save Task
      const btnSaveTask = root.getElementById("modal-save-task");
      if (btnSaveTask) {
        btnSaveTask.addEventListener("click", async () => {
          const title = root.getElementById("m-task-title").value.trim();
          if (!title) {
            alert("Title is required!");
            return;
          }
          const recEnabled = root.getElementById("m-task-rec-enable").checked;
          const subtaskInputs = root.querySelectorAll(".m-subtask-input");
          const subtasks = Array.from(subtaskInputs).map(inp => inp.value.trim()).filter(Boolean);

          const assignee = root.getElementById("m-task-assignee").value;

          const taskPayload = {
            id: this._modalState.task.id || undefined,
            title: title,
            description: root.getElementById("m-task-desc").value.trim(),
            due_date: root.getElementById("m-task-date").value,
            due_time: root.getElementById("m-task-time").value,
            priority: root.getElementById("m-task-priority").value,
            points: parseInt(root.getElementById("m-task-points").value, 10) || 10,
            assignees: assignee ? [assignee] : [],
            current_assignee: assignee || null,
            rotation_mode: root.getElementById("m-task-rotation").value,
            recurrence: {
              enabled: recEnabled,
              type: root.getElementById("m-task-rec-type") ? root.getElementById("m-task-rec-type").value : "none",
              interval: parseInt(root.getElementById("m-task-rec-interval") ? root.getElementById("m-task-rec-interval").value : "1", 10),
              based_on: root.getElementById("m-task-rec-based") ? root.getElementById("m-task-rec-based").value : "due_date"
            },
            subtasks: subtasks,
            linked_thing_id: root.getElementById("m-task-linked-thing").value || null,
            thing_action: "reset"
          };

          await this._callWS("task_manager/save_task", { task: taskPayload });
          this.closeModal();
        });
      }

      // Modal Recurrence Toggle
      const mRecEnable = root.getElementById("m-task-rec-enable");
      if (mRecEnable) {
        mRecEnable.addEventListener("change", (e) => {
          const f = root.getElementById("m-rec-fields");
          if (f) f.style.display = e.target.checked ? "grid" : "none";
        });
      }

      // Modal Add Subtask Row
      const btnAddSubtaskRow = root.getElementById("btn-add-subtask-row");
      if (btnAddSubtaskRow) {
        btnAddSubtaskRow.addEventListener("click", () => {
          const container = root.getElementById("subtasks-container");
          const div = document.createElement("div");
          div.style.cssText = "display:flex; gap:6px;";
          div.innerHTML = `
            <input type="text" class="text-input m-subtask-input" placeholder="New subtask step..." style="flex:1;">
            <button class="btn btn-secondary btn-del-subtask">×</button>
          `;
          div.querySelector(".btn-del-subtask").addEventListener("click", () => div.remove());
          container.appendChild(div);
        });
      }

      root.querySelectorAll(".btn-del-subtask").forEach(btn => {
        btn.addEventListener("click", (e) => {
          e.target.parentElement.remove();
        });
      });

      // Modal Save Thing
      const btnSaveThing = root.getElementById("modal-save-thing");
      if (btnSaveThing) {
        btnSaveThing.addEventListener("click", async () => {
          const name = root.getElementById("m-thing-name").value.trim();
          if (!name) {
            alert("Name is required!");
            return;
          }
          const thingPayload = {
            id: this._modalState.thing.id || undefined,
            name: name,
            category: root.getElementById("m-thing-category").value.trim(),
            unit: root.getElementById("m-thing-unit").value.trim(),
            current_value: parseFloat(root.getElementById("m-thing-current").value) || 0,
            target_value: parseFloat(root.getElementById("m-thing-target").value) || 30,
            auto_task_creation: root.getElementById("m-thing-auto-task").checked,
            auto_task_title: root.getElementById("m-thing-task-title").value.trim()
          };

          await this._callWS("task_manager/save_thing", { thing: thingPayload });
          this.closeModal();
        });
      }

      // Modal Save User
      const btnSaveUser = root.getElementById("modal-save-user");
      if (btnSaveUser) {
        btnSaveUser.addEventListener("click", async () => {
          const name = root.getElementById("m-user-name").value.trim();
          if (!name) {
            alert("Name is required!");
            return;
          }
          const userPayload = {
            id: this._modalState.user.id || undefined,
            name: name,
            color: root.getElementById("m-user-color").value,
            points: parseInt(root.getElementById("m-user-points").value, 10) || 0
          };

          await this._callWS("task_manager/save_user", { user: userPayload });
          this.closeModal();
        });
      }

      // Modal Save Label
      const btnSaveLabel = root.getElementById("modal-save-label");
      if (btnSaveLabel) {
        btnSaveLabel.addEventListener("click", async () => {
          const name = root.getElementById("m-label-name").value.trim();
          if (!name) {
            alert("Name is required!");
            return;
          }
          const labelPayload = {
            id: this._modalState.label.id || undefined,
            name: name,
            color: root.getElementById("m-label-color").value
          };

          await this._callWS("task_manager/save_label", { label: labelPayload });
          this.closeModal();
        });
      }
    }

    _escape(text) {
      if (!text) return "";
      const div = document.createElement("div");
      div.textContent = text;
      return div.innerHTML;
    }
  }

  customElements.define("task-manager-panel", TaskManagerPanel);
  console.info("Task Manager sidebar panel registered successfully");
})();
