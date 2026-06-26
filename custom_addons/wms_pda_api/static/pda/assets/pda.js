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
    arrival: {
      title: "到货签到",
      subtitle: "核对到货单，确认车辆或供应商到达后生成收货任务。",
      list: `${API_PREFIX}/inbound/tasks?stage=arrival`,
      complete: (id) => `${API_PREFIX}/inbound/arrival/${id}/checkin`,
      cancel: (id) => `${API_PREFIX}/inbound/arrival/${id}/cancel`,
      completeText: "确认到货",
      qtyKey: "done_qty",
      qtyLabel: "到货数量",
      needsLocation: false,
      readonlyLines: true,
    },
    inbound: {
      title: "入库收货",
      subtitle: "扫描商品条码，录入实收数量，确认后可完成收货任务。",
      list: `${API_PREFIX}/receipt/tasks`,
      lines: (id) => `${API_PREFIX}/receipt/tasks/${id}/lines`,
      confirm: (id) => `${API_PREFIX}/receipt/tasks/${id}/confirm-line`,
      complete: (id) => `${API_PREFIX}/receipt/tasks/${id}/complete`,
      close: (id) => `${API_PREFIX}/receipt/tasks/${id}/close`,
      manualProduct: `${API_PREFIX}/receipt/manual/product`,
      manualCreate: `${API_PREFIX}/receipt/manual/create`,
      qtyKey: "done_qty",
      qtyLabel: "实收数量",
      completeText: "完成收货",
      needsLocation: false,
    },
    outbound: {
      title: "出库复核",
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
    inbound_done: {
      title: "已完成",
      subtitle: "查看已完成上架的入库记录。",
      list: `${API_PREFIX}/inbound/tasks?stage=done`,
      completeText: "已完成",
      qtyKey: "done_qty",
      qtyLabel: "数量",
      needsLocation: false,
      readonlyLines: true,
    },
  };

  const HANDOVER_ENDPOINTS = {
    title: "交接出库",
    list: `${API_PREFIX}/handover/orders`,
    detail: (id) => `${API_PREFIX}/handover/orders/${id}`,
    confirm: (id) => `${API_PREFIX}/handover/orders/${id}/confirm`,
    complete: (id) => `${API_PREFIX}/handover/orders/${id}/complete`,
  };

  const FLOW_GROUPS = {
    "inbound-flow": {
      title: "入库上架",
      subtitle: "到货 · 收货 · 上架",
      scanPlaceholder: "扫收货任务 / 上架任务 / 商品 / 库位",
      defaultMode: "arrival",
      tabs: [
        { mode: "arrival", label: "到货签到", hint: "确认到货后生成收货任务" },
        { mode: "inbound", label: "收货", hint: "扫码收货、数量确认、异常预留" },
        { mode: "putaway", label: "待上架", hint: "扫商品与目标库位，确认上架" },
        { mode: "inbound_done", label: "已完成", hint: "查看完成记录" },
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
        { mode: "handover", label: "待交接", hint: "司机/车辆/运单核对后交接出库" },
      ],
    },
  };

  const ARRIVAL_STATUS_TABS = [
    { key: "unsigned", label: "未签到" },
    { key: "signed", label: "已签到" },
    { key: "cancelled", label: "已取消" },
  ];

  const RECEIPT_STATUS_TABS = [
    { key: "waiting_receipt", label: "待收货" },
    { key: "receiving", label: "收货中" },
    { key: "received", label: "已完成" },
  ];

  const RECEIPT_DETAIL_STATUS_TABS = [
    { key: "unreceived", label: "未收货" },
    { key: "partial", label: "部分收货" },
    { key: "complete", label: "足量收货" },
  ];

  const MAIN_ROUTES = ["home", "operation", "mine"];
  const OPERATION_ROUTES = ["operation", "scan", "inbound-flow", "outbound-flow", "inventory", "transfer", "exceptions", "dashboard"];
  const HOME_MODULES = [
    { route: "scan", icon: "□", title: "扫码执行", desc: "商品 / 库位 / 单据 / 编号", tone: "yellow" },
    { route: "inbound-flow", icon: "+", title: "入库上架", desc: "到货 / 收货 / 上架", tone: "blue" },
    { route: "outbound-flow", icon: "+", title: "出库履约", desc: "领取 / 拣货 / 复核 / 交接", tone: "green" },
    { route: "inventory", icon: "▤", title: "库存库位", desc: "库存 / 库位 / 批量移库", tone: "purple" },
    { route: "transfer", icon: "+", title: "调拨补货", desc: "调拨 / 补货 / 其他出入库", tone: "orange" },
    { route: "exceptions", icon: "△", title: "盘点异常", desc: "盘点 / 报损 / 禁售", tone: "red" },
    { route: "dashboard", icon: "▭", title: "数据看板", desc: "现场进度 / 异常概览", tone: "dark" },
  ];

  const STATUS_LABELS = {
    waiting_arrival: "待到货",
    arrival_signed: "已签到",
    arrival_cancelled: "已取消",
    waiting_receipt: "待收货",
    receiving: "收货中",
    received: "已收货",
    closed: "已关单",
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
    waiting_handover: "待交接",
    handover_ing: "交接中",
    handover_done: "已交接",
    handover_exception: "交接异常",
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
      "inbound-flow": "arrival",
      "outbound-flow": "pick",
    },
    arrivalStatus: "unsigned",
    receiptStatus: "waiting_receipt",
    receiptSearch: "",
    receiptDetailStatus: "unreceived",
    receiptDetailSearch: "",
    receiptWorkTab: "waiting",
    receiptWorkSearch: "",
    manualReceiptLines: [],
    receiptCounts: {},
    putawayStatus: "waiting",
    putawaySearch: "",
    putawayCounts: {},
    workbenchSummary: null,
    activeTasks: {},
    activeLines: {},
    lineMatches: {},
    lastResults: {},
    exceptionLastDraft: null,
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
    if (state.route === "operation") {
      renderOperation();
      return;
    }
    if (state.route === "mine") {
      renderMine();
      return;
    }
    if (state.route === "dashboard") {
      renderDashboard();
      return;
    }
    if (state.route === "scan") {
      renderScanExecution();
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
    document.body.classList.toggle("is-auth", loggedIn);
    document.body.classList.toggle("is-main-route", loggedIn && MAIN_ROUTES.includes(state.route));
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
      <section class="app-screen">
        <div class="app-page-title">
          <div>
            <h1>工作台</h1>
            <p>${escapeHtml(currentWarehouseName())} · 今日待办</p>
          </div>
          <button id="refreshWorkbench" class="mini-button" type="button">刷新</button>
        </div>
        <button class="scan-hero-card" type="button" data-route="scan">
          <span>
            <strong>扫码执行</strong>
            <small>扫商品 / 单据 / 库位 / 编号</small>
          </span>
          <em>□</em>
        </button>
        <div id="workbenchDashboard" class="workbench-dashboard">
          ${renderWorkbenchSkeleton()}
        </div>
        ${renderBottomNav("home")}
      </section>
    `;
    root.querySelectorAll("[data-route]").forEach((button) => {
      button.addEventListener("click", () => navigate(button.dataset.route));
    });
    document.getElementById("refreshWorkbench").addEventListener("click", loadWorkbenchSummary);
    bindBottomNav();
    loadWorkbenchSummary();
  }

  function renderOperation() {
    root.innerHTML = `
      <section class="app-screen">
        <div class="app-page-title">
          <div>
            <h1>经营</h1>
            <p>选择要处理的业务</p>
          </div>
        </div>
        <div class="operation-grid">
          ${HOME_MODULES.map((item) => moduleButton(item.route, item.icon, item.title, item.desc, item.tone)).join("")}
        </div>
        <div class="chain-title">作业进度</div>
        ${renderMainStatusChain()}
        ${renderBottomNav("operation")}
      </section>
    `;
    root.querySelectorAll("[data-route]").forEach((button) => {
      button.addEventListener("click", () => navigate(button.dataset.route));
    });
    bindBottomNav();
  }

  function renderMine() {
    root.innerHTML = `
      <section class="app-screen">
        <div class="app-page-title">
          <div>
            <h1>我的</h1>
            <p>账号 · 权限 · 设置</p>
          </div>
        </div>
        <div class="mine-profile">
          <span class="avatar"></span>
          <div>
            <strong>${escapeHtml(currentUserName() || "仓库主管")}</strong>
            <small>${escapeHtml(currentWarehouseName())} · 管理权限</small>
          </div>
        </div>
        <div class="mine-menu">
          ${renderMineWarehouseRow()}
          ${[
            ["角色权限", "主管 / 操作员权限查看"],
            ["消息通知", "异常、任务、审核提醒"],
            ["设备绑定", state.deviceId],
            ["问题反馈", "记录现场问题"],
            ["版本说明", "PDA H5 PRD 三入口版"],
          ].map(([label, value]) => `
            <div class="mine-row">
              <span>${escapeHtml(label)}</span>
              <small>${escapeHtml(value)}</small>
              <em>&gt;</em>
            </div>
          `).join("")}
        </div>
        <button id="mineLogout" class="danger-button full-width" type="button">退出登录</button>
        ${renderBottomNav("mine")}
      </section>
    `;
    const mineWarehouse = document.getElementById("mineWarehouseSelect");
    if (mineWarehouse) {
      mineWarehouse.addEventListener("change", () => switchWarehouseById(mineWarehouse.value));
    }
    document.getElementById("mineLogout").addEventListener("click", logout);
    bindBottomNav();
  }

  async function renderDashboard() {
    root.innerHTML = `
      <section class="app-screen">
        ${renderAppHeader("数据看板", "现场只保留轻量经营指标，详细 BI 仍放后台。", {
          action: `<button id="refreshDashboard" class="mini-button" type="button">刷新</button>`,
        })}
        <div id="dashboardSummary" class="workbench-dashboard">
          ${renderWorkbenchSkeleton()}
        </div>
        <div class="chain-title">作业进度</div>
        ${renderMainStatusChain()}
        ${renderBottomNav("operation")}
      </section>
    `;
    document.getElementById("refreshDashboard").addEventListener("click", loadDashboardSummary);
    bindAppChrome();
    await loadDashboardSummary();
  }

  function moduleButton(route, icon, title, desc, tone) {
    return `
      <button class="module-button tone-${escapeAttr(tone || "blue")}" type="button" data-route="${route}">
        <span class="module-icon">${escapeHtml(icon)}</span>
        <strong>${escapeHtml(title)}</strong>
        <span>${escapeHtml(desc)}</span>
      </button>
    `;
  }

  function renderBottomNav(active) {
    const items = [
      ["home", "工作台"],
      ["operation", "经营"],
      ["mine", "我的"],
    ];
    return `
      <nav class="bottom-nav" aria-label="主导航">
        ${items.map(([route, label]) => `
          <button class="${route === active ? "is-active" : ""}" type="button" data-main-route="${route}">
            <span></span>
            <strong>${escapeHtml(label)}</strong>
          </button>
        `).join("")}
      </nav>
    `;
  }

  function bindBottomNav() {
    root.querySelectorAll("[data-main-route]").forEach((button) => {
      button.addEventListener("click", () => navigate(button.dataset.mainRoute));
    });
  }

  function renderAppHeader(title, subtitle, options) {
    const config = options || {};
    const showBack = config.back !== false;
    return `
      <div class="app-page-title app-sub-title">
        ${showBack ? `<button class="app-back-button" type="button" data-app-back aria-label="返回">‹</button>` : ""}
        <div>
          <h1>${escapeHtml(title)}</h1>
          <p>${escapeHtml(subtitle || "")}</p>
        </div>
        ${config.action || ""}
      </div>
    `;
  }

  function bindAppChrome() {
    bindBottomNav();
    root.querySelectorAll("[data-app-back]").forEach((button) => {
      button.addEventListener("click", () => navigate(appBackRoute()));
    });
  }

  function appBackRoute() {
    return OPERATION_ROUTES.includes(state.route) ? "operation" : "home";
  }

  function renderMainStatusChain() {
    return `
      <div class="status-chain status-chain-graphic">
        ${["到货", "收货", "上架", "库位库存", "出库任务", "拣货", "复核交接", "配送签收"].map((item, index) => `
          <span class="${index < 3 ? "is-done" : index === 3 ? "is-current" : ""}">
            <i>${escapeHtml(index + 1)}</i>
            <b>${escapeHtml(item)}</b>
          </span>
        `).join("")}
      </div>
    `;
  }

  function renderWorkflowStrip(route, mode) {
    const chains = {
      "inbound-flow": [
        ["arrival", "到货"],
        ["inbound", "收货"],
        ["putaway", "上架"],
        ["done", "完成"],
      ],
      "outbound-flow": [
        ["pick", "领"],
        ["picking", "拣"],
        ["staging", "集"],
        ["outbound", "复"],
        ["handover", "交"],
      ],
    };
    const steps = chains[route] || [];
    const activeMap = {
      inbound: "inbound",
      putaway: "putaway",
      pick: "pick",
      outbound: "outbound",
      handover: "handover",
    };
    const activeKey = activeMap[mode] || mode;
    const currentIndex = Math.max(steps.findIndex(([key]) => key === activeKey), 0);
    if (!steps.length) {
      return "";
    }
    return `
      <div class="workflow-strip">
        ${steps.map(([key, label], index) => `
          <span class="${key === activeKey ? "is-current" : index < currentIndex ? "is-done" : ""}">
            <i>${escapeHtml(index + 1)}</i>
            <b>${escapeHtml(label)}</b>
          </span>
        `).join("")}
      </div>
    `;
  }

  function renderWorkbenchSkeleton() {
    return `
      <div class="kpi-grid">
        ${["待收货", "待上架", "待领取", "待出库"].map((label) => `
          <div class="kpi-card"><span>${escapeHtml(label)}</span><strong>...</strong><small>单</small></div>
        `).join("")}
      </div>
      <div class="exception-strip"><span>异常待处理</span><strong>...</strong></div>
      <div class="progress-card"><span>今日履约进度</span><div><i style="width: 20%"></i></div><small>正在读取</small></div>
    `;
  }

  function renderWorkbenchDashboard(todos) {
    const receipt = todoCount(todos, "receipt");
    const putaway = todoCount(todos, "putaway");
    const pick = todoCount(todos, "pick");
    const check = todoCount(todos, "check");
    const handover = todoCount(todos, "handover");
    const exception = todoCount(todos, "exception");
    const outbound = check + handover;
    const total = receipt + putaway + pick + outbound + exception;
    const progress = Math.max(12, Math.min(88, 88 - total * 4));
    return `
      <div class="kpi-grid">
        ${renderKpi("待收货", receipt, "inbound-flow", "inbound")}
        ${renderKpi("待上架", putaway, "inbound-flow", "putaway")}
        ${renderKpi("待领取", pick, "outbound-flow", "pick")}
        ${renderKpi("待出库", outbound, "outbound-flow", check ? "outbound" : "handover")}
      </div>
      <button class="exception-strip" type="button" data-todo-route="exceptions" data-todo-mode="">
        <span>异常待处理</span>
        <strong>${escapeHtml(exception)}</strong>
      </button>
      <div class="progress-card">
        <span>今日履约进度</span>
        <div><i style="width: ${progress}%"></i></div>
        <small>${escapeHtml(total ? `待办剩余 ${total} 单` : "今日暂无待办")}</small>
      </div>
    `;
  }

  function renderKpi(label, count, route, mode) {
    return `
      <button class="kpi-card" type="button" data-todo-route="${escapeAttr(route)}" data-todo-mode="${escapeAttr(mode)}">
        <span>${escapeHtml(label)}</span>
        <strong>${escapeHtml(count)}</strong>
        <small>单</small>
      </button>
    `;
  }

  function todoCount(todos, key) {
    const item = (todos || []).find((todo) => todo.key === key);
    return Number(item && item.count || 0);
  }

  function renderMineWarehouseRow() {
    if (!state.warehouses.length) {
      return `
        <div class="mine-row">
          <span>仓库切换</span>
          <small>暂无可选仓库</small>
          <em>&gt;</em>
        </div>
      `;
    }
    return `
      <label class="mine-row mine-select-row">
        <span>仓库切换</span>
        <select id="mineWarehouseSelect">
          ${state.warehouses.map((wh) => `<option value="${escapeAttr(wh.id)}" ${String(wh.id) === String(state.warehouseId) ? "selected" : ""}>${escapeHtml(wh.name || wh.display_name || `仓库 ${wh.id}`)}</option>`).join("")}
        </select>
      </label>
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

  function renderScanExecution() {
    root.innerHTML = `
      <section class="task-panel">
        ${renderAppHeader("扫码执行", "扫任务号、单据号、商品、库位后自动跳到对应作业页面。", {
          action: `<span class="mini-pill">${escapeHtml(currentWarehouseName())}</span>`,
        })}
        ${renderGlobalScan("scanExecutionForm", "扫商品 / 库位 / 收货单 / 拣货单 / 复核单 / 交接单")}
        <div class="scan-support-grid">
          ${[
            ["任务", "收货、上架、拣货、复核、交接任务"],
            ["商品", "优先匹配待执行任务，否则进入库存查询"],
            ["库位", "进入库存库位，查看当前库位现存"],
            ["单据", "识别入库、出库、交接相关单据"],
          ].map(([title, desc]) => `
            <article class="metric-card">
              <strong>${escapeHtml(title)}</strong>
              <small>${escapeHtml(desc)}</small>
            </article>
          `).join("")}
        </div>
        <div class="hint-state">
          当前扫码会优先查找待办任务；如果没有匹配到待执行任务，再按商品或库位进入库存库位查询。
        </div>
        ${renderBottomNav("operation")}
      </section>
    `;
    document.getElementById("scanExecutionForm").addEventListener("submit", submitGlobalScan);
    bindAppChrome();
    focusFirst("#scanExecutionFormCode");
  }

  function renderTodoSkeleton() {
    return ["待收货", "待上架", "待拣货", "待复核", "待交接", "异常待处理"].map((label) => `
      <button class="todo-card" type="button" disabled>
        <span>${escapeHtml(label)}</span>
        <strong>...</strong>
      </button>
    `).join("");
  }

  async function loadWorkbenchSummary() {
    const dashboard = document.getElementById("workbenchDashboard");
    const grid = document.getElementById("todoGrid");
    if (!grid && !dashboard) {
      return;
    }
    if (dashboard) {
      dashboard.innerHTML = renderWorkbenchSkeleton();
    }
    if (grid) {
      grid.innerHTML = renderTodoSkeleton();
    }
    try {
      const data = await apiGet(`${API_PREFIX}/workbench/summary`);
      state.workbenchSummary = data;
      if (dashboard) {
        dashboard.innerHTML = renderWorkbenchDashboard(data.todos || []);
        bindTodoButtons(dashboard);
      }
      if (grid) {
        grid.innerHTML = renderTodoGrid(data.todos || []);
        bindTodoButtons(grid);
      }
    } catch (error) {
      const target = dashboard || grid;
      target.innerHTML = `<div class="error-state full-row">${escapeHtml(messageOf(error))}</div>`;
    }
  }

  async function loadDashboardSummary() {
    const container = document.getElementById("dashboardSummary");
    if (!container) {
      return;
    }
    container.innerHTML = renderWorkbenchSkeleton();
    try {
      const data = await apiGet(`${API_PREFIX}/workbench/summary`);
      state.workbenchSummary = data;
      container.innerHTML = renderWorkbenchDashboard(data.todos || []);
      bindTodoButtons(container);
    } catch (error) {
      container.innerHTML = `<div class="error-state full-row">${escapeHtml(messageOf(error))}</div>`;
    }
  }

  function bindTodoButtons(container) {
    container.querySelectorAll("[data-todo-route]").forEach((button) => {
      button.addEventListener("click", () => {
        const route = button.dataset.todoRoute;
        const mode = button.dataset.todoMode;
        if (mode) {
          state.flowModes[route] = mode;
        }
        navigate(route);
      });
    });
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
    if (route === "inbound-flow") {
      await renderInboundFlowPage(route, group);
      return;
    }
    if (mode === "handover") {
      await renderHandoverFlowPage(route, group);
      return;
    }
    const config = ENDPOINTS[mode];
    root.innerHTML = `
      <section class="task-panel">
        ${renderAppHeader(group.title, group.subtitle, {
          action: `<span class="mini-pill">${escapeHtml(currentWarehouseName())}</span>`,
        })}
        ${renderWorkflowStrip(route, mode)}
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
        ${renderBottomNav("operation")}
      </section>
    `;
    root.querySelectorAll("[data-flow-mode]").forEach((button) => {
      button.addEventListener("click", () => {
        state.flowModes[button.dataset.flowRoute] = button.dataset.flowMode;
        renderFlowPage(button.dataset.flowRoute);
      });
    });
    document.getElementById("refreshTasks").addEventListener("click", () => loadTasks(mode));
    document.getElementById("completeTask").addEventListener("click", () => completeTask(mode));
    bindAppChrome();
    await loadTasks(mode);
  }

  async function renderInboundFlowPage(route, group) {
    const mode = state.flowModes[route] || group.defaultMode;
    if (mode === "inbound") {
      await renderReceiptFlowPage(route, group);
      return;
    }
    if (mode === "putaway") {
      await renderPutawayFlowPage(route, group);
      return;
    }
    root.innerHTML = `
      <section class="task-panel inbound-page">
        <div class="app-page-title inbound-title">
          <div>
            <h1>${escapeHtml(group.title)}</h1>
            <p>${escapeHtml(group.subtitle)}</p>
          </div>
        </div>
        <div class="inbound-status-tabs" role="tablist">
          ${group.tabs.map((tab) => `
            <button class="inbound-status-tab ${tab.mode === mode ? "is-active" : ""}" type="button" data-flow-route="${escapeAttr(route)}" data-flow-mode="${escapeAttr(tab.mode)}">
              ${escapeHtml(tab.label)}
            </button>
          `).join("")}
        </div>
        ${mode === "arrival" ? renderArrivalStatusTabs() : ""}
        <div id="taskItems" class="task-items inbound-card-list">
          <div class="empty-state">正在读取任务...</div>
        </div>
        <div class="inbound-process-hint">流程：到货签到 / 收货 / 按单收货 / 上架 / 上架执行 / 上架融合</div>
        ${renderBottomNav("operation")}
      </section>
    `;
    root.querySelectorAll("[data-flow-mode]").forEach((button) => {
      button.addEventListener("click", () => {
        state.flowModes[button.dataset.flowRoute] = button.dataset.flowMode;
        renderInboundFlowPage(button.dataset.flowRoute, group);
      });
    });
    root.querySelectorAll("[data-arrival-status]").forEach((button) => {
      button.addEventListener("click", () => {
        state.arrivalStatus = button.dataset.arrivalStatus;
        renderInboundFlowPage(route, group);
      });
    });
    bindAppChrome();
    await loadInboundTasks(mode);
  }

  function renderArrivalStatusTabs() {
    return `
      <div class="arrival-filter-tabs" role="tablist" aria-label="到货签到状态">
        ${ARRIVAL_STATUS_TABS.map((tab) => `
          <button class="arrival-filter-tab ${tab.key === state.arrivalStatus ? "is-active" : ""}" type="button" data-arrival-status="${escapeAttr(tab.key)}">
            ${escapeHtml(tab.label)}
          </button>
        `).join("")}
      </div>
    `;
  }

  async function renderPutawayFlowPage(route, group) {
    root.innerHTML = `
      <section class="task-panel putaway-page">
        <div class="receipt-nav putaway-nav">
          <button id="backToInboundReceipt" class="app-back-button" type="button" aria-label="返回">‹</button>
          <h1>上架</h1>
          <span></span>
        </div>
        <div class="putaway-status-tabs" role="tablist" aria-label="上架状态">
          <button class="putaway-status-tab ${state.putawayStatus === "waiting" ? "is-active" : ""}" type="button" data-putaway-status="waiting">
            <span>待上架</span><em data-putaway-count="waiting"></em>
          </button>
          <button class="putaway-status-tab ${state.putawayStatus === "done" ? "is-active" : ""}" type="button" data-putaway-status="done">
            <span>已上架</span><em data-putaway-count="done"></em>
          </button>
        </div>
        <form id="putawaySearchForm" class="putaway-search" autocomplete="off">
          <input id="putawaySearchInput" type="search" value="${escapeAttr(state.putawaySearch)}" placeholder="任务单号/商品名称/UPC/SKU" />
          <button type="submit" aria-label="搜索">⌗</button>
        </form>
        <div id="putawayItems" class="putaway-card-list">
          <div class="empty-state">正在读取上架任务...</div>
        </div>
        ${renderBottomNav("operation")}
      </section>
    `;
    document.getElementById("backToInboundReceipt").addEventListener("click", () => {
      state.flowModes[route] = "inbound";
      renderReceiptFlowPage(route, group);
    });
    document.getElementById("putawaySearchForm").addEventListener("submit", (event) => {
      event.preventDefault();
      state.putawaySearch = document.getElementById("putawaySearchInput").value.trim();
      loadPutawayTasks();
    });
    document.getElementById("putawaySearchInput").addEventListener("input", (event) => {
      state.putawaySearch = event.target.value.trim();
      loadPutawayTasks();
    });
    root.querySelectorAll("[data-putaway-status]").forEach((button) => {
      button.addEventListener("click", () => {
        state.putawayStatus = button.dataset.putawayStatus;
        loadPutawayTasks();
      });
    });
    bindAppChrome();
    await loadPutawayTasks();
  }

  async function loadPutawayTasks() {
    const container = document.getElementById("putawayItems");
    if (!container) {
      return;
    }
    container.innerHTML = `<div class="empty-state">正在读取上架任务...</div>`;
    try {
      const groups = await Promise.all(["waiting", "done"].map(async (status) => {
        const data = await apiGet(ENDPOINTS.putaway.list, { state: status, limit: 100 });
        return [status, getRecords(data)];
      }));
      const byStatus = Object.fromEntries(groups);
      state.putawayCounts = Object.fromEntries(groups.map(([key, records]) => [key, countPutawayRows(records, key)]));
      updatePutawayTabs();
      const records = filterPutawayRecords(byStatus[state.putawayStatus] || []);
      state.activeTasks.putaway = records;
      if (!records.length) {
        container.innerHTML = `<div class="empty-state inbound-empty">${escapeHtml(putawayEmptyText())}</div>`;
        return;
      }
      container.innerHTML = records.map(putawayCard).join("");
      container.querySelectorAll("[data-putaway-receipt-id]").forEach((button) => {
        button.addEventListener("click", () => renderReceiptViewDetailPage(Number(button.dataset.putawayReceiptId)));
      });
      container.querySelectorAll("[data-putaway-edit-id]").forEach((button) => {
        button.addEventListener("click", () => renderInboundTaskDetailPage("putaway", Number(button.dataset.putawayEditId)));
      });
      container.querySelectorAll("[data-putaway-confirm-id]").forEach((button) => {
        button.addEventListener("click", () => quickConfirmPutaway(button));
      });
    } catch (error) {
      container.innerHTML = `<div class="error-state">${escapeHtml(messageOf(error))}</div>`;
    }
  }

  function updatePutawayTabs() {
    ["waiting", "done"].forEach((status) => {
      const button = document.querySelector(`[data-putaway-status="${status}"]`);
      const count = document.querySelector(`[data-putaway-count="${status}"]`);
      if (button) {
        button.classList.toggle("is-active", state.putawayStatus === status);
      }
      if (count) {
        const value = Number(state.putawayCounts[status] || 0);
        count.textContent = value ? (value > 99 ? "99+" : String(value)) : "";
      }
    });
  }

  function filterPutawayRecords(records) {
    const keyword = state.putawaySearch.trim().toLowerCase();
    if (!keyword) {
      return records;
    }
    return records.map((task) => {
      const lines = putawayTaskLines(task);
      const taskMatched = [
        task.name,
        task.receipt_task_name,
        task.picking_name,
        task.product_summary,
        task.dest_location,
      ].filter(Boolean).some((value) => String(value).toLowerCase().includes(keyword));
      if (taskMatched) {
        return task;
      }
      const matchedLines = lines.filter((line) => [
        line.product_name,
        line.default_code,
        line.barcode,
        line.dest_location,
      ].filter(Boolean).some((value) => String(value).toLowerCase().includes(keyword)));
      return matchedLines.length ? { ...task, lines: matchedLines } : null;
    }).filter(Boolean);
  }

  function countPutawayRows(records, status) {
    return records.reduce((total, task) => total + putawayVisibleLines(task, status).length, 0);
  }

  function putawayEmptyText() {
    if (state.putawaySearch) {
      return `没有匹配“${state.putawaySearch}”的上架任务。`;
    }
    return state.putawayStatus === "done" ? "暂无已上架记录。" : "暂无待上架任务。";
  }

  function putawayCard(task) {
    const visibleLines = putawayVisibleLines(task, state.putawayStatus);
    return visibleLines.map((line, index) => putawayLineCard(task, line, index)).join("");
  }

  function putawayVisibleLines(task, status) {
    const lines = putawayTaskLines(task);
    const source = lines.length ? lines : [{}];
    if (status !== "waiting") {
      return source;
    }
    const pending = source.filter((line) => !isPutawayLineDone(task, line));
    return pending.length ? pending : source;
  }

  function isPutawayLineDone(task, line) {
    if (task.state === "putaway_done") {
      return true;
    }
    const demandQty = Number(line.demand_qty ?? task.total_qty ?? 0);
    const putawayQty = Number(line.putaway_qty ?? task.putaway_qty ?? 0);
    const remainingQty = Number(line.remaining_qty ?? Math.max(demandQty - putawayQty, 0));
    return remainingQty <= 0;
  }

  function putawayLineCard(task, line, index) {
    const unit = displayUom(line.uom) || "份";
    const demandQty = Number(line.demand_qty ?? task.total_qty ?? 0);
    const putawayQty = Number(line.putaway_qty ?? task.putaway_qty ?? 0);
    const remainingQty = Number(line.remaining_qty ?? Math.max(demandQty - putawayQty, 0));
    const done = isPutawayLineDone(task, line);
    const destLocation = task.dest_location || line.dest_location || "待确认";
    const taskNo = task.name || "上架任务";
    const cardNo = index ? `${taskNo}-${index + 1}` : taskNo;
    return `
      <article class="putaway-card">
        <div class="putaway-card-head">
          <div>
            <span>上架</span>
            <strong>${escapeHtml(cardNo)}</strong>
            <small>${escapeHtml(formatDateTime(task.create_date))} 创建</small>
          </div>
          ${task.receipt_task_id ? `<button type="button" data-putaway-receipt-id="${escapeAttr(task.receipt_task_id)}">关联收货单 ›</button>` : `<em>关联收货单</em>`}
        </div>
        <div class="putaway-product">
          <div class="receipt-line-thumb putaway-thumb">
            <span>${escapeHtml(receiptLineAvatarText(normalizeLineLike(line)))}</span>
          </div>
          <div>
          <strong>${escapeHtml(line.product_name || task.product_summary || "未命名商品")}</strong>
          <p>UPC：${escapeHtml(line.barcode || "-")}　${escapeHtml(line.default_code ? `SKU：${line.default_code}` : "")}</p>
          <p>规格：${escapeHtml(putawaySpecText(line))}</p>
        </div>
        </div>
        <div class="putaway-metrics">
          <span>应上架量（${escapeHtml(unit)}）</span>
          <strong>${escapeHtml(formatQty(demandQty))}</strong>
          <em class="${done ? "is-done" : ""}">${done ? "已完成" : "未完成"}</em>
          <button type="button" data-putaway-edit-id="${escapeAttr(task.id)}">已上架明细 ›</button>
          <span>剩余上架量（${escapeHtml(unit)}）</span>
          <strong>${escapeHtml(formatQty(remainingQty))}</strong>
          <i></i>
          <i></i>
          <span>已上架量（${escapeHtml(unit)}）</span>
          <strong>${escapeHtml(formatQty(putawayQty))}</strong>
          <i></i>
          <i></i>
          <span>上架库位</span>
          <strong>${escapeHtml(destLocation)}</strong>
        </div>
        <div class="putaway-card-actions">
          <button class="putaway-edit-button" type="button" data-putaway-edit-id="${escapeAttr(task.id)}">修改上架信息</button>
          ${done
            ? `<button class="putaway-confirm-button" type="button" disabled>已上架</button>`
            : `<button class="putaway-confirm-button" type="button" data-putaway-confirm-id="${escapeAttr(task.id)}" data-line-barcode="${escapeAttr(line.barcode || line.default_code || "")}" data-line-qty="${escapeAttr(remainingQty)}" data-location-barcode="${escapeAttr(task.dest_location_barcode || line.dest_location_barcode || "")}">确认上架</button>`}
        </div>
      </article>
    `;
  }

  function putawayTaskLines(task) {
    return Array.isArray(task.lines) ? task.lines : [];
  }

  function normalizeLineLike(line) {
    return {
      productName: line.product_name || "",
      defaultCode: line.default_code || "",
      barcode: line.barcode || "",
    };
  }

  function putawaySpecText(line) {
    return line.default_code || line.barcode || "暂无规格";
  }

  async function quickConfirmPutaway(button) {
    const taskId = Number(button.dataset.putawayConfirmId || 0);
    const barcode = button.dataset.lineBarcode || "";
    const qty = Number(button.dataset.lineQty || 0);
    const locationBarcode = button.dataset.locationBarcode || "";
    if (!taskId) {
      return;
    }
    if (!barcode || !qty || !locationBarcode) {
      showToast("请先进入修改上架信息，补充商品、数量和库位", true);
      renderInboundTaskDetailPage("putaway", taskId);
      return;
    }
    try {
      button.disabled = true;
      const result = await apiPost(ENDPOINTS.putaway.confirm(taskId), {
        request_id: requestId("putaway_quick"),
        device_id: state.deviceId,
        product_barcode: barcode,
        dest_location_barcode: locationBarcode,
        qty,
      });
      if (Number(result.remaining_products || 0) <= 0) {
        await apiPost(ENDPOINTS.putaway.complete(taskId), {
          request_id: requestId("putaway_quick_complete"),
          device_id: state.deviceId,
        });
        state.putawayStatus = "done";
        showToast("上架已完成");
      } else {
        showToast("已确认上架");
      }
      await loadPutawayTasks();
    } catch (error) {
      showError(error);
      button.disabled = false;
    }
  }

  async function renderReceiptFlowPage(route, group) {
    root.innerHTML = `
      <section class="task-panel receipt-page">
        <div class="receipt-nav">
          <button id="backToInboundArrival" class="app-back-button" type="button" aria-label="返回">‹</button>
          <h1>收货单</h1>
          <button id="receiptFilterButton" class="receipt-filter-button" type="button">筛选</button>
        </div>
        <div class="inbound-status-tabs" role="tablist">
          ${group.tabs.map((tab) => `
            <button class="inbound-status-tab ${tab.mode === "inbound" ? "is-active" : ""}" type="button" data-flow-route="${escapeAttr(route)}" data-flow-mode="${escapeAttr(tab.mode)}">
              ${escapeHtml(tab.label)}
            </button>
          `).join("")}
        </div>
        <form id="receiptSearchForm" class="receipt-search" autocomplete="off">
          <input id="receiptSearchInput" type="search" value="${escapeAttr(state.receiptSearch)}" placeholder="搜索 扫描或输入单号/商品条码/发货方等" />
          <button type="submit" aria-label="搜索">⌕</button>
        </form>
        <div class="receipt-state-tabs" role="tablist" aria-label="收货状态">
          ${RECEIPT_STATUS_TABS.map((tab) => `
            <button class="receipt-state-tab ${tab.key === state.receiptStatus ? "is-active" : ""}" type="button" data-receipt-status="${escapeAttr(tab.key)}">
              <span>${escapeHtml(tab.label)}</span>
              <em class="receipt-state-count" data-receipt-count="${escapeAttr(tab.key)}"></em>
            </button>
          `).join("")}
        </div>
        <div id="receiptItems" class="receipt-card-list">
          <div class="empty-state">正在读取收货单...</div>
        </div>
        <button id="manualReceiptCreate" class="receipt-manual-button" type="button">手动新建</button>
        ${renderBottomNav("operation")}
      </section>
    `;
    document.getElementById("backToInboundArrival").addEventListener("click", () => {
      state.flowModes[route] = "arrival";
      renderInboundFlowPage(route, group);
    });
    document.getElementById("receiptFilterButton").addEventListener("click", () => focusFirst("#receiptSearchInput"));
    document.getElementById("receiptSearchForm").addEventListener("submit", (event) => {
      event.preventDefault();
      state.receiptSearch = document.getElementById("receiptSearchInput").value.trim();
      loadReceiptTasks();
    });
    document.getElementById("receiptSearchInput").addEventListener("input", (event) => {
      state.receiptSearch = event.target.value.trim();
      loadReceiptTasks();
    });
    document.getElementById("manualReceiptCreate").addEventListener("click", () => renderManualReceiptPage(route, group));
    root.querySelectorAll("[data-flow-mode]").forEach((button) => {
      button.addEventListener("click", () => {
        state.flowModes[button.dataset.flowRoute] = button.dataset.flowMode;
        renderInboundFlowPage(button.dataset.flowRoute, group);
      });
    });
    root.querySelectorAll("[data-receipt-status]").forEach((button) => {
      button.addEventListener("click", () => {
        state.receiptStatus = button.dataset.receiptStatus;
        loadReceiptTasks();
      });
    });
    bindBottomNav();
    await loadReceiptTasks();
  }

  function renderManualReceiptPage(route, group) {
    state.manualReceiptLines = [];
    root.innerHTML = `
      <section class="task-panel manual-receipt-page">
        <div class="receipt-detail-nav">
          <button id="backToReceiptList" class="app-back-button" type="button" aria-label="返回">‹</button>
          <h1>新建收货单</h1>
          <span></span>
        </div>
        <section class="manual-receipt-section">
          <div class="manual-section-title">
            <strong>单据信息</strong>
            <span>${escapeHtml(currentWarehouseName())}</span>
          </div>
          <div class="manual-receipt-fields">
            <label>
              <span>发货方</span>
              <input id="manualPartnerName" type="text" value="天枢日用品供应商" placeholder="输入供应商或发货方" />
            </label>
            <label>
              <span>关联单号</span>
              <input id="manualOrigin" type="text" value="${escapeAttr(manualReceiptDefaultNo())}" placeholder="采购单/预约单/外部单号" />
            </label>
            <label>
              <span>物流单号</span>
              <input id="manualLogisticsNo" type="text" placeholder="可选" />
            </label>
          </div>
        </section>
        <form id="manualReceiptLineForm" class="manual-receipt-section manual-product-form" autocomplete="off">
          <div class="manual-section-title">
            <strong>添加商品</strong>
            <span>扫码或输入 SKU</span>
          </div>
          <div class="manual-product-row">
            <label>
              <span>商品</span>
              <input id="manualProductCode" type="search" inputmode="text" autocomplete="off" placeholder="商品条码 / SKU / 外部编码" required />
            </label>
            <label>
              <span>数量</span>
              <input id="manualProductQty" type="number" min="0.001" step="0.001" inputmode="decimal" placeholder="数量" required />
            </label>
          </div>
          <button class="receipt-work-confirm" type="submit">加入商品</button>
          <div class="manual-sample-codes">
            <button type="button" data-manual-code="6901234567001">抽纸</button>
            <button type="button" data-manual-code="6901234567003">牛奶</button>
            <button type="button" data-manual-code="6901234567004">大米</button>
            <button type="button" data-manual-code="6901234567005">矿泉水</button>
          </div>
        </form>
        <section class="manual-receipt-section">
          <div class="manual-section-title">
            <strong>商品明细</strong>
            <span id="manualLineCount">0 种</span>
          </div>
          <div id="manualReceiptLines" class="manual-line-list">
            <div class="empty-state">还没有商品，先扫码添加。</div>
          </div>
        </section>
        <div class="manual-receipt-bottom">
          <button id="manualCreateReceipt" type="button" disabled>生成收货单</button>
        </div>
      </section>
    `;
    document.getElementById("backToReceiptList").addEventListener("click", () => renderReceiptFlowPage(route, group));
    document.getElementById("manualReceiptLineForm").addEventListener("submit", addManualReceiptLine);
    document.getElementById("manualCreateReceipt").addEventListener("click", () => createManualReceipt(route, group));
    root.querySelectorAll("[data-manual-code]").forEach((button) => {
      button.addEventListener("click", () => {
        document.getElementById("manualProductCode").value = button.dataset.manualCode;
        focusFirst("#manualProductQty");
      });
    });
    focusFirst("#manualProductCode");
  }

  async function addManualReceiptLine(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const codeInput = document.getElementById("manualProductCode");
    const qtyInput = document.getElementById("manualProductQty");
    const code = codeInput.value.trim();
    const qty = Number(qtyInput.value || 0);
    if (!code || qty <= 0) {
      showToast("请填写商品和数量", true);
      return;
    }
    try {
      setBusy(form, true);
      const data = await apiGet(ENDPOINTS.inbound.manualProduct, { code });
      const product = data.product || {};
      const existing = state.manualReceiptLines.find((line) => String(line.product_id) === String(product.id));
      if (existing) {
        existing.qty += qty;
      } else {
        state.manualReceiptLines.push({
          product_id: product.id,
          productName: product.product_name || product.name || code,
          defaultCode: product.default_code || "",
          barcode: product.barcode || code,
          uom: displayUom(product.uom) || "件",
          qty,
        });
      }
      codeInput.value = "";
      qtyInput.value = "";
      renderManualReceiptLines();
      showToast("商品已加入");
      focusFirst("#manualProductCode");
    } catch (error) {
      showError(error);
      codeInput.select();
    } finally {
      setBusy(form, false);
    }
  }

  function renderManualReceiptLines() {
    const container = document.getElementById("manualReceiptLines");
    const count = document.getElementById("manualLineCount");
    const createButton = document.getElementById("manualCreateReceipt");
    if (!container) {
      return;
    }
    if (count) {
      count.textContent = `${state.manualReceiptLines.length} 种`;
    }
    if (createButton) {
      createButton.disabled = !state.manualReceiptLines.length;
    }
    if (!state.manualReceiptLines.length) {
      container.innerHTML = `<div class="empty-state">还没有商品，先扫码添加。</div>`;
      return;
    }
    container.innerHTML = state.manualReceiptLines.map((line, index) => `
      <article class="manual-line-card">
        <div class="receipt-line-thumb">
          <span>${escapeHtml(receiptLineAvatarText(line))}</span>
        </div>
        <div class="manual-line-main">
          <strong>${escapeHtml(line.productName)}</strong>
          <p>${escapeHtml([line.defaultCode, line.barcode].filter(Boolean).join(" · "))}</p>
          <div>应收：<b>${escapeHtml(formatQty(line.qty))}${escapeHtml(displayUom(line.uom) || "件")}</b></div>
        </div>
        <button type="button" data-remove-manual-line="${escapeAttr(index)}">删除</button>
      </article>
    `).join("");
    container.querySelectorAll("[data-remove-manual-line]").forEach((button) => {
      button.addEventListener("click", () => {
        state.manualReceiptLines.splice(Number(button.dataset.removeManualLine), 1);
        renderManualReceiptLines();
      });
    });
  }

  async function createManualReceipt(route, group) {
    if (!state.manualReceiptLines.length) {
      showToast("请先添加商品", true);
      return;
    }
    const button = document.getElementById("manualCreateReceipt");
    const payload = {
      request_id: requestId("manual_receipt"),
      device_id: state.deviceId,
      partner_name: document.getElementById("manualPartnerName").value.trim(),
      origin: document.getElementById("manualOrigin").value.trim(),
      logistics_no: document.getElementById("manualLogisticsNo").value.trim(),
      lines: state.manualReceiptLines.map((line) => ({
        barcode: line.barcode || line.defaultCode,
        qty: line.qty,
      })),
    };
    try {
      button.disabled = true;
      const result = await apiPost(ENDPOINTS.inbound.manualCreate, payload);
      showToast("收货单已生成");
      state.manualReceiptLines = [];
      state.receiptStatus = "waiting_receipt";
      state.receiptSearch = result.task && (result.task.name || result.task.origin) || "";
      await renderReceiptFlowPage(route, group);
    } catch (error) {
      showError(error);
      button.disabled = false;
    }
  }

  function manualReceiptDefaultNo() {
    const now = new Date();
    const pad = (value) => String(value).padStart(2, "0");
    return `手动收货-${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}${pad(now.getHours())}${pad(now.getMinutes())}`;
  }

  async function loadReceiptTasks() {
    const container = document.getElementById("receiptItems");
    if (!container) {
      return;
    }
    container.innerHTML = `<div class="empty-state">正在读取收货单...</div>`;
    try {
      const groups = await Promise.all(RECEIPT_STATUS_TABS.map(async (tab) => {
        const data = await apiGet(ENDPOINTS.inbound.list, { state: tab.key, limit: 100 });
        return [tab.key, getRecords(data)];
      }));
      const byStatus = Object.fromEntries(groups);
      state.receiptCounts = Object.fromEntries(groups.map(([key, records]) => [key, records.length]));
      updateReceiptStateTabs();
      const records = filterReceiptRecords(byStatus[state.receiptStatus] || []);
      state.activeTasks.inbound = records;
      if (!records.length) {
        container.innerHTML = `<div class="empty-state receipt-empty">${escapeHtml(receiptEmptyText())}</div>`;
        return;
      }
      container.innerHTML = records.map(receiptCard).join("");
      container.querySelectorAll("[data-receipt-detail-id]").forEach((button) => {
        button.addEventListener("click", () => renderReceiptViewDetailPage(Number(button.dataset.receiptDetailId)));
      });
      container.querySelectorAll("[data-receipt-work-id]").forEach((button) => {
        button.addEventListener("click", () => renderInboundTaskDetailPage("inbound", Number(button.dataset.receiptWorkId)));
      });
    } catch (error) {
      container.innerHTML = `<div class="error-state">${escapeHtml(messageOf(error))}</div>`;
    }
  }

  function updateReceiptStateTabs() {
    RECEIPT_STATUS_TABS.forEach((tab) => {
      const button = document.querySelector(`[data-receipt-status="${tab.key}"]`);
      const count = document.querySelector(`[data-receipt-count="${tab.key}"]`);
      if (button) {
        button.classList.toggle("is-active", tab.key === state.receiptStatus);
      }
      if (count) {
        const value = Number(state.receiptCounts[tab.key] || 0);
        count.textContent = value ? String(value) : "";
      }
    });
  }

  function filterReceiptRecords(records) {
    const keyword = state.receiptSearch.trim().toLowerCase();
    if (!keyword) {
      return records;
    }
    return records.filter((task) => [
      task.name,
      task.picking_name,
      task.origin,
      task.partner_name,
      task.product_summary,
      task.related_no,
      task.logistics_no,
    ].filter(Boolean).some((value) => String(value).toLowerCase().includes(keyword)));
  }

  function receiptEmptyText() {
    const label = receiptStatusLabel(state.receiptStatus);
    if (state.receiptSearch) {
      return `没有匹配“${state.receiptSearch}”的${label}收货单。`;
    }
    return `暂无${label}收货单。`;
  }

  function receiptCard(task) {
    const canReceive = task.state !== "received";
    const progress = receiptProgressText(task);
    return `
      <article class="receipt-card">
        <div class="receipt-card-head">
          <div>
            <span class="receipt-type-tag">${escapeHtml(task.source_type_label || "采购")}</span>
            <strong>单号 ${escapeHtml(task.origin || task.picking_name || task.name)}</strong>
          </div>
          <em>${escapeHtml(receiptStatusLabel(task.state))}</em>
        </div>
        <div class="receipt-info-list">
          ${receiptInfoLine("发货方", task.partner_name)}
          ${receiptInfoLine("创建人", task.create_uid_name)}
          ${receiptInfoLine("创建时间", formatDateTime(task.create_date))}
          ${receiptInfoLine("送达时间", formatDateTime(task.scheduled_date) || "-")}
          ${receiptInfoLine("关联单号", task.related_no || task.picking_name)}
          ${receiptInfoLine("物流单号", task.logistics_no)}
        </div>
        <div class="receipt-progress">进度：${escapeHtml(progress)}</div>
        <div class="receipt-progress-bar" aria-hidden="true">
          <i style="width: ${escapeAttr(receiptProgressPercent(task))}%"></i>
        </div>
        <div class="receipt-card-actions">
          <button class="receipt-detail-button" type="button" data-receipt-detail-id="${escapeAttr(task.id)}">查看详情</button>
          ${canReceive ? `<button class="receipt-work-button" type="button" data-receipt-work-id="${escapeAttr(task.id)}">收货</button>` : ""}
        </div>
      </article>
    `;
  }

  function receiptInfoLine(label, value) {
    return `<p><span>${escapeHtml(label)}：</span><strong>${escapeHtml(value || "-")}</strong></p>`;
  }

  function receiptProgressText(task) {
    const doneLines = Number(task.done_line_count || 0);
    const lineCount = Number(task.line_count || 0);
    const doneQty = formatQty(task.done_qty || 0);
    const totalQty = formatQty(task.demand_qty || 0);
    return `商品 ${doneLines}/${lineCount}、数量 ${doneQty}/${totalQty}、箱数 ${doneQty}/${totalQty}`;
  }

  function receiptProgressPercent(task) {
    const total = Number(task.demand_qty || 0);
    if (!total) {
      return 0;
    }
    return Math.max(0, Math.min(100, Math.round((Number(task.done_qty || 0) / total) * 100)));
  }

  function receiptStatusLabel(value) {
    return {
      waiting_receipt: "待收货",
      receiving: "收货中",
      received: "已完成",
      closed: "已关单",
    }[value] || statusLabel(value) || value || "";
  }

  async function renderReceiptViewDetailPage(taskId) {
    const group = FLOW_GROUPS["inbound-flow"];
    const task = findTask("inbound", taskId) || {};
    state.receiptDetailStatus = defaultReceiptDetailStatus(task);
    state.receiptDetailSearch = "";
    root.innerHTML = `
      <section class="task-panel receipt-detail-page">
        <div class="receipt-detail-nav">
          <button id="backToReceiptList" class="app-back-button" type="button" aria-label="返回">‹</button>
          <h1>收货单详情</h1>
          <span></span>
        </div>
        <div class="empty-state receipt-detail-loading">正在读取收货单明细...</div>
      </section>
    `;
    document.getElementById("backToReceiptList").addEventListener("click", () => renderReceiptFlowPage("inbound-flow", group));
    try {
      const data = await apiGet(ENDPOINTS.inbound.lines(taskId), { lock: 0 });
      const focusedTask = { ...task, ...(data.task || {}), id: taskId };
      const lines = normalizeLines(data.lines || data.records || [], "inbound");
      state.receiptDetailStatus = defaultReceiptDetailStatus(focusedTask, lines);
      state.activeTasks.receiptDetail = focusedTask;
      state.activeLines.receiptDetail = lines;
      root.innerHTML = renderReceiptDetailShell(focusedTask);
      bindReceiptDetailPage(taskId, group);
      renderReceiptDetailLines();
    } catch (error) {
      root.innerHTML = `
        <section class="task-panel receipt-detail-page">
          <div class="receipt-detail-nav">
            <button id="backToReceiptList" class="app-back-button" type="button" aria-label="返回">‹</button>
            <h1>收货单详情</h1>
            <span></span>
          </div>
          <div class="error-state">${escapeHtml(messageOf(error))}</div>
        </section>
      `;
      document.getElementById("backToReceiptList").addEventListener("click", () => renderReceiptFlowPage("inbound-flow", group));
    }
  }

  function renderReceiptDetailShell(task) {
    const orderNo = task.origin || task.picking_name || task.name || "收货单";
    return `
      <section class="task-panel receipt-detail-page">
        <div class="receipt-detail-nav">
          <button id="backToReceiptList" class="app-back-button" type="button" aria-label="返回">‹</button>
          <h1>收货单详情</h1>
          <span></span>
        </div>
        <section class="receipt-detail-order">
          <div class="receipt-detail-order-main">
            <strong>单号 ${escapeHtml(orderNo)}</strong>
            <div>
              <span>${escapeHtml(receiptStatusLabel(task.state))}</span>
              <button id="receiptDetailExpand" type="button">展开</button>
            </div>
          </div>
          <div id="receiptDetailExtra" class="receipt-detail-extra" hidden>
            ${receiptInfoLine("发货方", task.partner_name)}
            ${receiptInfoLine("创建人", task.create_uid_name)}
            ${receiptInfoLine("创建时间", formatDateTime(task.create_date))}
            ${receiptInfoLine("送达时间", formatDateTime(task.scheduled_date) || "-")}
            ${receiptInfoLine("关联单号", task.related_no || task.picking_name)}
            ${receiptInfoLine("物流单号", task.logistics_no)}
            ${receiptInfoLine("当前进度", receiptProgressText(task))}
          </div>
        </section>
        <form id="receiptDetailSearchForm" class="receipt-detail-search" autocomplete="off">
          <input id="receiptDetailSearchInput" type="search" value="${escapeAttr(state.receiptDetailSearch)}" placeholder="搜索 商品名称/条码/SKU/外部编码" />
          <button class="receipt-detail-scan" type="submit" aria-label="搜索">⌗</button>
          <button id="receiptDetailTag" class="receipt-detail-tag" type="button">标签⌄</button>
        </form>
        <div class="receipt-detail-tabs" role="tablist" aria-label="明细收货状态">
          ${RECEIPT_DETAIL_STATUS_TABS.map((tab) => `
            <button class="receipt-detail-tab ${tab.key === state.receiptDetailStatus ? "is-active" : ""}" type="button" data-receipt-detail-status="${escapeAttr(tab.key)}">
              ${escapeHtml(tab.label)}<em data-receipt-detail-count="${escapeAttr(tab.key)}"></em>
            </button>
          `).join("")}
        </div>
        <div id="receiptDetailLines" class="receipt-line-list"></div>
        <div class="receipt-detail-bottom-actions">
          <button id="receiptDetailClose" type="button">关单</button>
          <button id="receiptDetailStart" type="button">开始收货</button>
        </div>
      </section>
    `;
  }

  function bindReceiptDetailPage(taskId, group) {
    document.getElementById("backToReceiptList").addEventListener("click", () => renderReceiptFlowPage("inbound-flow", group));
    document.getElementById("receiptDetailSearchForm").addEventListener("submit", (event) => {
      event.preventDefault();
      state.receiptDetailSearch = document.getElementById("receiptDetailSearchInput").value.trim();
      renderReceiptDetailLines();
    });
    document.getElementById("receiptDetailSearchInput").addEventListener("input", (event) => {
      state.receiptDetailSearch = event.target.value.trim();
      renderReceiptDetailLines();
    });
    document.getElementById("receiptDetailTag").addEventListener("click", () => showToast("标签筛选预留，当前可按状态与关键词筛选"));
    document.getElementById("receiptDetailExpand").addEventListener("click", (event) => {
      const extra = document.getElementById("receiptDetailExtra");
      const expanded = extra.hasAttribute("hidden");
      extra.toggleAttribute("hidden", !expanded);
      event.currentTarget.textContent = expanded ? "收起" : "展开";
    });
    document.getElementById("receiptDetailClose").addEventListener("click", () => closeReceiptTask(taskId, group));
    document.getElementById("receiptDetailStart").addEventListener("click", () => renderInboundTaskDetailPage("inbound", taskId));
    root.querySelectorAll("[data-receipt-detail-status]").forEach((button) => {
      button.addEventListener("click", () => {
        state.receiptDetailStatus = button.dataset.receiptDetailStatus;
        renderReceiptDetailLines();
      });
    });
    focusFirst("#receiptDetailSearchInput");
  }

  async function closeReceiptTask(taskId, group) {
    if (!window.confirm("确认关闭当前收货单？关闭后将不再进入待收货/收货中。")) {
      return;
    }
    const button = document.getElementById("receiptDetailClose");
    try {
      if (button) {
        button.disabled = true;
      }
      await apiPost(ENDPOINTS.inbound.close(taskId), {
        request_id: requestId("receipt_close"),
        device_id: state.deviceId,
        reason: "PDA 关单",
      });
      showToast("收货单已关闭");
      await renderReceiptFlowPage("inbound-flow", group);
    } catch (error) {
      showError(error);
      if (button) {
        button.disabled = false;
      }
    }
  }

  function renderReceiptDetailLines() {
    const container = document.getElementById("receiptDetailLines");
    if (!container) {
      return;
    }
    const lines = state.activeLines.receiptDetail || [];
    updateReceiptDetailTabs(lines);
    const records = lines
      .filter((line) => receiptDetailLineMatches(line, state.receiptDetailStatus))
      .filter(receiptDetailSearchMatches);
    if (!records.length) {
      container.innerHTML = `<div class="receipt-detail-no-more">没有更多数据</div>`;
      return;
    }
    container.innerHTML = `
      ${records.map(receiptDetailLineCard).join("")}
      <div class="receipt-detail-no-more">没有更多数据</div>
    `;
    container.querySelectorAll("[data-diff-line]").forEach((button) => {
      button.addEventListener("click", () => showToast(`差异提报预留：${button.dataset.diffLine}`));
    });
  }

  function updateReceiptDetailTabs(lines) {
    RECEIPT_DETAIL_STATUS_TABS.forEach((tab) => {
      const button = document.querySelector(`[data-receipt-detail-status="${tab.key}"]`);
      const count = document.querySelector(`[data-receipt-detail-count="${tab.key}"]`);
      if (button) {
        button.classList.toggle("is-active", tab.key === state.receiptDetailStatus);
      }
      if (count) {
        const value = lines.filter((line) => receiptDetailLineMatches(line, tab.key)).length;
        count.textContent = value ? String(value) : "";
      }
    });
  }

  function receiptDetailLineMatches(line, status) {
    const demandQty = Number(line.demandQty || 0);
    const doneQty = Number(line.doneQty || 0);
    if (status === "partial") {
      return doneQty > 0 && (!demandQty || doneQty < demandQty);
    }
    if (status === "complete") {
      return demandQty ? doneQty >= demandQty : doneQty > 0;
    }
    return doneQty <= 0;
  }

  function defaultReceiptDetailStatus(task, lines) {
    if (task && task.state === "received") {
      return "complete";
    }
    if (task && task.state === "waiting_receipt") {
      return "unreceived";
    }
    if (Array.isArray(lines) && lines.length) {
      return ["partial", "unreceived", "complete"].find((status) => lines.some((line) => receiptDetailLineMatches(line, status))) || "unreceived";
    }
    return "unreceived";
  }

  function receiptDetailSearchMatches(line) {
    const keyword = state.receiptDetailSearch.trim().toLowerCase();
    if (!keyword) {
      return true;
    }
    return [
      line.productName,
      line.defaultCode,
      line.barcode,
      line.location,
      line.raw && line.raw.sku,
      line.raw && line.raw.external_code,
      line.raw && line.raw.product_code,
    ].filter(Boolean).some((value) => String(value).toLowerCase().includes(keyword));
  }

  function receiptDetailLineCard(line) {
    const diffQty = receiptLineDiffQty(line);
    const imageUrl = line.raw && (line.raw.image_url || line.raw.product_image_url || line.raw.image);
    const spec = (line.raw && (line.raw.spec || line.raw.specification || line.raw.variant || line.raw.product_spec)) || "-";
    const unit = displayUom(line.uom) || "件";
    const codeText = line.barcode || line.defaultCode || "-";
    const packageText = line.raw && (line.raw.package_ratio || line.raw.packaging_ratio) || `1${unit}/${unit}`;
    return `
      <article class="receipt-line-card">
        <div class="receipt-line-thumb">
          ${imageUrl ? `<img src="${escapeAttr(imageUrl)}" alt="" />` : `<span>${escapeHtml(receiptLineAvatarText(line))}</span>`}
        </div>
        <div class="receipt-line-main">
          <strong class="receipt-line-title">${escapeHtml(line.productName || "未命名商品")}</strong>
          <p class="receipt-line-meta">规格：${escapeHtml(spec)}</p>
          <p class="receipt-line-meta">条码：${escapeHtml(codeText)}　共 ${escapeHtml(formatQty(line.demandQty))}${escapeHtml(unit)}</p>
          <p class="receipt-line-meta">包装比率：${escapeHtml(packageText)}</p>
          <div class="receipt-line-qty">
            <span>待收：<b>${escapeHtml(formatQty(line.remainingQty))}${escapeHtml(unit)}</b></span>
            <span>应收：<b>${escapeHtml(formatQty(line.demandQty))}${escapeHtml(unit)}</b></span>
            <span>实收：<b>${escapeHtml(formatQty(line.doneQty))}${escapeHtml(unit)}</b></span>
            <span>差异上报：<b>${escapeHtml(formatQty(diffQty))}${escapeHtml(unit)}</b></span>
          </div>
          <div class="receipt-line-actions">
            <button type="button" data-diff-line="${escapeAttr(line.productName || line.defaultCode || line.key)}">差异提报</button>
          </div>
        </div>
      </article>
    `;
  }

  function receiptLineAvatarText(line) {
    const value = line.defaultCode || line.barcode || line.productName || "货";
    return String(value).replace(/[^A-Za-z0-9\u4e00-\u9fa5]/g, "").slice(0, 2).toUpperCase() || "货";
  }

  function receiptLineDiffQty(line) {
    const raw = line.raw || {};
    return Number(raw.exception_qty ?? raw.diff_qty ?? raw.discrepancy_qty ?? raw.reported_diff_qty ?? 0);
  }

  async function renderReceiptWorkPage(taskId) {
    const group = FLOW_GROUPS["inbound-flow"];
    const task = findTask("inbound", taskId) || {};
    state.activeTasks["inbound:id"] = taskId;
    state.receiptWorkTab = "waiting";
    state.receiptWorkSearch = "";
    state.lineMatches.inbound = "";
    root.innerHTML = renderReceiptWorkShell(task);
    bindReceiptWorkPage(taskId, group);
    await loadReceiptWorkTask(taskId);
  }

  function renderReceiptWorkShell(task) {
    const title = task.origin || task.picking_name || task.name || "收货单";
    return `
      <section class="task-panel receipt-work-page">
        <div class="receipt-work-nav">
          <button id="backToReceiptList" class="app-back-button" type="button" aria-label="返回">‹</button>
          <h1>扫商品</h1>
          <div>
            <button id="receiptWorkDetail" type="button">详情</button>
            <button id="receiptWorkBatch" type="button">批量收货</button>
          </div>
        </div>
        <p class="receipt-work-order">${escapeHtml(title)}</p>
        <form id="receiptWorkScanForm" class="receipt-work-scan" autocomplete="off">
          <label class="receipt-work-search">
            <span>商品</span>
            <input id="receiptWorkBarcode" type="search" inputmode="text" autocomplete="off" placeholder="扫描 / 输入商品条码/SKU/外部编码" />
            <button type="submit" aria-label="确认商品">⌗</button>
          </label>
          <div id="receiptWorkMatched" class="receipt-work-matched is-empty">请先扫描或选择待收商品。</div>
          <button id="receiptWorkConfirm" class="receipt-work-confirm" type="submit" disabled>确认</button>
        </form>
        <div class="receipt-work-tabs" role="tablist" aria-label="收货作业状态">
          <button class="receipt-work-tab is-active" type="button" data-receipt-work-tab="waiting">本次待收商品<em data-receipt-work-count="waiting"></em></button>
          <button class="receipt-work-tab" type="button" data-receipt-work-tab="submitted">待提交收货<em data-receipt-work-count="submitted"></em></button>
        </div>
        <div id="receiptWorkLines" class="receipt-work-lines">
          <div class="empty-state receipt-detail-loading">正在读取商品...</div>
        </div>
        <div class="receipt-work-bottom">
          <button id="receiptWorkSubmit" type="button" disabled>提交收货</button>
        </div>
      </section>
    `;
  }

  function bindReceiptWorkPage(taskId, group) {
    document.getElementById("backToReceiptList").addEventListener("click", () => renderReceiptFlowPage("inbound-flow", group));
    document.getElementById("receiptWorkDetail").addEventListener("click", () => renderReceiptViewDetailPage(taskId));
    document.getElementById("receiptWorkBatch").addEventListener("click", () => showToast("批量收货入口已保留，当前请逐一扫码确认数量"));
    document.getElementById("receiptWorkSubmit").addEventListener("click", () => completeTask("inbound"));
    document.getElementById("receiptWorkScanForm").addEventListener("submit", (event) => confirmReceiptWorkLine(event));
    document.getElementById("receiptWorkBarcode").addEventListener("input", (event) => {
      state.receiptWorkSearch = event.target.value.trim();
      updateReceiptWorkMatchedLine();
      renderReceiptWorkLines();
    });
    root.querySelectorAll("[data-receipt-work-tab]").forEach((button) => {
      button.addEventListener("click", () => {
        state.receiptWorkTab = button.dataset.receiptWorkTab;
        renderReceiptWorkLines();
      });
    });
    focusFirst("#receiptWorkBarcode");
  }

  async function loadReceiptWorkTask(taskId) {
    const linesContainer = document.getElementById("receiptWorkLines");
    if (linesContainer) {
      linesContainer.innerHTML = `<div class="empty-state receipt-detail-loading">正在读取商品...</div>`;
    }
    try {
      const data = await apiGet(ENDPOINTS.inbound.lines(taskId));
      const task = data.task || findTask("inbound", taskId);
      if (task) {
        state.activeTasks["inbound:focusedTask"] = task;
      }
      state.activeLines.inbound = normalizeLines(data.lines || data.records || [], "inbound");
      updateReceiptWorkMatchedLine();
      renderReceiptWorkLines();
    } catch (error) {
      if (linesContainer) {
        linesContainer.innerHTML = `<div class="error-state">${escapeHtml(messageOf(error))}</div>`;
      }
    }
  }

  function updateReceiptWorkMatchedLine() {
    const input = document.getElementById("receiptWorkBarcode");
    const matchedBox = document.getElementById("receiptWorkMatched");
    const confirmButton = document.getElementById("receiptWorkConfirm");
    if (!input || !matchedBox || !confirmButton) {
      return;
    }
    const keyword = input.value.trim();
    const lines = state.activeLines.inbound || [];
    const match = lines.find((line) => receiptWorkProductMatches(line, keyword));
    state.lineMatches.inbound = match ? match.key : "";
    if (!keyword) {
      matchedBox.className = "receipt-work-matched is-empty";
      matchedBox.innerHTML = "请先扫描或选择待收商品。";
      confirmButton.disabled = true;
      return;
    }
    if (!match) {
      matchedBox.className = "receipt-work-matched is-empty";
      matchedBox.innerHTML = "没有匹配到商品，请核对条码或 SKU。";
      confirmButton.disabled = true;
      return;
    }
    matchedBox.className = "receipt-work-matched";
    matchedBox.innerHTML = renderReceiptWorkMatchedLine(match);
    const qtyInput = document.getElementById("receiptWorkQty");
    if (qtyInput && !qtyInput.value) {
      qtyInput.value = formatQty(preferredQty(match) || match.remainingQty || match.demandQty || 0);
    }
    confirmButton.disabled = Number(match.remainingQty || 0) <= 0;
  }

  function renderReceiptWorkMatchedLine(line) {
    const unit = displayUom(line.uom) || "件";
    return `
      <div>
        <strong>${escapeHtml(line.productName || "未命名商品")}</strong>
        <small>${escapeHtml(receiptWorkLineMeta(line))}</small>
      </div>
      <label>
        <span>本次数量</span>
        <input id="receiptWorkQty" type="number" min="0" step="0.001" inputmode="decimal" value="${escapeAttr(formatQty(preferredQty(line) || line.remainingQty || line.demandQty || 0))}" />
        <b>${escapeHtml(unit)}</b>
      </label>
    `;
  }

  function renderReceiptWorkLines() {
    const container = document.getElementById("receiptWorkLines");
    if (!container) {
      return;
    }
    const lines = state.activeLines.inbound || [];
    updateReceiptWorkTabs(lines);
    updateReceiptWorkSubmit(lines);
    const source = state.receiptWorkTab === "submitted"
      ? lines.filter((line) => Number(line.doneQty || 0) > 0)
      : lines.filter((line) => Number(line.remainingQty || 0) > 0);
    const records = filterReceiptWorkLines(source);
    if (!records.length) {
      container.innerHTML = `<div class="receipt-detail-no-more">没有更多数据</div>`;
      return;
    }
    container.innerHTML = `
      ${records.map((line) => receiptWorkLineCard(line, state.receiptWorkTab)).join("")}
      <div class="receipt-detail-no-more">没有更多数据</div>
    `;
    container.querySelectorAll("[data-receipt-work-line]").forEach((button) => {
      button.addEventListener("click", () => selectReceiptWorkLine(button.dataset.receiptWorkLine));
    });
  }

  function updateReceiptWorkTabs(lines) {
    const counts = {
      waiting: lines.filter((line) => Number(line.remainingQty || 0) > 0).length,
      submitted: lines.filter((line) => Number(line.doneQty || 0) > 0).length,
    };
    root.querySelectorAll("[data-receipt-work-tab]").forEach((button) => {
      button.classList.toggle("is-active", button.dataset.receiptWorkTab === state.receiptWorkTab);
    });
    Object.entries(counts).forEach(([key, value]) => {
      const target = document.querySelector(`[data-receipt-work-count="${key}"]`);
      if (target) {
        target.textContent = value ? String(value) : "";
      }
    });
  }

  function updateReceiptWorkSubmit(lines) {
    const button = document.getElementById("receiptWorkSubmit");
    if (!button) {
      return;
    }
    const hasSubmitted = lines.some((line) => Number(line.doneQty || 0) > 0);
    button.disabled = !hasSubmitted;
  }

  function filterReceiptWorkLines(lines) {
    const keyword = state.receiptWorkSearch.trim().toLowerCase();
    if (!keyword) {
      return lines;
    }
    return lines.filter((line) => receiptWorkProductMatches(line, keyword, true));
  }

  function receiptWorkProductMatches(line, keyword, fuzzy) {
    if (!keyword) {
      return false;
    }
    const normalized = String(keyword).toLowerCase();
    const exactValues = [
      line.barcode,
      line.defaultCode,
      line.raw && line.raw.sku,
      line.raw && line.raw.external_code,
      line.raw && line.raw.product_code,
    ].filter(Boolean).map((value) => String(value).toLowerCase());
    if (!fuzzy) {
      return exactValues.some((value) => value === normalized);
    }
    const values = [
      ...exactValues,
      line.productName ? String(line.productName).toLowerCase() : "",
    ].filter(Boolean);
    return fuzzy
      ? values.some((value) => value.includes(normalized))
      : false;
  }

  function selectReceiptWorkLine(lineKey) {
    const line = (state.activeLines.inbound || []).find((item) => item.key === lineKey);
    const input = document.getElementById("receiptWorkBarcode");
    if (!line || !input) {
      return;
    }
    input.value = line.barcode || line.defaultCode || line.productName || "";
    state.receiptWorkSearch = input.value.trim();
    updateReceiptWorkMatchedLine();
    renderReceiptWorkLines();
    const qtyInput = document.getElementById("receiptWorkQty");
    if (qtyInput) {
      qtyInput.select();
    }
  }

  function receiptWorkLineCard(line, tab) {
    const unit = displayUom(line.uom) || "件";
    const qtyLabel = tab === "submitted" ? "已确认" : "待收";
    const qty = tab === "submitted" ? line.doneQty : line.remainingQty;
    const action = tab === "submitted"
      ? `<span class="receipt-work-done">待提交</span>`
      : `<button type="button" data-receipt-work-line="${escapeAttr(line.key)}">选择</button>`;
    return `
      <article class="receipt-work-line ${state.lineMatches.inbound === line.key ? "is-match" : ""}">
        <div class="receipt-line-thumb">
          <span>${escapeHtml(receiptLineAvatarText(line))}</span>
        </div>
        <div class="receipt-work-line-main">
          <strong>${escapeHtml(line.productName || "未命名商品")}</strong>
          <p>${escapeHtml(receiptWorkLineMeta(line))}</p>
          <p>SKU：${escapeHtml(line.defaultCode || "-")}</p>
          <div class="receipt-work-line-qty">${escapeHtml(qtyLabel)}：<b>${escapeHtml(formatQty(qty))}${escapeHtml(unit)}</b></div>
        </div>
        <div class="receipt-work-line-action">
          ${action}
        </div>
      </article>
    `;
  }

  function receiptWorkLineMeta(line) {
    const spec = (line.raw && (line.raw.spec || line.raw.specification || line.raw.variant || line.raw.product_spec)) || "";
    return [
      spec ? `规格：${spec}` : "",
      line.barcode ? `条码：${line.barcode}` : "",
    ].filter(Boolean).join("　") || "暂无规格与条码";
  }

  async function confirmReceiptWorkLine(event) {
    event.preventDefault();
    const taskId = activeTaskId("inbound");
    const form = event.currentTarget;
    const line = (state.activeLines.inbound || []).find((item) => item.key === state.lineMatches.inbound);
    const barcode = document.getElementById("receiptWorkBarcode").value.trim();
    const qtyInput = document.getElementById("receiptWorkQty");
    const qty = qtyInput && qtyInput.value;
    if (!taskId || !line || !barcode) {
      showToast("请先扫描或选择商品");
      return;
    }
    if (!qty) {
      showToast("请填写本次数量");
      if (qtyInput) {
        qtyInput.focus();
      }
      return;
    }
    try {
      setBusy(form, true);
      const result = await apiPost(ENDPOINTS.inbound.confirm(taskId), {
        request_id: requestId("inbound_line"),
        device_id: state.deviceId,
        barcode,
        product_barcode: barcode,
        done_qty: qty,
      });
      rememberResult("inbound", "本行已确认", result);
      showToast("本行已确认");
      state.receiptWorkTab = "submitted";
      state.receiptWorkSearch = "";
      state.lineMatches.inbound = "";
      const input = document.getElementById("receiptWorkBarcode");
      if (input) {
        input.value = "";
      }
      await loadReceiptWorkTask(taskId);
      focusFirst("#receiptWorkBarcode");
    } catch (error) {
      showError(error);
    } finally {
      setBusy(form, false);
      updateReceiptWorkMatchedLine();
    }
  }

  async function loadInboundTasks(mode) {
    const container = document.getElementById("taskItems");
    if (!container) {
      return;
    }
    const config = ENDPOINTS[mode];
    container.innerHTML = `<div class="empty-state">正在读取任务...</div>`;
    try {
      const query = { limit: 50 };
      if (mode === "arrival") {
        query.arrival_status = state.arrivalStatus;
      }
      const data = await apiGet(config.list, query);
      const records = getRecords(data);
      const displayRecords = await enrichTaskCards(mode, records);
      state.activeTasks[mode] = displayRecords;
      if (!displayRecords.length) {
        container.innerHTML = `<div class="empty-state inbound-empty">${escapeHtml(inboundEmptyText(mode))}</div>`;
        return;
      }
      container.innerHTML = displayRecords.map((task) => taskCard(task, false, mode)).join("");
      container.querySelectorAll("[data-task-detail-id]").forEach((button) => {
        button.addEventListener("click", () => renderInboundTaskDetailPage(mode, Number(button.dataset.taskDetailId)));
      });
      bindTaskActionButtons(container, mode);
    } catch (error) {
      container.innerHTML = `<div class="error-state">${escapeHtml(messageOf(error))}</div>`;
    }
  }

  function inboundEmptyText(mode) {
    if (mode === "arrival") {
      return {
        unsigned: "暂无未签到到货单，可切换已签到、已取消查看记录。",
        signed: "暂无已签到记录，未签到单确认到货后会出现在这里。",
        cancelled: "暂无已取消到货单。",
      }[state.arrivalStatus] || "暂无待到货单。";
    }
    return {
      arrival: "暂无待到货单，可切换待收货、待上架查看后续任务。",
      inbound: "暂无待收货任务，到货签到后会生成收货任务。",
      putaway: "暂无待上架任务，收货完成后会生成上架任务。",
      inbound_done: "暂无已完成记录。",
    }[mode] || "暂无待处理任务。";
  }

  async function renderInboundTaskDetailPage(mode, taskId) {
    if (mode === "arrival") {
      renderArrivalTaskDetailPage(taskId);
      return;
    }
    if (mode === "inbound_done") {
      renderInboundDoneDetailPage(taskId);
      return;
    }
    if (mode === "inbound") {
      renderReceiptWorkPage(taskId);
      return;
    }
    const group = FLOW_GROUPS["inbound-flow"];
    const config = ENDPOINTS[mode];
    root.innerHTML = `
      <section class="task-panel inbound-detail-page">
        <div class="app-page-title app-sub-title">
          <button id="backToInboundList" class="app-back-button" type="button" aria-label="返回">‹</button>
          <div>
            <h1>${escapeHtml(config.title)}</h1>
            <p>${escapeHtml(group.subtitle)}</p>
          </div>
          <button id="completeTask" class="mini-button" type="button" disabled>${escapeHtml(config.completeText)}</button>
        </div>
        ${renderWorkflowStrip("inbound-flow", mode)}
        <section class="task-detail inbound-detail-card">
          <div id="detailBody" class="detail-body">
            <div class="empty-state">正在读取明细...</div>
          </div>
        </section>
        ${renderBottomNav("operation")}
      </section>
    `;
    document.getElementById("backToInboundList").addEventListener("click", () => renderInboundFlowPage("inbound-flow", group));
    document.getElementById("completeTask").addEventListener("click", () => completeTask(mode));
    bindBottomNav();
    await selectTask(mode, taskId);
  }

  function renderArrivalTaskDetailPage(taskId) {
    const group = FLOW_GROUPS["inbound-flow"];
    const task = findTask("arrival", taskId) || {};
    const arrivalStatus = task.arrival_status || "unsigned";
    const canCheckin = arrivalStatus === "unsigned";
    state.activeTasks["arrival:id"] = taskId;
    root.innerHTML = `
      <section class="task-panel inbound-detail-page">
        <div class="app-page-title app-sub-title">
          <button id="backToInboundList" class="app-back-button" type="button" aria-label="返回">‹</button>
          <div>
            <h1>到货签到</h1>
            <p>${escapeHtml(group.subtitle)}</p>
          </div>
          ${canCheckin
            ? `<div class="arrival-detail-actions">
                <button id="cancelArrivalTask" class="mini-button is-plain" type="button">取消到货</button>
                <button id="completeTask" class="mini-button" type="button">确认到货</button>
              </div>`
            : `<span class="mini-pill">${escapeHtml(arrivalStatusLabel(task))}</span>`}
        </div>
        <section class="task-detail inbound-detail-card">
          <div class="detail-body">
            ${renderLastResult("arrival")}
            <div class="scan-box">
              <h2>${escapeHtml(task.name || task.picking_name || "到货单")}</h2>
              <div class="info-grid">
                ${infoItem("签到状态", arrivalStatusLabel(task))}
                ${infoItem("供应商", task.partner_name)}
                ${infoItem("入库单", task.picking_name)}
                ${infoItem("收货任务", task.receipt_task_name)}
                ${infoItem("目标库位", task.dest_location)}
                ${infoItem("计划到货", task.scheduled_date ? String(task.scheduled_date).slice(0, 16) : "")}
                ${infoItem("商品", task.product_summary)}
                ${infoItem("数量", task.demand_qty ? formatQty(task.demand_qty) : "")}
              </div>
            </div>
            ${renderArrivalProductLines(task)}
          </div>
        </section>
        ${renderBottomNav("operation")}
      </section>
    `;
    document.getElementById("backToInboundList").addEventListener("click", () => renderInboundFlowPage("inbound-flow", group));
    if (canCheckin) {
      document.getElementById("completeTask").addEventListener("click", () => completeTask("arrival"));
      document.getElementById("cancelArrivalTask").addEventListener("click", () => cancelArrivalTask(taskId));
    }
    bindBottomNav();
  }

  function renderArrivalProductLines(task) {
    const lines = normalizeLines(task.lines || [], "arrival");
    return `
      <section class="arrival-lines-panel">
        <div class="arrival-lines-head">
          <strong>到货商品</strong>
          <span>${escapeHtml(lines.length ? `${lines.length} 种` : "暂无商品")}</span>
        </div>
        <div class="arrival-line-list">
          ${lines.length ? lines.map(arrivalLineCard).join("") : `<div class="empty-state">暂无商品明细。</div>`}
        </div>
      </section>
    `;
  }

  function arrivalLineCard(line) {
    const unit = displayUom(line.uom) || "件";
    const targetLocation = line.raw && (line.raw.dest_location || line.raw.dest_location_name) || line.location || "";
    return `
      <article class="arrival-line-card">
        <div class="receipt-line-thumb">
          <span>${escapeHtml(receiptLineAvatarText(line))}</span>
        </div>
        <div class="arrival-line-main">
          <strong>${escapeHtml(line.productName || "未命名商品")}</strong>
          <p>${escapeHtml([line.defaultCode, line.barcode].filter(Boolean).join(" · ") || "暂无条码信息")}</p>
          <p>${escapeHtml(targetLocation ? `目标：${targetLocation}` : "")}</p>
        </div>
        <div class="arrival-line-qty">
          <span>应到</span>
          <b>${escapeHtml(formatQty(line.demandQty))}${escapeHtml(unit)}</b>
        </div>
      </article>
    `;
  }

  function arrivalStatusLabel(task) {
    const status = task && task.arrival_status || state.arrivalStatus || "unsigned";
    return {
      unsigned: "未签到",
      signed: "已签到",
      cancelled: "已取消",
    }[status] || task && task.arrival_status_label || "未签到";
  }

  function renderInboundDoneDetailPage(taskId) {
    const group = FLOW_GROUPS["inbound-flow"];
    const task = findTask("inbound_done", taskId) || {};
    state.activeTasks["inbound_done:id"] = taskId;
    root.innerHTML = `
      <section class="task-panel inbound-detail-page">
        <div class="app-page-title app-sub-title">
          <button id="backToInboundList" class="app-back-button" type="button" aria-label="返回">‹</button>
          <div>
            <h1>已完成</h1>
            <p>${escapeHtml(group.subtitle)}</p>
          </div>
          <span class="mini-pill">已完成</span>
        </div>
        <section class="task-detail inbound-detail-card">
          <div class="detail-body">
            <div class="scan-box">
              <h2>${escapeHtml(task.name || task.picking_name || "完成记录")}</h2>
              <div class="info-grid">
                ${infoItem("收货任务", task.receipt_task_name)}
                ${infoItem("入库单", task.picking_name)}
                ${infoItem("商品", task.product_summary)}
                ${infoItem("数量", task.total_qty ? formatQty(task.total_qty) : "")}
                ${infoItem("上架数量", task.putaway_qty ? formatQty(task.putaway_qty) : "")}
                ${infoItem("目标库位", task.dest_location)}
              </div>
            </div>
          </div>
        </section>
        ${renderBottomNav("operation")}
      </section>
    `;
    document.getElementById("backToInboundList").addEventListener("click", () => renderInboundFlowPage("inbound-flow", group));
    bindBottomNav();
  }

  async function renderHandoverFlowPage(route, group) {
    const mode = "handover";
    root.innerHTML = `
      <section class="task-panel">
        ${renderAppHeader(group.title, group.subtitle, {
          action: `<span class="mini-pill">${escapeHtml(currentWarehouseName())}</span>`,
        })}
        ${renderWorkflowStrip(route, mode)}
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
              <strong>${escapeHtml(HANDOVER_ENDPOINTS.title)}</strong>
              <button id="refreshHandover" class="refresh-button" type="button">刷新</button>
            </div>
            <div id="handoverItems" class="task-items">
              <div class="empty-state">正在读取交接单...</div>
            </div>
          </section>
          <section class="task-detail">
            <div class="detail-header">
              <strong>交接明细</strong>
              <div class="detail-actions">
                <button id="startHandover" class="refresh-button" type="button" disabled>开始交接</button>
                <button id="completeHandover" class="refresh-button" type="button" disabled>完成交接</button>
              </div>
            </div>
            <div id="handoverDetail" class="detail-body">
              <div class="empty-state">请选择左侧交接单。</div>
            </div>
          </section>
        </div>
        ${renderBottomNav("operation")}
      </section>
    `;
    root.querySelectorAll("[data-flow-mode]").forEach((button) => {
      button.addEventListener("click", () => {
        state.flowModes[button.dataset.flowRoute] = button.dataset.flowMode;
        renderFlowPage(button.dataset.flowRoute);
      });
    });
    document.getElementById("refreshHandover").addEventListener("click", loadHandoverOrders);
    document.getElementById("startHandover").addEventListener("click", confirmHandoverOrder);
    document.getElementById("completeHandover").addEventListener("click", completeHandoverOrder);
    bindAppChrome();
    await loadHandoverOrders();
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
      if (route === "inbound-flow" && result.target_id && ENDPOINTS[mode]) {
        state.route = route;
        history.replaceState(null, "", `#/${route}`);
        renderInboundTaskDetailPage(mode, Number(result.target_id));
        return;
      }
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
        ${renderAppHeader(config.title, config.subtitle, {
          action: `<span class="mini-pill">${escapeHtml(currentWarehouseName())}</span>`,
        })}
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
        ${renderBottomNav("operation")}
      </section>
    `;
    document.getElementById("refreshTasks").addEventListener("click", () => loadTasks(mode));
    document.getElementById("completeTask").addEventListener("click", () => completeTask(mode));
    bindAppChrome();
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
      const displayRecords = await enrichTaskCards(mode, records);
      state.activeTasks[mode] = displayRecords;
      if (!records.length) {
        const focusedId = activeTaskId(mode);
        container.innerHTML = `<div class="empty-state">${focusedId ? "正在打开扫码指定任务..." : "暂无待处理任务。"}</div>`;
        if (focusedId) {
          await selectTask(mode, Number(focusedId));
          const focusedTask = state.activeTasks[`${mode}:focusedTask`];
          container.innerHTML = focusedTask
            ? taskCard(focusedTask, true, mode)
            : `<div class="empty-state">当前任务已打开，请在右侧扫码处理。</div>`;
          return;
        }
        detail.innerHTML = `${renderLastResult(mode)}<div class="empty-state">没有需要处理的任务。</div>`;
        return;
      }
      container.innerHTML = displayRecords.map((task) => taskCard(task, activeTaskId(mode) === task.id, mode)).join("");
      container.querySelectorAll("[data-task-detail-id]").forEach((button) => {
        button.addEventListener("click", () => selectTask(mode, Number(button.dataset.taskDetailId)));
      });
      bindTaskActionButtons(container, mode);
      const focusedId = activeTaskId(mode);
      if (focusedId) {
        await selectTask(mode, focusedId);
        return;
      }
      detail.innerHTML = `${renderLastResult(mode)}<div class="empty-state">点击任务里的商品和库位信息查看明细。</div>`;
    } catch (error) {
      container.innerHTML = `<div class="error-state">${escapeHtml(messageOf(error))}</div>`;
      detail.innerHTML = `<div class="hint-state">如果这里是 404，说明当前后端还没有启用该 PDA 接口；H5 页面本身已做好接入。</div>`;
    }
  }

  async function enrichTaskCards(mode, records) {
    return records.map((task) => ({
      ...task,
      card_summary: buildTaskCardSummary(mode, task, []),
    }));
  }

  function buildTaskCardSummary(mode, task, lines) {
    const firstLine = lines[0] || null;
    const lineCount = lines.length || Number(task.line_count || 0);
    const productText = firstLine
      ? `${firstLine.productName || "商品"}${lineCount > 1 ? ` 等 ${lineCount} 种` : ""}`
      : (task.product_summary || task.picking_name || task.outbound_task_name || "");
    const locationText = taskCardLocationText(mode, task, firstLine);
    const qty = taskCardQty(mode, task, lines);
    return {
      productText,
      locationText,
      qtyText: qty.text,
      doneQty: qty.done,
      totalQty: qty.total,
      actionText: taskActionText(mode, task),
    };
  }

  function taskCardLocationText(mode, task, line) {
    if (mode === "arrival") {
      return task.partner_name || task.dest_location || task.receipt_task_name || task.picking_name || "待到货确认";
    }
    if (mode === "inbound_done") {
      return task.dest_location || task.picking_name || "已完成";
    }
    if (mode === "putaway") {
      return task.dest_location || task.source_location || (line && line.location) || "推荐库位待确认";
    }
    if (mode === "pick") {
      return (line && line.location) || task.source_location || task.partner_name || "待拣货库位";
    }
    if (mode === "outbound") {
      return task.partner_name || task.pick_task_name || (line && line.location) || "待复核确认";
    }
    return task.partner_name || task.warehouse_name || task.picking_name || "待收货确认";
  }

  function taskCardQty(mode, task, lines) {
    if (lines.length) {
      const total = lines.reduce((sum, line) => sum + Number(line.demandQty || 0), 0);
      const done = lines.reduce((sum, line) => sum + Number(line.doneQty || 0), 0);
      return { done, total, text: taskQtyLabel(mode, done, total) };
    }
    const done = Number(task.done_qty ?? task.putaway_qty ?? task.total_done_qty ?? task.total_checked_qty ?? 0);
    const total = Number(task.demand_qty ?? task.total_qty ?? task.total_demand_qty ?? task.total_picked_qty ?? 0);
    if (mode === "arrival" && task.arrival_status === "signed") {
      return { done: total, total, text: total ? `已签到 ${formatQty(total)}` : "已签到" };
    }
    if (mode === "arrival" && task.arrival_status === "cancelled") {
      return { done: 0, total, text: total ? `已取消 ${formatQty(total)}` : "已取消" };
    }
    return { done, total, text: taskQtyLabel(mode, done, total) };
  }

  function taskQtyLabel(mode, done, total) {
    const action = {
      arrival: "应到",
      inbound: "应收",
      putaway: "应上架",
      inbound_done: "已上架",
      pick: "应拣",
      outbound: "应复核",
    }[mode] || "数量";
    const pending = Math.max(Number(total || 0) - Number(done || 0), 0);
    if (total) {
      return `${action} ${formatQty(total)}，剩余 ${formatQty(pending)}`;
    }
    return `${action}待确认`;
  }

  function taskActionText(mode, task) {
    if (mode === "arrival" && task && task.arrival_status && task.arrival_status !== "unsigned") {
      return "查看";
    }
    return {
      arrival: "签到",
      inbound: "收货",
      putaway: "确认上架",
      inbound_done: "查看",
      pick: "拣货",
      outbound: "复核",
    }[mode] || "处理";
  }

  async function loadHandoverOrders() {
    const container = document.getElementById("handoverItems");
    const detail = document.getElementById("handoverDetail");
    if (!container || !detail) {
      return;
    }
    container.innerHTML = `<div class="empty-state">正在读取交接单...</div>`;
    setHandoverButtons(false);
    try {
      const data = await apiGet(HANDOVER_ENDPOINTS.list, { limit: 50 });
      const records = getRecords(data);
      state.activeTasks.handover = records;
      if (!records.length) {
        container.innerHTML = `<div class="empty-state">暂无待交接单。</div>`;
        detail.innerHTML = `${renderLastResult("handover")}<div class="empty-state">复核完成后会在这里生成待交接单。</div>`;
        return;
      }
      container.innerHTML = records.map((order) => handoverCard(order, activeTaskId("handover") === order.id)).join("");
      container.querySelectorAll("[data-handover-id]").forEach((button) => {
        button.addEventListener("click", () => selectHandoverOrder(Number(button.dataset.handoverId)));
      });
      const focusedId = activeTaskId("handover");
      if (focusedId) {
        await selectHandoverOrder(focusedId);
        return;
      }
      detail.innerHTML = `${renderLastResult("handover")}<div class="empty-state">点击交接单信息查看明细。</div>`;
    } catch (error) {
      container.innerHTML = `<div class="error-state">${escapeHtml(messageOf(error))}</div>`;
      detail.innerHTML = `<div class="hint-state">交接接口暂不可用时，复核完成结果仍会提示下一步。</div>`;
    }
  }

  function handoverCard(order, active) {
    const name = order.name || `交接单 ${order.id}`;
    const summary = [
      order.partner_name,
      order.route_batch_name,
      order.waybill_names && order.waybill_names.length ? `${order.waybill_names.length} 张运单` : "",
    ].filter(Boolean).join(" · ");
    return `
      <button class="task-card ${active ? "is-active" : ""}" type="button" data-handover-id="${escapeAttr(order.id)}">
        <span class="task-card-top">
          <strong>${escapeHtml(name)}</strong>
          <em class="state-tag ${isDoneState(order.state) ? "is-done" : isExceptionState(order.state) ? "is-error" : ""}">${escapeHtml(statusLabel(order.state))}</em>
        </span>
        <small>${escapeHtml(summary || order.outbound_task_name || "交接出库")}</small>
        ${order.create_date ? `<small class="task-progress">创建 ${escapeHtml(String(order.create_date).slice(0, 16))}</small>` : ""}
      </button>
    `;
  }

  async function selectHandoverOrder(orderId) {
    const detail = document.getElementById("handoverDetail");
    state.activeTasks["handover:id"] = orderId;
    document.querySelectorAll("[data-handover-id]").forEach((card) => {
      card.classList.toggle("is-active", Number(card.dataset.handoverId) === orderId);
    });
    detail.innerHTML = `<div class="empty-state">正在读取交接明细...</div>`;
    setHandoverButtons(false);
    try {
      const data = await apiGet(HANDOVER_ENDPOINTS.detail(orderId));
      const order = data.order || findTask("handover", orderId) || {};
      state.activeTasks["handover:focusedTask"] = order;
      detail.innerHTML = renderHandoverDetail(order);
      setHandoverButtons(order && order.state !== "handover_done");
    } catch (error) {
      detail.innerHTML = `<div class="error-state">${escapeHtml(messageOf(error))}</div>`;
    }
  }

  function renderHandoverDetail(order) {
    const title = order.name || `交接单 ${order.id || ""}`;
    const waybills = Array.isArray(order.waybills) ? order.waybills : [];
    const stopLines = order.route_batch && Array.isArray(order.route_batch.stop_lines) ? order.route_batch.stop_lines : [];
    return `
      ${renderLastResult("handover")}
      <div class="scan-box">
        <h2>${escapeHtml(title)}</h2>
        <div class="info-grid">
          ${infoItem("客户/门店", order.partner_name)}
          ${infoItem("出库任务", order.outbound_task_name)}
          ${infoItem("复核任务", order.check_task_name)}
          ${infoItem("拣货任务", order.pick_task_name)}
          ${infoItem("司机", order.driver_profile_name)}
          ${infoItem("车辆", order.vehicle_profile_name)}
          ${infoItem("重量", order.weight_total ? `${formatQty(order.weight_total)} kg` : "")}
          ${infoItem("体积", order.volume_total ? `${formatQty(order.volume_total)} m3` : "")}
        </div>
      </div>
      <div class="line-grid">
        <article class="line-card">
          <div>
            <strong>关联运单</strong>
            <small>${escapeHtml((order.waybill_names || []).join(" · ") || "暂无运单信息")}</small>
          </div>
          <div class="qty">${escapeHtml(String((order.waybill_names || []).length || waybills.length || 0))}</div>
        </article>
        ${stopLines.length ? stopLines.map((line) => `
          <article class="line-card">
            <div>
              <strong>${escapeHtml(line.waybill_no || line.name || "线路停靠")}</strong>
              <small>${escapeHtml([line.store_name, line.address_detail, line.cargo_summary].filter(Boolean).join(" · "))}</small>
            </div>
            <div class="qty">${escapeHtml(line.stop_seq || "-")}</div>
          </article>
        `).join("") : ""}
      </div>
      ${order.note ? `<div class="hint-state">${escapeHtml(order.note)}</div>` : ""}
    `;
  }

  function infoItem(label, value) {
    return `
      <div class="info-item">
        <span>${escapeHtml(label)}</span>
        <strong>${escapeHtml(value || "-")}</strong>
      </div>
    `;
  }

  async function confirmHandoverOrder() {
    const orderId = activeTaskId("handover");
    const button = document.getElementById("startHandover");
    if (!orderId || !button) {
      return;
    }
    try {
      button.disabled = true;
      const result = await apiPost(HANDOVER_ENDPOINTS.confirm(orderId), {
        request_id: requestId("handover_confirm"),
        device_id: state.deviceId,
      });
      rememberResult("handover", "已开始交接", result);
      showToast("已开始交接");
      await selectHandoverOrder(orderId);
    } catch (error) {
      showError(error);
    } finally {
      button.disabled = false;
    }
  }

  async function completeHandoverOrder() {
    const orderId = activeTaskId("handover");
    const button = document.getElementById("completeHandover");
    if (!orderId || !button) {
      return;
    }
    try {
      button.disabled = true;
      const result = await apiPost(HANDOVER_ENDPOINTS.complete(orderId), {
        request_id: requestId("handover_complete"),
        device_id: state.deviceId,
      });
      rememberResult("handover", "交接已完成", result);
      showToast("交接已完成");
      state.activeTasks["handover:id"] = "";
      await loadHandoverOrders();
    } catch (error) {
      showError(error);
    } finally {
      button.disabled = false;
    }
  }

  function setHandoverButtons(enabled) {
    ["startHandover", "completeHandover"].forEach((id) => {
      const button = document.getElementById(id);
      if (button) {
        button.disabled = !enabled;
      }
    });
  }

  function taskCard(task, active, mode) {
    const name = task.name || task.picking_name || task.outbound_task_name || `任务 ${task.id}`;
    const summary = task.card_summary || buildTaskCardSummary(mode, task, []);
    const status = task.state || "";
    return `
      <article class="task-card app-task-card ${active ? "is-active" : ""}" data-task-card-id="${escapeAttr(task.id)}">
        <button class="app-task-main task-info-button" type="button" data-task-detail-id="${escapeAttr(task.id)}" aria-label="查看任务明细">
          <strong>${escapeHtml(name)}</strong>
          ${status ? `<em class="state-tag ${isDoneState(status) ? "is-done" : isExceptionState(status) ? "is-error" : ""}">${escapeHtml(statusLabel(status))}</em>` : ""}
          <small>${escapeHtml(summary.productText || "待执行任务")}</small>
          <small>${escapeHtml(summary.locationText || "请扫码处理")}</small>
          <small class="task-progress">${escapeHtml(summary.qtyText || taskProgressText(task) || "数量待确认")}</small>
        </button>
        ${taskActionButtons(mode, task, summary)}
      </article>
    `;
  }

  function taskActionButtons(mode, task, summary) {
    const actionText = summary.actionText || taskActionText(mode);
    if (mode === "arrival" && (task.arrival_status || state.arrivalStatus) === "unsigned") {
      return `
        <div class="task-action-group">
          <button class="task-action-chip is-secondary" type="button" data-arrival-cancel-id="${escapeAttr(task.id)}">取消</button>
          <button class="task-action-chip" type="button" data-task-action-id="${escapeAttr(task.id)}" data-task-action-mode="${escapeAttr(mode)}">${escapeHtml(actionText)}</button>
        </div>
      `;
    }
    return `
      <button class="task-action-chip" type="button" data-task-action-id="${escapeAttr(task.id)}" data-task-action-mode="${escapeAttr(mode)}">
        ${escapeHtml(actionText)}
      </button>
    `;
  }

  function bindTaskActionButtons(container, mode) {
    container.querySelectorAll("[data-task-action-id]").forEach((button) => {
      button.addEventListener("click", () => handleTaskCardAction(button, mode));
    });
    container.querySelectorAll("[data-arrival-cancel-id]").forEach((button) => {
      button.addEventListener("click", () => cancelArrivalTask(Number(button.dataset.arrivalCancelId), button));
    });
  }

  async function cancelArrivalTask(taskId, sourceButton) {
    if (!taskId) {
      return;
    }
    if (!window.confirm("确认取消当前到货单？取消后会进入已取消列表。")) {
      return;
    }
    const button = sourceButton || document.getElementById("cancelArrivalTask");
    try {
      if (button) {
        button.disabled = true;
      }
      const result = await apiPost(ENDPOINTS.arrival.cancel(taskId), {
        request_id: requestId("arrival_cancel"),
        device_id: state.deviceId,
      });
      rememberResult("arrival", "到货已取消", result);
      showToast("到货已取消");
      state.flowModes["inbound-flow"] = "arrival";
      state.arrivalStatus = "cancelled";
      await renderInboundFlowPage("inbound-flow", FLOW_GROUPS["inbound-flow"]);
    } catch (error) {
      showError(error);
      if (button) {
        button.disabled = false;
      }
    }
  }

  async function handleTaskCardAction(button, mode) {
    const taskId = Number(button.dataset.taskActionId || 0);
    if (!taskId) {
      return;
    }
    const task = findTask(mode, taskId) || {};
    if (mode === "arrival") {
      if ((task.arrival_status || state.arrivalStatus) === "unsigned") {
        state.activeTasks[`${mode}:id`] = taskId;
        try {
          button.disabled = true;
          await completeTask(mode);
        } finally {
          button.disabled = false;
        }
        return;
      }
      renderInboundTaskDetailPage(mode, taskId);
      return;
    }
    if (["inbound", "putaway", "inbound_done"].includes(mode)) {
      renderInboundTaskDetailPage(mode, taskId);
      return;
    }
    await selectTask(mode, taskId);
  }

  async function selectTask(mode, taskId) {
    const config = ENDPOINTS[mode];
    const detail = document.getElementById("detailBody");
    state.activeTasks[`${mode}:id`] = taskId;
    document.querySelectorAll(".task-card").forEach((card) => {
      card.classList.toggle("is-active", Number(card.dataset.taskCardId) === taskId);
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
    return `
      ${renderLastResult(mode)}
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
      const result = await apiPost(config.confirm(taskId), payload);
      rememberResult(mode, "本行已确认", result);
      showToast("本行已确认");
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
      if (button) {
        button.disabled = true;
      }
      if (!config.complete) {
        throw new Error("当前状态不需要提交完成。");
      }
      const result = await apiPost(config.complete(taskId), {
        request_id: requestId(`${mode}_complete`),
        device_id: state.deviceId,
      });
      const successText = {
        arrival: "到货已签到",
        inbound: "收货已完成",
        putaway: "上架已完成",
      }[mode] || "任务已完成";
      rememberResult(mode, successText, result);
      showToast(successText);
      state.activeTasks[`${mode}:id`] = "";
      if (mode === "arrival") {
        state.flowModes["inbound-flow"] = "arrival";
        state.arrivalStatus = "signed";
        await renderInboundFlowPage("inbound-flow", FLOW_GROUPS["inbound-flow"]);
        return;
      }
      if (state.route === "inbound-flow" || ["arrival", "inbound", "putaway"].includes(mode)) {
        const nextMode = {
          inbound: "putaway",
          putaway: "inbound_done",
        }[mode];
        if (nextMode) {
          state.flowModes["inbound-flow"] = nextMode;
          await renderInboundFlowPage("inbound-flow", FLOW_GROUPS["inbound-flow"]);
          return;
        }
      }
      await loadTasks(mode);
    } catch (error) {
      showError(error);
    } finally {
      if (button) {
        button.disabled = false;
      }
    }
  }

  function rememberResult(mode, title, result) {
    state.lastResults[mode] = {
      title,
      result: result || {},
      time: new Date().toLocaleTimeString("zh-CN", { hour12: false }),
    };
  }

  function renderLastResult(mode) {
    const entry = state.lastResults[mode];
    if (!entry) {
      return "";
    }
    const result = entry.result || {};
    const order = result.order || {};
    const task = result.task || {};
    const summary = result.summary || {};
    const stateValue = result.task_state || result.operation_state || task.state || order.state || result.state || "";
    const fields = [
      ["状态", statusLabel(stateValue) || operationStateLabel(stateValue)],
      ["下一步", nextStepLabel(result.next_step)],
      ["生成上架任务", formatIdList(result.putaway_task_ids)],
      ["生成交接单", formatIdList(result.handover_order_ids)],
      ["明细行数", summary.line_count ?? summary.done_line_count],
      ["数量合计", summary.total_qty ?? summary.done_qty ?? summary.checked_qty],
      ["单据", task.name || order.name || result.operation_name || result.name],
    ].filter(([, value]) => value !== undefined && value !== null && value !== "");
    return `
      <div class="result-card is-success">
        <div class="result-card-head">
          <strong>${escapeHtml(entry.title)}</strong>
          <span>${escapeHtml(entry.time)}</span>
        </div>
        ${fields.length ? `
          <div class="result-grid">
            ${fields.map(([label, value]) => `
              <div>
                <span>${escapeHtml(label)}</span>
                <strong>${escapeHtml(formatResultValue(value))}</strong>
              </div>
            `).join("")}
          </div>
        ` : `<small>接口已返回成功。</small>`}
      </div>
    `;
  }

  function formatIdList(value) {
    return Array.isArray(value) && value.length ? value.join(", ") : "";
  }

  function formatResultValue(value) {
    if (typeof value === "number") {
      return formatQty(value);
    }
    if (Array.isArray(value)) {
      return value.join(", ");
    }
    return value;
  }

  function nextStepLabel(value) {
    const labels = {
      receipt: "进入待收货",
      putaway: "进入待上架",
      check: "进入待复核",
      handover: "进入待交接",
      dispatch: "进入配送/TMS",
      done: "已完成",
    };
    return labels[value] || value || "";
  }

  function operationStateLabel(value) {
    return OPERATION_STATE_LABELS[value] || value || "";
  }

  function statusLabel(stateValue) {
    return STATUS_LABELS[stateValue] || stateValue || "";
  }

  function isDoneState(stateValue) {
    return ["received", "putaway_done", "picked", "checked", "handover_done"].includes(stateValue);
  }

  function isExceptionState(stateValue) {
    return String(stateValue || "").includes("exception");
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
    const qtyText = `${formatQty(line.doneQty)} / ${formatQty(line.demandQty)} ${displayUom(line.uom) || ""}`;
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
        ${renderAppHeader("调拨补货", "处理调拨下架、仓内移库和补货上架，扫码生成内部调拨。", {
          action: `<span class="mini-pill">${escapeHtml(currentWarehouseName())}</span>`,
        })}
        <div class="workflow-strip workflow-strip-short">
          ${["建单", "扫库位", "扫商品", "提交"].map((label, index) => `
            <span class="${operation ? index < 2 ? "is-done" : index === 2 ? "is-current" : "" : index === 0 ? "is-current" : ""}">
              <i>${escapeHtml(index + 1)}</i><b>${escapeHtml(label)}</b>
            </span>
          `).join("")}
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
        ${renderBottomNav("operation")}
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
    bindAppChrome();
  }

  function renderDownShelfCreateForm() {
    return `
      <form id="downShelfCreateForm" class="scan-box" autocomplete="off">
        <h2>创建调拨补货作业</h2>
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
        ${renderAppHeader("库存库位", "按商品、库位两种视角查询现存、锁定和可用库存。", {
          action: `<span class="mini-pill">${escapeHtml(currentWarehouseName())}</span>`,
        })}
        <div class="workflow-strip workflow-strip-short">
          ${["扫码", "查询", "调拨", "复核"].map((label, index) => `
            <span class="${index === 0 ? "is-current" : ""}">
              <i>${escapeHtml(index + 1)}</i><b>${escapeHtml(label)}</b>
            </span>
          `).join("")}
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
        ${renderBottomNav("operation")}
      </section>
    `;
    root.querySelectorAll("[data-mode]").forEach((button) => {
      button.addEventListener("click", () => {
        state.inventoryMode = button.dataset.mode;
        renderInventory();
      });
    });
    document.getElementById("inventoryForm").addEventListener("submit", submitInventory);
    bindAppChrome();
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
        <td>${escapeHtml(displayUom(item.uom || item.product_uom) || "")}</td>
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
    const last = state.exceptionLastDraft;
    root.innerHTML = `
      <section class="task-panel">
        ${renderAppHeader("盘点异常", "现场先记录证据，再进入主管审核。", {
          action: `<span class="mini-pill">${escapeHtml(currentWarehouseName())}</span>`,
        })}
        <div class="workflow-strip workflow-strip-short">
          ${["发现", "记录", "审核", "处理"].map((label, index) => `
            <span class="${last ? index < 2 ? "is-done" : index === 2 ? "is-current" : "" : index === 1 ? "is-current" : ""}">
              <i>${escapeHtml(index + 1)}</i><b>${escapeHtml(label)}</b>
            </span>
          `).join("")}
        </div>
        <div class="metric-grid">
          ${[
            ["待处理异常", "0", "后端审核接口待接入"],
            ["盘点任务", "预留", "按库位/商品盘点"],
            ["报损禁售", "预留", "破损、临期、禁售"],
            ["主管审核", "预留", "异常闭环状态"],
          ].map(([title, value, desc]) => `
            <article class="metric-card">
              <strong>${escapeHtml(value)}</strong>
              <span>${escapeHtml(title)}</span>
              <small>${escapeHtml(desc)}</small>
            </article>
          `).join("")}
        </div>
        <form id="exceptionForm" class="scan-box" autocomplete="off">
          <h2>记录现场异常</h2>
          <div class="scan-form">
            <label class="field">
              <span>异常类型</span>
              <select class="text-input" name="type">
                <option value="qty_mismatch">数量不符</option>
                <option value="damaged">破损报损</option>
                <option value="location_mismatch">库位不符</option>
                <option value="shortage">缺货少货</option>
                <option value="handover_failed">交接失败</option>
                <option value="forbidden_sale">禁售/冻结</option>
              </select>
            </label>
            <label class="field">
              <span>关联任务/单据</span>
              <input class="text-input" name="reference" type="text" inputmode="text" placeholder="任务号或单据号" />
            </label>
            <label class="field">
              <span>商品条码</span>
              <input class="text-input" name="product_barcode" type="text" inputmode="text" placeholder="扫描商品" />
            </label>
            <label class="field">
              <span>库位条码</span>
              <input class="text-input" name="location_barcode" type="text" inputmode="text" placeholder="扫描库位" />
            </label>
            <label class="field">
              <span>异常数量</span>
              <input class="qty-input" name="qty" type="number" min="0" step="0.001" inputmode="decimal" placeholder="数量" />
            </label>
            <label class="field">
              <span>图片证据</span>
              <input class="text-input" name="photo_note" type="text" inputmode="text" placeholder="先记录照片编号/说明" />
            </label>
            <label class="field full-row">
              <span>现场说明</span>
              <input class="text-input" name="note" type="text" inputmode="text" placeholder="描述原因、处理建议或责任环节" />
            </label>
            <button class="primary-button full-row" type="submit">记录异常</button>
          </div>
        </form>
        <div id="exceptionResult">
          ${last ? renderExceptionDraft(last) : `<div class="hint-state">当前为前端记录页，后续接入异常提交接口后会进入主管审核队列。</div>`}
        </div>
        ${renderBottomNav("operation")}
      </section>
    `;
    document.getElementById("exceptionForm").addEventListener("submit", submitExceptionDraft);
    bindAppChrome();
    focusFirst("#exceptionForm select");
  }

  function submitExceptionDraft(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries());
    state.exceptionLastDraft = {
      type: exceptionTypeLabel(data.type),
      reference: (data.reference || "").trim(),
      productBarcode: (data.product_barcode || "").trim(),
      locationBarcode: (data.location_barcode || "").trim(),
      qty: data.qty,
      photoNote: (data.photo_note || "").trim(),
      note: (data.note || "").trim(),
      time: new Date().toLocaleString("zh-CN", { hour12: false }),
    };
    document.getElementById("exceptionResult").innerHTML = renderExceptionDraft(state.exceptionLastDraft);
    form.reset();
    showToast("异常已记录，等待后端审核接口接入");
  }

  function renderExceptionDraft(item) {
    const details = [
      item.reference ? `任务/单据：${item.reference}` : "",
      item.productBarcode ? `商品：${item.productBarcode}` : "",
      item.locationBarcode ? `库位：${item.locationBarcode}` : "",
      item.qty ? `数量：${formatQty(item.qty)}` : "",
      item.photoNote ? `证据：${item.photoNote}` : "",
      item.note ? `说明：${item.note}` : "",
    ].filter(Boolean).join(" · ");
    return `
      <div class="result-card">
        <div class="result-card-head">
          <strong>${escapeHtml(item.type)}</strong>
          <span>${escapeHtml(item.time)}</span>
        </div>
        <small>${escapeHtml(details || "已记录现场异常。")}</small>
      </div>
    `;
  }

  function exceptionTypeLabel(value) {
    const labels = {
      qty_mismatch: "数量不符",
      damaged: "破损报损",
      location_mismatch: "库位不符",
      shortage: "缺货少货",
      handover_failed: "交接失败",
      forbidden_sale: "禁售/冻结",
    };
    return labels[value] || value || "现场异常";
  }

  async function switchWarehouse() {
    await switchWarehouseById(warehouseSelect.value);
  }

  async function switchWarehouseById(warehouseId) {
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
      if (warehouseSelect) {
        warehouseSelect.value = String(state.warehouseId);
      }
      const mineWarehouse = document.getElementById("mineWarehouseSelect");
      if (mineWarehouse) {
        mineWarehouse.value = String(state.warehouseId);
      }
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
        uom: displayUom(line.uom),
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
    if (Array.isArray(data.tasks)) {
      return data.tasks;
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

  function displayUom(value) {
    const text = String(value || "").trim();
    if (!text) {
      return "";
    }
    if (/^units?$/i.test(text)) {
      return "份";
    }
    return text;
  }

  function formatDateTime(value) {
    if (!value) {
      return "";
    }
    const raw = String(value).replace("T", " ").slice(0, 19);
    const [datePart, timePart = ""] = raw.split(" ");
    return `${datePart.replace(/-/g, "/")}${timePart ? ` ${timePart}` : ""}`;
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
