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

  const DOWN_SHELF_REASONS = [
    ["damaged", "破损"],
    ["expired", "过期"],
    ["oversupply", "补货过多"],
    ["slow_moving", "滞销"],
    ["other", "其他"],
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
    if (state.route === "inventory") {
      renderInventory();
      return;
    }
    if (state.route === "downshelf") {
      renderDownShelf();
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
          <p>入库、出库、拣货、上架、下架和库存查询，面向 PDA 扫码作业快速处理。</p>
        </div>
      </section>
      <section class="work-panel">
        <div class="page-title">
          <div>
            <h1>选择作业</h1>
            <p>${escapeHtml(currentWarehouseName())}，${escapeHtml(currentUserName())}。</p>
          </div>
        </div>
        <div class="action-grid">
          ${moduleButton("inbound", "IN", "入库", "收货任务扫码确认")}
          ${moduleButton("outbound", "OUT", "出库", "出库复核扫码处理")}
          ${moduleButton("pick", "PICK", "拣货", "商品与库位双扫码")}
          ${moduleButton("putaway", "PUT", "上架", "商品与目标库位双扫码")}
          ${moduleButton("downshelf", "RET", "下架", "库位商品下架退库")}
          ${moduleButton("inventory", "INV", "库存扫码查询", "按商品或库位实时查询")}
        </div>
      </section>
    `;
    root.querySelectorAll("[data-route]").forEach((button) => {
      button.addEventListener("click", () => navigate(button.dataset.route));
    });
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
        container.innerHTML = `<div class="empty-state">暂无待处理任务。</div>`;
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
    return `
      <button class="task-card ${active ? "is-active" : ""}" type="button" data-task-id="${escapeAttr(task.id)}">
        <strong>${escapeHtml(name)}</strong>
        <small>${escapeHtml([partner, summary].filter(Boolean).join(" · ") || "点击查看明细")}</small>
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
      state.activeLines[mode] = lines;
      state.lineMatches[mode] = "";
      detail.innerHTML = renderScanBox(mode, data.task || findTask(mode, taskId), lines);
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
            <h1>下架退库</h1>
            <p>先扫描来源库位创建下架单，再扫描商品与数量加入明细，最后提交生成退库作业。</p>
          </div>
          <span class="status-pill">${escapeHtml(currentWarehouseName())}</span>
        </div>
        <div class="task-layout">
          <section class="task-list">
            <div class="list-header">
              <strong>下架单</strong>
              <button id="resetDownShelf" class="refresh-button" type="button">${operation ? "新建" : "清空"}</button>
            </div>
            <div class="task-items">
              ${operation ? renderDownShelfOperationCard(operation) : `<div class="empty-state">请先创建下架单。</div>`}
              ${state.downShelfLastResult ? renderDownShelfResult(state.downShelfLastResult) : ""}
            </div>
          </section>
          <section class="task-detail">
            <div class="detail-header">
              <strong>${operation ? "扫码明细" : "创建下架单"}</strong>
              <button id="confirmDownShelf" class="refresh-button" type="button" ${operation && hasLines ? "" : "disabled"}>提交下架</button>
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
        <h2>创建下架单</h2>
        <div class="scan-form">
          <label class="field">
            <span>来源库位条码</span>
            <input id="downSourceLocation" class="text-input" name="source_location_barcode" type="text" inputmode="text" autocomplete="off" placeholder="扫描下架库位" required />
          </label>
          <label class="field">
            <span>退库目标库位</span>
            <input class="text-input" name="return_location_barcode" type="text" inputmode="text" autocomplete="off" placeholder="可选，默认按仓库规则" />
          </label>
          <label class="field full-row">
            <span>备注</span>
            <input class="text-input" name="note" type="text" inputmode="text" autocomplete="off" placeholder="可选" />
          </label>
          <button class="primary-button full-row" type="submit">创建下架单</button>
        </div>
      </form>
    `;
  }

  function renderDownShelfLineForm(operation) {
    return `
      <form id="downShelfLineForm" class="scan-box" autocomplete="off">
        <h2>${escapeHtml(operation.name || `下架单 ${operation.id}`)}</h2>
        <div class="scan-form">
          <label class="field">
            <span>商品条码</span>
            <input id="downProductBarcode" class="text-input" name="product_barcode" type="text" inputmode="text" autocomplete="off" placeholder="扫描或输入商品条码" required />
          </label>
          <label class="field">
            <span>下架数量</span>
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
      return `<div class="empty-state">暂无下架明细，请扫描商品后加入。</div>`;
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
        <strong>${escapeHtml(operation.name || `下架单 ${operation.id}`)}</strong>
        <small>${escapeHtml(summary)}</small>
        <small>${escapeHtml(stateLabel)}</small>
      </article>
    `;
  }

  function renderDownShelfResult(result) {
    const summary = result.summary || {};
    const title = result.operation_name || result.name || "下架单";
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
          <small>${escapeHtml(code || "下架明细")}</small>
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
        location_barcode: sourceLocation,
        source_location_barcode: sourceLocation,
        return_location_barcode: returnLocation,
        dest_location_barcode: returnLocation,
        note: (data.note || "").trim(),
      });
      state.downShelfOperation = normalizeDownShelfOperation(result);
      state.downShelfLines = [];
      state.downShelfLastResult = null;
      showToast("下架单已创建");
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
      showToast("请先创建下架单", true);
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
      showToast("已加入下架明细");
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
      showToast("请先创建下架单", true);
      return;
    }
    if (!state.downShelfLines.length) {
      showToast("请先加入下架明细", true);
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
      showToast("下架已提交");
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

  function sumDownShelfQty() {
    return state.downShelfLines.reduce((total, line) => total + Number(line.qty || 0), 0);
  }

  function renderInventory() {
    root.innerHTML = `
      <section class="inventory-panel">
        <div class="page-title">
          <div>
            <h1>库存扫码查询</h1>
            <p>扫描商品条码或库位条码，实时查询当前库存与位置。</p>
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
        <td>${escapeHtml(item.uom || item.product_uom || "")}</td>
      </tr>
    `).join("");
    return `
      <table class="result-table">
        <thead><tr><th>商品</th><th>库位</th><th>数量</th><th>单位</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
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
