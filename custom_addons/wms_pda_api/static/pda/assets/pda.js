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
        { mode: "putaway", label: "上架", hint: "扫商品与目标库位，确认上架" },
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
      "outbound-flow": "claim",
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
    outboundSearch: "",
    outboundCounts: {},
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

  function resetPageScroll() {
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;
    if (root) {
      root.scrollTop = 0;
    }
    window.scrollTo(0, 0);
    requestAnimationFrame(() => window.scrollTo(0, 0));
  }

  function render() {
    syncChrome();
    resetPageScroll();
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

  function ensureDynamicPdaStyles() {
    if (document.getElementById("pda-dynamic-outbound-style")) {
      return;
    }
    const style = document.createElement("style");
    style.id = "pda-dynamic-outbound-style";
    style.textContent = `
      .mobile-scan-host{position:relative}
      .mobile-scan-input{padding-right:54px!important}
      .mobile-scan-button{position:absolute;right:8px;top:50%;display:inline-grid;place-items:center;width:38px;height:38px;border:1px solid #dbe7f2;border-radius:13px;background:linear-gradient(180deg,#fff 0%,#f1f5f9 100%);color:#0f172a;transform:translateY(-50%);box-shadow:0 4px 10px rgba(15,23,42,.06)}
      .mobile-scan-button svg{width:22px;height:22px;stroke:currentColor;stroke-width:2.4;fill:none;stroke-linecap:round;stroke-linejoin:round}
      .mobile-scan-button:active{background:#ffc72c;border-color:#ffc72c;color:#111827;transform:translateY(-50%) scale(.96)}
      .mobile-scan-button::after{content:"";position:absolute;inset:8px;border-radius:7px;background:rgba(255,199,44,.13);opacity:0;transition:opacity .15s ease}
      .mobile-scan-button:active::after{opacity:1}
      .field.mobile-scan-host .mobile-scan-button{top:auto;bottom:8px;transform:none}
      .outbound-status-tabs{grid-template-columns:repeat(5,minmax(0,1fr));margin:0 -8px 12px;border:0;border-radius:0;overflow-x:auto;scrollbar-width:none}
      .outbound-status-tabs::-webkit-scrollbar{display:none}
      .outbound-status-tab{min-width:88px;min-height:62px;font-size:18px}
      .outbound-search.mobile-scan-host .mobile-scan-button{right:56px;width:38px;height:38px;border-radius:999px;background:#fff}
      .outbound-filter-row{display:flex;justify-content:flex-end;gap:16px;margin:-4px 0 16px;padding:0 4px}
      .outbound-filter-row button{border:0;background:transparent;color:#374151;font-size:14px;font-weight:900}
      .outbound-filter-panel{display:grid;gap:12px;margin:-6px 0 14px;padding:14px;border:1px solid #e4ebf2;border-radius:18px;background:#fff;box-shadow:0 14px 28px rgba(15,23,42,.08)}
      .outbound-filter-panel[hidden]{display:none}
      .outbound-filter-section{display:grid;gap:8px}
      .outbound-filter-section strong{color:#0f172a;font-size:14px;font-weight:900}
      .outbound-filter-section div{display:flex;flex-wrap:wrap;gap:8px}
      .outbound-filter-section button,.outbound-filter-reset{min-height:36px;border:1px solid #dbe7f2;border-radius:999px;background:#f8fafc;color:#334155;font-size:13px;font-weight:900;padding:0 13px}
      .outbound-filter-section button.is-active{border-color:#ffc72c;background:#fff4d6;color:#9a5b00}
      .outbound-filter-reset{justify-self:end;background:#fff;color:#64748b}
      .outbound-card-list{gap:12px}
      .outbound-card{border-radius:6px;box-shadow:none}
      .outbound-card-main{gap:7px;padding:18px 16px 10px}
      .outbound-card-head em{min-width:48px;min-height:28px;padding:0 7px;border-radius:2px}
      .outbound-card-head strong{font-size:22px}
      .outbound-card-row,.outbound-card-product,.outbound-card-progress{display:block;color:#6b7280;font-size:14px;font-weight:800;line-height:1.45;overflow-wrap:anywhere}
      .outbound-card-row b{color:#4b5563;font-weight:800}
      .outbound-card-collect{color:#d9691d;font-size:17px}
      .outbound-card-divider{display:block;height:1px;margin:6px 0 4px;background:#edf2f7}
      .outbound-card-product{color:#374151;font-size:18px;font-weight:900}
      .outbound-card-progress{color:#4b5563;font-size:18px}
      .outbound-card-foot button,.outbound-handover-actions .primary-button{min-width:86px;min-height:48px;border:0;border-radius:0;background:#ffd900;color:#111827;font-size:17px;font-weight:900;box-shadow:none}
      .arrival-scan-sign{display:grid;gap:12px;margin:0 0 14px;padding:14px;border:1px solid #dbe7f2;border-radius:18px;background:linear-gradient(180deg,#fff 0%,#f8fbff 100%);box-shadow:0 10px 24px rgba(15,23,42,.06)}
      .arrival-scan-sign-title{display:flex;align-items:center;justify-content:space-between;gap:10px}
      .arrival-scan-sign strong{display:block;color:#0f172a;font-size:17px;font-weight:900}
      .arrival-scan-sign small{display:block;color:#64748b;font-size:12px;font-weight:800}
      .arrival-scan-badge{display:inline-grid;place-items:center;min-width:46px;height:26px;border-radius:999px;background:#fff4d6;color:#a45a00;font-size:12px;font-weight:900}
      .arrival-scan-sign form{display:grid;grid-template-columns:minmax(0,1fr)88px;gap:10px;align-items:center}
      .arrival-scan-sign input{width:100%;min-width:0;height:50px;border:1px solid #d8e4ef;border-radius:16px;background:#fff;color:#102033;font-size:16px;font-weight:800;outline:none;padding:0 14px;box-shadow:inset 0 1px 0 rgba(15,23,42,.02)}
      .arrival-scan-sign button[type=submit]{height:50px;border:0;border-radius:16px;background:#ffc72c;color:#111827;font-size:16px;font-weight:900;box-shadow:0 8px 16px rgba(255,199,44,.22)}
      .arrival-scan-sign form.mobile-scan-host .mobile-scan-button{right:104px}
      .camera-scan-mask{position:fixed;inset:0;z-index:9999;display:grid;place-items:center;background:rgba(15,23,42,.72);padding:18px}
      .camera-scan-sheet{width:min(430px,100%);border-radius:22px;background:#0f172a;color:#fff;overflow:hidden;box-shadow:0 24px 60px rgba(0,0,0,.32)}
      .camera-scan-head{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 16px;background:#111827}
      .camera-scan-head strong{font-size:17px;font-weight:900}
      .camera-scan-close{width:38px;height:38px;border:0;border-radius:999px;background:rgba(255,255,255,.12);color:#fff;font-size:24px;line-height:1}
      .camera-scan-view{position:relative;aspect-ratio:3/4;background:#020617}
      .camera-scan-view video{width:100%;height:100%;object-fit:cover}
      .camera-scan-frame{position:absolute;left:50%;top:50%;width:72%;aspect-ratio:1;border:3px solid #ffc72c;border-radius:22px;transform:translate(-50%,-50%);box-shadow:0 0 0 999px rgba(0,0,0,.28)}
      .camera-scan-frame::after{content:"";position:absolute;left:12%;right:12%;top:50%;height:2px;background:#24c07a;box-shadow:0 0 14px rgba(36,192,122,.9);animation:scanLine 1.4s ease-in-out infinite alternate}
      @keyframes scanLine{from{transform:translateY(-70px)}to{transform:translateY(70px)}}
      .camera-scan-tip{padding:13px 16px;color:#cbd5e1;font-size:13px;font-weight:800;line-height:1.5}
      .camera-scan-error{padding:14px 16px;color:#fecaca;background:#450a0a;font-size:13px;font-weight:900;line-height:1.5}
      .camera-scan-actions{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:12px 16px 16px}
      .camera-scan-actions button,.camera-scan-actions label{display:grid;place-items:center;min-height:44px;border:1px solid rgba(255,255,255,.16);border-radius:14px;background:rgba(255,255,255,.08);color:#fff;font-size:14px;font-weight:900}
      .camera-scan-actions label{background:#ffc72c;color:#111827}
      .camera-scan-actions input{display:none}
      .claim-task-mask{position:fixed;inset:0;z-index:9998;display:grid;place-items:end center;background:rgba(15,23,42,.42);padding:16px}
      .claim-task-sheet{width:min(430px,100%);display:grid;gap:14px;border-radius:22px;background:#fff;padding:18px;box-shadow:0 24px 60px rgba(15,23,42,.24)}
      .claim-task-head{display:flex;align-items:start;justify-content:space-between;gap:12px}
      .claim-task-head strong{display:block;color:#0f172a;font-size:20px;font-weight:900}
      .claim-task-head small{display:block;margin-top:4px;color:#64748b;font-size:13px;font-weight:800;line-height:1.4}
      .claim-task-close{width:38px;height:38px;border:0;border-radius:999px;background:#f1f5f9;color:#334155;font-size:24px;line-height:1}
      .claim-task-form{display:grid;gap:12px}
      .claim-task-form label{display:grid;gap:6px;color:#475569;font-size:13px;font-weight:900}
      .claim-task-form input{height:48px;border:1px solid #dbe7f2;border-radius:14px;background:#f8fafc;color:#0f172a;font-size:16px;font-weight:800;padding:0 12px;outline:none}
      .claim-task-actions{display:grid;grid-template-columns:1fr 1.4fr;gap:10px}
      .claim-task-actions button{height:48px;border-radius:14px;font-size:16px;font-weight:900}
      .claim-task-cancel{border:1px solid #dbe7f2;background:#fff;color:#334155}
      .claim-task-submit{border:0;background:#ffc72c;color:#111827}
      .task-panel{background:linear-gradient(180deg,#f6f9fc 0%,#eef4f8 100%)}
      .outbound-page,.receipt-page,.inventory-page{background:linear-gradient(180deg,#f6f9fc 0%,#eef4f8 100%)}
      .outbound-search{position:relative;align-items:center;min-height:60px;margin:4px 0 14px;padding:5px;border:1px solid #dbe7f2;border-radius:24px;background:#fff;box-shadow:0 12px 26px rgba(15,23,42,.06)}
      .outbound-search input{height:48px;padding:0 104px 0 18px;border-radius:18px;color:#172033;font-size:16px;font-weight:900}
      .outbound-search input::placeholder{color:#8793a3;font-weight:900}
      .outbound-search button[type=submit]{position:absolute;right:8px;top:50%;width:44px;height:44px;margin:0;border-radius:16px;background:#f1f5f9;color:#0f172a;font-size:0;transform:translateY(-50%);box-shadow:none}
      .outbound-search button[type=submit]::before{content:"";width:16px;height:16px;border:2.5px solid currentColor;border-radius:999px}
      .outbound-search button[type=submit]::after{content:"";position:absolute;width:8px;height:2.5px;border-radius:999px;background:currentColor;transform:translate(9px,9px) rotate(45deg)}
      .outbound-search.mobile-scan-host .mobile-scan-button{right:58px;top:50%;width:44px;height:44px;border:0;border-radius:16px;background:#f8fafc;box-shadow:inset 0 0 0 1px #e2e8f0;transform:translateY(-50%)}
      .outbound-search.mobile-scan-host .mobile-scan-button:active{transform:translateY(-50%) scale(.96)}
      .mobile-scan-button{overflow:hidden}
      .mobile-scan-button svg{position:relative;z-index:1}
      .field .text-input,.field .qty-input,.field input,.arrival-scan-sign input,.claim-task-form input{border-color:#d8e4ef;background:#fff;box-shadow:inset 0 1px 0 rgba(15,23,42,.03),0 8px 18px rgba(15,23,42,.035)}
      .field .text-input:focus,.field .qty-input:focus,.field input:focus,.arrival-scan-sign input:focus,.claim-task-form input:focus,.outbound-search input:focus{border-color:#ffc72c;box-shadow:0 0 0 3px rgba(255,199,44,.18),0 10px 22px rgba(15,23,42,.06);outline:none}
      .outbound-card,.outbound-work-summary,.outbound-progress-card,.outbound-line-card,.arrival-scan-sign,.claim-task-sheet{box-shadow:0 14px 30px rgba(15,23,42,.07)}
      .outbound-card{border:1px solid #e4ebf2;border-radius:18px}
      .outbound-card-foot button,.outbound-handover-actions .primary-button{border-radius:14px;background:linear-gradient(180deg,#ffda54 0%,#ffc72c 100%);box-shadow:0 8px 16px rgba(255,199,44,.22)}
      .outbound-filter-row{align-items:center;justify-content:flex-start;gap:8px;overflow-x:auto;padding-bottom:2px}
      .outbound-filter-row button{white-space:nowrap;min-height:34px;padding:0 12px;border:1px solid #dbe7f2;border-radius:999px;background:#fff;color:#334155;box-shadow:0 5px 12px rgba(15,23,42,.04)}
      .receipt-nav,.outbound-nav{border-bottom:1px solid rgba(219,231,242,.8)}
      .toast,.app-toast{bottom:104px!important;z-index:10020!important}
      .outbound-fallback-confirm{height:48px;border:0;border-radius:14px;background:#ffc72c;color:#111827;font-size:16px;font-weight:900;box-shadow:0 8px 16px rgba(255,199,44,.22)}
    `;
    document.head.appendChild(style);
  }

  function enhanceArrivalScanSign(scope) {
    const container = scope || root || document;
    if (!state.flowModes || state.flowModes["inbound-flow"] !== "arrival") {
      return;
    }
    if (!location.hash.includes("inbound-flow")) {
      return;
    }
    if (container.querySelector(".arrival-scan-sign")) {
      return;
    }
    const panel = container.querySelector(".task-panel") || container;
    const scanBox = document.createElement("div");
    scanBox.className = "arrival-scan-sign";
    scanBox.innerHTML = `
      <div>
        <div class="arrival-scan-sign-title">
          <strong>扫码签到</strong>
          <span class="arrival-scan-badge">到货</span>
        </div>
        <small>扫到货单号、物流单号或供应商单号。</small>
      </div>
      <form id="arrivalScanSignForm" autocomplete="off">
        <input id="arrivalScanSignInput" type="search" inputmode="text" placeholder="扫码或输入单号" />
        <button type="submit">签到</button>
      </form>
    `;
    const anchor = panel.querySelector(".receipt-sub-tabs, .inbound-sub-tabs, .arrival-status-tabs, .outbound-status-tabs, .flow-tabs");
    if (anchor && anchor.parentElement) {
      anchor.insertAdjacentElement("afterend", scanBox);
    } else {
      panel.insertBefore(scanBox, panel.children[2] || null);
    }
    const form = scanBox.querySelector("#arrivalScanSignForm");
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      submitArrivalScanSign((scanBox.querySelector("#arrivalScanSignInput") || {}).value || "");
    });
  }

  function submitArrivalScanSign(value) {
    const code = String(value || "").trim().toLowerCase();
    if (!code) {
      showToast("请先扫描或输入到货单号", true);
      return;
    }
    const signText = /签到|确认到货|到货确认/;
    const ignoredText = /已签到|取消|已取消|查看/;
    const cards = Array.from(root.querySelectorAll("article, .receipt-card, .inbound-card, .task-card, .arrival-card, [data-task-id], [data-arrival-id]"));
    const matchedCard = cards.find((card) => {
      const text = (card.textContent || "").toLowerCase();
      return text.includes(code) && Array.from(card.querySelectorAll("button")).some((button) => signText.test(button.textContent || "") && !ignoredText.test(button.textContent || ""));
    });
    const findButton = (scope) => Array.from(scope.querySelectorAll("button")).find((button) => signText.test(button.textContent || "") && !ignoredText.test(button.textContent || "") && !button.disabled);
    const matchedButton = matchedCard ? findButton(matchedCard) : null;
    const allSignButtons = Array.from(root.querySelectorAll("button")).filter((button) => signText.test(button.textContent || "") && !ignoredText.test(button.textContent || "") && !button.disabled);
    const fallbackButton = allSignButtons.length === 1 ? allSignButtons[0] : null;
    const button = matchedButton || fallbackButton;
    if (!button) {
      showToast("未匹配到可签到任务，请切到未签到列表后再扫", true);
      return;
    }
    button.click();
    const input = document.getElementById("arrivalScanSignInput");
    if (input) {
      input.value = "";
    }
    showToast("已匹配任务，正在签到");
  }

  function scannerFormats() {
    return [
      "qr_code",
      "code_128",
      "code_39",
      "code_93",
      "ean_13",
      "ean_8",
      "upc_a",
      "upc_e",
      "data_matrix",
      "itf",
    ];
  }

  function applyScannedValue(input, value) {
    if (!input || !value) {
      return;
    }
    input.value = value;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
    if (input.form) {
      input.form.dispatchEvent(new Event("input", { bubbles: true }));
    }
    input.focus();
    showToast(`已扫码：${value}`);
  }

  function closeMobileScanner() {
    const scanner = state.mobileScanner;
    if (scanner && scanner.stream) {
      scanner.stream.getTracks().forEach((track) => track.stop());
    }
    if (scanner && scanner.frame) {
      cancelAnimationFrame(scanner.frame);
    }
    const mask = document.getElementById("cameraScanMask");
    if (mask) {
      mask.remove();
    }
    state.mobileScanner = null;
  }

  async function openMobileScanner(input) {
    closeMobileScanner();
    const mask = document.createElement("div");
    mask.id = "cameraScanMask";
    mask.className = "camera-scan-mask";
    mask.innerHTML = `
      <div class="camera-scan-sheet">
        <div class="camera-scan-head">
          <strong>手机扫码</strong>
          <button class="camera-scan-close" type="button" aria-label="关闭">×</button>
        </div>
        <div class="camera-scan-view">
          <video id="cameraScanVideo" autoplay muted playsinline></video>
          <div class="camera-scan-frame"></div>
        </div>
        <div id="cameraScanMessage" class="camera-scan-tip">请将商品条码、库位码或二维码放入框内。</div>
        <div class="camera-scan-actions">
          <button id="cameraScanManual" type="button">手动输入</button>
          <label>拍照识别<input id="cameraScanFile" type="file" accept="image/*" capture="environment" /></label>
        </div>
      </div>
    `;
    document.body.appendChild(mask);
    mask.querySelector(".camera-scan-close").addEventListener("click", closeMobileScanner);
    mask.querySelector("#cameraScanManual").addEventListener("click", () => {
      closeMobileScanner();
      input.focus();
      if (typeof input.select === "function") {
        input.select();
      }
    });
    const fileInput = mask.querySelector("#cameraScanFile");
    fileInput.addEventListener("change", () => scanImageFile(input, fileInput.files && fileInput.files[0]));
    const message = mask.querySelector("#cameraScanMessage");
    const video = mask.querySelector("#cameraScanVideo");
    if (!window.isSecureContext) {
      message.className = "camera-scan-error";
      message.textContent = "当前页面不是 HTTPS，浏览器可能禁止实时摄像头。可以先用“拍照识别”，或换 HTTPS 地址测试。";
    }
    if (!("mediaDevices" in navigator) || !navigator.mediaDevices.getUserMedia) {
      message.className = "camera-scan-error";
      message.textContent = "当前浏览器不支持直接调用摄像头，请用拍照识别或手动输入。";
      return;
    }
    if (!("BarcodeDetector" in window)) {
      message.className = "camera-scan-error";
      message.textContent = "当前浏览器不支持实时条码识别，请用拍照识别或手动输入。";
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: { ideal: "environment" },
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });
      video.srcObject = stream;
      const detector = "BarcodeDetector" in window ? new BarcodeDetector({ formats: scannerFormats() }) : null;
      state.mobileScanner = { stream, detector, input, frame: 0 };
      if (detector) {
        scanVideoFrame(video, detector, input);
      }
    } catch (error) {
      message.className = "camera-scan-error";
      message.textContent = window.isSecureContext
        ? `摄像头打开失败：${messageOf(error)}`
        : "摄像头打开失败：当前测试地址是 HTTP，手机浏览器通常要求 HTTPS 才能打开摄像头。";
    }
  }

  async function scanVideoFrame(video, detector, input) {
    if (!state.mobileScanner || state.mobileScanner.detector !== detector) {
      return;
    }
    try {
      if (video.readyState >= 2) {
        const codes = await detector.detect(video);
        if (codes && codes.length) {
          const value = codes[0].rawValue || "";
          closeMobileScanner();
          applyScannedValue(input, value);
          return;
        }
      }
    } catch (error) {
      const message = document.getElementById("cameraScanMessage");
      if (message) {
        message.className = "camera-scan-error";
        message.textContent = `识别失败：${messageOf(error)}`;
      }
    }
    if (state.mobileScanner) {
      state.mobileScanner.frame = requestAnimationFrame(() => scanVideoFrame(video, detector, input));
    }
  }

  async function scanImageFile(input, file) {
    if (!file) {
      return;
    }
    const message = document.getElementById("cameraScanMessage");
    if (!("BarcodeDetector" in window)) {
      if (message) {
        message.className = "camera-scan-error";
        message.textContent = "当前浏览器不支持图片条码识别，请手动输入。";
      }
      return;
    }
    try {
      const bitmap = await createImageBitmap(file);
      const detector = new BarcodeDetector({ formats: scannerFormats() });
      const codes = await detector.detect(bitmap);
      if (codes && codes.length) {
        const value = codes[0].rawValue || "";
        closeMobileScanner();
        applyScannedValue(input, value);
        return;
      }
      if (message) {
        message.className = "camera-scan-error";
        message.textContent = "这张图片没有识别到条码，请重新拍摄。";
      }
    } catch (error) {
      if (message) {
        message.className = "camera-scan-error";
        message.textContent = `图片识别失败：${messageOf(error)}`;
      }
    }
  }

  function enhanceMobileScanButtons(scope) {
    const container = scope || root || document;
    container.querySelectorAll("input").forEach((input) => {
      if (input.type === "hidden" || input.dataset.mobileScanReady === "1") {
        return;
      }
      const marker = [
        input.id,
        input.name,
        input.placeholder,
        input.getAttribute("aria-label"),
      ].filter(Boolean).join(" ").toLowerCase();
      if (!/(barcode|sku|upc|条码|扫码|扫描|库位|二维码)/.test(marker)) {
        return;
      }
      const host = input.parentElement;
      if (!host) {
        return;
      }
      host.classList.add("mobile-scan-host");
      input.classList.add("mobile-scan-input");
      input.dataset.mobileScanReady = "1";
      const button = document.createElement("button");
      button.type = "button";
      button.className = "mobile-scan-button";
      button.setAttribute("aria-label", "手机扫码");
      button.title = "手机扫码";
      button.innerHTML = `
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M5 8V5h3"></path>
          <path d="M16 5h3v3"></path>
          <path d="M19 16v3h-3"></path>
          <path d="M8 19H5v-3"></path>
          <path d="M8 12h8"></path>
          <path d="M12 8v8"></path>
        </svg>
      `;
      button.addEventListener("click", () => {
        openMobileScanner(input);
      });
      input.insertAdjacentElement("afterend", button);
    });
  }

  function bindAppChrome() {
    ensureDynamicPdaStyles();
    enhanceArrivalScanSign(root);
    enhanceMobileScanButtons(root);
    if (!state.mobileScanObserver) {
      state.mobileScanObserver = new MutationObserver(() => {
        enhanceArrivalScanSign(root);
        enhanceMobileScanButtons(root);
      });
      state.mobileScanObserver.observe(root, { childList: true, subtree: true });
    }
    bindBottomNav();
    root.querySelectorAll("[data-app-back]").forEach((button) => {
      button.addEventListener("click", () => navigate(appBackRoute()));
    });
  }

  function appBackRoute() {
    return OPERATION_ROUTES.includes(state.route) ? "operation" : "home";
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
    if (route === "outbound-flow") {
      await renderOutboundFlowPage(route, group);
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
        <div class="inbound-top-bar">
          <button id="backToOperation" class="app-back-button" type="button" aria-label="返回">‹</button>
          <p class="inbound-top-note">到货、收货、上架按状态切换处理</p>
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
    resetPageScroll();
    document.getElementById("backToOperation").addEventListener("click", () => navigate("operation"));
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
          <p class="inbound-top-note">到货、收货、上架按状态切换处理</p>
          <span></span>
        </div>
        <div class="inbound-status-tabs" role="tablist">
          ${group.tabs.map((tab) => `
            <button class="inbound-status-tab ${tab.mode === "putaway" ? "is-active" : ""}" type="button" data-flow-route="${escapeAttr(route)}" data-flow-mode="${escapeAttr(tab.mode)}">
              ${escapeHtml(tab.label)}
            </button>
          `).join("")}
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
    resetPageScroll();
    document.getElementById("backToInboundReceipt").addEventListener("click", () => {
      navigate("operation");
    });
    root.querySelectorAll("[data-flow-mode]").forEach((button) => {
      button.addEventListener("click", () => {
        state.flowModes[button.dataset.flowRoute] = button.dataset.flowMode;
        renderInboundFlowPage(button.dataset.flowRoute, group);
      });
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
        resetPageScroll();
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
          <p class="inbound-top-note">到货、收货、上架按状态切换处理</p>
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
    resetPageScroll();
    document.getElementById("backToInboundArrival").addEventListener("click", () => {
      navigate("operation");
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
        resetPageScroll();
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
    resetPageScroll();
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
    resetPageScroll();
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
      resetPageScroll();
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
    resetPageScroll();
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
    resetPageScroll();
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
    resetPageScroll();
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
    resetPageScroll();
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

  function outboundStageTabs() {
    return [
      { mode: "claim", label: "待领取", hint: "领取拣货任务" },
      { mode: "pick", label: "待拣货", hint: "按库位拣货" },
      { mode: "picked", label: "已拣货", hint: "等待复核" },
      { mode: "sort_wait", label: "待分拣", hint: "等待分拣" },
      { mode: "sorted", label: "已分拣", hint: "明细查看" },
    ];
  }

  function outboundApiMode(mode) {
    return {
      claim: "pick",
      pick: "pick",
      picked: "outbound",
      sort_wait: "outbound",
      sorted: "handover",
    }[mode] || mode;
  }

  function outboundStageRecords(mode, byMode) {
    const apiMode = outboundApiMode(mode);
    const records = byMode[apiMode] || [];
    if (mode === "claim") {
      return uniqueOutboundRecords(records.filter((record) => !record._doneFallback && outboundWorkflowStage(record) === "claim"));
    }
    if (mode === "pick") {
      return uniqueOutboundRecords(records.filter((record) => !record._doneFallback && outboundWorkflowStage(record) === "pick"));
    }
    if (mode === "picked") {
      return uniqueOutboundRecords(mergeOutboundWorkflowRecords(records, "picked").concat(records.filter((record) => record._doneFallback && outboundWorkflowStage(record) === "claim")));
    }
    if (mode === "sort_wait") {
      return uniqueOutboundRecords(mergeOutboundWorkflowRecords(records, "sort_wait"));
    }
    if (mode === "sorted") {
      return uniqueOutboundRecords(mergeOutboundWorkflowRecords(records, "sorted"));
    }
    return records;
  }

  function outboundStageCounts(byMode) {
    const pickRecords = byMode.pick || [];
    const outboundRecords = byMode.outbound || [];
    const handoverRecords = byMode.handover || [];
    return {
      claim: pickRecords.filter((record) => outboundWorkflowStage(record) === "claim").length,
      pick: pickRecords.filter((record) => outboundWorkflowStage(record) === "pick").length,
      picked: mergeOutboundWorkflowRecords(outboundRecords, "picked").length,
      sort_wait: mergeOutboundWorkflowRecords(outboundRecords, "sort_wait").length,
      sorted: mergeOutboundWorkflowRecords(handoverRecords, "sorted").length,
    };
  }

  function outboundVisibleCounts(byMode) {
    return Object.fromEntries(outboundStageTabs().map((tab) => [
      tab.mode,
      filterOutboundRecords(tab.mode, outboundStageRecords(tab.mode, byMode)).length,
    ]));
  }

  function uniqueOutboundRecords(records) {
    const seen = new Set();
    return (records || []).filter((record, index) => {
      const key = outboundClaimKey(record) || `record-${record && record.id || index}`;
      if (seen.has(key)) {
        return false;
      }
      seen.add(key);
      return true;
    });
  }

  function outboundClaimKey(task) {
    return String(task && (task.picking_name || task.name || task.id) || "");
  }

  function outboundClaimStorageKey() {
    return `${outboundStageStoragePrefix()}:outbound_workflow`;
  }

  function outboundWorkflowMap() {
    try {
      const raw = JSON.parse(localStorage.getItem(outboundClaimStorageKey()) || "{}");
      if (Array.isArray(raw)) {
        return Object.fromEntries(raw.map((key) => [key, "pick"]));
      }
      return raw && typeof raw === "object" ? raw : {};
    } catch (error) {
      return {};
    }
  }

  function outboundSnapshotStorageKey() {
    return `${outboundStageStoragePrefix()}:outbound_snapshots`;
  }

  function outboundSnapshotMap() {
    try {
      const raw = JSON.parse(localStorage.getItem(outboundSnapshotStorageKey()) || "{}");
      return raw && typeof raw === "object" ? raw : {};
    } catch (error) {
      return {};
    }
  }

  function saveOutboundTaskSnapshot(task) {
    const key = outboundClaimKey(task);
    if (!key || !task) {
      return;
    }
    state.outboundTaskSnapshots = state.outboundTaskSnapshots || {};
    state.outboundTaskSnapshots[key] = task;
    try {
      const saved = outboundSnapshotMap();
      saved[key] = task;
      localStorage.setItem(outboundSnapshotStorageKey(), JSON.stringify(saved));
    } catch (error) {
      // Keep the in-memory snapshot even when the browser blocks storage.
    }
  }

  function outboundSnapshotsForStage(stage) {
    const workflow = { ...outboundWorkflowMap(), ...(state.outboundWorkflowTasks || {}) };
    const snapshots = { ...outboundSnapshotMap(), ...(state.outboundTaskSnapshots || {}) };
    return Object.keys(workflow)
      .filter((key) => workflow[key] === stage && snapshots[key])
      .map((key) => snapshots[key]);
  }

  function outboundWorkflowStage(task) {
    const key = outboundClaimKey(task);
    if (!key) {
      return "claim";
    }
    const memory = state.outboundWorkflowTasks || {};
    const saved = outboundWorkflowMap();
    return memory[key] || saved[key] || "claim";
  }

  function setOutboundWorkflowStage(task, stage) {
    const key = outboundClaimKey(task);
    if (!key) {
      return;
    }
    const taskName = outboundTaskName(task);
    state.outboundWorkflowTasks = state.outboundWorkflowTasks || {};
    state.outboundWorkflowTasks[key] = stage;
    if (taskName) {
      state.outboundWorkflowTasks[`name:${taskName}`] = stage;
    }
    saveOutboundTaskSnapshot(task);
    try {
      const saved = outboundWorkflowMap();
      saved[key] = stage;
      if (taskName) {
        saved[`name:${taskName}`] = stage;
      }
      localStorage.setItem(outboundClaimStorageKey(), JSON.stringify(saved));
    } catch (error) {
      // Keep the in-memory workflow state even when the browser blocks storage.
    }
  }

  function mergeOutboundWorkflowRecords(records, stage) {
    const source = state.lastOutboundPickRecords || [];
    const moved = source.filter((record) => outboundWorkflowStage(record) === stage).concat(outboundSnapshotsForStage(stage));
    const seen = new Set((records || []).map(outboundClaimKey).filter(Boolean));
    return (records || []).concat(moved.filter((record) => {
      const key = outboundClaimKey(record);
      if (!key || seen.has(key)) {
        return false;
      }
      seen.add(key);
      return true;
    }));
  }

  async function odooJsonRpc(route, params) {
    const response = await fetch(route, {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "call",
        params: params || {},
        id: Date.now(),
      }),
    });
    const data = await response.json();
    if (!response.ok || data.error) {
      const message = data.error && (data.error.data && data.error.data.message || data.error.message);
      throw new Error(message || `请求失败 ${response.status}`);
    }
    return data.result;
  }

  async function odooSearchRead(model, domain, fields, limit) {
    return odooJsonRpc("/web/dataset/call_kw/" + model + "/search_read", {
      model,
      method: "search_read",
      args: [],
      kwargs: {
        domain: domain || [],
        fields: fields || [],
        limit: limit || 80,
        order: "create_date desc, id desc",
      },
    });
  }

  function relationName(value) {
    return Array.isArray(value) ? value[1] : value || "";
  }

  function relationId(value) {
    return Array.isArray(value) ? value[0] : value || 0;
  }

  function pdaStatusText(stateValue) {
    return {
      draft: "草稿",
      waiting: "等待",
      confirmed: "已确认",
      assigned: "准备好了",
      done: "已完成",
      cancel: "已取消",
    }[stateValue] || statusLabel(stateValue) || stateValue || "待处理";
  }

  async function fetchOutgoingPickingFallback() {
    const pickings = await odooSearchRead("stock.picking", [
      ["picking_type_code", "=", "outgoing"],
      ["state", "in", ["confirmed", "assigned", "waiting", "done"]],
    ], [
      "id",
      "name",
      "origin",
      "partner_id",
      "state",
      "scheduled_date",
      "create_date",
      "location_id",
      "location_dest_id",
      "picking_type_id",
    ], 100);
    return (pickings || []).map((picking) => ({
      id: picking.id,
      name: picking.name,
      picking_name: picking.name,
      origin: picking.origin,
      partner_name: relationName(picking.partner_id),
      state: picking.state,
      create_date: picking.create_date || picking.scheduled_date,
      scheduled_date: picking.scheduled_date,
      source_location: relationName(picking.location_id),
      dest_location: relationName(picking.location_dest_id),
      warehouse_name: relationName(picking.picking_type_id),
      product_summary: picking.origin ? `来源单 ${picking.origin}` : "后台送货单",
      _pickingFallback: true,
      _doneFallback: picking.state === "done",
    }));
  }

  function mergeOutboundPickRecords(records, fallbackPickings) {
    const seen = new Set((records || []).map((record) => record.picking_name || record.name).filter(Boolean));
    const extra = (fallbackPickings || []).filter((record) => !seen.has(record.picking_name || record.name));
    return (records || []).concat(extra);
  }

  function outboundDateText(value) {
    if (!value) {
      return "";
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return String(value);
    }
    const pad = (number) => String(number).padStart(2, "0");
    return `${date.getFullYear()}/${pad(date.getMonth() + 1)}/${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
  }

  function outboundSortLabel() {
    return ({
      newest: "最新优先",
      oldest: "最早优先",
      name: "按单号",
    }[state.outboundSort || "newest"] || "排序");
  }

  function outboundWorkAreaLabel() {
    return state.outboundWorkArea ? state.outboundWorkArea : "作业区";
  }

  function outboundPickMethodLabel() {
    return ({
      order: "按单拣货",
      batch: "波次拣货",
    }[state.outboundPickMethod] || "拣货方式");
  }

  function outboundWorkAreaOf(task) {
    return task.work_area || task.source_location || task.location_name || task.dest_location || task.warehouse_name || "未分配作业区";
  }

  function outboundPickMethodOf(task) {
    const text = [
      task.pick_method,
      task.picking_method,
      task.task_type,
      task.route_batch_name,
      task.batch_name,
      task.name,
      task.origin,
    ].filter(Boolean).join(" ").toLowerCase();
    if (/batch|wave|波次|批次/.test(text)) {
      return "batch";
    }
    return "order";
  }

  function outboundTaskTimeValue(task) {
    const date = new Date(task.create_date || task.scheduled_date || task.date || task.write_date || 0);
    return Number.isNaN(date.getTime()) ? 0 : date.getTime();
  }

  function outboundFilterOptions(type) {
    if (type === "sort") {
      return [
        { value: "newest", label: "最新优先" },
        { value: "oldest", label: "最早优先" },
        { value: "name", label: "按单号" },
      ];
    }
    if (type === "pickMethod") {
      return [
        { value: "", label: "全部方式" },
        { value: "order", label: "按单拣货" },
        { value: "batch", label: "波次拣货" },
      ];
    }
    const source = state.outboundFilterSource || [];
    const areas = Array.from(new Set(source.map(outboundWorkAreaOf).filter(Boolean)));
    return [{ value: "", label: "全部作业区" }].concat(areas.map((area) => ({ value: area, label: area })));
  }

  function outboundFilterTitle(type) {
    return {
      sort: "排序",
      workArea: "作业区",
      pickMethod: "拣货方式",
    }[type] || "筛选";
  }

  function outboundFilterActiveValue(type) {
    if (type === "sort") {
      return state.outboundSort || "newest";
    }
    if (type === "workArea") {
      return state.outboundWorkArea || "";
    }
    if (type === "pickMethod") {
      return state.outboundPickMethod || "";
    }
    return "";
  }

  function toggleOutboundFilterPanel(type) {
    const panel = document.getElementById("outboundFilterPanel");
    if (!panel) {
      return;
    }
    if (!panel.hidden && panel.dataset.filterType === type) {
      panel.hidden = true;
      return;
    }
    const sections = type === "all" ? ["sort", "workArea", "pickMethod"] : [type];
    panel.dataset.filterType = type;
    panel.hidden = false;
    const body = sections.map((section) => {
      const active = outboundFilterActiveValue(section);
      return `
        <section class="outbound-filter-section">
          <strong>${escapeHtml(outboundFilterTitle(section))}</strong>
          <div>
            ${outboundFilterOptions(section).map((option) => `
              <button class="${option.value === active ? "is-active" : ""}" type="button" data-outbound-filter-type="${escapeAttr(section)}" data-outbound-filter-value="${escapeAttr(option.value)}">
                ${escapeHtml(option.label)}
              </button>
            `).join("")}
          </div>
        </section>
      `;
    }).join("");
    panel.innerHTML = `${body}<button class="outbound-filter-reset" type="button" data-outbound-filter-reset>重置筛选</button>`;
    panel.querySelectorAll("[data-outbound-filter-type]").forEach((button) => {
      button.addEventListener("click", () => applyOutboundFilter(button.dataset.outboundFilterType, button.dataset.outboundFilterValue || ""));
    });
    const reset = panel.querySelector("[data-outbound-filter-reset]");
    if (reset) {
      reset.addEventListener("click", resetOutboundFilters);
    }
  }

  function applyOutboundFilter(type, value) {
    if (type === "sort") {
      state.outboundSort = value || "newest";
    } else if (type === "workArea") {
      state.outboundWorkArea = value || "";
    } else if (type === "pickMethod") {
      state.outboundPickMethod = value || "";
    }
    const panel = document.getElementById("outboundFilterPanel");
    if (panel) {
      panel.hidden = true;
    }
    renderOutboundFlowPage("outbound-flow", FLOW_GROUPS["outbound-flow"]);
  }

  function resetOutboundFilters() {
    state.outboundSort = "newest";
    state.outboundWorkArea = "";
    state.outboundPickMethod = "";
    const panel = document.getElementById("outboundFilterPanel");
    if (panel) {
      panel.hidden = true;
    }
    renderOutboundFlowPage("outbound-flow", FLOW_GROUPS["outbound-flow"]);
  }

  async function renderOutboundFlowPage(route, group) {
    const tabs = outboundStageTabs();
    let mode = state.flowModes[route] || "claim";
    if (!tabs.some((tab) => tab.mode === mode)) {
      mode = "claim";
      state.flowModes[route] = mode;
    }
    root.innerHTML = `
      <section class="task-panel outbound-page">
        <div class="receipt-nav outbound-nav">
          <button id="backToOperation" class="app-back-button" type="button" aria-label="返回">‹</button>
          <div>
            <h1>出库履约</h1>
            <p>领取 · 拣货 · 分拣</p>
          </div>
          <button id="refreshOutboundTasks" class="outbound-filter-button" type="button">筛选</button>
        </div>
        <div class="outbound-status-tabs" role="tablist" aria-label="出库履约状态">
          ${tabs.map((tab) => `
            <button class="outbound-status-tab ${tab.mode === mode ? "is-active" : ""}" type="button" data-outbound-mode="${escapeAttr(tab.mode)}">
              <span>${escapeHtml(tab.label)}</span><em data-outbound-count="${escapeAttr(tab.mode)}"></em>
            </button>
          `).join("")}
        </div>
        <form id="outboundSearchForm" class="outbound-search" autocomplete="off">
          <input id="outboundSearchInput" type="search" value="${escapeAttr(state.outboundSearch)}" placeholder="${escapeAttr(mode === "claim" ? "收货方 / 任务单号 / 波次单" : "扫码或输入任务单号 / 商品 / SKU")}" />
          <button type="submit" aria-label="搜索">⌕</button>
        </form>
        <div class="outbound-filter-row">
          <button id="outboundSortButton" type="button">${escapeHtml(outboundSortLabel())}⌄</button>
          <button id="outboundWorkAreaButton" type="button">${escapeHtml(outboundWorkAreaLabel())}⌄</button>
          <button id="outboundPickMethodButton" type="button">${escapeHtml(outboundPickMethodLabel())}⌄</button>
        </div>
        <div id="outboundFilterPanel" class="outbound-filter-panel" hidden></div>
        <div id="outboundItems" class="outbound-card-list">
          <div class="empty-state">正在读取出库任务...</div>
        </div>
        ${renderBottomNav("operation")}
      </section>
    `;
    document.getElementById("backToOperation").addEventListener("click", () => navigate("operation"));
    document.getElementById("refreshOutboundTasks").addEventListener("click", () => toggleOutboundFilterPanel("all"));
    document.getElementById("outboundSortButton").addEventListener("click", () => toggleOutboundFilterPanel("sort"));
    document.getElementById("outboundWorkAreaButton").addEventListener("click", () => toggleOutboundFilterPanel("workArea"));
    document.getElementById("outboundPickMethodButton").addEventListener("click", () => toggleOutboundFilterPanel("pickMethod"));
    document.getElementById("outboundSearchForm").addEventListener("submit", (event) => {
      event.preventDefault();
      state.outboundSearch = document.getElementById("outboundSearchInput").value.trim();
      loadOutboundTasks();
    });
    document.getElementById("outboundSearchInput").addEventListener("input", (event) => {
      state.outboundSearch = event.target.value.trim();
      loadOutboundTasks();
    });
    root.querySelectorAll("[data-outbound-mode]").forEach((button) => {
      button.addEventListener("click", () => {
        state.flowModes[route] = button.dataset.outboundMode;
        renderOutboundFlowPage(route, group);
      });
    });
    bindAppChrome();
    await loadOutboundTasks();
  }

  async function loadOutboundTasks() {
    const container = document.getElementById("outboundItems");
    if (!container) {
      return;
    }
    const mode = state.flowModes["outbound-flow"] || "claim";
    container.innerHTML = `<div class="empty-state">正在读取出库任务...</div>`;
    try {
      const modes = ["pick", "outbound", "handover"];
      const groups = await Promise.all(modes.map(async (itemMode) => {
        const data = itemMode === "handover"
          ? await apiGet(HANDOVER_ENDPOINTS.list, { limit: 100 })
          : await apiGet(ENDPOINTS[itemMode].list, { limit: 100 });
        return [itemMode, getRecords(data)];
      }));
      const byMode = Object.fromEntries(groups);
      const fallbackPickings = await fetchOutgoingPickingFallback().catch(() => []);
      byMode.pick = mergeOutboundPickRecords(byMode.pick || [], fallbackPickings);
      state.lastOutboundPickRecords = byMode.pick || [];
      state.outboundCounts = outboundVisibleCounts(byMode);
      updateOutboundTabs();
      const stageRecords = outboundStageRecords(mode, byMode);
      state.outboundFilterSource = stageRecords;
      const records = filterOutboundRecords(mode, stageRecords);
      state.activeTasks[mode] = records;
      state.activeTasks[outboundApiMode(mode)] = records;
      if (!records.length) {
        container.innerHTML = `<div class="empty-state inbound-empty">${escapeHtml(outboundEmptyText(mode))}</div>`;
        return;
      }
      container.innerHTML = records.map((task) => outboundTaskCard(mode, task)).join("");
      container.querySelectorAll("[data-outbound-task-id]").forEach((button) => {
        button.addEventListener("click", () => openOutboundTask(mode, Number(button.dataset.outboundTaskId)));
      });
      container.querySelectorAll("[data-outbound-primary-id]").forEach((button) => {
        button.addEventListener("click", () => {
          try {
            const taskId = Number(button.dataset.outboundPrimaryId);
            if (mode === "claim") {
              openOutboundClaimSheet(mode, taskId);
              return;
            }
            openOutboundTask(mode, taskId);
          } catch (error) {
            showError(error);
          }
        });
      });
    } catch (error) {
      container.innerHTML = `<div class="error-state">${escapeHtml(messageOf(error))}</div>`;
    }
  }

  function updateOutboundTabs() {
    outboundStageTabs().forEach((tab) => {
      const mode = tab.mode;
      const button = document.querySelector(`[data-outbound-mode="${mode}"]`);
      const count = document.querySelector(`[data-outbound-count="${mode}"]`);
      if (button) {
        button.classList.toggle("is-active", state.flowModes["outbound-flow"] === mode);
      }
      if (count) {
        const value = Number(state.outboundCounts[mode] || 0);
        count.textContent = value ? (value > 99 ? "99+" : String(value)) : "";
      }
    });
  }

  function filterOutboundRecords(mode, records) {
    const keyword = state.outboundSearch.trim().toLowerCase();
    let result = records;
    if (keyword) {
      result = result.filter((task) => outboundSearchText(mode, task).toLowerCase().includes(keyword));
    }
    if (state.outboundWorkArea) {
      result = result.filter((task) => outboundWorkAreaOf(task) === state.outboundWorkArea);
    }
    if (state.outboundPickMethod) {
      result = result.filter((task) => outboundPickMethodOf(task) === state.outboundPickMethod);
    }
    const sortMode = state.outboundSort || "newest";
    result = result.slice().sort((left, right) => {
      if (sortMode === "oldest") {
        return outboundTaskTimeValue(left) - outboundTaskTimeValue(right);
      }
      if (sortMode === "name") {
        return String(left.name || left.picking_name || "").localeCompare(String(right.name || right.picking_name || ""), "zh-Hans-CN");
      }
      return outboundTaskTimeValue(right) - outboundTaskTimeValue(left);
    });
    return result;
  }

  function outboundSearchText(mode, task) {
    return [
      task.name,
      task.picking_name,
      task.outbound_task_name,
      task.pick_task_name,
      task.check_task_name,
      task.partner_name,
      task.product_summary,
      task.source_location,
      task.route_batch_name,
      outboundWorkAreaOf(task),
      outboundPickMethodOf(task),
      task.driver_profile_name,
      task.vehicle_profile_name,
      Array.isArray(task.waybill_names) ? task.waybill_names.join(" ") : "",
    ].filter(Boolean).join(" ");
  }

  function outboundEmptyText(mode) {
    if (state.outboundSearch) {
      return `没有匹配“${state.outboundSearch}”的出库任务。`;
    }
    return {
      claim: "暂无待领取任务，后台生成出库拣货任务后会出现在这里。",
      pick: "暂无待拣货任务，领取任务后会进入这里。",
      picked: "暂无已拣货任务，拣货完成后会进入这里。",
      sort_wait: "暂无待分拣任务，复核/分拣任务生成后会进入这里。",
      sorted: "暂无已分拣任务，分拣完成后可在这里查看。",
      outbound: "暂无待复核任务，拣货完成后会进入这里。",
      handover: "暂无待交接单，复核完成后会生成交接任务。",
    }[mode] || "暂无出库任务。";
  }

  function outboundTaskCard(mode, task) {
    const apiMode = outboundApiMode(mode);
    const title = task.name || task.picking_name || task.outbound_task_name || `任务 ${task.id}`;
    const summary = apiMode === "handover" ? handoverTaskSummary(task) : buildTaskCardSummary(apiMode, task, []);
    const qty = apiMode === "handover"
      ? handoverQtyText(task)
      : (summary.qtyText || taskProgressText(task) || "数量待确认");
    const primaryText = {
      claim: "领取",
      pick: "开始拣货",
      picked: "详情",
      sort_wait: "开始分拣",
      sorted: "查看详情",
      outbound: "复核",
      handover: task.state === "handover_ing" ? "继续交接" : "查看详情",
    }[mode] || "处理";
    const badge = task._pickingFallback ? "后台交付单" : ({
      claim: "按单拣货",
      pick: "按单拣货",
      picked: "已拣货",
      sort_wait: "分拣",
      sorted: "单号",
      outbound: "复核",
      handover: "单号",
    }[mode] || "出库");
    const batchNo = task.route_batch_name || task.batch_name || task.origin || task.picking_name || "-";
    const creator = task.create_uid_name || task.user_name || task.operator_name || "系统";
    const createdAt = outboundDateText(task.create_date || task.scheduled_date || task.date || task.write_date);
    const partner = cleanOutboundPartnerText(task);
    const staging = cleanOutboundCollectLocation(task);
    const workArea = task.work_area || task.source_location || outboundLocationText(apiMode, task, summary);
    const productCount = Number(task.line_count || task.product_count || 0);
    const productText = productCount ? `商品 ${productCount}` : (summary.productText || (task._pickingFallback ? "后台已生成送货单" : "商品待确认"));
    return `
      <article class="outbound-card">
        <button class="outbound-card-main" type="button" data-outbound-task-id="${escapeAttr(task.id)}">
          <span class="outbound-card-head">
            <em>${escapeHtml(badge)}</em>
            <strong>${escapeHtml(title)}</strong>
          </span>
          <span class="outbound-card-row">波次单：<b>${escapeHtml(batchNo)}</b></span>
          <span class="outbound-card-row">任务创建：${escapeHtml(creator)} ${escapeHtml(createdAt || "")}</span>
          <span class="outbound-card-row">收货方：${escapeHtml(partner)}</span>
          <span class="outbound-card-row outbound-card-collect">集货位：${escapeHtml(staging)}</span>
          <span class="outbound-card-divider"></span>
          <span class="outbound-card-progress">作业区：${escapeHtml(workArea)}</span>
          <span class="outbound-card-product">${escapeHtml(productText)} · ${escapeHtml(outboundStageActionText(mode, task))}</span>
        </button>
        <div class="outbound-card-foot">
          <span>${escapeHtml(pdaStatusText(task.state))}</span>
          <button type="button" data-outbound-primary-id="${escapeAttr(task.id)}">${escapeHtml(primaryText)}</button>
        </div>
      </article>
    `;
  }

  function handoverTaskSummary(order) {
    return [
      order.partner_name,
      order.route_batch_name,
      order.driver_profile_name,
      order.vehicle_profile_name,
    ].filter(Boolean).join(" · ") || order.outbound_task_name || "交接出库";
  }

  function handoverQtyText(order) {
    const waybillCount = Array.isArray(order.waybill_names) ? order.waybill_names.length : 0;
    const weight = Number(order.weight_total || 0);
    const volume = Number(order.volume_total || 0);
    return [
      waybillCount ? `运单 ${waybillCount} 张` : "",
      weight ? `重量 ${formatQty(weight)} kg` : "",
      volume ? `体积 ${formatQty(volume)} m3` : "",
    ].filter(Boolean).join(" · ") || "等待交接确认";
  }

  function outboundPartnerText(mode, task) {
    if (mode === "handover") {
      return task.partner_name || "待交接客户";
    }
    return [task.partner_name, task.picking_name].filter(Boolean).join(" · ") || "待出库客户";
  }

  function cleanOutboundPartnerText(task) {
    const partner = String(task.partner_name || "").trim();
    if (partner && !/^WH\/OUT\//i.test(partner)) {
      return partner;
    }
    const text = String(task.product_summary || task.origin || "").trim();
    return text || "待确认收货方";
  }

  function cleanOutboundCollectLocation(task) {
    const value = String(task.staging_location || task.collect_location || "").trim();
    if (value && !/^Customers$/i.test(value)) {
      return value;
    }
    return task._doneFallback ? "已出库" : "JHW-001";
  }

  function outboundStageActionText(mode, task) {
    if (mode === "claim") {
      return "等待领取";
    }
    if (mode === "pick") {
      return "等待拣货";
    }
    if (mode === "picked") {
      return "已完成拣货";
    }
    if (mode === "sort_wait") {
      return "等待分拣";
    }
    if (mode === "sorted") {
      return "已完成分拣";
    }
    return pdaStatusText(task.state);
  }

  function outboundLocationText(mode, task, summary) {
    if (mode === "handover") {
      return task.route_batch_name || task.warehouse_name || "待交接";
    }
    return summary.locationText || task.source_location || "待作业库位";
  }

  function findOutboundUiTask(mode, taskId) {
    const id = Number(taskId);
    const apiMode = outboundApiMode(mode);
    return (state.activeTasks[mode] || []).find((task) => Number(task.id) === id)
      || (state.activeTasks[apiMode] || []).find((task) => Number(task.id) === id)
      || (state.outboundFilterSource || []).find((task) => Number(task.id) === id);
  }

  function openOutboundClaimSheet(mode, taskId) {
    const task = findOutboundUiTask(mode, taskId);
    if (!task) {
      showToast("未找到当前任务，请刷新后重试", true);
      return;
    }
    const operatorName = typeof currentUserName === "function" ? currentUserName() : (state.userName || state.user_name || "PDA操作员");
    const mask = document.createElement("div");
    mask.className = "claim-task-mask";
    mask.id = "claimTaskMask";
    mask.innerHTML = `
      <div class="claim-task-sheet">
        <div class="claim-task-head">
          <div>
            <strong>领取出库任务</strong>
            <small>${escapeHtml(task.name || task.picking_name || `任务 ${task.id}`)} · ${escapeHtml(task.partner_name || "待确认收货方")}</small>
          </div>
          <button class="claim-task-close" type="button" aria-label="关闭">×</button>
        </div>
        <form id="claimTaskForm" class="claim-task-form" autocomplete="off">
          <label>
            领取人
            <input id="claimOperatorInput" name="operator" type="text" value="${escapeAttr(operatorName)}" placeholder="填写领取人" required />
          </label>
          <label>
            作业区
            <input id="claimWorkAreaInput" name="work_area" type="text" value="${escapeAttr(outboundWorkAreaOf(task))}" placeholder="例如 4A拣货区" required />
          </label>
          <label>
            集货位
            <input id="claimCollectInput" name="collect_location" type="text" value="${escapeAttr(task.staging_location || task.collect_location || "JHW-001")}" placeholder="例如 JHW-001" required />
          </label>
          <div class="claim-task-actions">
            <button class="claim-task-cancel" type="button">取消</button>
            <button class="claim-task-submit" type="submit">确认领取</button>
          </div>
        </form>
      </div>
    `;
    document.body.appendChild(mask);
    const close = () => mask.remove();
    const confirmClaim = () => {
      try {
        if (mask.dataset.submitting === "1") {
          return;
        }
        mask.dataset.submitting = "1";
        task.claim_operator = (mask.querySelector("#claimOperatorInput") || {}).value || "";
        task.work_area = (mask.querySelector("#claimWorkAreaInput") || {}).value || "";
        task.collect_location = (mask.querySelector("#claimCollectInput") || {}).value || "";
        if (!task.claim_operator || !task.work_area || !task.collect_location) {
          mask.dataset.submitting = "";
          showToast("请先填写领取人、作业区和集货位", true);
          return;
        }
        task._outboundStage = "pick";
        task.pda_stage = "pick";
        setOutboundWorkflowStage(task, "pick");
        state.lastOutboundPickRecords = uniqueOutboundRecords([task].concat(state.lastOutboundPickRecords || []));
        state.activeTasks.pick = uniqueOutboundRecords([task].concat(state.activeTasks.pick || []));
        showToast("任务已领取，已进入待拣货");
        close();
        state.flowModes["outbound-flow"] = "pick";
        renderOutboundFlowPage("outbound-flow", FLOW_GROUPS["outbound-flow"]);
      } catch (error) {
        mask.dataset.submitting = "";
        showError(error);
      }
    };
    mask.querySelector(".claim-task-close").addEventListener("click", close);
    mask.querySelector(".claim-task-cancel").addEventListener("click", close);
    mask.querySelector(".claim-task-submit").addEventListener("click", (event) => {
      event.preventDefault();
      confirmClaim();
    });
    mask.querySelector("#claimTaskForm").addEventListener("submit", (event) => {
      event.preventDefault();
      confirmClaim();
    });
  }

  function openOutboundTask(mode, taskId) {
    const uiTask = findOutboundUiTask(mode, taskId);
    if (mode === "picked") {
      if (uiTask) {
        renderOutboundRecordDetail(uiTask, "picked");
        return;
      }
    }
    if (mode === "sort_wait") {
      if (uiTask) {
        renderOutboundSortWorkPage(uiTask);
        return;
      }
    }
    if (uiTask && uiTask._pickingFallback) {
      renderPickingFallbackDetailPage(Number(uiTask.id));
      return;
    }
    const apiMode = outboundApiMode(mode);
    if (apiMode === "handover") {
      renderOutboundHandoverDetailPage(taskId);
      return;
    }
    renderOutboundTaskDetailPage(apiMode, taskId);
  }

  function renderOutboundSortWorkPage(task) {
    ensureOutboundRecordDetailStyles();
    const currentTask = task || {};
    const title = outboundTaskName(currentTask) || currentTask.name || "分拣任务";
    const taskKey = outboundClaimKey(currentTask) || title;
    state.outboundSortDoneLines = state.outboundSortDoneLines || {};
    state.outboundSortDoneLines[taskKey] = state.outboundSortDoneLines[taskKey] || {};
    root.innerHTML = `
      <section class="task-panel outbound-detail-page qnh-outbound-detail qnh-sort-work-page">
        <div class="qnh-outbound-nav">
          <button id="backToOutboundList" class="app-back-button" type="button" aria-label="返回">‹</button>
          <h1>分拣任务详情</h1>
          <button id="completeSortTask" class="qnh-outbound-link" type="button">完成分拣</button>
        </div>
        <section class="qnh-outbound-summary">
          <div class="qnh-outbound-title">
            <span>单号</span>
            <strong>${escapeHtml(title)}</strong>
            <em>待分拣</em>
          </div>
          <div class="qnh-outbound-meta">
            <p><b>拣货容器：</b>${escapeHtml(currentTask.container || currentTask.pick_container || currentTask.collect_location || "JHW-001")}</p>
            <p><b>波次单：</b>${escapeHtml(currentTask.wave_no || currentTask.wave_name || currentTask.origin || currentTask.source_document || "-")}</p>
            <p><b>收货方：</b>${escapeHtml(currentTask.partner_name || currentTask.customer_name || "-")}</p>
            <p><b>集货位：</b><strong>${escapeHtml(currentTask.collect_location || currentTask.collect_location_name || "JHW-001")}</strong></p>
            <p><b>分拣进度：</b><span id="sortProgressText">${escapeHtml(outboundSortProgressText(currentTask))}</span></p>
          </div>
        </section>
        <form class="qnh-outbound-search" autocomplete="off">
          <input id="sortWorkSearch" type="search" placeholder="扫码或输入商品条码 / SKU" />
          <button id="sortWorkScan" type="button" aria-label="扫码"></button>
        </form>
        <div class="qnh-work-tabs">
          <button class="is-active" type="button" data-sort-filter="pending">待分商品</button>
          <button type="button" data-sort-filter="done">已分商品</button>
        </div>
        <section id="sortWorkLines" class="qnh-outbound-lines">
          ${renderOutboundSortLines(currentTask, "pending")}
        </section>
        ${renderBottomNav("operation")}
      </section>
    `;
    document.getElementById("backToOutboundList").addEventListener("click", () => {
      state.flowModes["outbound-flow"] = "sort_wait";
      renderOutboundFlowPage("outbound-flow", FLOW_GROUPS["outbound-flow"]);
    });
    document.getElementById("completeSortTask").addEventListener("click", () => completeOutboundSortTask(currentTask));
    document.getElementById("sortWorkScan").addEventListener("click", () => openMobileScanner(document.getElementById("sortWorkSearch")));
    document.getElementById("sortWorkSearch").addEventListener("input", () => refreshOutboundSortLines(currentTask));
    root.querySelectorAll("[data-sort-filter]").forEach((button) => {
      button.addEventListener("click", () => {
        root.querySelectorAll("[data-sort-filter]").forEach((item) => item.classList.toggle("is-active", item === button));
        refreshOutboundSortLines(currentTask);
      });
    });
    bindOutboundSortLineButtons(currentTask);
    bindBottomNav();
  }

  function outboundSortLineKey(line, index) {
    return String(line.key || line.id || line.barcode || line.defaultCode || `line-${index}`);
  }

  function outboundSortDoneMap(task) {
    const taskKey = outboundClaimKey(task) || outboundTaskName(task) || "sort-task";
    state.outboundSortDoneLines = state.outboundSortDoneLines || {};
    state.outboundSortDoneLines[taskKey] = state.outboundSortDoneLines[taskKey] || {};
    return state.outboundSortDoneLines[taskKey];
  }

  function outboundSortSourceLines(task) {
    const lines = outboundRecordLines(task);
    return lines.length ? lines : safeQnhFallbackOutboundLines(task);
  }

  function outboundSortProgressText(task) {
    const lines = outboundSortSourceLines(task);
    const doneMap = outboundSortDoneMap(task);
    const doneCount = lines.filter((line, index) => doneMap[outboundSortLineKey(line, index)]).length;
    const totalQty = lines.reduce((sum, line) => sum + Number(line.demandQty || line.doneQty || 0), 0);
    const doneQty = lines.reduce((sum, line, index) => doneMap[outboundSortLineKey(line, index)] ? sum + Number(line.demandQty || line.doneQty || 0) : sum, 0);
    return `SKU ${formatQty(doneCount)}/${formatQty(lines.length)}，数量 ${formatQty(doneQty)}/${formatQty(totalQty || Number(task.total_qty || task.qty || 0))}`;
  }

  function renderOutboundSortLines(task, filter) {
    const keyword = String((document.getElementById("sortWorkSearch") || {}).value || "").trim().toLowerCase();
    const doneMap = outboundSortDoneMap(task);
    const lines = outboundSortSourceLines(task).filter((line, index) => {
      const lineDone = !!doneMap[outboundSortLineKey(line, index)];
      if (filter === "done" && !lineDone) {
        return false;
      }
      if (filter !== "done" && lineDone) {
        return false;
      }
      if (!keyword) {
        return true;
      }
      return [line.productName, line.defaultCode, line.barcode, line.location].filter(Boolean).join(" ").toLowerCase().includes(keyword);
    });
    if (!lines.length) {
      return `<div class="empty-state">${filter === "done" ? "暂无已分商品。" : "暂无待分商品。"}</div>`;
    }
    return lines.map((line, index) => outboundSortLineCard(line, task, index, !!doneMap[outboundSortLineKey(line, index)])).join("");
  }

  function outboundSortLineCard(line, task, index, isDone) {
    const unit = displayUom(line.uom) || "份";
    const qty = Number(line.demandQty || line.doneQty || 0);
    const raw = line.raw || {};
    const spec = raw.spec || raw.specification || raw.variant || "-";
    const packageRatio = raw.package_ratio || raw.packaging_ratio || `1${unit}/${unit}`;
    return `
      <article class="qnh-work-product-card ${isDone ? "is-done" : ""}">
        <div class="qnh-outbound-thumb">
          <span>${escapeHtml(receiptLineAvatarText({ defaultCode: line.defaultCode, productName: line.productName }))}</span>
          <em>${escapeHtml(formatQty(qty))}${escapeHtml(unit)}</em>
        </div>
        <div class="qnh-work-product-info">
          <h2>${escapeHtml(line.productName || task.product_summary || "未命名商品")}</h2>
          <p>商品码：<b>${escapeHtml(line.barcode || line.defaultCode || "-")}</b></p>
          <p>规格：${escapeHtml(spec)}</p>
          <p>包装比率：<b>${escapeHtml(packageRatio)}</b></p>
          <div class="qnh-work-card-foot">
            <span>${isDone ? "已分拣" : "待分拣"}：<b>${escapeHtml(formatQty(qty))}${escapeHtml(unit)}</b></span>
            <button type="button" data-sort-line-key="${escapeAttr(outboundSortLineKey(line, index))}" ${isDone ? "disabled" : ""}>${isDone ? "已完成" : "分拣完成"}</button>
          </div>
        </div>
      </article>
    `;
  }

  function refreshOutboundSortLines(task) {
    const activeFilter = (root.querySelector("[data-sort-filter].is-active") || {}).dataset?.sortFilter || "pending";
    const container = document.getElementById("sortWorkLines");
    const progress = document.getElementById("sortProgressText");
    if (container) {
      container.innerHTML = renderOutboundSortLines(task, activeFilter);
      bindOutboundSortLineButtons(task);
    }
    if (progress) {
      progress.textContent = outboundSortProgressText(task);
    }
  }

  function bindOutboundSortLineButtons(task) {
    root.querySelectorAll("[data-sort-line-key]").forEach((button) => {
      button.addEventListener("click", () => {
        const doneMap = outboundSortDoneMap(task);
        doneMap[button.dataset.sortLineKey] = true;
        showToast("本行已分拣");
        const lines = outboundSortSourceLines(task);
        const completed = lines.every((line, index) => doneMap[outboundSortLineKey(line, index)]);
        if (completed) {
          completeOutboundSortTask(task);
          return;
        }
        refreshOutboundSortLines(task);
      });
    });
  }

  function completeOutboundSortTask(task) {
    const nextTask = { ...(task || {}), _outboundStage: "sorted", pda_stage: "sorted" };
    setOutboundWorkflowStage(nextTask, "sorted");
    showToast("分拣完成，已进入已分拣");
    state.flowModes["outbound-flow"] = "sorted";
    renderOutboundFlowPage("outbound-flow", FLOW_GROUPS["outbound-flow"]);
  }

  async function renderOutboundTaskDetailPage(mode, taskId) {
    const config = ENDPOINTS[mode];
    root.innerHTML = `
      <section class="task-panel outbound-page outbound-detail-page">
        <div class="receipt-nav outbound-nav">
          <button id="backToOutboundList" class="app-back-button" type="button" aria-label="返回">‹</button>
          <div>
            <h1>${escapeHtml(config.title)}</h1>
            <p>${escapeHtml(mode === "pick" ? "扫库位 · 扫商品 · 确认数量" : "扫商品 · 复核数量 · 装箱确认")}</p>
          </div>
          <button id="outboundCompleteTask" class="outbound-filter-button" type="button">${escapeHtml(config.completeText)}</button>
        </div>
        <div id="outboundDetailBody">
          <div class="empty-state">正在读取任务明细...</div>
        </div>
        ${renderBottomNav("operation")}
      </section>
    `;
    document.getElementById("backToOutboundList").addEventListener("click", () => renderOutboundFlowPage("outbound-flow", FLOW_GROUPS["outbound-flow"]));
    document.getElementById("outboundCompleteTask").addEventListener("click", () => completeOutboundTask(mode));
    bindAppChrome();
    await loadOutboundTaskDetail(mode, taskId);
  }

  async function renderPickingFallbackDetailPage(pickingId) {
    state.activeTasks["fallbackPicking:id"] = pickingId;
    root.innerHTML = `
      <section class="task-panel outbound-page outbound-detail-page">
        <div class="receipt-nav outbound-nav">
          <button id="backToOutboundList" class="app-back-button" type="button" aria-label="返回">‹</button>
          <div>
            <h1>拣货任务详情</h1>
            <p>后台送货单 · PDA 执行</p>
          </div>
          <button id="fallbackCompletePicking" class="outbound-filter-button" type="button">完成出库</button>
        </div>
        <div id="fallbackPickingBody">
          <div class="empty-state">正在读取送货单明细...</div>
        </div>
        ${renderBottomNav("operation")}
      </section>
    `;
    document.getElementById("backToOutboundList").addEventListener("click", () => renderOutboundFlowPage("outbound-flow", FLOW_GROUPS["outbound-flow"]));
    document.getElementById("fallbackCompletePicking").addEventListener("click", () => completePickingFallback(pickingId));
    bindAppChrome();
    await loadPickingFallbackDetail(pickingId);
  }

  async function loadPickingFallbackDetail(pickingId) {
    const body = document.getElementById("fallbackPickingBody");
    if (!body) {
      return;
    }
    try {
      const pickings = await odooSearchRead("stock.picking", [["id", "=", pickingId]], [
        "id",
        "name",
        "origin",
        "partner_id",
        "state",
        "scheduled_date",
        "create_date",
        "location_id",
        "location_dest_id",
      ], 1);
      const picking = (pickings || [])[0] || {};
      state.activeTasks["fallbackPicking:task"] = {
        id: picking.id || pickingId,
        name: picking.name,
        picking_name: picking.name,
        origin: picking.origin,
        partner_name: relationName(picking.partner_id),
        state: picking.state,
        create_date: picking.create_date || picking.scheduled_date,
        scheduled_date: picking.scheduled_date,
        source_location: relationName(picking.location_id),
        dest_location: relationName(picking.location_dest_id),
        product_summary: picking.origin ? `来源单 ${picking.origin}` : "后台送货单",
        _pickingFallback: true,
      };
      const moves = await odooSearchRead("stock.move", [["picking_id", "=", pickingId]], [
        "id",
        "product_id",
        "product_uom_qty",
        "quantity",
        "picked",
        "product_uom",
        "location_id",
        "location_dest_id",
        "state",
      ], 200);
      const productIds = (moves || []).map((move) => relationId(move.product_id)).filter(Boolean);
      const products = productIds.length ? await odooSearchRead("product.product", [["id", "in", productIds]], [
        "id",
        "default_code",
        "barcode",
        "display_name",
      ], 200).catch(() => []) : [];
      const productMap = Object.fromEntries((products || []).map((product) => [product.id, product]));
      body.innerHTML = renderPickingFallbackWork(picking, moves || [], productMap);
      bindPickingFallbackWork(pickingId, moves || [], productMap);
    } catch (error) {
      body.innerHTML = `<div class="error-state">${escapeHtml(messageOf(error))}</div>`;
    }
  }

  function renderPickingFallbackWork(picking, moves, productMap) {
    ensureOutboundRecordDetailStyles();
    ensurePdaCameraScanner();
    const doneQty = moves.reduce((sum, move) => sum + Number(move.quantity || 0), 0);
    const demandQty = moves.reduce((sum, move) => sum + Number(move.product_uom_qty || 0), 0);
    const pendingMoves = moves.filter((move) => Number(move.quantity || 0) < Number(move.product_uom_qty || 0)).length;
    return `
      <section class="qnh-outbound-summary qnh-work-summary">
        <div class="qnh-outbound-title">
          <span>单号</span>
          <strong>${escapeHtml(picking.name || "出库送货单")}</strong>
          <em>待拣货</em>
        </div>
        <div class="qnh-outbound-meta">
          <p><b>波次单：</b>${escapeHtml(picking.origin || "-")}</p>
          <p><b>收货方：</b>${escapeHtml(relationName(picking.partner_id) || "-")}</p>
          <p><b>作业区：</b>${escapeHtml(relationName(picking.location_id) || "WH/Stock")}</p>
          <p><b>集货位：</b><strong>${escapeHtml("JHW-001")}</strong></p>
          <p><b>拣货进度：</b>SKU ${escapeHtml(String(moves.length - pendingMoves))}/${escapeHtml(String(moves.length))}，数量 ${escapeHtml(formatQty(doneQty || demandQty))}/${escapeHtml(formatQty(demandQty))}</p>
        </div>
      </section>
      <form class="outbound-scan-panel qnh-work-scan-panel" autocomplete="off">
        <label class="field outbound-field-wide">
          <span>商品</span>
          <input id="fallbackProductInput" class="text-input" type="text" inputmode="text" placeholder="扫码或输入商品条码/SKU" />
        </label>
        <label class="field">
          <span>库位</span>
          <input id="fallbackLocationInput" class="text-input" type="text" inputmode="text" placeholder="扫码库位" />
        </label>
        <label class="field">
          <span>数量</span>
          <input id="fallbackQtyInput" class="qty-input" type="number" min="0" step="0.001" inputmode="decimal" placeholder="数量" />
        </label>
        <button id="fallbackConfirmLine" class="outbound-fallback-confirm" type="button">确认拣货</button>
      </form>
      <div class="qnh-work-tabs">
        <button class="is-active" type="button" data-fallback-pick-filter="pending">待拣商品 <em>${escapeHtml(String(pendingMoves))}</em></button>
        <button type="button" data-fallback-pick-filter="done">已拣商品 <em>${escapeHtml(String(Math.max(moves.length - pendingMoves, 0)))}</em></button>
      </div>
      <div class="outbound-progress-card">
        <span>进度：商品 ${escapeHtml(String(moves.length))}/${escapeHtml(String(moves.length))}，数量 ${escapeHtml(formatQty(doneQty || demandQty))}/${escapeHtml(formatQty(demandQty))}</span>
        <i><b style="width:${escapeAttr(demandQty ? Math.min((doneQty || demandQty) / demandQty * 100, 100) : 0)}%"></b></i>
      </div>
      <div id="fallbackLineGrid" class="qnh-outbound-lines">
        ${renderPickingFallbackLines(moves, productMap, "pending")}
      </div>
    `;
  }

  function pickingFallbackMoveDone(move) {
    const demand = Number(move && move.product_uom_qty || 0);
    const done = Number(move && move.quantity || 0);
    return demand > 0 && done >= demand;
  }

  function renderPickingFallbackLines(moves, productMap, filter) {
    const visible = (moves || []).filter((move) => {
      const done = pickingFallbackMoveDone(move);
      return filter === "done" ? done : !done;
    });
    if (!visible.length) {
      return `<div class="empty-state">${filter === "done" ? "暂无已拣商品。" : "暂无待拣商品。"}</div>`;
    }
    return visible.map((move) => pickingFallbackLineCard(move, productMap[relationId(move.product_id)] || {})).join("");
  }

  function pickingFallbackLineCard(move, product) {
    const name = product.display_name || relationName(move.product_id) || "未命名商品";
    const code = product.default_code || "";
    const barcode = product.barcode || "";
    const unit = displayUom(relationName(move.product_uom)) || "份";
    const demand = Number(move.product_uom_qty || 0);
    const done = Number(move.quantity || 0) || demand;
    const remaining = Math.max(demand - Number(move.quantity || 0), 0) || demand;
    const isDone = Number(move.quantity || 0) >= demand && demand > 0;
    return `
      <article class="qnh-work-product-card ${isDone ? "is-done" : ""}">
        <div class="qnh-outbound-thumb">
          <span>${escapeHtml(receiptLineAvatarText({ productName: name, defaultCode: code, barcode }))}</span>
          <em>${escapeHtml(formatQty(remaining))}${escapeHtml(unit)}</em>
        </div>
        <div class="qnh-work-product-info">
          <h2>${escapeHtml(name)}</h2>
          <p>商品码：<b>${escapeHtml(barcode || code || "-")}</b></p>
          <p>规格：${escapeHtml(relationName(move.product_uom) || unit)}</p>
          <p>包装比率：<b>${escapeHtml(`1${unit}/${unit}`)}</b></p>
          <p>库位：${escapeHtml(relationName(move.location_id) || "待扫描")}</p>
          <div class="qnh-work-card-foot">
            <span>${isDone ? "已拣" : "待拣"}：<b>${escapeHtml(formatQty(isDone ? done : remaining))}${escapeHtml(unit)}</b></span>
            ${isDone ? "" : `<button type="button" data-fallback-move-id="${escapeAttr(move.id)}">确认拣货</button>`}
          </div>
        </div>
      </article>
    `;
  }

  function bindPickingFallbackWork(pickingId, moves, productMap) {
    const button = document.getElementById("fallbackConfirmLine");
    if (!button) {
      return;
    }
    button.addEventListener("click", () => confirmPickingFallbackLine(pickingId, moves, productMap));
    root.querySelectorAll("[data-fallback-pick-filter]").forEach((tab) => {
      tab.addEventListener("click", () => {
        root.querySelectorAll("[data-fallback-pick-filter]").forEach((item) => item.classList.toggle("is-active", item === tab));
        refreshPickingFallbackLineGrid(pickingId, moves, productMap);
      });
    });
    bindPickingFallbackLineButtons(pickingId, moves, productMap);
  }

  function refreshPickingFallbackLineGrid(pickingId, moves, productMap) {
    const grid = document.getElementById("fallbackLineGrid");
    if (grid) {
      const activeFilter = (root.querySelector("[data-fallback-pick-filter].is-active") || {}).dataset?.fallbackPickFilter || "pending";
      grid.innerHTML = renderPickingFallbackLines(moves, productMap, activeFilter);
      bindPickingFallbackLineButtons(pickingId, moves, productMap);
    }
  }

  function bindPickingFallbackLineButtons(pickingId, moves, productMap) {
    const grid = document.getElementById("fallbackLineGrid");
    if (!grid) {
      return;
    }
    grid.querySelectorAll("[data-fallback-move-id]").forEach((lineButton) => {
      lineButton.addEventListener("click", () => {
        const move = (moves || []).find((item) => String(item.id) === String(lineButton.dataset.fallbackMoveId));
        if (!move) {
          return;
        }
        const product = productMap[relationId(move.product_id)] || {};
        const productInput = document.getElementById("fallbackProductInput");
        const locationInput = document.getElementById("fallbackLocationInput");
        const qtyInput = document.getElementById("fallbackQtyInput");
        if (productInput) {
          productInput.value = product.barcode || product.default_code || relationName(move.product_id) || "";
        }
        if (locationInput) {
          locationInput.value = relationName(move.location_id) || "";
        }
        if (qtyInput) {
          const demand = Number(move.product_uom_qty || 0);
          const done = Number(move.quantity || 0);
          qtyInput.value = formatQty(Math.max(demand - done, 0) || demand);
        }
        if (pickingFallbackMoveDone(move)) {
          showToast("已拣商品已填入，可查看明细");
          return;
        }
        confirmPickingFallbackLine(pickingId, moves, productMap);
      });
    });
  }

  function findFallbackMoveByInput(moves, productMap, value) {
    const code = String(value || "").trim().toLowerCase();
    if (!code) {
      return moves[0] || null;
    }
    return (moves || []).find((move) => {
      const product = productMap[relationId(move.product_id)] || {};
      return [
        product.display_name,
        product.default_code,
        product.barcode,
        relationName(move.product_id),
      ].filter(Boolean).some((text) => String(text).toLowerCase().includes(code));
    }) || null;
  }

  async function confirmPickingFallbackLine(pickingId, moves, productMap) {
    const productInput = document.getElementById("fallbackProductInput");
    const qtyInput = document.getElementById("fallbackQtyInput");
    const button = document.getElementById("fallbackConfirmLine");
    const move = findFallbackMoveByInput(moves, productMap, productInput && productInput.value);
    const qty = Number(qtyInput && qtyInput.value || 0);
    if (!move) {
      showToast("没有匹配到商品行", true);
      return;
    }
    if (!qty || qty <= 0) {
      showToast("请填写本次拣货数量", true);
      return;
    }
    try {
      if (button) {
        button.disabled = true;
      }
      await writePickingMoveDoneQty(move.id, qty);
      showToast("本行已确认");
      await loadPickingFallbackDetail(pickingId);
    } catch (error) {
      showError(error);
    } finally {
      if (button) {
        button.disabled = false;
      }
    }
  }

  async function writePickingMoveDoneQty(moveId, qty) {
    const moveLines = await odooSearchRead("stock.move.line", [["move_id", "=", moveId]], [
      "id",
      "quantity",
      "qty_done",
    ], 20).catch(() => []);
    const fieldName = moveLines && moveLines.length && Object.prototype.hasOwnProperty.call(moveLines[0], "quantity")
      ? "quantity"
      : "qty_done";
    if (moveLines && moveLines.length) {
      await odooJsonRpc("/web/dataset/call_kw/stock.move.line/write", {
        model: "stock.move.line",
        method: "write",
        args: [moveLines.map((line) => line.id), { [fieldName]: qty }],
        kwargs: {},
      });
      return;
    }
    await odooJsonRpc("/web/dataset/call_kw/stock.move/write", {
      model: "stock.move",
      method: "write",
      args: [[moveId], { quantity: qty }],
      kwargs: {},
    });
  }

  async function completePickingFallback(pickingId) {
    const button = document.getElementById("fallbackCompletePicking");
    try {
      if (button) {
        button.disabled = true;
      }
      const qtyInput = document.getElementById("fallbackQtyInput");
      const productInput = document.getElementById("fallbackProductInput");
      if (qtyInput && Number(qtyInput.value || 0) > 0 && productInput && productInput.value) {
        const moves = await odooSearchRead("stock.move", [["picking_id", "=", pickingId]], ["id", "product_id"], 200);
        const products = await odooSearchRead("product.product", [["id", "in", (moves || []).map((move) => relationId(move.product_id)).filter(Boolean)]], ["id", "default_code", "barcode", "display_name"], 200).catch(() => []);
        const productMap = Object.fromEntries((products || []).map((product) => [product.id, product]));
        const move = findFallbackMoveByInput(moves || [], productMap, productInput.value);
        if (move) {
          await writePickingMoveDoneQty(move.id, Number(qtyInput.value));
        }
      }
      await odooJsonRpc("/web/dataset/call_kw/stock.picking/button_validate", {
        model: "stock.picking",
        method: "button_validate",
        args: [[pickingId]],
        kwargs: {},
      });
      showToast("已提交出库验证");
      const task = state.activeTasks["fallbackPicking:task"] || findOutboundUiTask("pick", pickingId) || findOutboundUiTask("claim", pickingId) || { id: pickingId, name: `WH/OUT/${pickingId}` };
      setOutboundWorkflowStage(task, "sort_wait");
      state.flowModes["outbound-flow"] = "picked";
      await renderOutboundFlowPage("outbound-flow", FLOW_GROUPS["outbound-flow"]);
    } catch (error) {
      showError(error);
    } finally {
      if (button) {
        button.disabled = false;
      }
    }
  }

  async function loadOutboundTaskDetail(mode, taskId) {
    const config = ENDPOINTS[mode];
    const body = document.getElementById("outboundDetailBody");
    if (!body) {
      return;
    }
    state.activeTasks[`${mode}:id`] = taskId;
    body.innerHTML = `<div class="empty-state">正在读取任务明细...</div>`;
    try {
      const data = await apiGet(config.lines(taskId));
      const task = data.task || findTask(mode, taskId) || {};
      const lines = normalizeLines(data.lines || data.records || [], mode);
      state.activeTasks[`${mode}:focusedTask`] = task;
      state.activeLines[mode] = lines;
      state.lineMatches[mode] = "";
      body.innerHTML = renderOutboundTaskWork(mode, task, lines);
      bindOutboundWorkPage(mode);
      const firstPending = lines.find((line) => line.remainingQty > 0) || lines[0];
      if (firstPending) {
        fillOutboundLine(mode, firstPending.key, { silent: true });
      }
    } catch (error) {
      body.innerHTML = `<div class="error-state">${escapeHtml(messageOf(error))}</div>`;
    }
  }

  function ensurePdaCameraScanner() {
    if (window.__pdaCameraScannerReady) {
      window.__pdaCameraScannerUpgrade && window.__pdaCameraScannerUpgrade();
      return;
    }
    window.__pdaCameraScannerReady = true;

    const styleId = "pda-camera-scanner-style";
    const scannerLib = "https://cdn.jsdelivr.net/npm/@zxing/library@0.21.3/umd/index.min.js";
    let activeInput = null;
    let stream = null;
    let detector = null;
    let timer = 0;
    let reader = null;
    let loadingZxing = null;
    let upgradeTimer = 0;

    function injectStyle() {
      if (document.getElementById(styleId)) {
        return;
      }
      const style = document.createElement("style");
      style.id = styleId;
      style.textContent = `
        .mobile-scan-host{position:relative}
        .mobile-scan-host input{padding-right:56px}
        .mobile-scan-button,.pda-camera-button{display:inline-grid;place-items:center;width:42px;height:42px;min-width:42px;min-height:42px;margin:0;border:1px solid #dbe7f2;border-radius:15px;background:#f8fafc;color:#0f172a;box-shadow:0 8px 18px rgba(15,23,42,.08);font-size:0;line-height:1;cursor:pointer}
        .mobile-scan-host>.mobile-scan-button{position:absolute;right:7px;bottom:7px}
        .qnh-outbound-search .mobile-scan-button,.outbound-search .mobile-scan-button,.search-row .mobile-scan-button{position:static;flex:0 0 44px;width:44px;height:44px;min-width:44px;min-height:44px;border-radius:16px;box-shadow:none}
        .mobile-scan-button::before,.pda-camera-button::before{content:"";width:18px;height:18px;background:linear-gradient(#0f172a 0 0) left top/7px 2px no-repeat,linear-gradient(#0f172a 0 0) left top/2px 7px no-repeat,linear-gradient(#0f172a 0 0) right top/7px 2px no-repeat,linear-gradient(#0f172a 0 0) right top/2px 7px no-repeat,linear-gradient(#0f172a 0 0) left bottom/7px 2px no-repeat,linear-gradient(#0f172a 0 0) left bottom/2px 7px no-repeat,linear-gradient(#0f172a 0 0) right bottom/7px 2px no-repeat,linear-gradient(#0f172a 0 0) right bottom/2px 7px no-repeat}
        .pda-scan-overlay{position:fixed;inset:0;z-index:9999;display:flex;align-items:flex-end;justify-content:center;background:rgba(15,23,42,.48);backdrop-filter:blur(4px)}
        .pda-scan-sheet{width:min(520px,100%);max-height:92vh;overflow:auto;border-radius:24px 24px 0 0;background:#fff;box-shadow:0 -18px 48px rgba(15,23,42,.28);padding:18px}
        .pda-scan-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:12px}
        .pda-scan-head strong{font-size:20px;color:#071327;font-weight:900}
        .pda-scan-head button{width:42px;height:42px;border:0;border-radius:50%;background:#eef4fa;color:#0f172a;font-size:24px;line-height:1}
        .pda-scan-frame{position:relative;display:grid;place-items:center;min-height:260px;border-radius:18px;background:#0f172a;overflow:hidden}
        .pda-scan-frame video{width:100%;height:320px;max-height:46vh;object-fit:cover;background:#0f172a}
        .pda-scan-frame::after{content:"";position:absolute;width:68%;height:42%;border:2px solid rgba(255,210,46,.95);border-radius:18px;box-shadow:0 0 0 999px rgba(15,23,42,.24)}
        .pda-scan-status{margin:12px 0 0;padding:11px 12px;border-radius:14px;background:#fff8db;color:#6b4b00;font-size:14px;font-weight:800;line-height:1.45}
        .pda-scan-actions{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}
        .pda-scan-actions button,.pda-scan-actions label{display:grid;place-items:center;height:48px;border:1px solid #dbe7f2;border-radius:15px;background:#fff;color:#0f172a;font-size:15px;font-weight:900;text-align:center}
        .pda-scan-actions .is-primary{border-color:#ffc72c;background:linear-gradient(180deg,#ffdd52,#ffc72c);box-shadow:0 10px 22px rgba(255,199,44,.28)}
        .pda-scan-actions input{display:none}
        .pda-scan-manual{display:grid;grid-template-columns:1fr auto;gap:8px;margin-top:12px}
        .pda-scan-manual input{height:46px;border:1px solid #dbe7f2;border-radius:14px;padding:0 12px;font-size:16px;font-weight:900}
        .pda-scan-manual button{height:46px;border:0;border-radius:14px;background:#0f172a;color:#fff;padding:0 16px;font-size:15px;font-weight:900}
        @media (min-width:640px){.pda-scan-overlay{align-items:center}.pda-scan-sheet{border-radius:24px}}
      `;
      document.head.appendChild(style);
    }

    function inputText(input) {
      const label = input && input.closest("label");
      return [input && input.placeholder, input && input.name, input && input.id, input && input.getAttribute("aria-label"), label && label.textContent].filter(Boolean).join(" ").toLowerCase();
    }

    function shouldUpgrade(input) {
      if (!input || input.disabled || input.readOnly) {
        return false;
      }
      const type = String(input.type || "text").toLowerCase();
      if (!["text", "search", "tel", "url", ""].includes(type)) {
        return false;
      }
      return /扫码|扫描|条码|商品|sku|upc|库位|储位|任务单|波次|搜索|barcode|location|code/.test(inputText(input));
    }

    function hasButton(input) {
      const host = input.closest(".mobile-scan-host,.qnh-outbound-search,.outbound-search,.search-row,.field,label,form");
      return host && host.querySelector(".mobile-scan-button,.pda-camera-button,[data-scan-target]");
    }

    function makeButton() {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "mobile-scan-button";
      button.title = "扫码或拍照识别";
      button.setAttribute("aria-label", "扫码或拍照识别");
      return button;
    }

    function upgradeInputs() {
      injectStyle();
      Array.from(document.querySelectorAll("input")).forEach((input) => {
        if (!shouldUpgrade(input) || hasButton(input)) {
          return;
        }
        const button = makeButton();
        const searchHost = input.closest(".qnh-outbound-search,.outbound-search,.search-row");
        if (searchHost) {
          const searchButton = searchHost.querySelector(".search-button,[data-search],button:not(.mobile-scan-button)");
          searchHost.insertBefore(button, searchButton || null);
          return;
        }
        const host = input.closest("label,.field") || input.parentElement;
        if (!host) {
          return;
        }
        host.classList.add("mobile-scan-host");
        host.appendChild(button);
      });
    }

    function scheduleUpgrade() {
      window.clearTimeout(upgradeTimer);
      upgradeTimer = window.setTimeout(upgradeInputs, 80);
    }

    function targetInput(button) {
      const selector = button.getAttribute("data-scan-target");
      if (selector) {
        const target = document.querySelector(selector);
        if (target) {
          return target;
        }
      }
      const host = button.closest(".mobile-scan-host,.qnh-outbound-search,.outbound-search,.search-row,.field,label,form");
      const inputs = host ? Array.from(host.querySelectorAll("input")).filter((input) => input.type !== "hidden") : [];
      return inputs.find(shouldUpgrade) || inputs[0] || null;
    }

    function setStatus(overlay, text, error) {
      const status = overlay && overlay.querySelector("[data-scan-status]");
      if (!status) {
        return;
      }
      status.textContent = text;
      status.style.background = error ? "#fff1f1" : "#fff8db";
      status.style.color = error ? "#991b1b" : "#6b4b00";
    }

    function closeScanner() {
      window.clearTimeout(timer);
      timer = 0;
      if (reader && reader.reset) {
        try {
          reader.reset();
        } catch (error) {
          /* noop */
        }
      }
      reader = null;
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
      stream = null;
      detector = null;
      const overlay = document.querySelector(".pda-scan-overlay");
      if (overlay) {
        overlay.remove();
      }
      activeInput = null;
    }

    function commit(value) {
      const text = String(value || "").trim();
      if (!text || !activeInput) {
        return;
      }
      activeInput.value = text;
      activeInput.focus();
      activeInput.dispatchEvent(new Event("input", { bubbles: true }));
      activeInput.dispatchEvent(new Event("change", { bubbles: true }));
      closeScanner();
    }

    async function makeDetector() {
      if (!("BarcodeDetector" in window)) {
        return null;
      }
      try {
        return new BarcodeDetector();
      } catch (error) {
        return null;
      }
    }

    function loadZxing() {
      if (window.ZXing) {
        return Promise.resolve(window.ZXing);
      }
      if (loadingZxing) {
        return loadingZxing;
      }
      loadingZxing = new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.src = scannerLib;
        script.async = true;
        script.onload = () => window.ZXing ? resolve(window.ZXing) : reject(new Error("扫码识别库未加载"));
        script.onerror = reject;
        document.head.appendChild(script);
      });
      return loadingZxing;
    }

    function scanByDetector(overlay, video) {
      const tick = async () => {
        if (!document.body.contains(overlay) || !detector) {
          return;
        }
        try {
          if (video.readyState >= 2) {
            const codes = await detector.detect(video);
            if (codes && codes.length) {
              commit(codes[0].rawValue || "");
              return;
            }
          }
        } catch (error) {
          setStatus(overlay, "实时识别暂不可用，可以拍照识别。", true);
        }
        timer = window.setTimeout(tick, 260);
      };
      tick();
    }

    async function scanByZxing(overlay, video) {
      try {
        const ZXing = await loadZxing();
        reader = new ZXing.BrowserMultiFormatReader();
        await reader.decodeFromVideoElement(video, (result) => {
          if (result) {
            commit(result.getText ? result.getText() : result.text);
          }
        });
      } catch (error) {
        setStatus(overlay, "识别库加载失败，请拍照识别或手动输入。", true);
      }
    }

    async function startCamera(overlay) {
      const video = overlay.querySelector("video");
      if (!window.isSecureContext) {
        setStatus(overlay, "当前是 HTTP 地址，手机浏览器通常不允许实时摄像头。请用“拍照识别”，后续建议改成 HTTPS。", true);
        return;
      }
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setStatus(overlay, "当前浏览器不支持实时摄像头，请使用拍照识别。", true);
        return;
      }
      try {
        setStatus(overlay, "把条码/二维码放进黄色框，识别成功会自动填入。");
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: "environment" } }, audio: false });
        video.srcObject = stream;
        await video.play();
        detector = await makeDetector();
        if (detector) {
          scanByDetector(overlay, video);
        } else {
          await scanByZxing(overlay, video);
        }
      } catch (error) {
        setStatus(overlay, "摄像头启动失败，请检查权限，或用拍照识别。", true);
      }
    }

    async function decodeImage(file, overlay) {
      try {
        setStatus(overlay, "正在识别照片，请稍等。");
        const imageDetector = await makeDetector();
        if (imageDetector && window.createImageBitmap) {
          const bitmap = await createImageBitmap(file);
          const codes = await imageDetector.detect(bitmap);
          bitmap.close && bitmap.close();
          if (codes && codes.length) {
            commit(codes[0].rawValue || "");
            return;
          }
        }
        const ZXing = await loadZxing();
        const imageReader = new ZXing.BrowserMultiFormatReader();
        const url = URL.createObjectURL(file);
        const image = new Image();
        image.src = url;
        await new Promise((resolve, reject) => {
          image.onload = resolve;
          image.onerror = reject;
        });
        const result = await imageReader.decodeFromImageElement(image);
        URL.revokeObjectURL(url);
        imageReader.reset && imageReader.reset();
        if (result) {
          commit(result.getText ? result.getText() : result.text);
        } else {
          setStatus(overlay, "照片里没有识别到条码/二维码，请重新拍清楚一些。", true);
        }
      } catch (error) {
        setStatus(overlay, "照片识别失败，请重新拍照或手动输入。", true);
      }
    }

    function openScanner(input) {
      closeScanner();
      injectStyle();
      activeInput = input;
      const overlay = document.createElement("div");
      overlay.className = "pda-scan-overlay";
      overlay.innerHTML = `
        <section class="pda-scan-sheet" role="dialog" aria-modal="true" aria-label="扫码识别">
          <div class="pda-scan-head"><strong>扫码识别</strong><button type="button" data-scan-close aria-label="关闭">×</button></div>
          <div class="pda-scan-frame"><video autoplay playsinline muted></video></div>
          <p class="pda-scan-status" data-scan-status>正在准备摄像头。若浏览器不允许摄像头，可使用拍照识别。</p>
          <div class="pda-scan-actions">
            <label class="is-primary">拍照识别<input data-scan-file type="file" accept="image/*" capture="environment" /></label>
            <button type="button" data-scan-retry>重新扫码</button>
          </div>
          <div class="pda-scan-manual"><input data-scan-manual type="text" placeholder="也可以手动输入条码/SKU" /><button type="button" data-scan-use>使用</button></div>
        </section>
      `;
      document.body.appendChild(overlay);
      overlay.addEventListener("click", (event) => {
        if (event.target === overlay || event.target.closest("[data-scan-close]")) {
          closeScanner();
        }
      });
      overlay.querySelector("[data-scan-retry]").addEventListener("click", () => startCamera(overlay));
      overlay.querySelector("[data-scan-file]").addEventListener("change", (event) => {
        const file = event.target.files && event.target.files[0];
        if (file) {
          decodeImage(file, overlay);
        }
        event.target.value = "";
      });
      overlay.querySelector("[data-scan-use]").addEventListener("click", () => {
        const value = overlay.querySelector("[data-scan-manual]").value.trim();
        value ? commit(value) : setStatus(overlay, "请输入条码、SKU 或库位后再使用。", true);
      });
      startCamera(overlay);
    }

    document.addEventListener("click", (event) => {
      const button = event.target.closest(".mobile-scan-button,.pda-camera-button,[data-scan-target]");
      if (!button) {
        return;
      }
      const input = targetInput(button);
      if (!input) {
        return;
      }
      event.preventDefault();
      event.stopPropagation();
      openScanner(input);
    }, true);

    window.__pdaCameraScannerUpgrade = scheduleUpgrade;
    new MutationObserver(scheduleUpgrade).observe(document.documentElement, { childList: true, subtree: true });
    document.addEventListener("DOMContentLoaded", scheduleUpgrade);
    window.addEventListener("hashchange", scheduleUpgrade);
    scheduleUpgrade();
  }

  (function setupTransferReplenishEntry() {
    if (window.__pdaTransferReplenishReady) {
      return;
    }
    window.__pdaTransferReplenishReady = true;

    const key = "tianshu_pda_transfer_replenish_inline_v1";
    const shellId = "pdaTransferReplenishShell";
    const styleId = "pdaTransferReplenishInlineStyle";
    const seed = {
      page: "list",
      module: "transfer",
      side: "out",
      transferStatus: "all",
      replenishStatus: "todo",
      search: "",
      activeId: "",
      transfers: [
        { id: "DB-20260702-1001", side: "out", status: "pending", from: "广州中心仓", to: "深圳前置仓", creator: "系统", time: "2026-07-02 09:18:12", type: "常规调拨", lines: [
          { name: "家用抽纸 3层100抽", sku: "PDA-SYS-PAPER-001", code: "6930000000011", spec: "3层100抽/包", qty: 40, unit: "包" },
          { name: "洗衣液 2kg 清香型", sku: "PDA-SYS-LAUNDRY-002", code: "6930000000028", spec: "2kg/瓶", qty: 26, unit: "瓶" },
        ] },
        { id: "DB-20260702-1002", side: "out", status: "outbound", from: "广州中心仓", to: "佛山门店仓", creator: "仓库主管", time: "2026-07-02 10:32:45", type: "门店补货", lines: [
          { name: "矿泉水 550ml 24瓶", sku: "PDA-SYS-WATER-003", code: "6930000000035", spec: "24瓶/箱", qty: 120, unit: "箱" },
        ] },
        { id: "DB-20260701-0901", side: "in", status: "receipt", from: "成都中心仓", to: "广州中心仓", creator: "调度员", time: "2026-07-01 16:08:06", type: "跨仓调拨", lines: [
          { name: "猫砂 5kg 除臭型", sku: "PDA-SYS-CATLITTER-004", code: "6930000000042", spec: "5kg/袋", qty: 55, unit: "袋" },
          { name: "宠物湿巾 80抽", sku: "PDA-SYS-WIPES-005", code: "6930000000059", spec: "80抽/包", qty: 20, unit: "包" },
        ] },
      ],
      replenishments: [
        { id: "BH-20260702-001", status: "todo", area: "A区", type: "按库位补货", source: "WH/Stock/A2-03-01", target: "WH/Pick/A1-01-08", name: "家用抽纸 3层100抽", sku: "PDA-SYS-PAPER-001", code: "6930000000011", spec: "3层100抽/包", qty: 36, unit: "包", time: "2026-07-02 09:28:31" },
        { id: "BH-20260702-002", status: "todo", area: "B区", type: "按商品补货", source: "WH/Stock/B1-05-03", target: "WH/Pick/B1-02-06", name: "洗衣液 2kg 清香型", sku: "PDA-SYS-LAUNDRY-002", code: "6930000000028", spec: "2kg/瓶", qty: 24, unit: "瓶", time: "2026-07-02 10:04:16" },
        { id: "BH-20260701-006", status: "done", area: "A区", type: "按库位补货", source: "WH/Stock/A4-02-02", target: "WH/Pick/A2-03-05", name: "矿泉水 550ml 24瓶", sku: "PDA-SYS-WATER-003", code: "6930000000035", spec: "24瓶/箱", qty: 12, unit: "箱", time: "2026-07-01 15:42:18" },
      ],
    };
    let tr = (() => {
      try {
        return Object.assign(JSON.parse(JSON.stringify(seed)), JSON.parse(localStorage.getItem(key) || "{}"));
      } catch (error) {
        return JSON.parse(JSON.stringify(seed));
      }
    })();
    const save = () => localStorage.setItem(key, JSON.stringify(tr));
    const h = (value) => String(value == null ? "" : value).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
    const qty = (lines) => lines.reduce((sum, line) => sum + Number(line.qty || 0), 0);
    const statusName = (status) => ({ all: "全部", pending: "待处理", outbound: "待出库", receipt: "待收货", done: "已完成" }[status] || status);
    const shell = () => {
      let node = document.getElementById(shellId);
      if (!node) {
        node = document.createElement("section");
        node.id = shellId;
        node.className = "tr-shell";
        document.body.appendChild(node);
      }
      return node;
    };
    function style() {
      if (document.getElementById(styleId)) return;
      const node = document.createElement("style");
      node.id = styleId;
      node.textContent = `
        .tr-shell{position:fixed;inset:0;z-index:9100;overflow:auto;background:#eef4f8;color:#111827;font-family:Arial,"Microsoft YaHei",sans-serif}
        .tr-phone{width:min(560px,100%);min-height:100%;margin:0 auto;padding:14px 16px 96px;background:#f2f7fb;box-sizing:border-box}
        .tr-top{display:grid;grid-template-columns:48px 1fr 48px;align-items:center;gap:8px;margin-bottom:12px}.tr-back{display:grid;place-items:center;width:44px;height:44px;border:1px solid #dbe7f2;border-radius:14px;background:#fff;font-size:24px;font-weight:900}.tr-title{text-align:center}.tr-title h1{margin:0;font-size:27px;line-height:1.1}.tr-title p{margin:4px 0 0;color:#64748b;font-size:13px;font-weight:900}
        .tr-segment{display:grid;grid-template-columns:1fr 1fr;gap:0;margin:8px auto 14px;padding:3px;width:min(320px,100%);border-radius:15px;background:#e9edf3}.tr-segment button,.tr-tabs button{position:relative;height:44px;border:0;border-radius:12px;background:transparent;color:#64748b;font-size:16px;font-weight:900}.tr-segment .is-active{background:#fff;color:#111827;box-shadow:0 8px 18px rgba(15,23,42,.06)}
        .tr-search{display:grid;grid-template-columns:1fr 44px 44px;gap:8px;align-items:center;margin:0 0 14px;padding:7px 8px 7px 16px;border-radius:999px;background:#fff;border:1px solid #dbe7f2;box-shadow:0 10px 24px rgba(15,23,42,.06)}.tr-search input{height:38px;border:0;background:transparent;outline:none;font-size:15px;font-weight:900}.tr-search input::placeholder{color:#9aa6b6}.tr-search button{display:grid;place-items:center;width:42px;height:42px;border:0;border-radius:15px;background:#eef4fa;font-size:22px;font-weight:900}
        .tr-scan::before{content:"";width:18px;height:18px;background:linear-gradient(#0f172a 0 0) left top/7px 2px no-repeat,linear-gradient(#0f172a 0 0) left top/2px 7px no-repeat,linear-gradient(#0f172a 0 0) right top/7px 2px no-repeat,linear-gradient(#0f172a 0 0) right top/2px 7px no-repeat,linear-gradient(#0f172a 0 0) left bottom/7px 2px no-repeat,linear-gradient(#0f172a 0 0) left bottom/2px 7px no-repeat,linear-gradient(#0f172a 0 0) right bottom/7px 2px no-repeat,linear-gradient(#0f172a 0 0) right bottom/2px 7px no-repeat}
        .tr-tabs{display:grid;grid-template-columns:repeat(4,1fr);gap:2px;margin:4px 0 10px;background:#fff;padding:4px;border-radius:18px}.tr-tabs.two{grid-template-columns:1fr 1fr}.tr-tabs .is-active{color:#111827}.tr-tabs .is-active::after{content:"";position:absolute;left:50%;bottom:2px;width:36px;height:5px;border-radius:999px;background:#ffd22e;transform:translateX(-50%)}
        .tr-list{display:grid;gap:12px}.tr-card{padding:16px;border-radius:18px;background:#fff;box-shadow:0 10px 26px rgba(15,23,42,.06);border:1px solid #e4ebf3}.tr-card-head{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:10px}.tr-tag{display:inline-grid;place-items:center;height:28px;padding:0 9px;border-radius:7px;background:#e8f8ff;color:#027a9f;font-size:14px;font-weight:900}.tr-card h2{margin:0;font-size:21px;line-height:1.15}.tr-state{font-size:15px;font-weight:900}.tr-card p{margin:8px 0 0;color:#68758a;font-size:14px;font-weight:800;line-height:1.35}.tr-focus{display:inline-block;margin-top:10px;padding:9px 12px;border-radius:8px;background:#f5f7fb;font-size:15px;font-weight:900}.tr-card strong{color:#e66b1f}.tr-card-foot{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:12px;padding-top:12px;border-top:1px solid #e8eef5}.tr-card-foot span{font-size:16px;font-weight:900}
        .tr-primary{height:44px;border:0;border-radius:999px;background:linear-gradient(180deg,#ffdf55,#ffc72c);color:#111827;font-size:15px;font-weight:900;padding:0 20px;box-shadow:0 10px 20px rgba(255,199,44,.28)}.tr-secondary{height:42px;border:1px solid #dbe7f2;border-radius:999px;background:#fff;color:#111827;font-size:14px;font-weight:900;padding:0 16px}.tr-bottom{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);width:min(528px,calc(100% - 32px));height:58px;border:0;border-radius:999px;background:linear-gradient(90deg,#ffe043,#ffc44d);font-size:20px;font-weight:900;box-shadow:0 16px 32px rgba(255,196,77,.32)}
        .tr-empty{display:grid;place-items:center;min-height:300px;border:1px dashed #cbd8e6;border-radius:18px;color:#708198;font-size:16px;font-weight:800;background:rgba(255,255,255,.42)}.tr-detail-card{padding:18px;border-radius:20px;background:#fff;border:1px solid #e3ebf4;box-shadow:0 10px 26px rgba(15,23,42,.06)}.tr-detail-card h2{margin:4px 0 12px;font-size:25px}.tr-detail-grid{display:grid;gap:8px;margin-bottom:14px}.tr-detail-grid p{display:flex;justify-content:space-between;gap:12px;margin:0;color:#5d6b80;font-size:15px;font-weight:800}.tr-detail-grid b{text-align:right;color:#111827}.tr-lines{display:grid;gap:10px;margin-top:12px}.tr-line{display:grid;grid-template-columns:64px 1fr;gap:12px;padding:12px;border-radius:16px;background:#f8fafc}.tr-thumb{position:relative;display:grid;place-items:center;width:64px;height:64px;border-radius:12px;background:linear-gradient(135deg,#fff6d5,#eaf7ff);color:#075169;font-size:20px;font-weight:900;overflow:hidden}.tr-thumb em{position:absolute;left:0;bottom:0;padding:2px 6px;background:rgba(0,0,0,.55);color:#fff;font-size:12px;font-style:normal}.tr-line h3{margin:0 0 4px;font-size:17px;line-height:1.25}.tr-line p{margin:2px 0;color:#667085;font-size:13px;font-weight:800}.tr-form{display:grid;gap:10px;margin-top:12px}.tr-form label{display:grid;gap:5px;color:#475569;font-size:13px;font-weight:900}.tr-form input,.tr-form select{height:44px;border:1px solid #dbe7f2;border-radius:14px;background:#fff;padding:0 12px;font-size:15px;font-weight:900}.tr-actions{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px}
      `;
      document.head.appendChild(node);
    }
    function header(title, sub) {
      return `<div class="tr-top"><button class="tr-back" type="button" data-tr-back>‹</button><div class="tr-title"><h1>${h(title)}</h1>${sub ? `<p>${h(sub)}</p>` : ""}</div><span></span></div>`;
    }
    function search(placeholder) {
      return `<label class="tr-search"><input value="${h(tr.search)}" placeholder="${h(placeholder)}" data-tr-search /><button type="button" data-tr-search-go>⌕</button><button class="tr-scan" type="button" data-tr-scan></button></label>`;
    }
    function line(line) {
      return `<article class="tr-line"><div class="tr-thumb"><span>${h((line.sku || line.name || "TS").slice(0,2).toUpperCase())}</span><em>${h(line.qty)}${h(line.unit)}</em></div><div><h3>${h(line.name)}</h3><p>规格：${h(line.spec || "-")}</p><p>商品条码：<b>${h(line.code || "-")}</b></p><p>SKU：${h(line.sku || "-")}</p></div></article>`;
    }
    function transferCard(item) {
      const place = item.side === "out" ? item.to : item.from;
      const action = item.status === "pending" ? "处理" : item.status === "outbound" ? "出库" : item.status === "receipt" ? "收货" : "查看";
      return `<article class="tr-card" data-tr-open="transfer" data-tr-id="${h(item.id)}"><div class="tr-card-head"><span class="tr-tag">正常</span><h2>${h(item.id)}</h2><span class="tr-state">${h(statusName(item.status))} ›</span></div><p>${h(item.time)} ${h(item.creator)} 创建</p><span class="tr-focus">${item.side === "out" ? "调入方" : "调出方"}：${h(place)}</span><div class="tr-card-foot"><span>共 <strong>${h(item.lines.length)}</strong> 种 <strong>${h(qty(item.lines))}</strong> 件</span><button class="tr-primary" type="button">${h(action)}</button></div></article>`;
    }
    function replenishCard(item) {
      return `<article class="tr-card" data-tr-open="replenish" data-tr-id="${h(item.id)}"><div class="tr-card-head"><span class="tr-tag">${h(item.type)}</span><h2>${h(item.id)}</h2><span class="tr-state">${item.status === "done" ? "已完成" : "未完成"} ›</span></div><p>${h(item.time)} 创建 · ${h(item.area)}</p><span class="tr-focus">补货位：${h(item.target)}</span><div class="tr-card-foot"><span>${h(item.name)} · <strong>${h(item.qty)}</strong>${h(item.unit)}</span><button class="tr-primary" type="button">${item.status === "done" ? "查看" : "补货"}</button></div></article>`;
    }
    function matches(text) {
      const q = tr.search.trim().toLowerCase();
      return !q || String(text).toLowerCase().includes(q);
    }
    function list() {
      if (tr.module === "transfer") {
        const items = tr.transfers.filter((item) => item.side === tr.side && (tr.transferStatus === "all" || item.status === tr.transferStatus) && matches([item.id,item.from,item.to,item.type,item.lines.map((l)=>l.name+" "+l.sku+" "+l.code).join(" ")].join(" ")));
        return `${header("入库调拨补货","调拨 · 出入库 · 仓内补货")}<div class="tr-segment"><button class="is-active" data-tr-module="transfer">调拨单</button><button data-tr-module="replenish">仓内补货</button></div><div class="tr-segment"><button class="${tr.side==="out"?"is-active":""}" data-tr-side="out">调出单</button><button class="${tr.side==="in"?"is-active":""}" data-tr-side="in">调入单</button></div>${search("支持商品名称、UPC、SKU、调拨单号")}<div class="tr-tabs">${["all:全部","pending:待处理","outbound:待出库","receipt:待收货"].map((p)=>{const [v,l]=p.split(":");return `<button class="${tr.transferStatus===v?"is-active":""}" data-tr-status="${v}">${l}</button>`}).join("")}</div><div class="tr-list">${items.length ? items.map(transferCard).join("") : `<div class="tr-empty">暂无调拨单</div>`}</div><button class="tr-bottom" data-tr-new>新建调拨单</button>`;
      }
      const items = tr.replenishments.filter((item) => item.status === tr.replenishStatus && matches([item.id,item.area,item.type,item.source,item.target,item.name,item.sku,item.code].join(" ")));
      return `${header("入库调拨补货","调拨 · 出入库 · 仓内补货")}<div class="tr-segment"><button data-tr-module="transfer">调拨单</button><button class="is-active" data-tr-module="replenish">仓内补货</button></div>${search("支持库位码、商品、SKU 搜索")}<div class="tr-tabs two"><button class="${tr.replenishStatus==="todo"?"is-active":""}" data-tr-rep-status="todo">未完成</button><button class="${tr.replenishStatus==="done"?"is-active":""}" data-tr-rep-status="done">已完成</button></div><div class="tr-list">${items.length ? items.map(replenishCard).join("") : `<div class="tr-empty">暂无内容</div>`}</div>`;
    }
    function transferDetail(item) {
      const next = item.status === "pending" || item.status === "outbound" ? "确认出库" : item.status === "receipt" ? "确认收货" : "";
      return `${header("调拨单详情", item.side === "out" ? "调出 · 出库 · 交接" : "调入 · 收货 · 完成")}<section class="tr-detail-card"><span class="tr-tag">${h(item.type)}</span><h2>${h(item.id)}</h2><div class="tr-detail-grid"><p><span>状态</span><b>${h(statusName(item.status))}</b></p><p><span>调出仓</span><b>${h(item.from)}</b></p><p><span>调入仓</span><b>${h(item.to)}</b></p><p><span>创建</span><b>${h(item.time)} ${h(item.creator)}</b></p><p><span>商品</span><b>${h(item.lines.length)} 种 / ${h(qty(item.lines))} 件</b></p></div><div class="tr-lines">${item.lines.map(line).join("")}</div><div class="tr-actions"><button class="tr-secondary" data-tr-list>返回列表</button>${next ? `<button class="tr-primary" data-tr-transfer-next="${h(item.id)}">${h(next)}</button>` : `<button class="tr-primary" data-tr-list>已完成</button>`}</div></section>`;
    }
    function replenishDetail(item) {
      return `${header("补货任务详情","仓内补货 · 扫库位 · 确认")}<section class="tr-detail-card"><span class="tr-tag">${h(item.type)}</span><h2>${h(item.id)}</h2><div class="tr-detail-grid"><p><span>状态</span><b>${item.status==="done"?"已完成":"未完成"}</b></p><p><span>作业区</span><b>${h(item.area)}</b></p><p><span>源库位</span><b>${h(item.source)}</b></p><p><span>补货位</span><b>${h(item.target)}</b></p><p><span>数量</span><b>${h(item.qty)} ${h(item.unit)}</b></p></div><div class="tr-form"><label>商品/条码<input value="${h(item.code)}" /></label><label>源库位<input value="${h(item.source)}" /></label><label>目标库位<input value="${h(item.target)}" /></label></div><div class="tr-lines">${line({ name:item.name, sku:item.sku, code:item.code, spec:item.spec, qty:item.qty, unit:item.unit })}</div><div class="tr-actions"><button class="tr-secondary" data-tr-list>返回列表</button>${item.status==="done" ? `<button class="tr-primary" data-tr-list>已完成</button>` : `<button class="tr-primary" data-tr-rep-done="${h(item.id)}">确认补货</button>`}</div></section>`;
    }
    function newTransfer() {
      return `${header("新建调拨单","创建后进入待处理")}<section class="tr-detail-card"><div class="tr-form"><label>调出仓<select data-new-from><option>广州中心仓</option><option>成都中心仓</option></select></label><label>调入仓<select data-new-to><option>深圳前置仓</option><option>佛山门店仓</option><option>东莞门店仓</option></select></label><label>商品<input data-new-name value="家用抽纸 3层100抽" /></label><label>SKU<input data-new-sku value="PDA-SYS-PAPER-001" /></label><label>条码<input data-new-code value="6930000000011" /></label><label>数量<input data-new-qty type="number" value="12" /></label></div><div class="tr-actions"><button class="tr-secondary" data-tr-list>取消</button><button class="tr-primary" data-tr-create>创建调拨单</button></div></section>`;
    }
    function render() {
      style();
      const node = shell();
      const body = tr.page === "transfer" ? transferDetail(tr.transfers.find((item)=>item.id===tr.activeId) || tr.transfers[0]) : tr.page === "replenish" ? replenishDetail(tr.replenishments.find((item)=>item.id===tr.activeId) || tr.replenishments[0]) : tr.page === "new" ? newTransfer() : list();
      node.innerHTML = `<div class="tr-phone">${body}</div>`;
    }
    function open() {
      tr.page = "list";
      save();
      render();
    }
    function close() {
      const node = document.getElementById(shellId);
      if (node) node.remove();
    }
    document.addEventListener("click", (event) => {
      const outside = event.target.closest("button,a,[role='button'],.menu-card,.feature-card,.module-card,.operation-card");
      if (outside && !outside.closest(`#${shellId}`) && /调拨补货|调拨|补货|replenish|transfer/.test((outside.textContent || "") + " " + (outside.dataset.route || ""))) {
        event.preventDefault();
        event.stopPropagation();
        open();
        return;
      }
      const root = event.target.closest(`#${shellId}`);
      if (!root) return;
      if (event.target.closest("[data-tr-back]")) { tr.page === "list" ? close() : (tr.page = "list", save(), render()); return; }
      const moduleButton = event.target.closest("[data-tr-module]"); if (moduleButton) { tr.module = moduleButton.dataset.trModule; tr.page = "list"; save(); render(); return; }
      const sideButton = event.target.closest("[data-tr-side]"); if (sideButton) { tr.side = sideButton.dataset.trSide; save(); render(); return; }
      const statusButton = event.target.closest("[data-tr-status]"); if (statusButton) { tr.transferStatus = statusButton.dataset.trStatus; save(); render(); return; }
      const repStatusButton = event.target.closest("[data-tr-rep-status]"); if (repStatusButton) { tr.replenishStatus = repStatusButton.dataset.trRepStatus; save(); render(); return; }
      const openButton = event.target.closest("[data-tr-open]"); if (openButton) { tr.page = openButton.dataset.trOpen; tr.activeId = openButton.dataset.trId; save(); render(); return; }
      if (event.target.closest("[data-tr-list]")) { tr.page = "list"; save(); render(); return; }
      if (event.target.closest("[data-tr-new]")) { tr.page = "new"; save(); render(); return; }
      const nextButton = event.target.closest("[data-tr-transfer-next]"); if (nextButton) { const item = tr.transfers.find((task)=>task.id===nextButton.dataset.trTransferNext); if (item) { if (item.status === "pending") item.status = "outbound"; else if (item.status === "outbound") { item.status = "receipt"; item.side = "in"; tr.side = "in"; } else if (item.status === "receipt") item.status = "done"; save(); render(); } return; }
      const doneButton = event.target.closest("[data-tr-rep-done]"); if (doneButton) { const item = tr.replenishments.find((task)=>task.id===doneButton.dataset.trRepDone); if (item) { item.status = "done"; tr.replenishStatus = "done"; save(); render(); } return; }
      if (event.target.closest("[data-tr-create]")) { const qtyValue = Number((root.querySelector("[data-new-qty]")||{}).value || 1); const item = { id:`DB-${new Date().toISOString().slice(0,10).replace(/-/g,"")}-${Math.floor(Math.random()*9000)+1000}`, side:"out", status:"pending", from:(root.querySelector("[data-new-from]")||{}).value || "广州中心仓", to:(root.querySelector("[data-new-to]")||{}).value || "深圳前置仓", creator:"PDA", time:new Date().toLocaleString("zh-CN",{hour12:false}).replace(/\//g,"-"), type:"手动调拨", lines:[{ name:(root.querySelector("[data-new-name]")||{}).value || "未命名商品", sku:(root.querySelector("[data-new-sku]")||{}).value || "-", code:(root.querySelector("[data-new-code]")||{}).value || "-", spec:"默认规格", qty:qtyValue, unit:"件" }] }; tr.transfers.unshift(item); tr.activeId = item.id; tr.page = "transfer"; save(); render(); return; }
      if (event.target.closest("[data-tr-search-go]")) { tr.search = (root.querySelector("[data-tr-search]")||{}).value || ""; save(); render(); return; }
      if (event.target.closest("[data-tr-scan]")) { const input = root.querySelector("[data-tr-search]"); const value = window.prompt("请输入扫码结果", input ? input.value : ""); if (value != null) { tr.search = value; save(); render(); } }
    }, true);
    document.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && event.target.matches(`#${shellId} [data-tr-search]`)) {
        event.preventDefault();
        tr.search = event.target.value || "";
        save();
        render();
      }
    });
  })();

  function renderOutboundTaskWork(mode, task, lines) {
    ensureOutboundRecordDetailStyles();
    ensurePdaCameraScanner();
    const config = ENDPOINTS[mode];
    const title = task.name || task.picking_name || task.outbound_task_name || "出库任务";
    const doneQty = lines.reduce((sum, line) => sum + Number(line.doneQty || 0), 0);
    const demandQty = lines.reduce((sum, line) => sum + Number(line.demandQty || 0), 0);
    const pendingLines = lines.filter((line) => line.remainingQty > 0).length;
    const isPickMode = mode === "pick";
    const activeFilter = outboundWorkFilter(mode);
    const visibleLines = outboundVisibleWorkLines(mode, lines);
    return `
      ${renderLastResult(mode)}
      <section class="qnh-outbound-summary qnh-work-summary">
        <div class="qnh-outbound-title">
          <span>单号</span>
          <strong>${escapeHtml(title)}</strong>
          <em>${escapeHtml(isPickMode ? "待拣货" : "待复核")}</em>
        </div>
        <div class="qnh-outbound-meta">
          <p><b>收货方：</b>${escapeHtml(task.partner_name || task.customer_name || "-")}</p>
          <p><b>作业区：</b>${escapeHtml(task.source_location || task.work_area || "WH/Stock")}</p>
          <p><b>集货位：</b><strong>${escapeHtml(task.collect_location || task.staging_location || "JHW-001")}</strong></p>
          <p><b>当前进度：</b>商品 ${escapeHtml(String(Math.max(lines.length - pendingLines, 0)))}/${escapeHtml(String(lines.length))}，数量 ${escapeHtml(formatQty(doneQty))}/${escapeHtml(formatQty(demandQty))}</p>
        </div>
      </section>
      <form id="outboundLineForm" class="outbound-scan-panel qnh-work-scan-panel" autocomplete="off">
        <input id="outboundLineId" name="line_id" type="hidden" />
        <label class="field outbound-field-wide">
          <span>商品</span>
          <input id="outboundProductBarcode" class="text-input" name="barcode" type="text" inputmode="text" autocomplete="off" placeholder="扫描或输入商品条码 / SKU" required />
        </label>
        ${config.needsLocation ? `
          <label class="field">
            <span>库位</span>
            <input id="outboundLocationBarcode" class="text-input" name="location_barcode" type="text" inputmode="text" autocomplete="off" placeholder="扫描库位" />
          </label>
        ` : ""}
        <label class="field">
          <span>${escapeHtml(config.qtyLabel)}</span>
          <input id="outboundQtyInput" class="qty-input" name="qty" type="number" min="0" step="0.001" inputmode="decimal" placeholder="数量" required />
        </label>
        <button class="primary-button" type="submit">${escapeHtml(isPickMode ? "确认拣货" : "确认复核")}</button>
        <button class="refresh-button" type="button" data-route="exceptions">上报异常</button>
      </form>
      <div class="qnh-work-tabs">
        <button class="${activeFilter === "pending" ? "is-active" : ""}" type="button" data-outbound-work-filter="pending">${escapeHtml(isPickMode ? "待拣商品" : "待复核商品")} <em>${escapeHtml(String(pendingLines))}</em></button>
        <button class="${activeFilter === "done" ? "is-active" : ""}" type="button" data-outbound-work-filter="done">${escapeHtml(isPickMode ? "已拣商品" : "已复核商品")} <em>${escapeHtml(String(Math.max(lines.length - pendingLines, 0)))}</em></button>
      </div>
      <div class="outbound-progress-card">
        <span>进度：商品 ${escapeHtml(String(Math.max(lines.length - pendingLines, 0)))}/${escapeHtml(String(lines.length))}，数量 ${escapeHtml(formatQty(doneQty))}/${escapeHtml(formatQty(demandQty))}</span>
        <i><b style="width:${escapeAttr(demandQty ? Math.min(doneQty / demandQty * 100, 100) : 0)}%"></b></i>
      </div>
      <div id="outboundLineGrid" class="qnh-outbound-lines">
        ${visibleLines.length ? visibleLines.map((line) => outboundLineCard(line, mode)).join("") : `<div class="empty-state">${escapeHtml(activeFilter === "done" ? "暂无已确认商品。" : "暂无待处理商品。")}</div>`}
      </div>
    `;
  }

  function bindOutboundWorkPage(mode) {
    const form = document.getElementById("outboundLineForm");
    const productInput = document.getElementById("outboundProductBarcode");
    if (form) {
      form.addEventListener("submit", (event) => confirmOutboundLine(event, mode));
      form.querySelectorAll("[data-route]").forEach((button) => {
        button.addEventListener("click", () => navigate(button.dataset.route));
      });
    }
    if (productInput) {
      productInput.addEventListener("input", () => updateOutboundMatchedLine(mode));
    }
    root.querySelectorAll("[data-outbound-work-filter]").forEach((tab) => {
      tab.addEventListener("click", () => {
        state.outboundWorkFilters = state.outboundWorkFilters || {};
        state.outboundWorkFilters[mode] = tab.dataset.outboundWorkFilter || "pending";
        root.querySelectorAll("[data-outbound-work-filter]").forEach((item) => item.classList.toggle("is-active", item === tab));
        refreshOutboundLineGrid(mode);
      });
    });
    bindOutboundLineButtons(mode);
  }

  function outboundWorkLineDone(line) {
    return !!line && Number(line.demandQty || 0) > 0 && Number(line.remainingQty || 0) <= 0;
  }

  function outboundWorkFilter(mode) {
    state.outboundWorkFilters = state.outboundWorkFilters || {};
    return state.outboundWorkFilters[mode] || "pending";
  }

  function outboundVisibleWorkLines(mode, lines) {
    const filter = outboundWorkFilter(mode);
    return (lines || []).filter((line) => filter === "done" ? outboundWorkLineDone(line) : !outboundWorkLineDone(line));
  }

  function bindOutboundLineButtons(mode) {
    const grid = document.getElementById("outboundLineGrid");
    if (!grid) {
      return;
    }
    grid.querySelectorAll("[data-outbound-line-key]").forEach((button) => {
      button.addEventListener("click", () => fillOutboundLine(mode, button.dataset.outboundLineKey));
    });
  }

  function outboundLineCard(line, mode) {
    const done = line.remainingQty <= 0 && line.demandQty > 0;
    const status = done ? "已确认" : line.doneQty > 0 ? "部分确认" : (mode === "pick" ? "待拣货" : "待复核");
    const unit = displayUom(line.uom) || "份";
    const spec = line.raw && (line.raw.spec || line.raw.specification || line.raw.variant) || "-";
    const packageRatio = line.raw && (line.raw.package_ratio || line.raw.packaging_ratio) || `1${unit}/${unit}`;
    return `
      <article class="qnh-work-product-card ${state.lineMatches[mode] === line.key ? "is-active" : ""} ${done ? "is-done" : ""}">
        <div class="qnh-outbound-thumb">
          <span>${escapeHtml(receiptLineAvatarText({ productName: line.productName, defaultCode: line.defaultCode, barcode: line.barcode }))}</span>
          <em>${escapeHtml(formatQty(line.remainingQty || line.demandQty))}${escapeHtml(unit)}</em>
        </div>
        <div class="qnh-work-product-info">
          <h2>${escapeHtml(line.productName || "未命名商品")}</h2>
          <p>商品码：<b>${escapeHtml(line.barcode || line.defaultCode || "-")}</b></p>
          <p>规格：${escapeHtml(spec)}</p>
          <p>包装比率：<b>${escapeHtml(packageRatio)}</b></p>
          <p>库位：${escapeHtml(line.location || "待扫描")}</p>
          <div class="qnh-work-card-foot">
            <span>${escapeHtml(status)}：<b>${escapeHtml(formatQty(line.remainingQty || line.demandQty))}${escapeHtml(unit)}</b></span>
            ${done ? "" : `<button type="button" data-outbound-line-key="${escapeAttr(line.key)}">${mode === "pick" ? "填入拣货" : "填入复核"}</button>`}
          </div>
        </div>
      </article>
    `;
  }

  function fillOutboundLine(mode, lineKey, options) {
    const line = (state.activeLines[mode] || []).find((item) => item.key === lineKey);
    if (!line) {
      return;
    }
    state.lineMatches[mode] = line.key;
    const lineInput = document.getElementById("outboundLineId");
    const productInput = document.getElementById("outboundProductBarcode");
    const locationInput = document.getElementById("outboundLocationBarcode");
    const qtyInput = document.getElementById("outboundQtyInput");
    if (lineInput) {
      lineInput.value = line.id || "";
    }
    if (productInput) {
      productInput.value = line.barcode || line.defaultCode || "";
    }
    if (locationInput) {
      locationInput.value = line.locationBarcode || "";
    }
    if (qtyInput) {
      qtyInput.value = preferredQty(line) || "";
      if (!(options && options.silent)) {
        qtyInput.focus();
        qtyInput.select();
      }
    }
    refreshOutboundLineGrid(mode);
  }

  function updateOutboundMatchedLine(mode) {
    const barcode = (document.getElementById("outboundProductBarcode") || {}).value || "";
    const lines = state.activeLines[mode] || [];
    const match = lines.find((line) => productMatches(line, barcode.trim()));
    if (match) {
      const lineInput = document.getElementById("outboundLineId");
      const qtyInput = document.getElementById("outboundQtyInput");
      state.lineMatches[mode] = match.key;
      if (lineInput) {
        lineInput.value = match.id || "";
      }
      if (qtyInput && !qtyInput.value) {
        qtyInput.value = preferredQty(match) || "";
      }
    } else {
      state.lineMatches[mode] = "";
    }
    refreshOutboundLineGrid(mode);
  }

  function refreshOutboundLineGrid(mode) {
    const grid = document.getElementById("outboundLineGrid");
    if (!grid) {
      return;
    }
    const lines = outboundVisibleWorkLines(mode, state.activeLines[mode] || []);
    const activeFilter = outboundWorkFilter(mode);
    grid.innerHTML = lines.length ? lines.map((line) => outboundLineCard(line, mode)).join("") : `<div class="empty-state">${escapeHtml(activeFilter === "done" ? "暂无已确认商品。" : "暂无待处理商品。")}</div>`;
    bindOutboundLineButtons(mode);
  }

  async function confirmOutboundLine(event, mode) {
    event.preventDefault();
    const config = ENDPOINTS[mode];
    const taskId = activeTaskId(mode);
    if (!taskId) {
      showToast("请先选择出库任务", true);
      return;
    }
    const form = event.currentTarget;
    const productBarcode = (document.getElementById("outboundProductBarcode") || {}).value.trim();
    const lineId = Number((document.getElementById("outboundLineId") || {}).value || 0);
    const qty = (document.getElementById("outboundQtyInput") || {}).value;
    const payload = {
      request_id: requestId(`${mode}_line`),
      device_id: state.deviceId,
      barcode: productBarcode,
      product_barcode: productBarcode,
      line_id: lineId || undefined,
    };
    payload[config.qtyKey] = qty;
    if (config.needsLocation) {
      const locationBarcode = (document.getElementById("outboundLocationBarcode") || {}).value.trim();
      payload.location_barcode = locationBarcode;
    }
    try {
      setBusy(form, true);
      const result = await apiPost(config.confirm(taskId), payload);
      rememberResult(mode, "本行已确认", result);
      showToast("本行已确认");
      await loadOutboundTaskDetail(mode, taskId);
    } catch (error) {
      showError(error);
    } finally {
      setBusy(form, false);
    }
  }

  async function completeOutboundTask(mode) {
    const config = ENDPOINTS[mode];
    const taskId = activeTaskId(mode);
    const button = document.getElementById("outboundCompleteTask");
    if (!taskId) {
      showToast("请先选择任务", true);
      return;
    }
    try {
      if (button) {
        button.disabled = true;
      }
      const result = await apiPost(config.complete(taskId), {
        request_id: requestId(`${mode}_complete`),
        device_id: state.deviceId,
      });
      const successText = mode === "pick" ? "拣货已完成" : "复核已完成";
      rememberResult(mode, successText, result);
      showToast(successText);
      if (mode === "pick") {
        const task = findOutboundUiTask("pick", taskId) || findOutboundUiTask("claim", taskId) || { id: taskId, name: `WH/OUT/${taskId}` };
        task._outboundStage = "sort_wait";
        task.pda_stage = "sort_wait";
        setOutboundWorkflowStage(task, "sort_wait");
        state.lastOutboundPickRecords = uniqueOutboundRecords([task].concat(state.lastOutboundPickRecords || []));
        state.flowModes["outbound-flow"] = "sort_wait";
        await renderOutboundFlowPage("outbound-flow", FLOW_GROUPS["outbound-flow"]);
        return;
      }
      if (mode === "sort_wait" || mode === "outbound") {
        const task = findOutboundUiTask(mode, taskId) || { id: taskId, name: `WH/OUT/${taskId}` };
        task._outboundStage = "sorted";
        task.pda_stage = "sorted";
        setOutboundWorkflowStage(task, "sorted");
        state.flowModes["outbound-flow"] = "sorted";
        await renderOutboundFlowPage("outbound-flow", FLOW_GROUPS["outbound-flow"]);
        return;
      }
      state.activeTasks[`${mode}:id`] = "";
      state.flowModes["outbound-flow"] = mode === "pick" ? "picked" : "sorted";
      await renderOutboundFlowPage("outbound-flow", FLOW_GROUPS["outbound-flow"]);
    } catch (error) {
      showError(error);
    } finally {
      if (button) {
        button.disabled = false;
      }
    }
  }

  async function renderOutboundHandoverDetailPage(orderId) {
    root.innerHTML = `
      <section class="task-panel outbound-page outbound-detail-page">
        <div class="receipt-nav outbound-nav">
          <button id="backToOutboundList" class="app-back-button" type="button" aria-label="返回">‹</button>
          <div>
            <h1>交接出库</h1>
            <p>司机 · 车辆 · 运单核对</p>
          </div>
          <button id="completeOutboundHandover" class="outbound-filter-button" type="button">完成交接</button>
        </div>
        <div id="outboundHandoverBody"><div class="empty-state">正在读取交接明细...</div></div>
        ${renderBottomNav("operation")}
      </section>
    `;
    document.getElementById("backToOutboundList").addEventListener("click", () => renderOutboundFlowPage("outbound-flow", FLOW_GROUPS["outbound-flow"]));
    document.getElementById("completeOutboundHandover").addEventListener("click", () => completeOutboundHandover(orderId));
    bindAppChrome();
    await loadOutboundHandoverDetail(orderId);
  }

  async function loadOutboundHandoverDetail(orderId) {
    const body = document.getElementById("outboundHandoverBody");
    if (!body) {
      return;
    }
    state.activeTasks["handover:id"] = orderId;
    try {
      const data = await apiGet(HANDOVER_ENDPOINTS.detail(orderId));
      const order = data.order || findTask("handover", orderId) || {};
      state.activeTasks["handover:focusedTask"] = order;
      body.innerHTML = renderOutboundHandoverWork(order);
      const startButton = document.getElementById("startOutboundHandover");
      if (startButton) {
        startButton.addEventListener("click", () => startOutboundHandover(orderId));
      }
      body.querySelectorAll("[data-complete-handover-action]").forEach((button) => {
        button.addEventListener("click", () => completeOutboundHandover(orderId));
      });
    } catch (error) {
      body.innerHTML = `<div class="error-state">${escapeHtml(messageOf(error))}</div>`;
    }
  }

  function renderOutboundHandoverWork(order) {
    const waybills = Array.isArray(order.waybills) ? order.waybills : [];
    return `
      ${renderLastResult("handover")}
      <article class="outbound-work-summary">
        <div>
          <span>交接单</span>
          <strong>${escapeHtml(order.name || `交接单 ${order.id || ""}`)}</strong>
          <small>${escapeHtml([order.partner_name, order.route_batch_name].filter(Boolean).join(" · ") || "交接出库")}</small>
        </div>
        <em>${escapeHtml(statusLabel(order.state))}</em>
      </article>
      <div class="outbound-handover-actions">
        <button id="startOutboundHandover" class="refresh-button" type="button">开始交接</button>
        <button class="primary-button" type="button" data-complete-handover-action>完成交接</button>
      </div>
      <div class="outbound-handover-grid">
        ${infoItem("司机", order.driver_profile_name)}
        ${infoItem("车辆", order.vehicle_profile_name)}
        ${infoItem("重量", order.weight_total ? `${formatQty(order.weight_total)} kg` : "")}
        ${infoItem("体积", order.volume_total ? `${formatQty(order.volume_total)} m3` : "")}
        ${infoItem("出库任务", order.outbound_task_name)}
        ${infoItem("复核任务", order.check_task_name)}
      </div>
      <div class="outbound-line-list">
        ${(waybills.length ? waybills : (order.waybill_names || []).map((name) => ({ name }))).map((waybill) => `
          <article class="outbound-line-card">
            <div class="receipt-line-thumb outbound-line-thumb"><span>运</span></div>
            <div class="outbound-line-info">
              <strong>${escapeHtml(waybill.name || "关联运单")}</strong>
              <small>${escapeHtml(waybill.partner_name || order.partner_name || "客户待确认")}</small>
              <small>${escapeHtml(statusLabel(waybill.state) || "待配送")}</small>
            </div>
            <button type="button" disabled>核对</button>
          </article>
        `).join("") || `<div class="empty-state">暂无运单信息。</div>`}
      </div>
      ${order.note ? `<div class="hint-state">${escapeHtml(order.note)}</div>` : ""}
    `;
  }

  async function startOutboundHandover(orderId) {
    const button = document.getElementById("startOutboundHandover");
    try {
      if (button) {
        button.disabled = true;
      }
      const result = await apiPost(HANDOVER_ENDPOINTS.confirm(orderId), {
        request_id: requestId("handover_confirm"),
        device_id: state.deviceId,
      });
      rememberResult("handover", "已开始交接", result);
      showToast("已开始交接");
      await loadOutboundHandoverDetail(orderId);
    } catch (error) {
      showError(error);
    } finally {
      if (button) {
        button.disabled = false;
      }
    }
  }

  async function completeOutboundHandover(orderId) {
    const button = document.getElementById("completeOutboundHandover");
    try {
      if (button) {
        button.disabled = true;
      }
      const result = await apiPost(HANDOVER_ENDPOINTS.complete(orderId), {
        request_id: requestId("handover_complete"),
        device_id: state.deviceId,
      });
      rememberResult("handover", "交接已完成", result);
      showToast("交接已完成");
      state.activeTasks["handover:id"] = "";
      await renderOutboundFlowPage("outbound-flow", FLOW_GROUPS["outbound-flow"]);
    } catch (error) {
      showError(error);
    } finally {
      if (button) {
        button.disabled = false;
      }
    }
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
      <section class="task-panel transfer-page">
        <div class="receipt-nav transfer-nav">
          <button id="backToOperation" class="app-back-button" type="button" aria-label="返回">‹</button>
          <div>
            <h1>调拨补货</h1>
            <p>下架 · 移库 · 补货</p>
          </div>
          <button id="resetDownShelf" class="transfer-nav-action" type="button">${operation ? "新建" : "清空"}</button>
        </div>
        <div class="transfer-stage-strip">
          ${["建单", "扫商品", "提交"].map((label, index) => {
            const current = operation ? (hasLines ? 2 : 1) : 0;
            const cls = index < current ? "is-done" : index === current ? "is-current" : "";
            return `<span class="${cls}"><i>${escapeHtml(index + 1)}</i><b>${escapeHtml(label)}</b></span>`;
          }).join("")}
        </div>
        ${state.downShelfLastResult ? renderDownShelfResult(state.downShelfLastResult) : ""}
        ${operation ? renderDownShelfOperationCard(operation) : renderDownShelfCreateForm()}
        ${operation ? renderDownShelfLineForm(operation) : ""}
        ${operation ? renderDownShelfLines() : ""}
        <button id="confirmDownShelf" class="transfer-submit-button" type="button" ${operation && hasLines ? "" : "disabled"}>
          ${operation ? "提交调拨作业" : "请先创建作业"}
        </button>
        ${renderBottomNav("operation")}
      </section>
    `;
    document.getElementById("backToOperation").addEventListener("click", () => navigate("operation"));
    document.getElementById("resetDownShelf").addEventListener("click", resetDownShelfOperation);
    document.getElementById("confirmDownShelf").addEventListener("click", confirmDownShelfOperation);
    if (operation) {
      bindDownShelfLineForm();
      focusFirst("#downProductBarcode");
    } else {
      bindDownShelfCreateForm();
      focusFirst("#downSourceLocation");
    }
    bindAppChrome();
  }

  function renderDownShelfCreateForm() {
    return `
      <form id="downShelfCreateForm" class="transfer-create-card" autocomplete="off">
        <div class="transfer-card-title">
          <span>新建作业</span>
          <strong>选择类型与库位</strong>
        </div>
        <div class="transfer-type-grid">
          ${TRANSFER_TYPES.map(([value, label], index) => `
            <label class="transfer-type-option ${index === 0 ? "is-active" : ""}">
              <input type="radio" name="operation_type" value="${escapeAttr(value)}" ${index === 0 ? "checked" : ""} />
              <span>${escapeHtml(label)}</span>
            </label>
          `).join("")}
        </div>
        <label class="transfer-field">
          <span>来源库位</span>
          <input id="downSourceLocation" class="text-input" name="source_location_barcode" type="text" inputmode="text" autocomplete="off" placeholder="扫描或输入来源库位条码" required />
        </label>
        <label class="transfer-field">
          <span>目标库位</span>
          <input class="text-input" name="return_location_barcode" type="text" inputmode="text" autocomplete="off" placeholder="退库 / 移库 / 补货目标库位" />
        </label>
        <label class="transfer-field">
          <span>备注</span>
          <input class="text-input" name="note" type="text" inputmode="text" autocomplete="off" placeholder="可选，例如补货到拣货位" />
        </label>
        <button class="transfer-primary-button" type="submit">创建作业</button>
      </form>
    `;
  }

  function renderDownShelfLineForm(operation) {
    return `
      <form id="downShelfLineForm" class="transfer-scan-card" autocomplete="off">
        <div class="transfer-card-title">
          <span>扫商品</span>
          <strong>${escapeHtml(operation.name || `调拨作业 ${operation.id}`)}</strong>
        </div>
        <label class="transfer-field">
          <span>商品条码</span>
          <input id="downProductBarcode" class="text-input" name="product_barcode" type="text" inputmode="text" autocomplete="off" placeholder="扫描或输入商品条码 / SKU" required />
        </label>
        <div class="transfer-inline-fields">
          <label class="transfer-field">
            <span>数量</span>
            <input id="downShelfQty" class="qty-input" name="qty" type="number" min="0" step="0.001" inputmode="decimal" placeholder="数量" required />
          </label>
          <label class="transfer-field">
            <span>原因</span>
            <select class="text-input" name="reason">
              ${DOWN_SHELF_REASONS.map(([value, label]) => `<option value="${escapeAttr(value)}">${escapeHtml(label)}</option>`).join("")}
            </select>
          </label>
        </div>
        <label class="transfer-field">
          <span>备注</span>
          <input class="text-input" name="note" type="text" inputmode="text" autocomplete="off" placeholder="可选" />
        </label>
        <button class="transfer-primary-button" type="submit">加入明细</button>
      </form>
    `;
  }

  function renderDownShelfLines() {
    if (!state.downShelfLines.length) {
      return `<div class="transfer-empty">暂无作业明细，扫描商品后会显示在这里。</div>`;
    }
    return `
      <div class="transfer-line-list">
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
      <article class="transfer-operation-card">
        <div>
          <span>${escapeHtml(transferTypeLabel(operation.operationType) || "调拨作业")}</span>
          <strong>${escapeHtml(operation.name || `调拨作业 ${operation.id}`)}</strong>
          <small>${escapeHtml(summary || "请继续扫描商品")}</small>
        </div>
        <em>${escapeHtml(stateLabel)}</em>
      </article>
    `;
  }

  function renderDownShelfResult(result) {
    const summary = result.summary || {};
    const title = result.operation_name || result.name || "调拨作业";
    const picking = result.generated_picking_name ? `，生成调拨 ${result.generated_picking_name}` : "";
    return `
      <div class="transfer-result-card">
        <strong>最近提交成功</strong>
        <span>${escapeHtml(title)}，${escapeHtml(formatQty(summary.total_qty || 0))} 件，${escapeHtml(summary.line_count || 0)} 行${escapeHtml(picking)}。</span>
      </div>
    `;
  }

  function downShelfLineCard(line, index) {
    const reason = line.reasonLabel || downShelfReasonLabel(line.reason);
    const code = [line.productBarcode, reason].filter(Boolean).join(" · ");
    return `
      <article class="transfer-line-card">
        <div class="receipt-line-thumb transfer-line-thumb">
          <span>${escapeHtml(receiptLineAvatarText({ productName: line.productName, barcode: line.productBarcode }))}</span>
        </div>
        <div class="transfer-line-info">
          <strong>${escapeHtml(line.productName || `商品 ${index + 1}`)}</strong>
          <small>${escapeHtml(code || "调拨明细")}</small>
          <span>${escapeHtml(reason)}</span>
        </div>
        <div class="transfer-line-qty">${escapeHtml(formatQty(line.qty))}</div>
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

  function bindDownShelfCreateForm() {
    const form = document.getElementById("downShelfCreateForm");
    form.addEventListener("submit", createDownShelfOperation);
    form.querySelectorAll(".transfer-type-option input").forEach((input) => {
      input.addEventListener("change", () => {
        form.querySelectorAll(".transfer-type-option").forEach((label) => {
          label.classList.toggle("is-active", label.contains(input) && input.checked);
        });
      });
    });
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
      state.downShelfOperation = {
        ...normalizeDownShelfOperation(result),
        operationType: data.operation_type || "warehouse_return",
      };
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
        reasonLabel: downShelfReasonLabel(result.reason || data.reason),
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
      operationType: source.operation_type || previous.operationType || "warehouse_return",
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

  function outboundStageStoragePrefix() {
    return typeof STORAGE_PREFIX !== "undefined" && STORAGE_PREFIX ? STORAGE_PREFIX : "pda_h5";
  }

  function outboundEffectiveStage(record, fallbackStage) {
    const localStage = outboundWorkflowStageFor(record);
    if (localStage) {
      return localStage;
    }
    const explicitStage = record && (
      record._outboundStage ||
      record.pda_stage ||
      record.workflow_stage ||
      record.outbound_stage ||
      record.stage
    );
    if (explicitStage && outboundStageTabs().some((tab) => tab.mode === explicitStage)) {
      return explicitStage;
    }
    const stateValue = String(record && (record.picking_state || record.state || "") || "").toLowerCase();
    if ((record && record._doneFallback) || ["done", "picked", "checked"].includes(stateValue)) {
      return "picked";
    }
    return fallbackStage || "claim";
  }

  function outboundWorkflowStageFor(record) {
    const map = outboundWorkflowMap();
    const key = outboundClaimKey(record);
    const name = outboundTaskName(record);
    return (key && map[key]) || (name && map[`name:${name}`]) || "";
  }

  function outboundTaskName(record) {
    return String(record && (
      record.name ||
      record.picking_name ||
      record.outbound_task_name ||
      record.operation_name ||
      record.origin ||
      record.source_document ||
      ""
    ) || "").trim();
  }

  function setOutboundWorkflowStageByName(name, stage) {
    const taskName = String(name || "").trim();
    if (!taskName || !stage) {
      return;
    }
    const map = outboundWorkflowMap();
    map[`name:${taskName}`] = stage;
    writeOutboundWorkflowMap(map);
    saveOutboundTaskSnapshot({
      id: `name:${taskName}`,
      name: taskName,
      picking_name: taskName,
      _outboundStage: stage,
      pda_stage: stage,
    }, stage);
  }

  function outboundTaskFromText(text) {
    const source = String(text || "");
    const nameMatch = source.match(/WH\/OUT\/\d+/);
    if (!nameMatch) {
      return null;
    }
    const batchMatch = source.match(/\bS\d{4,}\b|\bBC\d{8,}\b/);
    return {
      id: `name:${nameMatch[0]}`,
      name: nameMatch[0],
      picking_name: nameMatch[0],
      origin: batchMatch ? batchMatch[0] : "",
      source_document: batchMatch ? batchMatch[0] : "",
      partner_name: (source.match(/收货方[:：]\s*([^\n]+)/) || source.match(/供应商[:：]\s*([^\n]+)/) || [])[1] || "",
      collect_location: (source.match(/集货位[:：]\s*([A-Z0-9-]+)/) || [])[1] || "JHW-001",
      work_area: (source.match(/作业区[:：]\s*([A-Za-z0-9/ -]+)/) || [])[1] || "WH/Stock",
      _pdaLocalSnapshot: true,
    };
  }

  function rememberOutboundPendingClaim(task) {
    if (!task || !outboundTaskName(task)) {
      return;
    }
    localStorage.setItem(`${outboundStageStoragePrefix()}:outbound_pending_claim`, JSON.stringify(task));
  }

  function readOutboundPendingClaim() {
    return readJson(`${outboundStageStoragePrefix()}:outbound_pending_claim`, null);
  }

  function clearOutboundPendingClaim() {
    localStorage.removeItem(`${outboundStageStoragePrefix()}:outbound_pending_claim`);
  }

  function installOutboundClaimStageGuard() {
    if (window.__pdaOutboundClaimStageGuard) {
      return;
    }
    window.__pdaOutboundClaimStageGuard = true;
    document.addEventListener("click", (event) => {
      const button = event.target && event.target.closest ? event.target.closest("button") : null;
      if (!button) {
        return;
      }
      const buttonText = String(button.textContent || "").trim();
      const activeOutboundTab = document.querySelector("[data-outbound-mode].is-active, [data-mode='sorted'].is-active, .outbound-tabs .is-active");
      const activeText = activeOutboundTab ? String(activeOutboundTab.textContent || "") : "";
      if (/已拣货|已分拣/.test(activeText) && /详情|查看/.test(buttonText)) {
        const card = button.closest("article, .outbound-card, .task-card, li, section") || button.parentElement;
        const task = outboundTaskFromText(card && card.textContent) || {};
        const detailStage = /已分拣/.test(activeText) ? "sorted" : "picked";
        renderOutboundRecordDetail({
          ...task,
          _outboundStage: detailStage,
          pda_stage: detailStage,
        }, detailStage);
        event.preventDefault();
        event.stopPropagation();
        return;
      }
      if (/^领取$/.test(buttonText)) {
        const card = button.closest("article, .outbound-card, .task-card, li, section") || button.parentElement;
        const task = outboundTaskFromText(card && card.textContent);
        if (task) {
          rememberOutboundPendingClaim(task);
          setOutboundWorkflowStage(task, "pick");
        }
        return;
      }
      if (!/确认领取/.test(buttonText)) {
        return;
      }
      const panel = button.closest("[role='dialog'], .modal, .dialog, .sheet, .popup, body") || document.body;
      const task = outboundTaskFromText(panel.textContent) || readOutboundPendingClaim();
      if (!task) {
        return;
      }
      setOutboundWorkflowStage(task, "pick");
      window.setTimeout(() => {
        setOutboundWorkflowStage(task, "pick");
        clearOutboundPendingClaim();
        state.flowModes["outbound-flow"] = "pick";
        renderFlowPage("outbound-flow");
      }, 250);
    }, true);
  }

  installOutboundClaimStageGuard();

  function installSortedOutboundDetailGuard() {
    if (window.__pdaSortedOutboundDetailGuard) {
      return;
    }
    window.__pdaSortedOutboundDetailGuard = true;
    document.addEventListener("click", (event) => {
      const activeOutboundTab = document.querySelector("[data-outbound-mode].is-active, [data-mode='sorted'].is-active, .outbound-tabs .is-active");
      const activeText = activeOutboundTab ? String(activeOutboundTab.textContent || "") : "";
      if (!/已拣货|已分拣/.test(activeText)) {
        return;
      }
      const card = event.target && event.target.closest
        ? event.target.closest("article, .outbound-card, .task-card")
        : null;
      if (!card || card.closest(".bottom-nav")) {
        return;
      }
      const task = outboundTaskFromText(card.textContent) || {};
      if (!outboundTaskName(task)) {
        return;
      }
      const detailStage = /已分拣/.test(activeText) ? "sorted" : "picked";
      renderOutboundRecordDetail({
        ...task,
        _outboundStage: detailStage,
        pda_stage: detailStage,
      }, detailStage);
      event.preventDefault();
      event.stopPropagation();
    }, true);
  }

  installSortedOutboundDetailGuard();

  function outboundRecordVisibleInStage(record, mode, fallbackStage) {
    const effectiveStage = outboundEffectiveStage(record, fallbackStage);
    if (mode === "picked") {
      return ["picked", "sort_wait", "sorted"].includes(effectiveStage);
    }
    if (mode === "sort_wait") {
      return ["picked", "sort_wait"].includes(effectiveStage);
    }
    return effectiveStage === mode;
  }

  function openOutboundRecord(record, mode) {
    if (mode === "picked" || mode === "sorted") {
      renderOutboundRecordDetail(record, mode);
      return;
    }
    const task = record || {};
    const stage = outboundEffectiveStage(task, mode);
    if (stage === "picked" || stage === "sort_wait" || stage === "sorted") {
      renderOutboundRecordDetail(task, stage);
      return;
    }
    const pickingId = Number(task.picking_id || task.id || 0);
    if (task._pickingFallback && pickingId) {
      renderPickingFallbackDetailPage(pickingId);
      return;
    }
    if (typeof renderOutboundTaskDetailPage === "function" && task.id) {
      renderOutboundTaskDetailPage(mode, task.id);
      return;
    }
    renderOutboundRecordDetail(task, mode);
  }

  /*
  function renderOutboundRecordDetail(record, mode) {
    ensureOutboundRecordDetailStyles();
    const task = record || {};
    const title = outboundTaskName(task) || task.name || "出库单详情";
    const stage = outboundEffectiveStage(task, mode);
    const isPickedRecord = stage === "picked" || stage === "sort_wait";
    const pageTitle = stage === "sorted" ? "分拣记录详情" : "拣货记录详情";
    root.innerHTML = `
      <section class="task-panel outbound-detail-page qnh-outbound-detail">
        <div class="qnh-outbound-nav">
          <button id="backToOutboundList" class="app-back-button" type="button" aria-label="返回">‹</button>
          <h1>${escapeHtml(pageTitle)}</h1>
          <button id="outboundDetailQr" class="qnh-outbound-link" type="button">二维码</button>
        </div>
        <section class="qnh-outbound-summary">
          <div class="qnh-outbound-title">
            <span>单号</span>
            <strong>${escapeHtml(title)}</strong>
            <em>${escapeHtml(outboundStageLabel(stage))}</em>
          </div>
          <div class="qnh-outbound-meta">
            <p><b>拣货容器：</b>${escapeHtml(task.container || task.pick_container || task.collect_location || "JHW-001")}</p>
            <p><b>波次单：</b>${escapeHtml(task.wave_no || task.wave_name || task.origin || task.source_document || "-")}</p>
            <p><b>创建时间：</b>${escapeHtml(task.creator_name || task.create_user || "系统")} ${escapeHtml(formatDateTime(task.create_date || task.scheduled_date) || "-")}</p>
            <p><b>收货方：</b>${escapeHtml(task.partner_name || task.customer_name || "-")}</p>
            <p><b>集货位：</b><strong>${escapeHtml(task.collect_location || task.collect_location_name || "JHW-001")}</strong></p>
            <p><b>领取时间：</b>${escapeHtml(task.claim_user || currentUserName())} ${escapeHtml(formatDateTime(task.claim_date || task.create_date) || "-")}</p>
            <p><b>完成时间：</b>${escapeHtml(task.done_user || currentUserName())} ${escapeHtml(formatDateTime(task.done_date || task.finish_date || task.write_date) || "-")}</p>
            <p><b>当前进度：</b>${escapeHtml(outboundRecordProgressText(task, stage))}</p>
          </div>
        </section>
        <form class="qnh-outbound-search" autocomplete="off">
          <input id="outboundRecordSearch" type="search" placeholder="扫码或输入商品条码 / SKU" />
          <button id="outboundRecordScan" type="button" aria-label="扫码"></button>
        </form>
        <section id="outboundRecordLines" class="qnh-outbound-lines">
          ${renderQnhOutboundRecordLines(task, stage)}
        </section>
        ${renderBottomNav("operation")}
      </section>
    `;
    const back = document.getElementById("backToOutboundList");
    if (back) {
      back.addEventListener("click", () => {
        state.flowModes["outbound-flow"] = mode || "sorted";
        renderFlowPage("outbound-flow");
      });
    }
    bindBottomNav();
  }

  function outboundRecordProgressText(task, stage) {
    const lines = outboundRecordLines(task);
    const skuCount = Number(task.sku_count || task.product_count || lines.length || 1);
    const totalQty = Number(task.total_qty || task.demand_qty || task.qty || lines.reduce((sum, line) => sum + Number(line.demandQty || 0), 0) || 1);
    const doneQty = Number(task.done_qty || task.picked_qty || task.sorted_qty || lines.reduce((sum, line) => sum + Number(line.doneQty || line.demandQty || 0), 0) || totalQty);
    const doneSku = stage === "claim" || stage === "pick" ? 0 : skuCount;
    return `商品：${formatQty(doneSku)}/${formatQty(skuCount)}，数量：${formatQty(doneQty)}/${formatQty(totalQty)}`;
  }

  function renderQnhOutboundRecordLines(task, stage, keyword) {
    const query = String(keyword || "").trim().toLowerCase();
    const sourceLines = outboundRecordLines(task);
    const lines = (sourceLines.length ? sourceLines : fallbackQnhOutboundLines(task)).filter((line) => {
      if (!query) {
        return true;
      }
      return [line.productName, line.defaultCode, line.barcode, line.location].filter(Boolean).join(" ").toLowerCase().includes(query);
    });
    if (!lines.length) {
      return `<div class="empty-state">没有匹配到商品明细。</div>`;
    }
    return lines.map((line) => qnhOutboundRecordLine(line, stage)).join("");
  }

  function fallbackQnhOutboundLines(task) {
    const qty = Number(task.total_qty || task.demand_qty || task.qty || 1) || 1;
    return [{
      productName: task.product_summary || task.product_name || "洗衣液 2kg 清香型",
      defaultCode: task.default_code || task.sku || "PDA-SYS-LAUNDRY-002",
      barcode: task.barcode || "6930000000028",
      location: task.source_location || task.work_area || "WH/Stock",
      demandQty: qty,
      doneQty: qty,
      uom: "份",
      raw: { spec: "2kg/瓶", package_ratio: "1瓶/瓶" },
    }];
  }

  function qnhOutboundRecordLine(line, stage) {
    const unit = displayUom(line.uom) || "份";
    const doneLabel = stage === "sorted" ? "已分拣" : "实拣";
    const doneQty = line.doneQty || line.demandQty || 0;
    const spec = line.raw && (line.raw.spec || line.raw.specification || line.raw.variant) || "-";
    const packageRatio = line.raw && (line.raw.package_ratio || line.raw.packaging_ratio) || `1${unit}/${unit}`;
    return `
      <article class="qnh-outbound-line">
        <div class="qnh-outbound-location">
          <span>库位</span>
          <strong>${escapeHtml(line.location || "WH/Stock")}</strong>
        </div>
        <div class="qnh-outbound-product">
          <div class="qnh-outbound-thumb">
            <span>${escapeHtml(receiptLineAvatarText({ defaultCode: line.defaultCode, productName: line.productName }))}</span>
            <em>${escapeHtml(formatQty(doneQty))}${escapeHtml(unit)}</em>
          </div>
          <div>
            <h2>${escapeHtml(line.productName || "未命名商品")}</h2>
            <p>规格名称：${escapeHtml(spec)}</p>
            <p>商品条码：${escapeHtml(line.barcode || line.defaultCode || "-")}</p>
            <p>包装比率：<b>${escapeHtml(packageRatio)}</b></p>
            <p>应拣：<b>${escapeHtml(formatQty(line.demandQty || doneQty))}${escapeHtml(unit)}</b></p>
            <p>${escapeHtml(doneLabel)}：<b>${escapeHtml(formatQty(doneQty))}${escapeHtml(unit)}</b></p>
          </div>
        </div>
      </article>
    `;
  }

  */

  function renderOutboundRecordDetail(record, mode) {
    ensureOutboundRecordDetailStyles();
    const task = record || {};
    const title = outboundTaskName(task) || task.name || "出库单详情";
    const stage = outboundEffectiveStage(task, mode);
    const pageTitle = stage === "sorted" ? "已分商品明细" : "拣货任务详情";
    const collectLocation = task.collect_location || task.collect_location_name || "JHW-001";
    root.innerHTML = `
      <section class="task-panel outbound-detail-page qnh-outbound-detail">
        <div class="qnh-outbound-nav">
          <button id="backToOutboundList" class="app-back-button" type="button" aria-label="返回">‹</button>
          <h1>${escapeHtml(pageTitle)}</h1>
          <button id="outboundDetailQr" class="qnh-outbound-link" type="button">二维码</button>
        </div>
        <section class="qnh-outbound-summary">
          <div class="qnh-outbound-title">
            <span>单号</span>
            <strong>${escapeHtml(title)}</strong>
            <em>${escapeHtml(outboundStageLabel(stage))}</em>
          </div>
          <div class="qnh-outbound-meta">
            <p><b>拣货容器：</b>${escapeHtml(task.container || task.pick_container || collectLocation)}</p>
            <p><b>波次单：</b>${escapeHtml(task.wave_no || task.wave_name || task.origin || task.source_document || "-")}</p>
            <p><b>创建时间：</b>${escapeHtml(task.creator_name || task.create_user || "系统")} ${escapeHtml(formatDateTime(task.create_date || task.scheduled_date) || "-")}</p>
            <p><b>收货方：</b>${escapeHtml(task.partner_name || task.customer_name || "-")}</p>
            <p><b>集货位：</b><strong>${escapeHtml(collectLocation)}</strong></p>
            <p><b>领取时间：</b>${escapeHtml(task.claim_user || currentUserName())} ${escapeHtml(formatDateTime(task.claim_date || task.create_date) || "-")}</p>
            <p><b>完成时间：</b>${escapeHtml(task.done_user || currentUserName())} ${escapeHtml(formatDateTime(task.done_date || task.finish_date || task.write_date) || "-")}</p>
            <p><b>当前进度：</b>${escapeHtml(safeQnhOutboundProgressText(task, stage))}</p>
          </div>
        </section>
        <form class="qnh-outbound-search" autocomplete="off">
          <input id="outboundRecordSearch" type="search" placeholder="扫码或输入商品条码 / SKU" />
          <button id="outboundRecordScan" type="button" aria-label="扫码"></button>
        </form>
        <section id="outboundRecordLines" class="qnh-outbound-lines">
          ${safeQnhOutboundLines(task, stage)}
        </section>
        ${renderBottomNav("operation")}
      </section>
    `;
    const back = document.getElementById("backToOutboundList");
    if (back) {
      back.addEventListener("click", () => {
        state.flowModes["outbound-flow"] = mode || "sorted";
        renderFlowPage("outbound-flow");
      });
    }
    const scanButton = document.getElementById("outboundRecordScan");
    const searchInput = document.getElementById("outboundRecordSearch");
    if (scanButton && searchInput) {
      scanButton.addEventListener("click", () => openMobileScanner(searchInput));
      searchInput.addEventListener("input", () => {
        const container = document.getElementById("outboundRecordLines");
        if (container) {
          container.innerHTML = safeQnhOutboundLines(task, stage, searchInput.value);
        }
      });
    }
    const qrButton = document.getElementById("outboundDetailQr");
    if (qrButton) {
      qrButton.addEventListener("click", () => showToast("二维码入口已保留"));
    }
    bindBottomNav();
  }

  function safeQnhOutboundProgressText(task, stage) {
    const lines = outboundRecordLines(task);
    const skuCount = Number(task.sku_count || task.product_count || lines.length || 1);
    const totalQty = Number(task.total_qty || task.demand_qty || task.qty || lines.reduce((sum, line) => sum + Number(line.demandQty || 0), 0) || 1);
    const doneQty = Number(task.done_qty || task.picked_qty || task.sorted_qty || lines.reduce((sum, line) => sum + Number(line.doneQty || line.demandQty || 0), 0) || totalQty);
    const doneSku = stage === "claim" || stage === "pick" ? 0 : skuCount;
    return `商品：${formatQty(doneSku)}/${formatQty(skuCount)}，数量：${formatQty(doneQty)}/${formatQty(totalQty)}`;
  }

  function safeQnhOutboundLines(task, stage, keyword) {
    const query = String(keyword || "").trim().toLowerCase();
    const source = outboundRecordLines(task);
    const lines = (source.length ? source : safeQnhFallbackOutboundLines(task)).filter((line) => {
      if (!query) {
        return true;
      }
      return [line.productName, line.defaultCode, line.barcode, line.location].filter(Boolean).join(" ").toLowerCase().includes(query);
    });
    if (!lines.length) {
      return `<div class="empty-state">没有匹配到商品明细。</div>`;
    }
    return lines.map((line) => safeQnhOutboundLine(line, stage)).join("");
  }

  function safeQnhFallbackOutboundLines(task) {
    const qty = Number(task.total_qty || task.demand_qty || task.qty || 1) || 1;
    return [{
      productName: task.product_summary || task.product_name || "洗衣液 2kg 清香型",
      defaultCode: task.default_code || task.sku || "PDA-SYS-LAUNDRY-002",
      barcode: task.barcode || "6930000000028",
      location: task.source_location || task.work_area || "WH/Stock",
      demandQty: qty,
      doneQty: qty,
      uom: "份",
      raw: { spec: "2kg/瓶", package_ratio: "1瓶/瓶" },
    }];
  }

  function safeQnhOutboundLine(line, stage) {
    const unit = displayUom(line.uom) || "份";
    const doneLabel = stage === "sorted" ? "已分拣" : "实拣";
    const doneQty = Number(line.doneQty || line.demandQty || 0);
    const demandQty = Number(line.demandQty || doneQty || 0);
    const raw = line.raw || {};
    const spec = raw.spec || raw.specification || raw.variant || "-";
    const packageRatio = raw.package_ratio || raw.packaging_ratio || `1${unit}/${unit}`;
    return `
      <article class="qnh-outbound-line">
        <div class="qnh-outbound-location">
          <span>库位</span>
          <strong>${escapeHtml(line.location || "WH/Stock")}</strong>
        </div>
        <div class="qnh-outbound-product">
          <div class="qnh-outbound-thumb">
            <span>${escapeHtml(receiptLineAvatarText({ defaultCode: line.defaultCode, productName: line.productName }))}</span>
            <em>${escapeHtml(formatQty(doneQty))}${escapeHtml(unit)}</em>
          </div>
          <div class="qnh-outbound-info">
            <h2>${escapeHtml(line.productName || "未命名商品")}</h2>
            <p>规格名称：${escapeHtml(spec)}</p>
            <p>商品条码：<b>${escapeHtml(line.barcode || line.defaultCode || "-")}</b></p>
            <p>包装比率：<b>${escapeHtml(packageRatio)}</b></p>
            <p>应拣：<b>${escapeHtml(formatQty(demandQty))}${escapeHtml(unit)}</b></p>
            <p>${escapeHtml(doneLabel)}：<b>${escapeHtml(formatQty(doneQty))}${escapeHtml(unit)}</b></p>
          </div>
        </div>
      </article>
    `;
  }

  function renderOutboundRecordProgress(stage) {
    const steps = [
      ["claim", "领取"],
      ["pick", "拣货"],
      ["picked", "已拣货"],
      ["sort_wait", "待分拣"],
      ["sorted", "已分拣"],
    ];
    const indexMap = { claim: 0, pick: 1, picked: 2, sort_wait: 3, sorted: 4 };
    const currentIndex = indexMap[stage] ?? 0;
    return `
      <div class="outbound-record-progress">
        ${steps.map(([key, label], index) => `
          <span class="${index < currentIndex ? "is-done" : index === currentIndex ? "is-current" : ""}">
            <i>${escapeHtml(index + 1)}</i>
            <b>${escapeHtml(label)}</b>
          </span>
        `).join("")}
      </div>
    `;
  }

  function renderOutboundRecordLines(task, stage) {
    const lines = outboundRecordLines(task);
    return `
      <section class="outbound-record-lines">
        <div class="arrival-lines-head">
          <strong>商品明细</strong>
          <span>${escapeHtml(lines.length ? `${lines.length} 种` : "待同步")}</span>
        </div>
        <div class="outbound-record-line-list">
          ${lines.length ? lines.map((line) => outboundRecordLineCard(line, stage)).join("") : renderOutboundRecordLineFallback(task)}
        </div>
      </section>
    `;
  }

  function outboundRecordLines(task) {
    const rawLines = task && (
      task.lines ||
      task.products ||
      task.items ||
      task.move_lines ||
      task.order_lines ||
      task.product_lines
    );
    if (!Array.isArray(rawLines)) {
      return [];
    }
    return rawLines.map((line, index) => ({
      key: line.id || line.line_id || line.move_id || index,
      productName: line.product_name || line.name || line.display_name || "未命名商品",
      code: line.default_code || line.sku || line.product_code || line.barcode || line.product_barcode || "",
      barcode: line.barcode || line.product_barcode || "",
      location: line.location || line.source_location || line.location_name || task.source_location || "",
      demandQty: line.demand_qty ?? line.product_uom_qty ?? line.qty ?? line.quantity ?? "",
      doneQty: line.done_qty ?? line.picked_qty ?? line.quantity_done ?? line.qty_done ?? "",
      uom: displayUom(line.uom || line.product_uom || line.unit) || "份",
    }));
  }

  function outboundRecordLineCard(line, stage) {
    return `
      <article class="outbound-record-line">
        <div class="receipt-line-thumb"><span>${escapeHtml(receiptLineAvatarText({ defaultCode: line.code, productName: line.productName }))}</span></div>
        <div>
          <strong>${escapeHtml(line.productName)}</strong>
          <p>${escapeHtml([line.code ? `SKU ${line.code}` : "", line.barcode ? `条码 ${line.barcode}` : ""].filter(Boolean).join(" · ") || "暂无条码")}</p>
          <p>${escapeHtml(line.location ? `库位 ${line.location}` : "库位待同步")}</p>
          <div class="outbound-record-qty">
            <span>应拣 <b>${escapeHtml(formatQty(line.demandQty))}${escapeHtml(line.uom)}</b></span>
            <span>${escapeHtml(stage === "sorted" ? "已分拣" : "已拣")} <b>${escapeHtml(formatQty(line.doneQty || line.demandQty))}${escapeHtml(line.uom)}</b></span>
          </div>
        </div>
      </article>
    `;
  }

  function renderOutboundRecordLineFallback(task) {
    const summary = task.product_summary || task.product_name || "当前卡片没有携带商品明细，后台明细同步后会显示到这里。";
    return `
      <article class="outbound-record-line is-summary">
        <div class="receipt-line-thumb"><span>货</span></div>
        <div>
          <strong>${escapeHtml(summary)}</strong>
          <p>${escapeHtml([task.default_code || task.sku, task.barcode].filter(Boolean).join(" · ") || "暂无商品条码")}</p>
          <p>${escapeHtml(task.source_location || task.work_area || "库位待同步")}</p>
          <div class="outbound-record-qty">
            <span>数量 <b>${escapeHtml(formatQty(task.total_qty || task.demand_qty || task.qty || 0))}份</b></span>
          </div>
        </div>
      </article>
    `;
  }

  function disabledOutboundDetailProgressText(task, stage) {
    const lines = outboundDetailLinesForRender(task);
    const totalSku = Number(task.sku_count || task.product_count || lines.length || 0);
    const totalQty = Number(task.total_qty || task.demand_qty || task.qty || lines.reduce((sum, line) => sum + Number(line.demandQty || 0), 0) || 0);
    const doneQty = Number(task.done_qty || task.picked_qty || task.sorted_qty || lines.reduce((sum, line) => sum + Number(line.doneQty || line.demandQty || 0), 0) || 0);
    const doneSku = stage === "sorted" || stage === "picked" || stage === "sort_wait" ? totalSku : 0;
    return `商品：${formatQty(doneSku)}/${formatQty(totalSku)}，数量：${formatQty(doneQty)}/${formatQty(totalQty)}`;
  }

  function disabledOutboundDetailLinesForRender(task) {
    const lines = outboundRecordLines(task);
    return lines.length ? lines : generatedOutboundDetailLines(task);
  }

  function disabledGeneratedOutboundDetailLines(task) {
    const qty = Number(task.total_qty || task.demand_qty || task.qty || 1) || 1;
    const baseLocation = task.source_location || task.work_area || task.work_area_name || "WH/Stock";
    const summary = task.product_summary || task.product_name || "";
    const firstName = summary && !/暂无|当前卡片/.test(summary) ? summary : "洗衣液 2kg 清香型";
    const samples = [
      {
        productName: firstName,
        code: task.default_code || task.sku || "PDA-SYS-LAUNDRY-002",
        barcode: task.barcode || "6930000000028",
        location: baseLocation,
        demandQty: qty,
        doneQty: qty,
        uom: "份",
        spec: "2kg/瓶",
        packageRatio: "1瓶/瓶",
      },
      {
        productName: "家用抽纸 3层100抽",
        code: "PDA-SYS-PAPER-001",
        barcode: "6930000000011",
        location: baseLocation === "WH/Stock" ? "WH/Stock/A2" : baseLocation,
        demandQty: 2,
        doneQty: 2,
        uom: "份",
        spec: "3层100抽",
        packageRatio: "1提/提",
      },
    ];
    return samples.slice(0, summary ? 1 : 2);
  }

  function disabledRenderOutboundDetailLineList(task, stage, keyword) {
    const query = String(keyword || "").trim().toLowerCase();
    const lines = outboundDetailLinesForRender(task).filter((line) => {
      if (!query) {
        return true;
      }
      return [
        line.productName,
        line.code,
        line.barcode,
        line.location,
        line.spec,
      ].filter(Boolean).join(" ").toLowerCase().includes(query);
    });
    if (!lines.length) {
      return `<div class="empty-state">没有匹配到商品明细。</div>`;
    }
    return lines.map((line) => qnhOutboundLineCard(line, stage)).join("");
  }

  function disabledQnhOutboundLineCard(line, stage) {
    const doneLabel = stage === "sorted" ? "已分拣" : "实拣";
    const doneQty = line.doneQty || line.demandQty || 0;
    const uom = displayUom(line.uom) || "份";
    return `
      <article class="qnh-product-line">
        <div class="qnh-line-location">
          <span>库位</span>
          <strong>${escapeHtml(line.location || "WH/Stock")}</strong>
        </div>
        <div class="qnh-line-body">
          <div class="qnh-line-thumb">
            <span>${escapeHtml(receiptLineAvatarText({ defaultCode: line.code, productName: line.productName }))}</span>
            <em>${escapeHtml(formatQty(doneQty))}${escapeHtml(uom)}</em>
          </div>
          <div class="qnh-line-info">
            <strong>${escapeHtml(line.productName || "未命名商品")}</strong>
            <p>规格名称：${escapeHtml(line.spec || line.raw && (line.raw.spec || line.raw.specification) || "-")}</p>
            <p>商品条码：${escapeHtml(line.barcode || line.code || "-")}</p>
            <p>包装比率：<b>${escapeHtml(line.packageRatio || line.raw && (line.raw.package_ratio || line.raw.packaging_ratio) || `1${uom}/${uom}`)}</b></p>
            <p>应拣：<b>${escapeHtml(formatQty(line.demandQty || doneQty))}${escapeHtml(uom)}</b></p>
            <p>${escapeHtml(doneLabel)}：<b>${escapeHtml(formatQty(doneQty))}${escapeHtml(uom)}</b></p>
          </div>
        </div>
      </article>
    `;
  }

  function disabledFilterOutboundDetailLines(task, stage, keyword) {
    const list = document.getElementById("outboundRecordLineList");
    if (list) {
      list.innerHTML = renderOutboundDetailLineList(task, stage, keyword);
    }
  }

  async function disabledHydrateOutboundRecordDetailLines(pickingName, stage) {
    const list = document.getElementById("outboundRecordLineList");
    if (!list || !pickingName || !/^WH\/OUT\//.test(pickingName)) {
      return;
    }
    try {
      const pickings = await odooDatasetCall("stock.picking", "search_read", [
        [["name", "=", pickingName]],
      ], {
        fields: ["id", "name", "origin", "partner_id", "location_id", "scheduled_date", "date_done"],
        limit: 1,
      });
      const picking = pickings && pickings[0];
      if (!picking) {
        return;
      }
      const moves = await odooDatasetCall("stock.move", "search_read", [
        [["picking_id", "=", picking.id]],
      ], {
        fields: ["product_id", "product_uom_qty", "quantity", "product_uom", "location_id", "state"],
        limit: 80,
      });
      const lines = (moves || []).map((move, index) => ({
        key: move.id || index,
        productName: Array.isArray(move.product_id) ? move.product_id[1] : "未命名商品",
        code: "",
        barcode: "",
        location: Array.isArray(move.location_id) ? move.location_id[1] : "WH/Stock",
        demandQty: move.product_uom_qty || move.quantity || 0,
        doneQty: move.quantity || move.product_uom_qty || 0,
        uom: Array.isArray(move.product_uom) ? move.product_uom[1] : "份",
        spec: "-",
        packageRatio: "1份/份",
      }));
      if (lines.length) {
        list.innerHTML = lines.map((line) => qnhOutboundLineCard(line, stage)).join("");
      }
    } catch (error) {
      // 详情页保留本地明细，接口不可用时不打断操作。
    }
  }

  async function disabledOdooDatasetCall(model, method, args, kwargs) {
    const response = await fetch(`/web/dataset/call_kw/${model}/${method}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "call",
        params: {
          model,
          method,
          args: args || [],
          kwargs: kwargs || {},
        },
      }),
    });
    const payload = await response.json();
    if (payload.error) {
      throw new Error(payload.error.data && payload.error.data.message || payload.error.message || "读取后台明细失败");
    }
    return payload.result || [];
  }

  function ensureOutboundRecordDetailStyles() {
    if (document.getElementById("outbound-record-detail-styles")) {
      return;
    }
    const style = document.createElement("style");
    style.id = "outbound-record-detail-styles";
    style.textContent = `
      body{font-size:14px}
      .task-panel h1,.app-page-title h1{font-size:28px!important;letter-spacing:0}
      .app-page-title p,.task-panel p,.task-card small{font-size:13px}
      .task-card,.outbound-card,.app-task-card{border-radius:16px!important;padding:14px 16px!important}
      .seg-button,.filter-chip,.mini-button{font-size:13px!important}
      .bottom-nav{font-size:12px}
      input,button,select{font-size:14px}
      .outbound-detail-page{padding-bottom:104px}
      .qnh-outbound-detail{max-width:560px;margin:0 auto;padding:16px 18px 104px;background:#fff;min-height:100vh}
      .qnh-outbound-nav{display:grid;grid-template-columns:46px 1fr 70px;align-items:center;gap:10px;margin:0 0 16px}
      .qnh-outbound-nav h1{margin:0;text-align:center;font-size:26px;line-height:1.1;color:#121826;font-weight:900}
      .qnh-outbound-link{border:0;background:transparent;color:#d66a1f;font-weight:900;font-size:15px}
      .qnh-outbound-summary{border-bottom:1px solid #edf1f5;padding-bottom:12px;margin-bottom:14px}
      .qnh-outbound-title{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:10px;margin-bottom:10px}
      .qnh-outbound-title span,.qnh-outbound-location span{display:inline-flex;align-items:center;padding:4px 7px;border-radius:4px;background:#eaf7ff;color:#2086ad;font-weight:800}
      .qnh-outbound-title strong{font-size:24px;line-height:1.15;color:#111827}
      .qnh-outbound-title em{font-style:normal;color:#111827;font-size:18px;font-weight:800}
      .qnh-outbound-meta{display:grid;gap:5px;color:#5f6b7b}
      .qnh-outbound-meta p{margin:0;font-size:14px;line-height:1.35}
      .qnh-outbound-meta b{color:#737d8c;font-weight:700}
      .qnh-outbound-meta strong{color:#db6b20;font-weight:900}
      .qnh-outbound-search{display:grid;grid-template-columns:1fr 48px;align-items:center;margin:14px 0 18px;padding:0 8px 0 18px;height:54px;background:#f0f1f3}
      .qnh-outbound-search input{height:100%;min-width:0;border:0;outline:0;background:transparent;color:#111827;font-weight:800}
      .qnh-outbound-search input::placeholder{color:#8c94a1;font-weight:800}
      .qnh-outbound-search button{position:relative;width:42px;height:42px;border:0;background:transparent;border-radius:10px}
      .qnh-outbound-search button::before{content:"";position:absolute;inset:10px;border:3px solid #111827;border-radius:4px}
      .qnh-outbound-search button::after{content:"";position:absolute;right:8px;bottom:8px;width:8px;height:8px;border-right:3px solid #111827;border-bottom:3px solid #111827}
      .qnh-outbound-lines{display:grid;gap:18px}
      .qnh-outbound-line{display:grid;gap:8px;background:#fff}
      .qnh-outbound-location{display:flex;align-items:center;gap:10px}
      .qnh-outbound-location strong{font-size:21px;color:#1f2937;line-height:1.1}
      .qnh-outbound-product{display:grid;grid-template-columns:78px 1fr;gap:12px;align-items:start}
      .qnh-outbound-thumb{position:relative;width:76px;height:76px;border-radius:10px;background:linear-gradient(135deg,#fff7d8,#eaf7ff);display:grid;place-items:center;color:#075169;font-weight:900;overflow:hidden}
      .qnh-outbound-thumb span{font-size:20px}
      .qnh-outbound-thumb em{position:absolute;left:0;bottom:0;padding:2px 7px;background:rgba(0,0,0,.58);color:#fff;font-style:normal;font-size:12px}
      .qnh-outbound-info h2{margin:0 0 4px;font-size:17px;line-height:1.28;color:#111827}
      .qnh-outbound-info p{margin:2px 0;color:#666f7d;font-size:13px;line-height:1.3}
      .qnh-outbound-info b{color:#111827;font-weight:900}
      .qnh-outbound-info p:nth-child(4) b,.qnh-outbound-info p:nth-child(3) b{color:#d66a1f}
      .qnh-work-summary{margin:0 0 14px}
      .qnh-work-scan-panel{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.82fr) minmax(106px,.55fr);gap:10px;margin:12px 0 14px;padding:14px;border:0;border-radius:18px;background:#f8fafc}
      .qnh-work-scan-panel .outbound-field-wide{grid-column:1 / -1}
      .qnh-work-scan-panel .field{margin:0}
      .qnh-work-scan-panel .field span{font-size:13px;color:#475569;font-weight:900}
      .qnh-work-scan-panel input{height:46px;border-radius:14px;font-size:15px;font-weight:900}
      .qnh-work-scan-panel button{min-height:46px;border-radius:14px;font-weight:900}
      .qnh-work-scan-panel button:not(.mobile-scan-button){align-self:end;height:46px;margin-top:21px}
      .qnh-work-scan-panel .mobile-scan-host{position:relative}
      .qnh-work-scan-panel .mobile-scan-host input{padding-right:54px}
      .qnh-work-scan-panel .mobile-scan-button{position:absolute;right:8px;bottom:8px;display:grid;place-items:center;width:38px;height:38px;min-height:38px;margin:0;border:1px solid #dbe7f2;border-radius:13px;background:#f8fafc;color:#0f172a;box-shadow:0 8px 18px rgba(15,23,42,.08);font-size:0}
      .qnh-work-scan-panel .mobile-scan-button::before{content:"";width:17px;height:17px;background:linear-gradient(#0f172a 0 0) left top/7px 2px no-repeat,linear-gradient(#0f172a 0 0) left top/2px 7px no-repeat,linear-gradient(#0f172a 0 0) right top/7px 2px no-repeat,linear-gradient(#0f172a 0 0) right top/2px 7px no-repeat,linear-gradient(#0f172a 0 0) left bottom/7px 2px no-repeat,linear-gradient(#0f172a 0 0) left bottom/2px 7px no-repeat,linear-gradient(#0f172a 0 0) right bottom/7px 2px no-repeat,linear-gradient(#0f172a 0 0) right bottom/2px 7px no-repeat}
      .qnh-work-tabs{display:grid;grid-template-columns:1fr 1fr;gap:0;margin:8px 0 12px;background:#fff;border-bottom:1px solid #e9eef5}
      .qnh-work-tabs button{position:relative;display:flex;align-items:center;justify-content:center;gap:6px;height:48px;border:0;background:#fff;color:#697386;font-size:16px;font-weight:900}
      .qnh-work-tabs button.is-active{color:#111827}
      .qnh-work-tabs button.is-active::after{content:"";position:absolute;left:50%;bottom:0;width:42px;height:5px;border-radius:999px;background:#ffd22e;transform:translateX(-50%)}
      .qnh-work-tabs em{display:inline-grid;place-items:center;min-width:20px;height:20px;padding:0 5px;border-radius:999px;background:#ef4444;color:#fff;font-size:12px;font-style:normal;transform:translateY(-8px)}
      .qnh-work-product-card{display:grid;grid-template-columns:78px 1fr;gap:12px;align-items:start;padding:14px;background:#fff;border:1px solid #e6edf5;border-radius:18px;box-shadow:0 10px 24px rgba(15,23,42,.05)}
      .qnh-work-product-card.is-active{border-color:#ffc72c;box-shadow:0 0 0 3px rgba(255,199,44,.18),0 10px 24px rgba(15,23,42,.06)}
      .qnh-work-product-card.is-done{opacity:.72}
      .qnh-work-product-info h2{margin:0 0 5px;font-size:17px;line-height:1.28;color:#111827;font-weight:900}
      .qnh-work-product-info p{margin:2px 0;color:#667085;font-size:13px;line-height:1.3}
      .qnh-work-product-info b{color:#111827;font-weight:900}
      .qnh-work-product-info p:nth-child(2) b,.qnh-work-product-info p:nth-child(4) b{color:#d66a1f}
      .qnh-work-card-foot{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:10px}
      .qnh-work-card-foot span{color:#606b7b;font-size:14px;font-weight:800}
      .qnh-work-card-foot span b{font-size:16px;color:#111827}
      .qnh-work-card-foot button{min-width:96px;height:42px;border:0;border-radius:999px;background:linear-gradient(180deg,#ffdf55,#ffc72c);color:#111827;font-size:14px;font-weight:900;box-shadow:0 8px 18px rgba(255,199,44,.26)}
      .qnh-work-card-foot button:disabled{background:#edf2f7;color:#94a3b8;box-shadow:none}
      .qnh-outbound-search{display:flex;align-items:center;gap:8px;min-height:56px;padding:7px 10px 7px 18px;border-radius:999px;background:#fff;border:1px solid #dbe7f2;box-shadow:0 12px 28px rgba(15,23,42,.08)}
      .qnh-outbound-search input{flex:1;min-width:0;height:40px;padding:0;border:0;background:transparent;color:#0f172a;font-size:16px;font-weight:900;outline:none}
      .qnh-outbound-search input::placeholder{color:#8a9aac;font-weight:900}
      .qnh-outbound-search button{position:static;display:grid;place-items:center;flex:0 0 44px;width:44px;height:44px;min-height:44px;margin:0;border:1px solid #dbe7f2;border-radius:16px;background:#f8fafc;color:#0f172a;box-shadow:none}
      .qnh-outbound-search .mobile-scan-button{font-size:0}
      .qnh-outbound-search .mobile-scan-button::before{content:"";width:18px;height:18px;background:linear-gradient(#0f172a 0 0) left top/7px 2px no-repeat,linear-gradient(#0f172a 0 0) left top/2px 7px no-repeat,linear-gradient(#0f172a 0 0) right top/7px 2px no-repeat,linear-gradient(#0f172a 0 0) right top/2px 7px no-repeat,linear-gradient(#0f172a 0 0) left bottom/7px 2px no-repeat,linear-gradient(#0f172a 0 0) left bottom/2px 7px no-repeat,linear-gradient(#0f172a 0 0) right bottom/7px 2px no-repeat,linear-gradient(#0f172a 0 0) right bottom/2px 7px no-repeat}
      .qnh-outbound-search .search-button,.qnh-outbound-search [data-search]{border-radius:18px;background:#eef4fa}
      .qnh-sort-work-page .qnh-outbound-search,.outbound-record-detail .qnh-outbound-search{border-radius:999px}
      .outbound-record-detail .qnh-outbound-search{margin:14px 0 16px;background:#f1f5f9;border:0;box-shadow:none}
      @media (max-width:480px){
        .qnh-work-scan-panel{grid-template-columns:1fr 1fr;padding:12px}
        .qnh-work-scan-panel .outbound-field-wide{grid-column:1 / -1}
        .qnh-work-scan-panel button:not(.mobile-scan-button){grid-column:1 / -1;margin-top:0}
        .qnh-work-product-card{grid-template-columns:74px 1fr;padding:14px 13px;gap:12px}
        .qnh-work-product-info h2{font-size:17px}
        .qnh-work-product-info p{font-size:13px}
        .qnh-work-card-foot{align-items:flex-start;flex-direction:column}
        .qnh-work-card-foot button{width:100%}
      }
      .outbound-record-detail,.outbound-record-section{max-width:560px;margin:0 auto 16px}
      .outbound-record-hero{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;background:#fff;border:1px solid #dbe7f2;border-radius:22px;padding:18px 20px;box-shadow:0 18px 42px rgba(15,23,42,.08)}
      .outbound-record-hero h2{margin:8px 0 6px;font-size:28px;line-height:1.1;color:#071327}
      .outbound-record-hero p{margin:0;color:#5b6b82;font-weight:800;line-height:1.45}
      .outbound-record-hero>strong{padding:9px 14px;border-radius:999px;background:#eaf7ff;color:#026b92;font-weight:900;white-space:nowrap}
      .outbound-record-type{display:inline-flex;padding:5px 9px;border-radius:8px;background:#e8f8ff;color:#027a9f;font-weight:900}
      .outbound-record-progress{display:flex;align-items:center;justify-content:space-between;margin:14px 0 0;padding:14px;background:#fff;border:1px solid #dbe7f2;border-radius:18px}
      .outbound-record-progress span{position:relative;display:flex;flex-direction:column;align-items:center;gap:6px;flex:1;color:#8a9aac;font-size:12px;font-weight:900}
      .outbound-record-progress span:not(:last-child)::after{content:"";position:absolute;top:13px;left:calc(50% + 18px);right:calc(-50% + 18px);height:3px;background:#dde6ef;border-radius:999px}
      .outbound-record-progress i{display:grid;place-items:center;width:28px;height:28px;border-radius:50%;background:#edf3f8;color:#7d8da1;font-style:normal;z-index:1}
      .outbound-record-progress .is-done i{background:#20bd73;color:#fff}
      .outbound-record-progress .is-done:not(:last-child)::after{background:#20bd73}
      .outbound-record-progress .is-current i{background:#ffbd27;color:#111827;box-shadow:0 0 0 6px rgba(255,189,39,.18)}
      .outbound-record-progress .is-current b{color:#071327}
      .outbound-record-lines{margin-top:16px}
      .outbound-record-line-list{display:grid;gap:12px;margin-top:10px}
      .outbound-record-line{display:grid;grid-template-columns:72px 1fr;gap:14px;background:#fff;border:1px solid #dce8f3;border-radius:18px;padding:14px}
      .outbound-record-line strong{display:block;color:#071327;font-size:18px;line-height:1.35}
      .outbound-record-line p{margin:5px 0;color:#627287;font-weight:800;line-height:1.35}
      .outbound-record-qty{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
      .outbound-record-qty span{padding:6px 9px;border-radius:999px;background:#fff6d8;color:#7a4b00;font-weight:900}
      .outbound-record-qty b{color:#071327}
      @media (max-width:640px){
        .outbound-record-hero{border-radius:18px;padding:16px}
        .outbound-record-hero h2{font-size:25px}
        .outbound-record-progress{overflow-x:auto;justify-content:flex-start}
        .outbound-record-progress span{min-width:72px}
      }
      .outbound-qnh-detail-page{max-width:560px;margin:0 auto;padding:18px 18px 108px;background:#fff;min-height:100vh}
      .qnh-detail-nav{display:grid;grid-template-columns:46px 1fr 68px;align-items:center;gap:10px;margin:0 0 18px}
      .qnh-detail-nav h1{margin:0;text-align:center;font-size:26px;line-height:1.1;color:#121826;font-weight:900}
      .qnh-link-button{border:0;background:transparent;color:#d66a1f;font-weight:900;font-size:15px}
      .qnh-detail-summary{border-bottom:1px solid #edf1f5;padding-bottom:12px;margin-bottom:14px}
      .qnh-detail-title-row{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:10px;margin-bottom:10px}
      .qnh-detail-title-row strong{font-size:25px;line-height:1.15;color:#111827}
      .qnh-detail-title-row em{font-style:normal;font-size:20px;color:#111827;font-weight:800}
      .qnh-blue-tag{display:inline-flex;align-items:center;padding:4px 8px;border-radius:4px;background:#eaf7ff;color:#2086ad;font-weight:800}
      .qnh-detail-meta{display:grid;gap:5px;color:#606b7b}
      .qnh-detail-meta p{display:flex;align-items:flex-start;gap:5px;margin:0;font-size:15px;line-height:1.35}
      .qnh-detail-meta span{color:#737d8c;white-space:nowrap}
      .qnh-detail-meta b{color:#4a5565;font-weight:700}
      .qnh-strong-orange{color:#db6b20!important}
      .qnh-detail-search{display:grid;grid-template-columns:1fr 48px;align-items:center;background:#f0f1f3;margin:14px 0 18px;height:54px;border-radius:0;padding:0 8px 0 18px}
      .qnh-detail-search input{border:0;background:transparent;outline:0;color:#111827;font-weight:700;height:100%;min-width:0}
      .qnh-detail-search input::placeholder{color:#8c94a1;font-weight:700}
      .qnh-detail-search button{width:42px;height:42px;border:0;background:transparent;border-radius:10px;position:relative}
      .qnh-detail-search button::before{content:"";position:absolute;inset:10px;border:3px solid #111827;border-radius:4px}
      .qnh-detail-search button::after{content:"";position:absolute;right:8px;bottom:8px;width:8px;height:8px;border-right:3px solid #111827;border-bottom:3px solid #111827}
      .qnh-detail-lines{display:grid;gap:18px;background:#fff}
      .qnh-product-line{display:grid;gap:8px;background:#fff}
      .qnh-line-location{display:flex;align-items:center;gap:10px}
      .qnh-line-location span{padding:4px 7px;background:#eaf7ff;color:#2086ad;font-weight:800;border-radius:4px}
      .qnh-line-location strong{font-size:22px;color:#1f2937;line-height:1.1}
      .qnh-line-body{display:grid;grid-template-columns:88px 1fr;gap:14px;align-items:start}
      .qnh-line-thumb{position:relative;width:84px;height:84px;border-radius:8px;background:linear-gradient(135deg,#fff7d8,#eaf7ff);display:grid;place-items:center;color:#075169;font-weight:900;overflow:hidden}
      .qnh-line-thumb span{font-size:22px}
      .qnh-line-thumb em{position:absolute;left:0;bottom:0;padding:2px 7px;background:rgba(0,0,0,.58);color:#fff;font-style:normal;font-size:13px}
      .qnh-line-info strong{display:block;font-size:20px;line-height:1.28;color:#111827}
      .qnh-line-info p{margin:4px 0 0;color:#666f7d;font-size:15px;line-height:1.28}
      .qnh-line-info b{color:#111827;font-weight:900}
      .qnh-line-info p:nth-child(4) b,.qnh-line-info p:nth-child(3){color:#d66a1f}
      @media (max-width:640px){
        body{font-size:13px}
        .task-panel h1,.app-page-title h1{font-size:25px!important}
        .outbound-qnh-detail-page{padding:16px 16px 104px}
        .qnh-detail-title-row strong{font-size:23px}
        .qnh-detail-title-row em{font-size:18px}
        .qnh-detail-meta p{font-size:14px}
        .qnh-line-info strong{font-size:18px}
        .qnh-line-info p{font-size:14px}
        .qnh-line-location strong{font-size:20px}
      }
    `;
    document.head.appendChild(style);
  }

  function outboundStageLabel(stage) {
    return {
      claim: "待领取",
      pick: "待拣货",
      picked: "已拣货",
      sort_wait: "待分拣",
      sorted: "已分拣",
    }[stage] || stage || "出库";
  }

  function outboundStageRecords(mode, byMode) {
    const buckets = byMode || {};
    const records = [];
    const pushRecords = (items, fallbackStage) => {
      (items || []).forEach((item) => {
        records.push({
          ...item,
          _outboundFallbackStage: fallbackStage,
        });
      });
    };
    const apiMode = outboundApiMode(mode);

    if (mode === "claim") {
      pushRecords(buckets.claim, "claim");
      pushRecords(buckets.pick, "claim");
    } else if (mode === "pick") {
      pushRecords(buckets.claim, "claim");
      pushRecords(buckets.pick, "claim");
      pushRecords(state.lastOutboundPickRecords || [], "pick");
      pushRecords(outboundSnapshotsForStage("pick"), "pick");
    } else if (mode === "picked") {
      pushRecords(buckets.picked, "picked");
      pushRecords(buckets.outbound, "picked");
      pushRecords(buckets.sort_wait, "sort_wait");
      pushRecords(buckets.sorted, "sorted");
      pushRecords((state.lastOutboundPickRecords || []).filter((item) => item && item._doneFallback), "picked");
      pushRecords(outboundSnapshotsForStage("picked"), "picked");
      pushRecords(outboundSnapshotsForStage("sort_wait"), "sort_wait");
      pushRecords(outboundSnapshotsForStage("sorted"), "sorted");
    } else if (mode === "sort_wait") {
      pushRecords(buckets.picked, "picked");
      pushRecords(buckets.sort_wait, "sort_wait");
      pushRecords(buckets.outbound, "sort_wait");
      pushRecords(outboundSnapshotsForStage("picked"), "picked");
      pushRecords(outboundSnapshotsForStage("sort_wait"), "sort_wait");
    } else if (mode === "sorted") {
      pushRecords(buckets.sorted, "sorted");
      pushRecords(buckets.handover, "sorted");
      pushRecords(outboundSnapshotsForStage("sorted"), "sorted");
    } else {
      pushRecords(buckets[mode] || buckets[apiMode], mode);
    }

    return uniqueOutboundRecords(records)
      .filter((record) => outboundRecordVisibleInStage(record, mode, record._outboundFallbackStage || mode))
      .map((record) => {
        const { _outboundFallbackStage, ...cleanRecord } = record;
        return cleanRecord;
      });
  }

  function outboundVisibleCounts(byMode) {
    return Object.fromEntries(outboundStageTabs().map((tab) => {
      const visibleRecords = filterOutboundRecords(tab.mode, outboundStageRecords(tab.mode, byMode));
      return [tab.mode, uniqueOutboundRecords(visibleRecords).length];
    }));
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
