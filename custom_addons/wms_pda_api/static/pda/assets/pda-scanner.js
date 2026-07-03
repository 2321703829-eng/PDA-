(function () {
  "use strict";

  if (window.__pdaCameraScannerReady) {
    return;
  }
  window.__pdaCameraScannerReady = true;

  const SCANNER_SCRIPT_ID = "pda-camera-scanner-script";
  const STYLE_ID = "pda-camera-scanner-style";
  const ZXING_SRC = "https://cdn.jsdelivr.net/npm/@zxing/library@0.21.3/umd/index.min.js";
  const BARCODE_FORMATS = [
    "qr_code",
    "code_128",
    "code_39",
    "ean_13",
    "ean_8",
    "upc_a",
    "upc_e",
    "itf",
    "data_matrix",
  ];

  let activeTarget = null;
  let activeStream = null;
  let activeDetector = null;
  let scanTimer = 0;
  let zxingReader = null;
  let zxingLoading = null;
  let upgradeTimer = 0;

  function injectScannerStyle() {
    if (document.getElementById(STYLE_ID)) {
      return;
    }
    const style = document.createElement("style");
    style.id = STYLE_ID;
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

  function textOfInput(input) {
    if (!input) {
      return "";
    }
    const label = input.closest("label");
    return [
      input.placeholder,
      input.name,
      input.id,
      input.getAttribute("aria-label"),
      label ? label.textContent : "",
    ].filter(Boolean).join(" ").toLowerCase();
  }

  function shouldEnhanceInput(input) {
    if (!input || input.disabled || input.readOnly) {
      return false;
    }
    const type = String(input.type || "text").toLowerCase();
    if (!["text", "search", "tel", "url", ""].includes(type)) {
      return false;
    }
    const text = textOfInput(input);
    return /扫码|扫描|条码|商品|sku|upc|库位|储位|任务单|波次|搜索|barcode|location|code/.test(text);
  }

  function existingButtonNear(input) {
    const host = input.closest(".mobile-scan-host,.qnh-outbound-search,.outbound-search,.search-row,.field,label,form");
    return host && host.querySelector(".mobile-scan-button,.pda-camera-button,[data-scan-target]");
  }

  function makeScanButton(input) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "mobile-scan-button";
    button.setAttribute("aria-label", "扫码或拍照识别");
    button.title = "扫码或拍照识别";
    button.dataset.pdaScannerAuto = "1";
    return button;
  }

  function upgradeScanInputs() {
    injectScannerStyle();
    const inputs = Array.from(document.querySelectorAll("input"));
    inputs.forEach((input) => {
      if (!shouldEnhanceInput(input) || existingButtonNear(input)) {
        return;
      }
      const button = makeScanButton(input);
      const searchHost = input.closest(".qnh-outbound-search,.outbound-search,.search-row");
      if (searchHost) {
        const searchButton = searchHost.querySelector(".search-button,[data-search],button:not(.mobile-scan-button)");
        if (searchButton) {
          searchHost.insertBefore(button, searchButton);
        } else {
          searchHost.appendChild(button);
        }
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
    upgradeTimer = window.setTimeout(upgradeScanInputs, 80);
  }

  function resolveTargetInput(button) {
    const selector = button.getAttribute("data-scan-target");
    if (selector) {
      const target = document.querySelector(selector);
      if (target) {
        return target;
      }
    }
    const host = button.closest(".mobile-scan-host,.qnh-outbound-search,.outbound-search,.search-row,.field,label,form");
    if (host) {
      const inputs = Array.from(host.querySelectorAll("input")).filter((input) => input.type !== "hidden");
      const preferred = inputs.find(shouldEnhanceInput) || inputs[0];
      if (preferred) {
        return preferred;
      }
    }
    return null;
  }

  function buildScanner() {
    closeScanner();
    const overlay = document.createElement("div");
    overlay.className = "pda-scan-overlay";
    overlay.innerHTML = `
      <section class="pda-scan-sheet" role="dialog" aria-modal="true" aria-label="扫码识别">
        <div class="pda-scan-head">
          <strong>扫码识别</strong>
          <button type="button" data-scan-close aria-label="关闭">×</button>
        </div>
        <div class="pda-scan-frame">
          <video autoplay playsinline muted></video>
        </div>
        <p class="pda-scan-status" data-scan-status>正在准备摄像头。若浏览器不允许摄像头，可使用拍照识别。</p>
        <div class="pda-scan-actions">
          <label class="is-primary">拍照识别<input data-scan-file type="file" accept="image/*" capture="environment" /></label>
          <button type="button" data-scan-retry>重新扫码</button>
        </div>
        <div class="pda-scan-manual">
          <input data-scan-manual type="text" placeholder="也可以手动输入条码/SKU" />
          <button type="button" data-scan-use>使用</button>
        </div>
      </section>
    `;
    document.body.appendChild(overlay);
    overlay.addEventListener("click", (event) => {
      if (event.target === overlay || event.target.closest("[data-scan-close]")) {
        closeScanner();
      }
    });
    overlay.querySelector("[data-scan-retry]").addEventListener("click", () => startLiveScan(overlay));
    overlay.querySelector("[data-scan-file]").addEventListener("change", (event) => decodeSelectedFile(event, overlay));
    overlay.querySelector("[data-scan-use]").addEventListener("click", () => {
      const value = overlay.querySelector("[data-scan-manual]").value.trim();
      if (value) {
        commitScan(value);
      } else {
        setStatus(overlay, "请输入条码、SKU 或库位后再使用。", true);
      }
    });
    overlay.querySelector("[data-scan-manual]").addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        overlay.querySelector("[data-scan-use]").click();
      }
    });
    return overlay;
  }

  function setStatus(overlay, text, isError) {
    const status = overlay && overlay.querySelector("[data-scan-status]");
    if (!status) {
      return;
    }
    status.textContent = text;
    status.style.background = isError ? "#fff1f1" : "#fff8db";
    status.style.color = isError ? "#991b1b" : "#6b4b00";
  }

  async function createBarcodeDetector() {
    if (!("BarcodeDetector" in window)) {
      return null;
    }
    try {
      const supported = BarcodeDetector.getSupportedFormats ? await BarcodeDetector.getSupportedFormats() : BARCODE_FORMATS;
      const formats = BARCODE_FORMATS.filter((format) => supported.includes(format));
      return new BarcodeDetector({ formats: formats.length ? formats : undefined });
    } catch (error) {
      try {
        return new BarcodeDetector();
      } catch (fallbackError) {
        return null;
      }
    }
  }

  async function startLiveScan(overlay) {
    stopLiveScan();
    const video = overlay.querySelector("video");
    if (!window.isSecureContext) {
      setStatus(overlay, "当前是 HTTP 地址，手机浏览器通常不允许实时摄像头。请点“拍照识别”，或后续改用 HTTPS。", true);
      return;
    }
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setStatus(overlay, "当前浏览器不支持实时摄像头，请使用拍照识别或手动输入。", true);
      return;
    }
    try {
      setStatus(overlay, "请把条码/二维码放到黄色框内，识别成功会自动填入。");
      activeStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: "environment" }, width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
      video.srcObject = activeStream;
      await video.play();
      activeDetector = await createBarcodeDetector();
      if (activeDetector) {
        scanWithBarcodeDetector(overlay, video);
      } else {
        await scanWithZxing(overlay, video);
      }
    } catch (error) {
      setStatus(overlay, "摄像头启动失败。请检查浏览器权限，或使用拍照识别。", true);
    }
  }

  function scanWithBarcodeDetector(overlay, video) {
    const tick = async () => {
      if (!document.body.contains(overlay) || !activeDetector) {
        return;
      }
      try {
        if (video.readyState >= 2) {
          const codes = await activeDetector.detect(video);
          if (codes && codes.length) {
            commitScan(codes[0].rawValue || codes[0].rawValueText || "");
            return;
          }
        }
      } catch (error) {
        setStatus(overlay, "实时识别暂不可用，可拍照识别。", true);
      }
      scanTimer = window.setTimeout(tick, 260);
    };
    tick();
  }

  function loadZxing() {
    if (window.ZXing) {
      return Promise.resolve(window.ZXing);
    }
    if (zxingLoading) {
      return zxingLoading;
    }
    zxingLoading = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.id = SCANNER_SCRIPT_ID;
      script.src = ZXING_SRC;
      script.async = true;
      script.onload = () => window.ZXing ? resolve(window.ZXing) : reject(new Error("ZXing 未加载成功"));
      script.onerror = () => reject(new Error("扫码识别库加载失败"));
      document.head.appendChild(script);
    });
    return zxingLoading;
  }

  async function scanWithZxing(overlay, video) {
    try {
      const ZXing = await loadZxing();
      zxingReader = new ZXing.BrowserMultiFormatReader();
      await zxingReader.decodeFromVideoElement(video, (result) => {
        if (result) {
          commitScan(result.getText ? result.getText() : String(result.text || result));
        }
      });
    } catch (error) {
      setStatus(overlay, "当前浏览器没有内置识别能力，且识别库加载失败。请使用拍照识别或手动输入。", true);
    }
  }

  async function decodeSelectedFile(event, overlay) {
    const file = event.target.files && event.target.files[0];
    if (!file) {
      return;
    }
    setStatus(overlay, "正在识别照片，请稍等。");
    try {
      const detector = await createBarcodeDetector();
      if (detector && window.createImageBitmap) {
        const bitmap = await createImageBitmap(file);
        const codes = await detector.detect(bitmap);
        if (bitmap.close) {
          bitmap.close();
        }
        if (codes && codes.length) {
          commitScan(codes[0].rawValue || codes[0].rawValueText || "");
          return;
        }
      }
      const text = await decodeImageWithZxing(file);
      if (text) {
        commitScan(text);
      } else {
        setStatus(overlay, "照片里没有识别到条码/二维码，请重新拍清楚一些。", true);
      }
    } catch (error) {
      setStatus(overlay, "照片识别失败，请重新拍照或手动输入。", true);
    } finally {
      event.target.value = "";
    }
  }

  async function decodeImageWithZxing(file) {
    const ZXing = await loadZxing();
    const reader = new ZXing.BrowserMultiFormatReader();
    const url = URL.createObjectURL(file);
    const image = new Image();
    image.src = url;
    await new Promise((resolve, reject) => {
      image.onload = resolve;
      image.onerror = reject;
    });
    try {
      const result = await reader.decodeFromImageElement(image);
      return result && (result.getText ? result.getText() : String(result.text || result));
    } finally {
      URL.revokeObjectURL(url);
      if (reader.reset) {
        reader.reset();
      }
    }
  }

  function stopLiveScan() {
    window.clearTimeout(scanTimer);
    scanTimer = 0;
    if (zxingReader && zxingReader.reset) {
      try {
        zxingReader.reset();
      } catch (error) {
        /* ignore */
      }
    }
    zxingReader = null;
    if (activeStream) {
      activeStream.getTracks().forEach((track) => track.stop());
    }
    activeStream = null;
    activeDetector = null;
  }

  function closeScanner() {
    stopLiveScan();
    const overlay = document.querySelector(".pda-scan-overlay");
    if (overlay) {
      overlay.remove();
    }
    activeTarget = null;
  }

  function commitScan(value) {
    const text = String(value || "").trim();
    if (!text || !activeTarget) {
      return;
    }
    activeTarget.value = text;
    activeTarget.focus();
    activeTarget.dispatchEvent(new Event("input", { bubbles: true }));
    activeTarget.dispatchEvent(new Event("change", { bubbles: true }));
    closeScanner();
  }

  function openScannerFor(input) {
    if (!input) {
      return;
    }
    injectScannerStyle();
    activeTarget = input;
    const overlay = buildScanner();
    startLiveScan(overlay);
  }

  document.addEventListener("click", (event) => {
    const button = event.target.closest(".mobile-scan-button,.pda-camera-button,[data-scan-target]");
    if (!button) {
      return;
    }
    const input = resolveTargetInput(button);
    if (!input) {
      return;
    }
    event.preventDefault();
    event.stopPropagation();
    openScannerFor(input);
  }, true);

  document.addEventListener("DOMContentLoaded", scheduleUpgrade);
  window.addEventListener("hashchange", scheduleUpgrade);
  new MutationObserver(scheduleUpgrade).observe(document.documentElement, { childList: true, subtree: true });
  scheduleUpgrade();
})();
