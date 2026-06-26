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
        { mode: "handover", label: "待交接", hint: "司机/车辆/运单核对后交接出库" },
      ],
    },
  };

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
    waiting_handover: "待交接",
    handover_ing: "交接中",
    handover_done: "已交接",
    handover_exception: "交接异常",
  };

  const STATUS_FLOWS = {
    inbound: ["waiting_receipt", "receiving", "received", "waiting_putaway", "putaway_ing", "putaway_done"],
    putaway: ["waiting_putaway", "putaway_ing", "putaway_done"],
    pick: ["waiting_pick", "picking", "picked", "waiting_check"],
    outbound: ["waiting_check", "checking", "checked", "waiting_handover"],
    handover: ["waiting_handover", "handover_ing", "handover_done"],
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
    waiting_handover: "下一步：核对司机、车辆、运单后开始交接。",
    handover_ing: "下一步：现场交接确认，完成后结束出库履约。",
    handover_done: "已完成交接：出库履约闭环完成。",
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
            <p>7 个合并功能入口</p>
          </div>
        </div>
        <div class="operation-grid">
          ${HOME_MODULES.map((item) => moduleButton(item.route, item.icon, item.title, item.desc, item.tone)).join("")}
        </div>
        <div class="strategy-card">
          <strong>模块合并策略</strong>
          <small>菜单不再平铺到首页，经营页只保留现场作业入口；明细流程进入对应业务页继续处理。</small>
        </div>
        ${renderFunctionBridge()}
        <div class="chain-title">主业务状态链</div>
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
        <div class="chain-title">主业务状态链</div>
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

  function renderFunctionBridge() {
    const items = [
      ["扫码执行", "全局识别商品、库位、单据、编号，扫码后自动跳转业务。"],
      ["入库上架", "合并到货签到、收货、按单收货、上架、上架执行。"],
      ["出库履约", "合并出库、扫码拣货、集货位查询、复核装箱、装箱信息。"],
      ["库存库位", "合并库存查询、新库位查询、库位库存查询、库位管理、批量移库。"],
      ["调拨补货", "合并调拨、新调拨、仓内补货、其他入库、其他出库。"],
      ["盘点异常", "合并盘点、盘点任务、仓内异常、报损、禁售任务。"],
      ["数据看板", "移动端只保留轻量经营指标，详细 BI 仍放后台。"],
    ];
    return `
      <div class="bridge-list">
        ${items.map(([title, desc]) => `
          <div>
            <strong>${escapeHtml(title)}</strong>
            <small>${escapeHtml(desc)}</small>
          </div>
        `).join("")}
      </div>
    `;
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
        ${renderBottomNav("operation")}
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
    bindAppChrome();
    await loadTasks(mode);
  }

  async function renderHandoverFlowPage(route, group) {
    const mode = "handover";
    root.innerHTML = `
      <section class="task-panel">
        ${renderAppHeader(group.title, group.subtitle, {
          action: `<span class="mini-pill">${escapeHtml(currentWarehouseName())}</span>`,
        })}
        ${renderWorkflowStrip(route, mode)}
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
    document.getElementById(`${route}ScanForm`).addEventListener("submit", submitGlobalScan);
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
      container.querySelectorAll("[data-task-id]").forEach((button) => {
        button.addEventListener("click", () => selectTask(mode, Number(button.dataset.taskId)));
      });
      const firstId = activeTaskId(mode) || displayRecords[0].id;
      await selectTask(mode, firstId);
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
      actionText: taskActionText(mode),
    };
  }

  function taskCardLocationText(mode, task, line) {
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
    return { done, total, text: taskQtyLabel(mode, done, total) };
  }

  function taskQtyLabel(mode, done, total) {
    const action = {
      inbound: "应收",
      putaway: "应上架",
      pick: "应拣",
      outbound: "应复核",
    }[mode] || "数量";
    const pending = Math.max(Number(total || 0) - Number(done || 0), 0);
    if (total) {
      return `${action} ${formatQty(total)}，剩余 ${formatQty(pending)}`;
    }
    return `${action}待确认`;
  }

  function taskActionText(mode) {
    return {
      inbound: "收货",
      putaway: "确认上架",
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
      const firstId = activeTaskId("handover") || records[0].id;
      await selectHandoverOrder(firstId);
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
      ${renderTaskStatus("handover", order.state || "")}
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
      <button class="task-card app-task-card ${active ? "is-active" : ""}" type="button" data-task-id="${escapeAttr(task.id)}">
        <span class="app-task-main">
          <strong>${escapeHtml(name)}</strong>
          ${status ? `<em class="state-tag ${isDoneState(status) ? "is-done" : isExceptionState(status) ? "is-error" : ""}">${escapeHtml(statusLabel(status))}</em>` : ""}
          <small>${escapeHtml(summary.productText || "待执行任务")}</small>
          <small>${escapeHtml(summary.locationText || "请扫码处理")}</small>
          <small class="task-progress">${escapeHtml(summary.qtyText || taskProgressText(task) || "数量待确认")}</small>
        </span>
        <span class="task-action-chip">${escapeHtml(summary.actionText || taskActionText(mode))}</span>
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
      button.disabled = true;
      const result = await apiPost(config.complete(taskId), {
        request_id: requestId(`${mode}_complete`),
        device_id: state.deviceId,
      });
      rememberResult(mode, "任务已完成", result);
      showToast("任务已完成");
      state.activeTasks[`${mode}:id`] = "";
      await loadTasks(mode);
    } catch (error) {
      showError(error);
    } finally {
      button.disabled = false;
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
