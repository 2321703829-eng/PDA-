(function () {
  "use strict";

  const API_PREFIX = "/api/pda/wms/v1";
  const STORAGE = {
    token: "tianshu.pda.token",
    user: "tianshu.pda.user",
    warehouses: "tianshu.pda.warehouses",
    warehouseId: "tianshu.pda.warehouseId",
    apiBase: "tianshu.pda.apiBase",
    deviceId: "tianshu.pda.deviceId",
  };

  const ENDPOINTS = {
    inbound: {
      title: "入库收货",
      subtitle: "扫描商品条码，录入实收数量，确认后可完成收货任务。",
      list: `${API_PREFIX}/receipt/tasks`,
      lines: (id) => `${API_PREFIX}/receipt/tasks/${id}/lines`,
      confirm: (id) => `${API_PREFIX}/receipt/tasks/${id}/confirm-line`,
      complete: (id) => `${API_PREFIX}/receipt/tasks/${id}/complete`,
      qtyKey: "done_qty",
      qtyLabel: "实收数量",
      completeText: "完成收货",
      needsLocation: false,
    },
    outbound: {
      title: "出库处理",
      subtitle: "当前沿用 PDA 复核接口完成出库前扫描确认；如后端补独立出库接口，只需替换这里的 endpoint。",
      list: `${API_PREFIX}/check/tasks`,
      lines: (id) => `${API_PREFIX}/check/tasks/${id}/lines`,
      confirm: (id) => `${API_PREFIX}/check/tasks/${id}/confirm-line`,
      complete: (id) => `${API_PREFIX}/check/tasks/${id}/complete`,
      qtyKey: "checked_qty",
      qtyLabel: "确认数量",
      completeText: "完成出库复核",
      needsLocation: false,
    },
    pick: {
      title: "拣货任务",
      subtitle: "扫描商品条码与库位条码，确认拣货数量，最后完成拣货。",
      list: `${API_PREFIX}/pick/tasks`,
      lines: (id) => `${API_PREFIX}/pick/tasks/${id}/lines`,
      confirm: (id) => `${API_PREFIX}/pick/tasks/${id}/confirm-line`,
      complete: (id) => `${API_PREFIX}/pick/tasks/${id}/complete`,
      qtyKey: "done_qty",
      qtyLabel: "拣货数量",
      completeText: "完成拣货",
      needsLocation: true,
    },
    putaway: {
      title: "上架任务",
      subtitle: "扫描商品条码与目标库位条码，确认上架数量，最后完成上架。",
      list: `${API_PREFIX}/putaway/tasks`,
      lines: (id) => `${API_PREFIX}/putaway/tasks/${id}/lines`,
      confirm: (id) => `${API_PREFIX}/putaway/tasks/${id}/confirm`,
      complete: (id) => `${API_PREFIX}/putaway/tasks/${id}/complete`,
      qtyKey: "qty",
      qtyLabel: "上架数量",
      completeText: "完成上架",
      needsLocation: true,
      locationLabel: "目标库位条码",
      locationKey: "dest_location_barcode",
    },
  };

  const FLOW_GROUPS = {
    "inbound-flow": {
      title: "入库上架",
      subtitle: "按 PRD 合并收货与上架：待收货、待上架在一个入口内推进，扫码贯穿商品和库位确认。",
      scanPlaceholder: "扫收货任务 / 上架任务 / 商品 / 库位",
      defaultMode: "inbound",
      tabs: [
        { mode: "inbound", label: "待收货", hint: "扫码收货、数量确认、异常预留" },
        { mode: "putaway", label: "待上架", hint: "扫商品与目标库位，确认上架" },
      ],
    },
    "outbound-flow": {
      title: "出库履约",
      subtitle: "按 PRD 合并拣货与复核：待拣货、待复核、待交接沿同一履约链路推进。",
      scanPlaceholder: "扫拣货任务 / 复核任务 / 商品 / 库位 / 集货位",
      defaultMode: "pick",
      tabs: [
        { mode: "pick", label: "待拣货", hint: "领取任务、扫库位、扫商品确认数量" },
        { mode: "outbound", label: "待复核", hint: "复核装箱、数量确认、交接预留" },
      ],
    },
  };

  const HOME_MODULES = [
    { route: "inbound-flow", icon: "IN", title: "入库上架", desc: "收货、异常预留、上架确认" },
    { route: "outbound-flow", icon: "OUT", title: "出库履约", desc: "拣货、复核、交接预留" },
    { route: "inventory", icon: "INV", title: "库存库位", desc: "商品、库位、库存明细查询" },
    { route: "transfer", icon: "MOVE", title: "调拨下架", desc: "下架退库、移库、补货" },
  ];

  const STATUS_LABELS = {
    waiting_receipt: "待收货",
    receiving: "收货中",
    received: "已收货",
    receipt_exception: "收货异常",
    waiting_putaway: "待上架",
    putaway_ing: "上架中",
    putaway_done: "已上架",
    putaway_exception: "上架异常",
    waiting_pick: "待拣货",
    picking: "拣货中",
    picked: "已拣货",
    pick_exception: "拣货异常",
    waiting_check: "待复核",
    checking: "复核中",
    checked: "已复核",
    check_exception: "复核异常",
  };

  const STATUS_FLOWS = {
    inbound: ["waiting_receipt", "receiving", "received", "waiting_putaway", "putaway_ing", "putaway_done"],
    putaway: ["waiting_putaway", "putaway_ing", "putaway_done"],
    pick: ["waiting_pick", "picking", "picked", "waiting_check"],
    outbound: ["waiting_check", "checking", "checked"],
  };

  const NEXT_ACTION_HINTS = {
    waiting_receipt: "下一步：扫商品并录入实收数量。",
    receiving: "下一步：继续确认收货明细，完成后生成上架任务。",
    received: "已完成收货：请进入待上架继续库位上架。",
    waiting_putaway: "下一步：扫商品和目标库位，确认上架数量。",
    putaway_ing: "下一步：继续确认上架明细，全部完成后点完成上架。",
    putaway_done: "已完成上架：库位库存已形成。",
    waiting_pick: "下一步：扫来源库位、商品和拣货数量。",
    picking: "下一步：继续拣货，完成后生成复核任务。",
    picked: "已完成拣货：请进入待复核继续出库履约。",
    waiting_check: "下一步：扫商品并确认复核数量。",
    checking: "下一步：继续复核，完成后进入交接预留。",
    checked: "已完成复核：可进入交接出库。",
  };

  const DOWN_SHELF_REASONS = [
    ["location_cleanup", "库位整理"],
    ["replenishment", "拣货位补货"],
    ["damaged", "破损下架"],
    ["expired", "临期下架"],
    ["misplaced", "错放调整"],
    ["supervisor", "主管指令"],
    ["other", "其他"],
  ];

  const TRANSFER_TYPES = [
    ["warehouse_return", "下架退库"],
    ["internal_move", "仓内移库"],
    ["replenishment", "补货上架"],
  ];

  const OPERATION_STATE_LABELS = {
    draft: "草稿",
    in_progress: "进行中",
    done: "已完成",
    cancelled: "已取消",
  };

  const state = {
    route: "login",
    token: localStorage.getItem(STORAGE.token) || "",
    user: readJson(STORAGE.user, null),
    warehouses: readJson(STORAGE.warehouses, []),
    warehouseId: localStorage.getItem(STORAGE.warehouseId) || "",
    deviceId: ensureDeviceId(),
    inventoryMode: "product",
    pendingInventoryCode: "",
    flowModes: {
      "inbound-flow": "inbound",
      "outbound-flow": "pick",
    },
    workbenchSummary: null,
    activeTasks: {},
    activeLines: {},
    lineMatches: {},
    downShelfOperation: null,
    downShelfLines: [],
    downShelfLastResult: null,
    loading: false,
  };

  const root = document.getElementById("viewRoot");
  const toast = document.getElementById("toast");
  const backButton = document.getElementById("backButton");
  const logoutButton = document.getElementById("logoutButton");
  const warehouseSelect = document.getElementById("warehouseSelect");
  const warehouseField = document.querySelector(".warehouse-field");

  document.addEventListener("DOMContentLoaded", init);

  function init() {
    window.addEventListener("hashchange", renderFromHash);
    backButton.addEventListener("click", () => navigate("home"));
    logoutButton.addEventListener("click", logout);
    warehouseSelect.addEventListener("change", switchWarehouse);
    renderFromHash();
  }

  function renderFromHash() {
    const route = (location.hash.replace(/^#\/?/, "") || "").split("?")[0];
    state.route = route || (state.token ? "home" : "login");
    if (!state.token && state.route !== "login") {
      navigate("login", true);
      return;
    }
    render();
  }

  function navigate(route, replace) {
    const next = `#/${route}`;
    if (replace) {
      history.replaceState(null, "", next);
      renderFromHash();
      return;
    }
    location.hash = next;
  }

  function render() {
    syncChrome();
    if (state.route === "login") {
      renderLogin();
      return;
    }
    if (state.route === "home") {
      renderHome();
      return;
    }
    if (FLOW_GROUPS[state.route]) {
      renderFlowPage(state.route);
      return;
    }
    if (state.route === "inventory") {
      renderInventory();
      return;
    }
    if (state.route === "downshelf" || state.route === "transfer") {
      renderDownShelf();
      return;
    }
    if (state.route === "exceptions") {
      renderExceptionPlaceholder();
      return;
    }
    if (ENDPOINTS[state.route]) {
      renderTaskPage(state.route);
      return;
    }
    navigate("home", true);
  }

  function syncChrome() {
    const loggedIn = Boolean(state.token);
    backButton.classList.toggle("is-visible", loggedIn && state.route !== "home");
    logoutButton.classList.toggle("is-visible", loggedIn);
    warehouseField.classList.toggle("is-visible", loggedIn && state.warehouses.length > 0);
    warehouseSelect.innerHTML = state.warehouses
      .map((wh) => `<option value="${escapeAttr(wh.id)}">${escapeHtml(wh.name || wh.display_name || `仓库 ${wh.id}`)}</option>`)
      .join("");
    if (state.warehouseId) {
      warehouseSelect.value = String(state.warehouseId);
    }
  }

  function renderLogin() {
    root.innerHTML = `
      <section class="hero">
        <div class="hero-content">
          <span class="eyebrow">Tianshu PDA Lite</span>
          <h1>仓内作业轻量入口</h1>
          <p>面向 PDA 与扫码枪的 H5 页面，仅加载原生 HTML/CSS/JS，进入后直接处理入库、出库、拣货和库存扫码查询。</p>
        </div>
      </section>
      <section class="login-panel">
        <div class="page-title">
          <div>
            <h1>登录 PDA</h1>
            <p>请使用已开通 PDA 权限的系统账号。测试账号不在页面明文展示。</p>
          </div>
          <span class="status-pill">/pda</span>
        </div>
        <form id="loginForm" class="form-grid" autocomplete="off">
          <label class="field">
            <span>账号</span>
            <input class="text-input" name="login" type="text" inputmode="text" autocomplete="username" required />
          </label>
          <label class="field">
            <span>密码</span>
            <input class="text-input" name="password" type="password" autocomplete="current-password" required />
          </label>
          <button class="primary-button" type="submit">登录</button>
        </form>
      </section>
    `;
    const form = document.getElementById("loginForm");
    form.addEventListener("submit", submitLogin);
    focusFirst("input[name='login']");
  }

  async function submitLogin(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries());
    try {
      setBusy(form, true);
      const result = await apiPost(`${API_PREFIX}/auth/login`, {
        login: data.login,
        password: data.password,
        device_id: state.deviceId,
      }, { auth: false });
      state.token = result.token || "";
      state.user = result.user || {};
      state.warehouses = result.warehouses || [];
      state.warehouseId = result.current_warehouse_id || (state.warehouses[0] && state.warehouses[0].id) || "";
      if (!state.token) {
        throw new Error("登录成功但未返回 token，请检查后端 PDA 登录接口。");
      }
      localStorage.setItem(STORAGE.token, state.token);
      localStorage.setItem(STORAGE.user, JSON.stringify(state.user || {}));
      localStorage.setItem(STORAGE.warehouses, JSON.stringify(state.warehouses || []));
      localStorage.setItem(STORAGE.warehouseId, String(state.warehouseId || ""));
      showToast("登录成功");
      navigate("home", true);
    } catch (error) {
      showError(error);
    } finally {
      setBusy(form, false);
    }
  }

  function renderHome() {
    root.innerHTML = `
      <section class="hero hero-compact">
        <div class="hero-content">
          <span class="eyebrow">Tianshu PDA Lite</span>
          <h1>仓库移动作业台</h1>
          <p>工作台优先展示今日待办，通过统一扫码进入入库上架、出库履约、库存库位和调拨下架。</p>
        </div>
      </section>
      <section class="work-panel">
        <div class="page-title">
          <div>
            <h1>现场工作台</h1>
            <p>${escapeHtml(currentWarehouseName())}，${escapeHtml(currentUserName())}。</p>
          </div>
          <button id="refreshWorkbench" class="refresh-button" type="button">刷新</button>
        </div>
        ${renderGlobalScan("homeScanForm", "扫商品 / 库位 / 单据 / 任务号")}
        <div class="section-title">
          <strong>今日待办</strong>
          <small>按当前仓库和账号聚合</small>
        </div>
        <div id="todoGrid" class="todo-grid">
          ${renderTodoSkeleton()}
        </div>
        <div class="section-title">
          <strong>常用作业</strong>
          <small>按 PRD 合并后的一级入口</small>
        </div>
        <div class="action-grid">
          ${HOME_MODULES.map((item) => moduleButton(item.route, item.icon, item.title, item.desc)).join("")}
        </div>
      </section>
    `;
    root.querySelectorAll("[data-route]").forEach((button) => {
      button.addEventListener("click", () => navigate(button.dataset.route));
    });
    document.getElementById("homeScanForm").addEventListener("submit", submitGlobalScan);
    document.getElementById("refreshWorkbench").addEventListener("click", loadWorkbenchSummary);
    loadWorkbenchSummary();
    focusFirst("#homeScanCode");
  }

  function moduleButton(route, icon, title, desc) {
    return `
      <button class="module-button" type="button" data-route="${route}">
        <span class="module-icon">${escapeHtml(icon)}</span>
        <strong>${escapeHtml(title)}</strong>
        <span>${escapeHtml(desc)}</span>
      </button>
    `;
  }

  function renderGlobalScan(formId, placeholder) {
    const inputId = formId === "homeScanForm" ? "homeScanCode" : `${formId}Code`;
    return `
      <form id="${escapeAttr(formId)}" class="global-scan" autocomplete="off">
        <label class="field">
          <span>统一扫码</span>
          <input id="${escapeAttr(inputId)}" class="text-input" name="barcode" type="text" inputmode="text" autocomplete="off" placeholder="${escapeAttr(placeholder)}" required />
        </label>
        <button class="primary-button" type="submit">识别</button>
      </form>
    `;
  }

  function renderTodoSkeleton() {
    return ["待收货", "待上架", "待拣货", "待复核", "异常待处理"].map((label) => `
      <button class="todo-card" type="button" disabled>
        <span>${escapeHtml(label)}</span>
        <strong>...</strong>
      </button>
    `).join("");
  }

  async function loadWorkbenchSummary() {
    const grid = document.getElementById("todoGrid");
    if (!grid) {
      return;
    }
    grid.innerHTML = renderTodoSkeleton();
    try {
      const data = await apiGet(`${API_PREFIX}/workbench/summary`);
      state.workbenchSummary = data;
      grid.innerHTML = renderTodoGrid(data.todos || []);
      grid.querySelectorAll("[data-todo-route]").forEach((button) => {
        button.addEventListener("click", () => {
          const route = button.dataset.todoRoute;
          const mode = button.dataset.todoMode;
          if (mode) {
            state.flowModes[route] = mode;
          }
          navigate(route);
        });
      });
    } catch (error) {
      grid.innerHTML = `<div class="error-state full-row">${escapeHtml(messageOf(error))}</div>`;
    }
  }

  function renderTodoGrid(todos) {
    if (!todos.length) {
      return `<div class="empty-state full-row">暂无待办数据。</div>`;
    }
    return todos.map((item) => `
      <button class="todo-card" type="button" data-todo-route="${escapeAttr(item.route || "home")}" data-todo-mode="${escapeAttr(item.mode || "")}">
        <span>${escapeHtml(item.label)}</span>
        <strong>${escapeHtml(item.count ?? 0)}</strong>
      </button>
    `).join("");
  }

  async function renderFlowPage(route) {
    const group = FLOW_GROUPS[route];
    const mode = state.flowModes[route] || group.defaultMode;
    const config = ENDPOINTS[mode];
    root.innerHTML = `
      <section class="task-panel">
        <div class="page-title">
          <div>
            <h1>${escapeHtml(group.title)}</h1>
            <p>${escapeHtml(group.subtitle)}</p>
          </div>
          <span class="status-pill">${escapeHtml(currentWarehouseName())}</span>
        </div>
        ${renderGlobalScan(`${route}ScanForm`, group.scanPlaceholder)}
        <div class="flow-tabs">
          ${group.tabs.map((tab) => `
            <button class="seg-button ${tab.mode === mode ? "is-active" : ""}" type="button" data-flow-route="${escapeAttr(route)}" data-flow-mode="${escapeAttr(tab.mode)}">
              <strong>${escapeHtml(tab.label)}</strong>
              <small>${escapeHtml(tab.hint)}</small>
            </button>
          `).join("")}
        </div>
        <div class="task-layout">
          <section class="task-list">
            <div class="list-header">
              <strong>${escapeHtml(config.title)}</strong>
              <button id="refreshTasks" class="refresh-button" type="button">刷新</button>
            </div>
            <div id="taskItems" class="task-items">
              <div class="empty-state">正在读取任务...</div>
            </div>
          </section>
          <section class="task-detail">
            <div class="detail-header">
              <strong>任务明细</strong>
              <button id="completeTask" class="refresh-button" type="button" disabled>${escapeHtml(config.completeText)}</button>
            </div>
            <div id="detailBody" class="detail-body">
              <div class="empty-state">请选择左侧任务。</div>
            </div>
          </section>
        </div>
      </section>
    `;
    document.getElementById(`${route}ScanForm`).addEventListener("submit", submitGlobalScan);
    root.querySelectorAll("[data-flow-mode]").forEach((button) => {
      button.addEventListener("click", () => {
        state.flowModes[button.dataset.flowRoute] = button.dataset.flowMode;
        renderFlowPage(button.dataset.flowRoute);
      });
    });
    document.getElementById("refreshTasks").addEventListener("click", () => loadTasks(mode));
    document.getElementById("completeTask").addEventListener("click", () => completeTask(mode));
    await loadTasks(mode);
  }

  async function submitGlobalScan(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const input = form.querySelector("input[name='barcode']");
    const barcode = (input && input.value || "").trim();
    if (!barcode) {
      return;
    }
    try {
      setBusy(form, true);
      const result = await apiPost(`${API_PREFIX}/scan/resolve`, {
        barcode,
        device_id: state.deviceId,
        current_route: state.route,
      });
      handleScanResolution(result, barcode);
      if (input) {
        input.value = "";
      }
    } catch (error) {
      showError(error);
      if (input) {
        input.select();
      }
    } finally {
      setBusy(form, false);
    }
  }

  function handleScanResolution(result, scannedCode) {
    const route = result.route || "home";
    const mode = result.mode || "";
    if (mode && FLOW_GROUPS[route]) {
      state.flowModes[route] = mode;
      if (result.target_id) {
        state.activeTasks[`${mode}:id`] = Number(result.target_id);
      }
      showToast(result.message || "已识别任务");
      openRoute(route);
      return;
    }
    if (route === "inventory") {
      state.inventoryMode = result.inventory_mode || "product";
      state.pendingInventoryCode = result.barcode || scannedCode;
      showToast(result.message || "进入库存库位");
      openRoute("inventory");
      return;
    }
    if (route === "outbound-flow" || route === "inbound-flow") {
      showToast(result.message || "已识别单据");
      openRoute(route);
      return;
    }
    showToast(result.message || "已识别条码");
  }

  function openRoute(route) {
    if (state.route === route) {
      renderFromHash();
      return;
    }
    navigate(route);
  }

  async function renderTaskPage(mode) {
    const config = ENDPOINTS[mode];
    root.innerHTML = `
      <section class="task-panel">
        <div class="page-title">
          <div>
            <h1>${escapeHtml(config.title)}</h1>
            <p>${escapeHtml(config.subtitle)}</p>
          </div>
          <span class="status-pill">${escapeHtml(currentWarehouseName())}</span>
        </div>
        <div class="task-layout">
          <section class="task-list">
            <div class="list-header">
              <strong>待处理任务</strong>
              <button id="refreshTasks" class="refresh-button" type="button">刷新</button>
            </div>
            <div id="taskItems" class="task-items">
              <div class="empty-state">正在读取任务...</div>
            </div>
          </section>
          <section class="task-detail">
            <div class="detail-header">
              <strong>任务明细</strong>
              <button id="completeTask" class="refresh-button" type="button" disabled>${escapeHtml(config.completeText)}</button>
            </div>
            <div id="detailBody" class="detail-body">
              <div class="empty-state">请选择左侧任务。</div>
            </div>
          </section>
        </div>
      </section>
    `;
    document.getElementById("refreshTasks").addEventListener("click", () => loadTasks(mode));
    document.getElementById("completeTask").addEventListener("click", () => completeTask(mode));
    await loadTasks(mode);
  }

  async function loadTasks(mode) {
    const config = ENDPOINTS[mode];
    const container = document.getElementById("taskItems");
    const detail = document.getElementById("detailBody");
    container.innerHTML = `<div class="empty-state">正在读取任务...</div>`;
    document.getElementById("completeTask").disabled = true;
    try {
      const data = await apiGet(config.list, { limit: 50 });
      const records = getRecords(data);
      state.activeTasks[mode] = records;
      if (!records.length) {
        const focusedId = activeTaskId(mode);
        container.innerHTML = `<div class="empty-state">${focusedId ? "正在打开扫码指定任务..." : "暂无待处理任务。"}</div>`;
        if (focusedId) {
          await selectTask(mode, Number(focusedId));
          const focusedTask = state.activeTasks[`${mode}:focusedTask`];
          container.innerHTML = focusedTask
            ? taskCard(focusedTask, true)
            : `<div class="empty-state">当前任务已打开，请在右侧扫码处理。</div>`;
          return;
        }
        detail.innerHTML = `<div class="empty-state">没有需要处理的任务。</div>`;
        return;
      }
      container.innerHTML = records.map((task) => taskCard(task, activeTaskId(mode) === task.id)).join("");
      container.querySelectorAll("[data-task-id]").forEach((button) => {
        button.addEventListener("click", () => selectTask(mode, Number(button.dataset.taskId)));
      });
      const firstId = activeTaskId(mode) || records[0].id;
      await selectTask(mode, firstId);
    } catch (error) {
      container.innerHTML = `<div class="error-state">${escapeHtml(messageOf(error))}</div>`;
      detail.innerHTML = `<div class="hint-state">如果这里是 404，说明当前后端还没有启用该 PDA 接口；H5 页面本身已做好接入。</div>`;
    }
  }

  function taskCard(task, active) {
    const name = task.name || task.picking_name || task.outbound_task_name || `任务 ${task.id}`;
    const partner = task.partner_name || task.warehouse_name || task.source_location || "";
    const summary = task.product_summary || task.picking_name || task.outbound_task_name || task.state_label || "";
    const status = task.state || "";
    const progress = taskProgressText(task);
    return `
      <button class="task-card ${active ? "is-active" : ""}" type="button" data-task-id="${escapeAttr(task.id)}">
        <span class="task-card-top">
          <strong>${escapeHtml(name)}</strong>
          ${status ? `<em class="state-tag ${isDoneState(status) ? "is-done" : isExceptionState(status) ? "is-error" : ""}">${escapeHtml(statusLabel(status))}</em>` : ""}
        </span>
        <small>${escapeHtml([partner, summary].filter(Boolean).join(" · ") || "点击查看明细")}</small>
        ${progress ? `<small class="task-progress">${escapeHtml(progress)}</small>` : ""}
      </button>
    `;
  }

  async function selectTask(mode, taskId) {
    const config = ENDPOINTS[mode];
    const detail = document.getElementById("detailBody");
    state.activeTasks[`${mode}:id`] = taskId;
    document.querySelectorAll(".task-card").forEach((card) => {
      card.classList.toggle("is-active", Number(card.dataset.taskId) === taskId);
    });
    detail.innerHTML = `<div class="empty-state">正在读取明细...</div>`;
    document.getElementById("completeTask").disabled = true;
    try {
      const data = await apiGet(config.lines(taskId));
      const lines = normalizeLines(data.lines || data.records || [], mode);
      const task = data.task || findTask(mode, taskId);
      if (task) {
        state.activeTasks[`${mode}:focusedTask`] = task;
      }
      state.activeLines[mode] = lines;
      state.lineMatches[mode] = "";
      detail.innerHTML = renderScanBox(mode, task, lines);
      bindScanForm(mode);
      document.getElementById("completeTask").disabled = false;
      focusFirst("#productBarcode");
    } catch (error) {
      detail.innerHTML = `<div class="error-state">${escapeHtml(messageOf(error))}</div>`;
    }
  }

  function renderScanBox(mode, task, lines) {
    const config = ENDPOINTS[mode];
    const taskName = task && (task.name || task.picking_name || task.outbound_task_name) || "当前任务";
    const taskState = task && task.state || "";
    return `
      ${renderTaskStatus(mode, taskState)}
      <div class="scan-box">
        <h2>${escapeHtml(taskName)}</h2>
        <form id="scanForm" class="scan-form" autocomplete="off">
          <label class="field">
            <span>商品条码</span>
            <input id="productBarcode" class="text-input" name="barcode" type="text" inputmode="text" autocomplete="off" placeholder="扫描或输入商品条码" required />
          </label>
          ${config.needsLocation ? `
            <label class="field">
              <span>${escapeHtml(config.locationLabel || "库位条码")}</span>
              <input id="locationBarcode" class="text-input" name="location_barcode" type="text" inputmode="text" autocomplete="off" placeholder="${escapeAttr(config.locationPlaceholder || "扫描库位")}" required />
            </label>
          ` : ""}
          <label class="field">
            <span>${escapeHtml(config.qtyLabel)}</span>
            <input id="qtyInput" class="qty-input" name="qty" type="number" min="0" step="0.001" inputmode="decimal" placeholder="数量" required />
          </label>
          <button class="primary-button full-row" type="submit">确认本行</button>
          <button class="refresh-button full-row" type="button" data-route="exceptions">上报异常</button>
        </form>
      </div>
      <div class="line-grid" id="lineGrid">
        ${lines.length ? lines.map((line) => lineCard(line, state.lineMatches[mode])).join("") : `<div class="empty-state">暂无明细。</div>`}
      </div>
    `;
  }

  function renderTaskStatus(mode, stateValue) {
    const label = statusLabel(stateValue);
    const hint = NEXT_ACTION_HINTS[stateValue] || "请选择任务后按页面提示扫码处理。";
    const flow = STATUS_FLOWS[mode] || [];
    const currentIndex = flow.indexOf(stateValue);
    return `
      <div class="status-panel">
        <div class="status-summary">
          <span>当前状态</span>
          <strong>${escapeHtml(label || "未选择")}</strong>
          <small>${escapeHtml(hint)}</small>
        </div>
        ${flow.length ? `
          <div class="state-flow">
            ${flow.map((step, index) => `
              <span class="${stateFlowClass(step, stateValue, currentIndex, index)}">${escapeHtml(statusLabel(step))}</span>
            `).join("")}
          </div>
        ` : ""}
      </div>
    `;
  }

  function bindScanForm(mode) {
    const form = document.getElementById("scanForm");
    const productInput = document.getElementById("productBarcode");
    const locationInput = document.getElementById("locationBarcode");
    productInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && locationInput && !locationInput.value.trim()) {
        event.preventDefault();
        updateMatchedLine(mode);
        locationInput.focus();
      }
    });
    productInput.addEventListener("input", () => updateMatchedLine(mode));
    form.addEventListener("submit", (event) => confirmLine(event, mode));
    form.querySelectorAll("[data-route]").forEach((button) => {
      button.addEventListener("click", () => navigate(button.dataset.route));
    });
  }

  function updateMatchedLine(mode) {
    const barcode = document.getElementById("productBarcode").value.trim();
    const lines = state.activeLines[mode] || [];
    const match = lines.find((line) => productMatches(line, barcode));
    state.lineMatches[mode] = match ? match.key : "";
    if (match) {
      const qty = preferredQty(match);
      const qtyInput = document.getElementById("qtyInput");
      if (qty && !qtyInput.value) {
        qtyInput.value = qty;
      }
    }
    const grid = document.getElementById("lineGrid");
    if (grid) {
      grid.innerHTML = lines.map((line) => lineCard(line, state.lineMatches[mode])).join("");
    }
  }

  async function confirmLine(event, mode) {
    event.preventDefault();
    const config = ENDPOINTS[mode];
    const taskId = activeTaskId(mode);
    const form = event.currentTarget;
    const productBarcode = document.getElementById("productBarcode").value.trim();
    const qty = document.getElementById("qtyInput").value;
    const payload = {
      request_id: requestId(`${mode}_line`),
      device_id: state.deviceId,
      barcode: productBarcode,
      product_barcode: productBarcode,
    };
    payload[config.qtyKey] = qty;
    if (config.needsLocation) {
      const locationBarcode = document.getElementById("locationBarcode").value.trim();
      const locationKey = config.locationKey || "location_barcode";
      payload[locationKey] = locationBarcode;
      if (locationKey !== "location_barcode") {
        payload.location_barcode = locationBarcode;
      }
    }
    try {
      setBusy(form, true);
      await apiPost(config.confirm(taskId), payload);
      showToast("已确认");
      await selectTask(mode, taskId);
    } catch (error) {
      showError(error);
    } finally {
      setBusy(form, false);
    }
  }

  async function completeTask(mode) {
    const config = ENDPOINTS[mode];
    const taskId = activeTaskId(mode);
    if (!taskId) {
      return;
    }
    const button = document.getElementById("completeTask");
    try {
      button.disabled = true;
      await apiPost(config.complete(taskId), {
        request_id: requestId(`${mode}_complete`),
        device_id: state.deviceId,
      });
      showToast("任务已完成");
      state.activeTasks[`${mode}:id`] = "";
      await loadTasks(mode);
    } catch (error) {
      showError(error);
    } finally {
      button.disabled = false;
    }
  }

  function statusLabel(stateValue) {
    return STATUS_LABELS[stateValue] || stateValue || "";
  }

  function isDoneState(stateValue) {
    return ["received", "putaway_done", "picked", "checked"].includes(stateValue);
  }

  function isExceptionState(stateValue) {
    return String(stateValue || "").includes("exception");
  }

  function stateFlowClass(step, currentState, currentIndex, index) {
    const classes = ["state-step"];
    if (step === currentState) {
      classes.push("is-current");
    } else if (currentIndex >= 0 && index < currentIndex) {
      classes.push("is-past");
    }
    if (isDoneState(step)) {
      classes.push("is-terminal");
    }
    return classes.join(" ");
  }

  function taskProgressText(task) {
    const parts = [];
    if (Number.isFinite(Number(task.done_line_count)) || Number.isFinite(Number(task.line_count))) {
      const done = Number(task.done_line_count || 0);
      const total = Number(task.line_count || 0);
      if (total) {
        parts.push(`明细 ${done}/${total}`);
      }
    }
    if (Number.isFinite(Number(task.done_qty)) || Number.isFinite(Number(task.putaway_qty)) || Number.isFinite(Number(task.total_demand_qty))) {
      const doneQty = task.done_qty ?? task.putaway_qty ?? task.total_picked_qty ?? 0;
      const demandQty = task.demand_qty ?? task.total_qty ?? task.total_demand_qty ?? "";
      if (demandQty !== "") {
        parts.push(`数量 ${formatQty(doneQty)}/${formatQty(demandQty)}`);
      }
    }
    if (task.create_date) {
      parts.push(`创建 ${String(task.create_date).slice(0, 16)}`);
    }
    return parts.join(" · ");
  }

  function lineCard(line, matchedKey) {
    const isMatch = matchedKey && matchedKey === line.key;
    const qtyText = `${formatQty(line.doneQty)} / ${formatQty(line.demandQty)} ${line.uom || ""}`;
    return `
      <article class="line-card ${isMatch ? "is-match" : ""}">
        <div>
          <strong>${escapeHtml(line.productName || "未命名商品")}</strong>
          <small>${escapeHtml([line.defaultCode, line.barcode, line.location].filter(Boolean).join(" · ") || "无条码信息")}</small>
        </div>
        <div class="qty">${escapeHtml(qtyText)}</div>
      </article>
    `;
  }

  function renderDownShelf() {
    const operation = state.downShelfOperation;
    const hasLines = state.downShelfLines.length > 0;
    root.innerHTML = `
      <section class="task-panel">
        <div class="page-title">
          <div>
            <h1>调拨下架</h1>
            <p>处理下架退库、仓内移库和补货上架；先扫来源库位，再扫商品、数量和目标库位，提交后生成内部调拨。</p>
          </div>
          <span class="status-pill">${escapeHtml(currentWarehouseName())}</span>
        </div>
        <div class="task-layout">
          <section class="task-list">
            <div class="list-header">
              <strong>调拨作业</strong>
              <button id="resetDownShelf" class="refresh-button" type="button">${operation ? "新建" : "清空"}</button>
            </div>
            <div class="task-items">
              ${operation ? renderDownShelfOperationCard(operation) : `<div class="empty-state">请先创建调拨下架作业。</div>`}
              ${state.downShelfLastResult ? renderDownShelfResult(state.downShelfLastResult) : ""}
            </div>
          </section>
          <section class="task-detail">
            <div class="detail-header">
              <strong>${operation ? "扫码明细" : "创建作业"}</strong>
              <button id="confirmDownShelf" class="refresh-button" type="button" ${operation && hasLines ? "" : "disabled"}>提交作业</button>
            </div>
            <div class="detail-body">
              ${operation ? renderDownShelfLineForm(operation) : renderDownShelfCreateForm()}
              ${operation ? renderDownShelfLines() : ""}
            </div>
          </section>
        </div>
      </section>
    `;
    document.getElementById("resetDownShelf").addEventListener("click", resetDownShelfOperation);
    document.getElementById("confirmDownShelf").addEventListener("click", confirmDownShelfOperation);
    if (operation) {
      bindDownShelfLineForm();
      focusFirst("#downProductBarcode");
    } else {
      document.getElementById("downShelfCreateForm").addEventListener("submit", createDownShelfOperation);
      focusFirst("#downSourceLocation");
    }
  }

  function renderDownShelfCreateForm() {
    return `
      <form id="downShelfCreateForm" class="scan-box" autocomplete="off">
        <h2>创建调拨下架作业</h2>
        <div class="scan-form">
          <label class="field">
            <span>作业类型</span>
            <select class="text-input" name="operation_type">
              ${TRANSFER_TYPES.map(([value, label]) => `<option value="${escapeAttr(value)}">${escapeHtml(label)}</option>`).join("")}
            </select>
          </label>
          <label class="field">
            <span>来源库位条码</span>
            <input id="downSourceLocation" class="text-input" name="source_location_barcode" type="text" inputmode="text" autocomplete="off" placeholder="扫描来源库位" required />
          </label>
          <label class="field">
            <span>目标库位条码</span>
            <input class="text-input" name="return_location_barcode" type="text" inputmode="text" autocomplete="off" placeholder="下架退库/移库/补货目标库位" />
          </label>
          <label class="field full-row">
            <span>备注</span>
            <input class="text-input" name="note" type="text" inputmode="text" autocomplete="off" placeholder="可选" />
          </label>
          <button class="primary-button full-row" type="submit">创建作业</button>
        </div>
      </form>
    `;
  }

  function renderDownShelfLineForm(operation) {
    return `
      <form id="downShelfLineForm" class="scan-box" autocomplete="off">
        <h2>${escapeHtml(operation.name || `调拨作业 ${operation.id}`)}</h2>
        <div class="scan-form">
          <label class="field">
            <span>商品条码</span>
            <input id="downProductBarcode" class="text-input" name="product_barcode" type="text" inputmode="text" autocomplete="off" placeholder="扫描或输入商品条码" required />
          </label>
          <label class="field">
            <span>作业数量</span>
            <input id="downShelfQty" class="qty-input" name="qty" type="number" min="0" step="0.001" inputmode="decimal" placeholder="数量" required />
          </label>
          <label class="field">
            <span>原因</span>
            <select class="text-input" name="reason">
              ${DOWN_SHELF_REASONS.map(([value, label]) => `<option value="${escapeAttr(value)}">${escapeHtml(label)}</option>`).join("")}
            </select>
          </label>
          <label class="field full-row">
            <span>备注</span>
            <input class="text-input" name="note" type="text" inputmode="text" autocomplete="off" placeholder="可选" />
          </label>
          <button class="primary-button full-row" type="submit">加入明细</button>
        </div>
      </form>
    `;
  }

  function renderDownShelfLines() {
    if (!state.downShelfLines.length) {
      return `<div class="empty-state">暂无作业明细，请扫描商品后加入。</div>`;
    }
    return `
      <div class="line-grid">
        ${state.downShelfLines.map((line, index) => downShelfLineCard(line, index)).join("")}
      </div>
    `;
  }

  function renderDownShelfOperationCard(operation) {
    const stateLabel = OPERATION_STATE_LABELS[operation.state] || operation.state || "草稿";
    const summary = [
      operation.locationName ? `来源：${operation.locationName}` : "",
      operation.returnLocationName ? `目标：${operation.returnLocationName}` : "",
      `${operation.lineCount || state.downShelfLines.length || 0} 行`,
      `${formatQty(operation.totalQty || sumDownShelfQty())} 件`,
    ].filter(Boolean).join(" · ");
    return `
      <article class="task-card is-active">
        <strong>${escapeHtml(operation.name || `调拨作业 ${operation.id}`)}</strong>
        <small>${escapeHtml(summary)}</small>
        <small>${escapeHtml(stateLabel)}</small>
      </article>
    `;
  }

  function renderDownShelfResult(result) {
    const summary = result.summary || {};
    const title = result.operation_name || result.name || "调拨作业";
    const picking = result.generated_picking_name ? `，生成调拨 ${result.generated_picking_name}` : "";
    return `
      <div class="hint-state">
        最近提交：${escapeHtml(title)}，${escapeHtml(formatQty(summary.total_qty || 0))} 件，${escapeHtml(summary.line_count || 0)} 行${escapeHtml(picking)}。
      </div>
    `;
  }

  function downShelfLineCard(line, index) {
    const reason = line.reasonLabel || downShelfReasonLabel(line.reason);
    const code = [line.productBarcode, reason].filter(Boolean).join(" · ");
    return `
      <article class="line-card">
        <div>
          <strong>${escapeHtml(line.productName || `商品 ${index + 1}`)}</strong>
          <small>${escapeHtml(code || "调拨明细")}</small>
        </div>
        <div class="qty">${escapeHtml(formatQty(line.qty))}</div>
      </article>
    `;
  }

  function bindDownShelfLineForm() {
    const form = document.getElementById("downShelfLineForm");
    const productInput = document.getElementById("downProductBarcode");
    const qtyInput = document.getElementById("downShelfQty");
    productInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !qtyInput.value.trim()) {
        event.preventDefault();
        qtyInput.focus();
      }
    });
    form.addEventListener("submit", addDownShelfLine);
  }

  async function createDownShelfOperation(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries());
    const sourceLocation = (data.source_location_barcode || "").trim();
    const returnLocation = (data.return_location_barcode || "").trim();
    try {
      setBusy(form, true);
      const result = await apiPost(`${API_PREFIX}/return/create`, {
        request_id: requestId("downshelf_create"),
        device_id: state.deviceId,
        operation_type: data.operation_type || "warehouse_return",
        location_barcode: sourceLocation,
        source_location_barcode: sourceLocation,
        return_location_barcode: returnLocation,
        dest_location_barcode: returnLocation,
        note: [transferTypeLabel(data.operation_type), (data.note || "").trim()].filter(Boolean).join("："),
      });
      state.downShelfOperation = normalizeDownShelfOperation(result);
      state.downShelfLines = [];
      state.downShelfLastResult = null;
      showToast("作业已创建");
      renderDownShelf();
    } catch (error) {
      showError(error);
    } finally {
      setBusy(form, false);
    }
  }

  async function addDownShelfLine(event) {
    event.preventDefault();
    const operation = state.downShelfOperation;
    if (!operation || !operation.id) {
      showToast("请先创建调拨下架作业", true);
      return;
    }
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries());
    const productBarcode = (data.product_barcode || "").trim();
    try {
      setBusy(form, true);
      const result = await apiPost(`${API_PREFIX}/return/${operation.id}/add-line`, {
        request_id: requestId("downshelf_line"),
        device_id: state.deviceId,
        barcode: productBarcode,
        product_barcode: productBarcode,
        qty: data.qty,
        reason: data.reason || "other",
        note: (data.note || "").trim(),
      });
      state.downShelfLines.unshift({
        id: result.line_id || requestId("downshelf_local_line"),
        productName: result.product_name || productBarcode,
        productBarcode,
        qty: Number(result.qty ?? data.qty ?? 0),
        reason: result.reason || data.reason || "other",
        reasonLabel: result.reason_label || downShelfReasonLabel(data.reason),
      });
      state.downShelfOperation = normalizeDownShelfOperation(result.operation || result);
      showToast("已加入作业明细");
      renderDownShelf();
    } catch (error) {
      showError(error);
    } finally {
      setBusy(form, false);
    }
  }

  async function confirmDownShelfOperation() {
    const operation = state.downShelfOperation;
    if (!operation || !operation.id) {
      showToast("请先创建调拨下架作业", true);
      return;
    }
    if (!state.downShelfLines.length) {
      showToast("请先加入作业明细", true);
      return;
    }
    const button = document.getElementById("confirmDownShelf");
    try {
      button.disabled = true;
      const result = await apiPost(`${API_PREFIX}/return/${operation.id}/confirm`, {
        request_id: requestId("downshelf_confirm"),
        device_id: state.deviceId,
      });
      state.downShelfLastResult = result;
      state.downShelfOperation = null;
      state.downShelfLines = [];
      showToast("作业已提交");
      renderDownShelf();
    } catch (error) {
      showError(error);
    } finally {
      button.disabled = false;
    }
  }

  function resetDownShelfOperation() {
    state.downShelfOperation = null;
    state.downShelfLines = [];
    state.downShelfLastResult = null;
    renderDownShelf();
  }

  function normalizeDownShelfOperation(data) {
    const source = data || {};
    const previous = state.downShelfOperation || {};
    return {
      id: source.operation_id || source.id || previous.id || "",
      name: source.name || source.operation_name || previous.name || "",
      state: source.state || source.operation_state || previous.state || "draft",
      locationName: source.location_name || previous.locationName || "",
      returnLocationName: source.return_location_name || previous.returnLocationName || "",
      lineCount: Number(source.line_count ?? source.current_line_count ?? previous.lineCount ?? state.downShelfLines.length ?? 0),
      totalQty: Number(source.total_qty ?? previous.totalQty ?? sumDownShelfQty()),
    };
  }

  function downShelfReasonLabel(reason) {
    const found = DOWN_SHELF_REASONS.find(([value]) => value === reason);
    return found ? found[1] : (reason || "其他");
  }

  function transferTypeLabel(type) {
    const found = TRANSFER_TYPES.find(([value]) => value === type);
    return found ? found[1] : "";
  }

  function sumDownShelfQty() {
    return state.downShelfLines.reduce((total, line) => total + Number(line.qty || 0), 0);
  }

  function renderInventory() {
    root.innerHTML = `
      <section class="inventory-panel">
        <div class="page-title">
          <div>
            <h1>库存库位</h1>
            <p>按商品、库位两种视角查询现存、锁定和可用库存，并作为调拨下架的辅助入口。</p>
          </div>
          <span class="status-pill">${escapeHtml(currentWarehouseName())}</span>
        </div>
        <div class="inventory-mode" role="tablist">
          <button class="seg-button ${state.inventoryMode === "product" ? "is-active" : ""}" type="button" data-mode="product">按商品</button>
          <button class="seg-button ${state.inventoryMode === "location" ? "is-active" : ""}" type="button" data-mode="location">按库位</button>
        </div>
        <form id="inventoryForm" class="scan-box" autocomplete="off">
          <label class="field">
            <span id="inventoryLabel">${state.inventoryMode === "product" ? "商品条码" : "库位条码"}</span>
            <input id="inventoryCode" class="text-input" name="code" type="text" inputmode="text" placeholder="扫描或输入条码" required />
          </label>
          <button class="primary-button" type="submit">查询</button>
        </form>
        <div id="inventoryResult" class="detail-body"></div>
      </section>
    `;
    root.querySelectorAll("[data-mode]").forEach((button) => {
      button.addEventListener("click", () => {
        state.inventoryMode = button.dataset.mode;
        renderInventory();
      });
    });
    document.getElementById("inventoryForm").addEventListener("submit", submitInventory);
    if (state.pendingInventoryCode) {
      document.getElementById("inventoryCode").value = state.pendingInventoryCode;
      state.pendingInventoryCode = "";
      document.getElementById("inventoryForm").requestSubmit();
      return;
    }
    focusFirst("#inventoryCode");
  }

  async function submitInventory(event) {
    event.preventDefault();
    const code = document.getElementById("inventoryCode").value.trim();
    const result = document.getElementById("inventoryResult");
    if (!code) {
      return;
    }
    result.innerHTML = `<div class="empty-state">正在查询...</div>`;
    try {
      const path = state.inventoryMode === "product"
        ? `${API_PREFIX}/inventory/product`
        : `${API_PREFIX}/inventory/location`;
      const query = state.inventoryMode === "product"
        ? { barcode: code, default_code: code }
        : { barcode: code, location_barcode: code };
      const data = await apiGet(path, query);
      result.innerHTML = renderInventoryResult(data);
      result.querySelectorAll("[data-route]").forEach((button) => {
        button.addEventListener("click", () => navigate(button.dataset.route));
      });
      document.getElementById("inventoryCode").select();
    } catch (error) {
      result.innerHTML = `<div class="error-state">${escapeHtml(messageOf(error))}</div>`;
      showError(error);
    }
  }

  function renderInventoryResult(data) {
    const records = getRecords(data);
    if (!records.length && typeof data === "object") {
      return `<pre class="empty-state">${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;
    }
    if (!records.length) {
      return `<div class="empty-state">未查询到库存。</div>`;
    }
    const rows = records.map((item) => `
      <tr>
        <td>${escapeHtml(item.product_name || item.product || item.name || "")}</td>
        <td>${escapeHtml(item.location_name || item.location || item.location_barcode || "")}</td>
        <td>${escapeHtml(formatQty(item.quantity_on_hand ?? item.qty_available ?? item.quantity ?? item.qty ?? item.available_qty ?? 0))}</td>
        <td>${escapeHtml(formatQty(item.available_quantity ?? item.available_qty ?? 0))}</td>
        <td>${escapeHtml(formatQty(item.reserved_quantity ?? item.reserved_qty ?? 0))}</td>
        <td>${escapeHtml(item.uom || item.product_uom || "")}</td>
      </tr>
    `).join("");
    return `
      <div class="result-actions">
        <button class="refresh-button" type="button" data-route="transfer">发起调拨下架</button>
      </div>
      <table class="result-table">
        <thead><tr><th>商品</th><th>库位</th><th>现存</th><th>可用</th><th>锁定</th><th>单位</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    `;
  }

  function renderExceptionPlaceholder() {
    root.innerHTML = `
      <section class="task-panel">
        <div class="page-title">
          <div>
            <h1>盘点异常</h1>
            <p>按 PRD 统一承接缺货、破损、数量不符、库位不符、交接失败等现场异常。第一版先预留入口，后续接主管审核与图片证据。</p>
          </div>
          <span class="status-pill">预留</span>
        </div>
        <div class="hint-state">
          当前版本先在各任务详情页保留异常入口位置，完整异常闭环将在下一阶段接入。
        </div>
      </section>
    `;
  }

  async function switchWarehouse() {
    const warehouseId = warehouseSelect.value;
    if (!warehouseId || warehouseId === String(state.warehouseId)) {
      return;
    }
    try {
      await apiPost(`${API_PREFIX}/auth/switch-warehouse`, {
        warehouse_id: warehouseId,
        device_id: state.deviceId,
      });
      state.warehouseId = warehouseId;
      localStorage.setItem(STORAGE.warehouseId, String(warehouseId));
      showToast("仓库已切换");
      state.activeTasks = {};
      state.activeLines = {};
      render();
    } catch (error) {
      warehouseSelect.value = String(state.warehouseId);
      showError(error);
    }
  }

  function logout() {
    localStorage.removeItem(STORAGE.token);
    localStorage.removeItem(STORAGE.user);
    localStorage.removeItem(STORAGE.warehouses);
    localStorage.removeItem(STORAGE.warehouseId);
    state.token = "";
    state.user = null;
    state.warehouses = [];
    state.warehouseId = "";
    navigate("login", true);
  }

  function activeTaskId(mode) {
    return state.activeTasks[`${mode}:id`] || "";
  }

  function findTask(mode, taskId) {
    return (state.activeTasks[mode] || []).find((task) => task.id === taskId) || null;
  }

  function normalizeLines(lines, mode) {
    return lines.map((line, index) => {
      const demandQty = Number(line.demand_qty ?? line.picked_qty ?? line.product_uom_qty ?? 0);
      const doneQty = Number(line.done_qty ?? line.checked_qty ?? line.received_qty ?? line.picked_qty_done ?? line.putaway_qty ?? 0);
      return {
        key: String(line.line_id || line.id || line.move_id || index),
        id: line.line_id || line.id || line.move_id || "",
        productName: line.product_name || line.name || "",
        defaultCode: line.default_code || "",
        barcode: line.barcode || line.product_barcode || "",
        location: line.source_location || line.location || line.dest_location || line.dest_location_name || "",
        locationBarcode: line.source_location_barcode || line.location_barcode || line.dest_location_barcode || "",
        demandQty,
        doneQty,
        remainingQty: Number(line.remaining_qty ?? Math.max(demandQty - doneQty, 0)),
        uom: line.uom || "",
        raw: line,
        mode,
      };
    });
  }

  function productMatches(line, barcode) {
    if (!barcode) {
      return false;
    }
    return [line.barcode, line.defaultCode].filter(Boolean).includes(barcode);
  }

  function preferredQty(line) {
    return line.remainingQty || line.demandQty || line.doneQty || "";
  }

  async function apiGet(path, query) {
    return request(path, { method: "GET", query });
  }

  async function apiPost(path, body, options) {
    return request(path, { method: "POST", body, auth: !(options && options.auth === false) });
  }

  async function request(path, options) {
    const url = new URL(path, apiBase());
    Object.entries(options.query || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, value);
      }
    });
    const headers = { Accept: "application/json" };
    if (options.method !== "GET") {
      headers["Content-Type"] = "application/json";
    }
    if (options.auth !== false && state.token) {
      headers.Authorization = `Bearer ${state.token}`;
    }
    const response = await fetch(url.toString(), {
      method: options.method,
      headers,
      body: options.method === "GET" ? undefined : JSON.stringify(options.body || {}),
    });
    const text = await response.text();
    let payload = {};
    try {
      payload = text ? JSON.parse(text) : {};
    } catch (error) {
      throw new Error(`接口返回不是 JSON：${text.slice(0, 120)}`);
    }
    if (response.status === 401) {
      logout();
      throw new Error(payload.message || "登录已失效，请重新登录。");
    }
    if (!response.ok || payload.code !== 0) {
      throw new Error(payload.message || `接口请求失败：${response.status}`);
    }
    return payload.data || {};
  }

  function apiBase() {
    const queryBase = new URLSearchParams(location.search).get("apiBase");
    if (queryBase) {
      localStorage.setItem(STORAGE.apiBase, queryBase);
      return queryBase;
    }
    return localStorage.getItem(STORAGE.apiBase) || location.origin;
  }

  function getRecords(data) {
    if (Array.isArray(data)) {
      return data;
    }
    if (!data || typeof data !== "object") {
      return [];
    }
    if (Array.isArray(data.records)) {
      return data.records;
    }
    if (Array.isArray(data.items)) {
      return data.items;
    }
    if (Array.isArray(data.lines)) {
      return data.lines;
    }
    if (Array.isArray(data.quants)) {
      return data.quants;
    }
    return [];
  }

  function currentWarehouseName() {
    const current = state.warehouses.find((wh) => String(wh.id) === String(state.warehouseId));
    return current ? (current.name || current.display_name || `仓库 ${current.id}`) : "未选择仓库";
  }

  function currentUserName() {
    const name = (state.user && state.user.name || "").trim();
    return name && !/\?{2,}/.test(name) ? name : "PDA 用户";
  }

  function setBusy(element, busy) {
    element.querySelectorAll("button, input, select").forEach((item) => {
      item.disabled = busy;
    });
  }

  function focusFirst(selector) {
    window.setTimeout(() => {
      const input = document.querySelector(selector);
      if (input) {
        input.focus();
      }
    }, 40);
  }

  function showToast(message, error) {
    toast.textContent = message;
    toast.classList.toggle("is-error", Boolean(error));
    toast.classList.add("is-visible");
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => toast.classList.remove("is-visible"), 2200);
  }

  function showError(error) {
    showToast(messageOf(error), true);
  }

  function messageOf(error) {
    return error && error.message ? error.message : String(error || "操作失败");
  }

  function requestId(prefix) {
    return `${prefix}_${Date.now()}_${Math.random().toString(16).slice(2, 10)}`;
  }

  function ensureDeviceId() {
    let value = localStorage.getItem(STORAGE.deviceId);
    if (!value) {
      value = `pda_h5_${Math.random().toString(16).slice(2)}_${Date.now()}`;
      localStorage.setItem(STORAGE.deviceId, value);
    }
    return value;
  }

  function readJson(key, fallback) {
    try {
      const value = localStorage.getItem(key);
      return value ? JSON.parse(value) : fallback;
    } catch (error) {
      return fallback;
    }
  }

  function formatQty(value) {
    const number = Number(value || 0);
    return Number.isInteger(number) ? String(number) : number.toFixed(3).replace(/0+$/, "").replace(/\.$/, "");
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function escapeAttr(value) {
    return escapeHtml(value);
  }
})();
