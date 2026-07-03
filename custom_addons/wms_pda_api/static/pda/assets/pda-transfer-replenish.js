(function () {
  "use strict";

  const STORE_KEY = "tianshu_pda_transfer_replenish_v1";
  const SHELL_ID = "pdaTransferReplenishShell";
  const STYLE_ID = "pdaTransferReplenishStyle";

  const defaultState = {
    mode: "transfer",
    transferSide: "out",
    transferStatus: "all",
    replenishStatus: "todo",
    warehouseFilter: "all",
    areaFilter: "all",
    replenishTypeFilter: "all",
    search: "",
    view: "list",
    activeId: "",
    transfers: [
      {
        id: "DB-20260702-1001",
        side: "out",
        status: "pending",
        createdAt: "2026-07-02 09:18:12",
        creator: "系统",
        source: "广州中心仓",
        target: "深圳前置仓",
        warehouse: "广州中心仓",
        type: "常规调拨",
        skuCount: 2,
        qty: 66,
        lines: [
          { name: "家用抽纸 3层100抽", sku: "PDA-SYS-PAPER-001", upc: "6930000000011", spec: "3层100抽/包", qty: 40, unit: "包" },
          { name: "洗衣液 2kg 清香型", sku: "PDA-SYS-LAUNDRY-002", upc: "6930000000028", spec: "2kg/瓶", qty: 26, unit: "瓶" },
        ],
      },
      {
        id: "DB-20260702-1002",
        side: "out",
        status: "outbound",
        createdAt: "2026-07-02 10:32:45",
        creator: "仓库主管",
        source: "广州中心仓",
        target: "佛山门店仓",
        warehouse: "广州中心仓",
        type: "门店补货",
        skuCount: 1,
        qty: 120,
        lines: [
          { name: "矿泉水 550ml 24瓶", sku: "PDA-SYS-WATER-003", upc: "6930000000035", spec: "24瓶/箱", qty: 120, unit: "箱" },
        ],
      },
      {
        id: "DB-20260701-0901",
        side: "in",
        status: "receipt",
        createdAt: "2026-07-01 16:08:06",
        creator: "调度员",
        source: "成都中心仓",
        target: "广州中心仓",
        warehouse: "广州中心仓",
        type: "跨仓调拨",
        skuCount: 2,
        qty: 75,
        lines: [
          { name: "猫砂 5kg 除臭型", sku: "PDA-SYS-CATLITTER-004", upc: "6930000000042", spec: "5kg/袋", qty: 55, unit: "袋" },
          { name: "宠物湿巾 80抽", sku: "PDA-SYS-WIPES-005", upc: "6930000000059", spec: "80抽/包", qty: 20, unit: "包" },
        ],
      },
      {
        id: "DB-20260630-0801",
        side: "in",
        status: "done",
        createdAt: "2026-06-30 11:20:18",
        creator: "系统",
        source: "广州中心仓",
        target: "东莞门店仓",
        warehouse: "东莞门店仓",
        type: "常规调拨",
        skuCount: 1,
        qty: 18,
        lines: [
          { name: "垃圾袋 45cm*50cm", sku: "PDA-SYS-BAG-006", upc: "6930000000066", spec: "50只/卷", qty: 18, unit: "卷" },
        ],
      },
    ],
    replenishments: [
      {
        id: "BH-20260702-001",
        status: "todo",
        area: "A区",
        type: "按库位补货",
        sourceLocation: "WH/Stock/A2-03-01",
        targetLocation: "WH/Pick/A1-01-08",
        product: "家用抽纸 3层100抽",
        sku: "PDA-SYS-PAPER-001",
        upc: "6930000000011",
        spec: "3层100抽/包",
        qty: 36,
        unit: "包",
        createdAt: "2026-07-02 09:28:31",
      },
      {
        id: "BH-20260702-002",
        status: "todo",
        area: "B区",
        type: "按商品补货",
        sourceLocation: "WH/Stock/B1-05-03",
        targetLocation: "WH/Pick/B1-02-06",
        product: "洗衣液 2kg 清香型",
        sku: "PDA-SYS-LAUNDRY-002",
        upc: "6930000000028",
        spec: "2kg/瓶",
        qty: 24,
        unit: "瓶",
        createdAt: "2026-07-02 10:04:16",
      },
      {
        id: "BH-20260701-006",
        status: "done",
        area: "A区",
        type: "按库位补货",
        sourceLocation: "WH/Stock/A4-02-02",
        targetLocation: "WH/Pick/A2-03-05",
        product: "矿泉水 550ml 24瓶",
        sku: "PDA-SYS-WATER-003",
        upc: "6930000000035",
        spec: "24瓶/箱",
        qty: 12,
        unit: "箱",
        createdAt: "2026-07-01 15:42:18",
        completedAt: "2026-07-01 16:10:05",
      },
    ],
  };

  let state = loadState();

  function copyDefault() {
    return JSON.parse(JSON.stringify(defaultState));
  }

  function loadState() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORE_KEY) || "null");
      return Object.assign(copyDefault(), saved || {});
    } catch (error) {
      return copyDefault();
    }
  }

  function saveState() {
    localStorage.setItem(STORE_KEY, JSON.stringify(state));
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function injectStyle() {
    if (document.getElementById(STYLE_ID)) {
      return;
    }
    const style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = `
      .tr-shell{position:fixed;inset:0;z-index:9000;background:#eef4f8;color:#111827;font-family:Arial,"Microsoft YaHei",sans-serif;overflow:auto}
      .tr-phone{width:min(560px,100%);min-height:100%;margin:0 auto;background:#f2f7fb;padding:14px 16px 96px;box-sizing:border-box}
      .tr-top{display:grid;grid-template-columns:48px 1fr 48px;align-items:center;gap:8px;margin-bottom:12px}
      .tr-back,.tr-icon-btn{display:grid;place-items:center;width:44px;height:44px;border:1px solid #dbe7f2;border-radius:14px;background:#fff;color:#0f172a;font-size:24px;font-weight:900;box-shadow:0 8px 20px rgba(15,23,42,.05)}
      .tr-title{text-align:center}
      .tr-title h1{margin:0;font-size:28px;line-height:1.1;color:#101828}
      .tr-title p{margin:4px 0 0;color:#64748b;font-size:13px;font-weight:900}
      .tr-mode{display:grid;grid-template-columns:1fr 1fr;gap:0;margin:10px auto 14px;padding:3px;width:min(320px,100%);border-radius:15px;background:#e9edf3}
      .tr-mode button,.tr-tabs button{position:relative;height:44px;border:0;border-radius:12px;background:transparent;color:#64748b;font-size:17px;font-weight:900}
      .tr-mode button.is-active{background:#fff;color:#111827;box-shadow:0 8px 18px rgba(15,23,42,.06)}
      .tr-search{display:grid;grid-template-columns:1fr 44px 44px;gap:8px;align-items:center;margin:0 0 14px;padding:7px 8px 7px 16px;border-radius:999px;background:#fff;border:1px solid #dbe7f2;box-shadow:0 10px 24px rgba(15,23,42,.06)}
      .tr-search input{height:38px;border:0;background:transparent;outline:none;color:#0f172a;font-size:15px;font-weight:900}
      .tr-search input::placeholder{color:#9aa6b6}
      .tr-scan{display:grid;place-items:center;width:42px;height:42px;border:0;border-radius:15px;background:#f4f7fb}
      .tr-do-search{display:grid;place-items:center;width:42px;height:42px;border:0;border-radius:15px;background:#eef4fa;color:#0f172a;font-size:28px;font-weight:900;line-height:1}
      .tr-scan::before{content:"";width:18px;height:18px;background:linear-gradient(#0f172a 0 0) left top/7px 2px no-repeat,linear-gradient(#0f172a 0 0) left top/2px 7px no-repeat,linear-gradient(#0f172a 0 0) right top/7px 2px no-repeat,linear-gradient(#0f172a 0 0) right top/2px 7px no-repeat,linear-gradient(#0f172a 0 0) left bottom/7px 2px no-repeat,linear-gradient(#0f172a 0 0) left bottom/2px 7px no-repeat,linear-gradient(#0f172a 0 0) right bottom/7px 2px no-repeat,linear-gradient(#0f172a 0 0) right bottom/2px 7px no-repeat}
      .tr-tabs{display:grid;grid-template-columns:repeat(4,1fr);gap:2px;margin:4px 0 10px;background:#fff;padding:4px;border-radius:18px}
      .tr-tabs.two{grid-template-columns:1fr 1fr}
      .tr-tabs button.is-active{color:#111827}
      .tr-tabs button.is-active::after{content:"";position:absolute;left:50%;bottom:2px;width:36px;height:5px;border-radius:999px;background:#ffd22e;transform:translateX(-50%)}
      .tr-filters{display:flex;justify-content:flex-end;gap:8px;margin:8px 0 14px}
      .tr-filters select{height:36px;border:1px solid #dbe7f2;border-radius:999px;background:#fff;color:#172033;font-size:14px;font-weight:900;padding:0 10px}
      .tr-list{display:grid;gap:12px}
      .tr-card{padding:16px;border-radius:18px;background:#fff;box-shadow:0 10px 26px rgba(15,23,42,.06);border:1px solid #e4ebf3}
      .tr-card-head{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:10px}
      .tr-tag{display:inline-grid;place-items:center;height:28px;padding:0 9px;border-radius:7px;background:#e8f8ff;color:#027a9f;font-size:14px;font-weight:900}
      .tr-card h2{margin:0;color:#111827;font-size:22px;line-height:1.15}
      .tr-state{color:#111827;font-size:15px;font-weight:900}
      .tr-card p{margin:8px 0 0;color:#68758a;font-size:14px;font-weight:800;line-height:1.35}
      .tr-card .tr-focus{display:inline-block;margin-top:10px;padding:9px 12px;border-radius:8px;background:#f5f7fb;color:#111827;font-size:15px;font-weight:900}
      .tr-card strong{color:#e66b1f}
      .tr-card-foot{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:12px;padding-top:12px;border-top:1px solid #e8eef5}
      .tr-card-foot span{color:#111827;font-size:16px;font-weight:900}
      .tr-primary{height:44px;border:0;border-radius:999px;background:linear-gradient(180deg,#ffdf55,#ffc72c);color:#111827;font-size:15px;font-weight:900;padding:0 20px;box-shadow:0 10px 20px rgba(255,199,44,.28)}
      .tr-secondary{height:42px;border:1px solid #dbe7f2;border-radius:999px;background:#fff;color:#111827;font-size:14px;font-weight:900;padding:0 16px}
      .tr-bottom{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);width:min(528px,calc(100% - 32px));height:58px;border:0;border-radius:999px;background:linear-gradient(90deg,#ffe043,#ffc44d);color:#111827;font-size:20px;font-weight:900;box-shadow:0 16px 32px rgba(255,196,77,.32)}
      .tr-empty{display:grid;place-items:center;min-height:320px;border:1px dashed #cbd8e6;border-radius:18px;color:#708198;font-size:16px;font-weight:800;background:rgba(255,255,255,.42)}
      .tr-detail-card{padding:18px;border-radius:20px;background:#fff;border:1px solid #e3ebf4;box-shadow:0 10px 26px rgba(15,23,42,.06)}
      .tr-detail-card h2{margin:4px 0 12px;font-size:26px;color:#111827}
      .tr-detail-grid{display:grid;gap:8px;margin-bottom:14px}
      .tr-detail-grid p{display:flex;justify-content:space-between;gap:12px;margin:0;color:#5d6b80;font-size:15px;font-weight:800}
      .tr-detail-grid b{color:#111827;text-align:right}
      .tr-lines{display:grid;gap:10px;margin-top:12px}
      .tr-line{display:grid;grid-template-columns:64px 1fr;gap:12px;padding:12px;border-radius:16px;background:#f8fafc}
      .tr-thumb{position:relative;display:grid;place-items:center;width:64px;height:64px;border-radius:12px;background:linear-gradient(135deg,#fff6d5,#eaf7ff);color:#075169;font-size:20px;font-weight:900;overflow:hidden}
      .tr-thumb em{position:absolute;left:0;bottom:0;padding:2px 6px;background:rgba(0,0,0,.55);color:#fff;font-size:12px;font-style:normal}
      .tr-line h3{margin:0 0 4px;color:#111827;font-size:17px;line-height:1.25}
      .tr-line p{margin:2px 0;color:#667085;font-size:13px;font-weight:800}
      .tr-form{display:grid;gap:10px;margin-top:12px}
      .tr-form label{display:grid;gap:5px;color:#475569;font-size:13px;font-weight:900}
      .tr-form input,.tr-form select{height:44px;border:1px solid #dbe7f2;border-radius:14px;background:#fff;padding:0 12px;color:#111827;font-size:15px;font-weight:900}
      .tr-actions{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px}
      @media(max-width:420px){.tr-phone{padding-left:12px;padding-right:12px}.tr-title h1{font-size:25px}.tr-card h2{font-size:20px}.tr-tabs button{font-size:15px}.tr-line{grid-template-columns:58px 1fr}.tr-thumb{width:58px;height:58px}}
    `;
    document.head.appendChild(style);
  }

  function shell() {
    let node = document.getElementById(SHELL_ID);
    if (!node) {
      node = document.createElement("section");
      node.id = SHELL_ID;
      node.className = "tr-shell";
      document.body.appendChild(node);
    }
    return node;
  }

  function close() {
    const node = document.getElementById(SHELL_ID);
    if (node) {
      node.remove();
    }
  }

  function open() {
    injectStyle();
    state.view = "list";
    saveState();
    render();
  }

  function matchSearch(text) {
    const q = state.search.trim().toLowerCase();
    return !q || String(text).toLowerCase().includes(q);
  }

  function transferStatusName(status) {
    return {
      pending: "待处理",
      outbound: "待出库",
      receipt: "待收货",
      done: "已完成",
      cancel: "已取消",
    }[status] || status;
  }

  function transferVisible(item) {
    const sideOk = item.side === state.transferSide;
    const statusOk = state.transferStatus === "all" || item.status === state.transferStatus;
    const warehouseOk = state.warehouseFilter === "all" || item.warehouse === state.warehouseFilter;
    const text = [item.id, item.source, item.target, item.type].concat(item.lines.map((line) => [line.name, line.sku, line.upc].join(" "))).join(" ");
    return sideOk && statusOk && warehouseOk && matchSearch(text);
  }

  function replenishVisible(item) {
    const statusOk = item.status === state.replenishStatus;
    const areaOk = state.areaFilter === "all" || item.area === state.areaFilter;
    const typeOk = state.replenishTypeFilter === "all" || item.type === state.replenishTypeFilter;
    const text = [item.id, item.area, item.type, item.sourceLocation, item.targetLocation, item.product, item.sku, item.upc].join(" ");
    return statusOk && areaOk && typeOk && matchSearch(text);
  }

  function transferCard(item) {
    const placeLabel = item.side === "out" ? "调入方" : "调出方";
    const place = item.side === "out" ? item.target : item.source;
    const action = item.status === "pending" ? "处理" : item.status === "outbound" ? "出库" : item.status === "receipt" ? "收货" : "查看";
    return `
      <article class="tr-card" data-tr-detail="${escapeHtml(item.id)}" data-tr-kind="transfer">
        <div class="tr-card-head">
          <span class="tr-tag">正常</span>
          <h2>${escapeHtml(item.id)}</h2>
          <span class="tr-state">${escapeHtml(transferStatusName(item.status))} ›</span>
        </div>
        <p>${escapeHtml(item.createdAt)} ${escapeHtml(item.creator)} 创建</p>
        <span class="tr-focus">${escapeHtml(placeLabel)}：${escapeHtml(place)}</span>
        <div class="tr-card-foot">
          <span>共 <strong>${escapeHtml(item.skuCount)}</strong> 种 <strong>${escapeHtml(item.qty)}</strong> 件</span>
          <button class="tr-primary" type="button" data-tr-detail="${escapeHtml(item.id)}" data-tr-kind="transfer">${escapeHtml(action)}</button>
        </div>
      </article>
    `;
  }

  function replenishCard(item) {
    return `
      <article class="tr-card" data-tr-detail="${escapeHtml(item.id)}" data-tr-kind="replenish">
        <div class="tr-card-head">
          <span class="tr-tag">${escapeHtml(item.type)}</span>
          <h2>${escapeHtml(item.id)}</h2>
          <span class="tr-state">${item.status === "done" ? "已完成" : "未完成"} ›</span>
        </div>
        <p>${escapeHtml(item.createdAt)} 创建</p>
        <span class="tr-focus">补货位：${escapeHtml(item.targetLocation)}</span>
        <div class="tr-card-foot">
          <span>${escapeHtml(item.product)} · <strong>${escapeHtml(item.qty)}</strong>${escapeHtml(item.unit)}</span>
          <button class="tr-primary" type="button" data-tr-detail="${escapeHtml(item.id)}" data-tr-kind="replenish">${item.status === "done" ? "查看" : "补货"}</button>
        </div>
      </article>
    `;
  }

  function renderHeader(title, subtitle) {
    return `
      <div class="tr-top">
        <button class="tr-back" type="button" data-tr-back>‹</button>
        <div class="tr-title"><h1>${escapeHtml(title)}</h1>${subtitle ? `<p>${escapeHtml(subtitle)}</p>` : ""}</div>
        <span></span>
      </div>
    `;
  }

  function renderTransferList() {
    const items = state.transfers.filter(transferVisible);
    return `
      <div class="tr-mode">
        <button class="${state.transferSide === "out" ? "is-active" : ""}" type="button" data-tr-side="out">调出单</button>
        <button class="${state.transferSide === "in" ? "is-active" : ""}" type="button" data-tr-side="in">调入单</button>
      </div>
      ${renderSearch("支持商品名称、UPC、SKU、调拨单号")}
      <div class="tr-tabs">
        ${["all:全部", "pending:待处理", "outbound:待出库", "receipt:待收货"].map((pair) => {
          const [value, label] = pair.split(":");
          return `<button class="${state.transferStatus === value ? "is-active" : ""}" type="button" data-tr-transfer-status="${value}">${label}</button>`;
        }).join("")}
      </div>
      <div class="tr-filters">
        <select data-tr-filter="warehouse">
          ${["all:全部店/仓", "广州中心仓:广州中心仓", "深圳前置仓:深圳前置仓", "东莞门店仓:东莞门店仓"].map((pair) => {
            const [value, label] = pair.split(":");
            return `<option value="${escapeHtml(value)}" ${state.warehouseFilter === value ? "selected" : ""}>${escapeHtml(label)}</option>`;
          }).join("")}
        </select>
      </div>
      <div class="tr-list">${items.length ? items.map(transferCard).join("") : `<div class="tr-empty">暂无调拨单</div>`}</div>
      <button class="tr-bottom" type="button" data-tr-new-transfer>新建调拨单</button>
    `;
  }

  function renderReplenishList() {
    const items = state.replenishments.filter(replenishVisible);
    return `
      ${renderSearch("支持库位码、商品、SKU 搜索")}
      <div class="tr-tabs two">
        <button class="${state.replenishStatus === "todo" ? "is-active" : ""}" type="button" data-tr-replenish-status="todo">未完成</button>
        <button class="${state.replenishStatus === "done" ? "is-active" : ""}" type="button" data-tr-replenish-status="done">已完成</button>
      </div>
      <div class="tr-filters">
        <select data-tr-filter="area">
          ${["all:按库区筛选", "A区:A区", "B区:B区"].map((pair) => {
            const [value, label] = pair.split(":");
            return `<option value="${escapeHtml(value)}" ${state.areaFilter === value ? "selected" : ""}>${escapeHtml(label)}</option>`;
          }).join("")}
        </select>
        <select data-tr-filter="replenishType">
          ${["all:按补货类型筛选", "按库位补货:按库位补货", "按商品补货:按商品补货"].map((pair) => {
            const [value, label] = pair.split(":");
            return `<option value="${escapeHtml(value)}" ${state.replenishTypeFilter === value ? "selected" : ""}>${escapeHtml(label)}</option>`;
          }).join("")}
        </select>
      </div>
      <div class="tr-list">${items.length ? items.map(replenishCard).join("") : `<div class="tr-empty">暂无内容</div>`}</div>
    `;
  }

  function renderSearch(placeholder) {
    return `
      <label class="tr-search">
        <input type="search" value="${escapeHtml(state.search)}" placeholder="${escapeHtml(placeholder)}" data-tr-search />
        <button class="tr-do-search" type="button" data-tr-do-search aria-label="搜索">⌕</button>
        <button class="tr-scan" type="button" data-tr-scan aria-label="扫码"></button>
      </label>
    `;
  }

  function lineHtml(line) {
    return `
      <article class="tr-line">
        <div class="tr-thumb"><span>${escapeHtml((line.sku || line.name || "TS").slice(0, 2).toUpperCase())}</span><em>${escapeHtml(line.qty)}${escapeHtml(line.unit)}</em></div>
        <div>
          <h3>${escapeHtml(line.name)}</h3>
          <p>规格：${escapeHtml(line.spec || "-")}</p>
          <p>商品条码：<b>${escapeHtml(line.upc || "-")}</b></p>
          <p>SKU：${escapeHtml(line.sku || "-")}</p>
        </div>
      </article>
    `;
  }

  function renderTransferDetail(item) {
    const nextAction = item.status === "pending" || item.status === "outbound" ? "确认出库" : item.status === "receipt" ? "确认收货" : "";
    return `
      ${renderHeader("调拨单详情", item.side === "out" ? "调出 · 出库 · 交接" : "调入 · 收货 · 完成")}
      <section class="tr-detail-card">
        <span class="tr-tag">正常</span>
        <h2>${escapeHtml(item.id)}</h2>
        <div class="tr-detail-grid">
          <p><span>状态</span><b>${escapeHtml(transferStatusName(item.status))}</b></p>
          <p><span>调出仓</span><b>${escapeHtml(item.source)}</b></p>
          <p><span>调入仓</span><b>${escapeHtml(item.target)}</b></p>
          <p><span>类型</span><b>${escapeHtml(item.type)}</b></p>
          <p><span>创建</span><b>${escapeHtml(item.createdAt)} ${escapeHtml(item.creator)}</b></p>
          <p><span>商品</span><b>${escapeHtml(item.skuCount)} 种 / ${escapeHtml(item.qty)} 件</b></p>
        </div>
        <div class="tr-lines">${item.lines.map(lineHtml).join("")}</div>
        <div class="tr-actions">
          <button class="tr-secondary" type="button" data-tr-list>返回列表</button>
          ${nextAction ? `<button class="tr-primary" type="button" data-tr-transfer-next="${escapeHtml(item.id)}">${escapeHtml(nextAction)}</button>` : `<button class="tr-primary" type="button" data-tr-list>已完成</button>`}
        </div>
      </section>
    `;
  }

  function renderReplenishDetail(item) {
    return `
      ${renderHeader("补货任务详情", "仓内补货 · 扫库位 · 确认")}
      <section class="tr-detail-card">
        <span class="tr-tag">${escapeHtml(item.type)}</span>
        <h2>${escapeHtml(item.id)}</h2>
        <div class="tr-detail-grid">
          <p><span>状态</span><b>${item.status === "done" ? "已完成" : "未完成"}</b></p>
          <p><span>作业区</span><b>${escapeHtml(item.area)}</b></p>
          <p><span>源库位</span><b>${escapeHtml(item.sourceLocation)}</b></p>
          <p><span>补货位</span><b>${escapeHtml(item.targetLocation)}</b></p>
          <p><span>数量</span><b>${escapeHtml(item.qty)} ${escapeHtml(item.unit)}</b></p>
        </div>
        <div class="tr-form">
          <label>商品/条码<input value="${escapeHtml(item.upc)}" data-tr-replenish-product /></label>
          <label>源库位<input value="${escapeHtml(item.sourceLocation)}" data-tr-replenish-source /></label>
          <label>目标库位<input value="${escapeHtml(item.targetLocation)}" data-tr-replenish-target /></label>
        </div>
        <div class="tr-lines">${lineHtml({ name: item.product, sku: item.sku, upc: item.upc, spec: item.spec, qty: item.qty, unit: item.unit })}</div>
        <div class="tr-actions">
          <button class="tr-secondary" type="button" data-tr-list>返回列表</button>
          ${item.status === "done" ? `<button class="tr-primary" type="button" data-tr-list>已完成</button>` : `<button class="tr-primary" type="button" data-tr-replenish-done="${escapeHtml(item.id)}">确认补货</button>`}
        </div>
      </section>
    `;
  }

  function renderNewTransfer() {
    return `
      ${renderHeader("新建调拨单", "创建后进入待处理")}
      <section class="tr-detail-card">
        <div class="tr-form">
          <label>调出仓<select data-new-source><option>广州中心仓</option><option>成都中心仓</option><option>深圳前置仓</option></select></label>
          <label>调入仓<select data-new-target><option>深圳前置仓</option><option>佛山门店仓</option><option>东莞门店仓</option></select></label>
          <label>商品<input data-new-product value="家用抽纸 3层100抽" /></label>
          <label>SKU<input data-new-sku value="PDA-SYS-PAPER-001" /></label>
          <label>条码<input data-new-upc value="6930000000011" /></label>
          <label>数量<input data-new-qty type="number" min="1" value="12" /></label>
        </div>
        <div class="tr-actions">
          <button class="tr-secondary" type="button" data-tr-list>取消</button>
          <button class="tr-primary" type="button" data-tr-create-transfer>创建调拨单</button>
        </div>
      </section>
    `;
  }

  function render() {
    injectStyle();
    const node = shell();
    const body = state.view === "transferDetail"
      ? renderTransferDetail(state.transfers.find((item) => item.id === state.activeId) || state.transfers[0])
      : state.view === "replenishDetail"
        ? renderReplenishDetail(state.replenishments.find((item) => item.id === state.activeId) || state.replenishments[0])
        : state.view === "newTransfer"
          ? renderNewTransfer()
          : `
            ${renderHeader("入库调拨补货", "调拨 · 出入库 · 仓内补货")}
            <div class="tr-mode">
              <button class="${state.mode === "transfer" ? "is-active" : ""}" type="button" data-tr-mode="transfer">调拨单</button>
              <button class="${state.mode === "replenish" ? "is-active" : ""}" type="button" data-tr-mode="replenish">仓内补货</button>
            </div>
            ${state.mode === "transfer" ? renderTransferList() : renderReplenishList()}
          `;
    node.innerHTML = `<div class="tr-phone">${body}</div>`;
  }

  function nextTransfer(item) {
    if (!item) {
      return;
    }
    if (item.status === "pending") {
      item.status = "outbound";
    } else if (item.status === "outbound") {
      item.status = "receipt";
      item.side = "in";
      state.transferSide = "in";
    } else if (item.status === "receipt") {
      item.status = "done";
    }
    saveState();
    render();
  }

  function createTransfer() {
    const root = shell();
    const qty = Number((root.querySelector("[data-new-qty]") || {}).value || 1);
    const item = {
      id: `DB-${new Date().toISOString().slice(0, 10).replace(/-/g, "")}-${String(Math.floor(Math.random() * 9000) + 1000)}`,
      side: "out",
      status: "pending",
      createdAt: new Date().toLocaleString("zh-CN", { hour12: false }).replace(/\//g, "-"),
      creator: "PDA",
      source: (root.querySelector("[data-new-source]") || {}).value || "广州中心仓",
      target: (root.querySelector("[data-new-target]") || {}).value || "深圳前置仓",
      warehouse: "广州中心仓",
      type: "手动调拨",
      skuCount: 1,
      qty,
      lines: [{
        name: (root.querySelector("[data-new-product]") || {}).value || "未命名商品",
        sku: (root.querySelector("[data-new-sku]") || {}).value || "-",
        upc: (root.querySelector("[data-new-upc]") || {}).value || "-",
        spec: "默认规格",
        qty,
        unit: "件",
      }],
    };
    state.transfers.unshift(item);
    state.view = "transferDetail";
    state.activeId = item.id;
    saveState();
    render();
  }

  function bindEvents() {
    document.addEventListener("click", (event) => {
      const opener = event.target.closest("button,a,[role='button'],.menu-card,.feature-card,.module-card,.operation-card");
      if (opener && !opener.closest(`#${SHELL_ID}`) && /调拨补货|调拨|补货/.test((opener.textContent || "") + " " + (opener.dataset.route || ""))) {
        event.preventDefault();
        event.stopPropagation();
        open();
        return;
      }
      const root = event.target.closest(`#${SHELL_ID}`);
      if (!root) {
        return;
      }
      if (event.target.closest("[data-tr-back]")) {
        if (state.view === "list") {
          close();
        } else {
          state.view = "list";
          saveState();
          render();
        }
        return;
      }
      const mode = event.target.closest("[data-tr-mode]");
      if (mode) {
        state.mode = mode.dataset.trMode;
        state.view = "list";
        saveState();
        render();
        return;
      }
      const side = event.target.closest("[data-tr-side]");
      if (side) {
        state.transferSide = side.dataset.trSide;
        saveState();
        render();
        return;
      }
      const transferStatus = event.target.closest("[data-tr-transfer-status]");
      if (transferStatus) {
        state.transferStatus = transferStatus.dataset.trTransferStatus;
        saveState();
        render();
        return;
      }
      const replenishStatus = event.target.closest("[data-tr-replenish-status]");
      if (replenishStatus) {
        state.replenishStatus = replenishStatus.dataset.trReplenishStatus;
        saveState();
        render();
        return;
      }
      const detail = event.target.closest("[data-tr-detail]");
      if (detail) {
        state.activeId = detail.dataset.trDetail;
        state.view = detail.dataset.trKind === "replenish" ? "replenishDetail" : "transferDetail";
        saveState();
        render();
        return;
      }
      const list = event.target.closest("[data-tr-list]");
      if (list) {
        state.view = "list";
        saveState();
        render();
        return;
      }
      const next = event.target.closest("[data-tr-transfer-next]");
      if (next) {
        nextTransfer(state.transfers.find((item) => item.id === next.dataset.trTransferNext));
        return;
      }
      const done = event.target.closest("[data-tr-replenish-done]");
      if (done) {
        const item = state.replenishments.find((task) => task.id === done.dataset.trReplenishDone);
        if (item) {
          item.status = "done";
          item.completedAt = new Date().toLocaleString("zh-CN", { hour12: false }).replace(/\//g, "-");
          state.replenishStatus = "done";
          saveState();
          render();
        }
        return;
      }
      if (event.target.closest("[data-tr-new-transfer]")) {
        state.view = "newTransfer";
        saveState();
        render();
        return;
      }
      if (event.target.closest("[data-tr-create-transfer]")) {
        createTransfer();
        return;
      }
      if (event.target.closest("[data-tr-scan]")) {
        const input = root.querySelector("[data-tr-search]") || root.querySelector("input");
        if (input) {
          input.focus();
          const value = window.prompt("请输入扫码结果", input.value || "");
          if (value != null) {
            input.value = value;
            state.search = value;
            saveState();
            render();
          }
        }
      }
      if (event.target.closest("[data-tr-do-search]")) {
        const input = root.querySelector("[data-tr-search]");
        state.search = input ? input.value : "";
        saveState();
        render();
      }
    }, true);
    document.addEventListener("keydown", (event) => {
      if (!event.target.closest(`#${SHELL_ID}`)) {
        return;
      }
      if (event.target.matches("[data-tr-search]") && event.key === "Enter") {
        event.preventDefault();
        state.search = event.target.value;
        saveState();
        render();
      }
    });
    document.addEventListener("change", (event) => {
      if (!event.target.closest(`#${SHELL_ID}`)) {
        return;
      }
      if (event.target.matches("[data-tr-filter='warehouse']")) {
        state.warehouseFilter = event.target.value;
      } else if (event.target.matches("[data-tr-filter='area']")) {
        state.areaFilter = event.target.value;
      } else if (event.target.matches("[data-tr-filter='replenishType']")) {
        state.replenishTypeFilter = event.target.value;
      } else {
        return;
      }
      saveState();
      render();
    });
  }

  bindEvents();
})();
