/** @odoo-module **/

const BACK_BUTTON_CLASS = "o_logistics_web_back_button";
const BACK_BUTTON_LABEL = "\u8fd4\u56de";
const BACK_BUTTON_TITLE = "\u8fd4\u56de\u4e0a\u4e00\u7ea7\u9875\u9762";

function findControlPanel() {
    return document.querySelector(".o_action_manager .o_control_panel");
}

function isDetailPage() {
    const actionManager = document.querySelector(".o_action_manager");
    return Boolean(actionManager && actionManager.querySelector(".o_form_view"));
}

function findButtonHost(controlPanel) {
    return (
        controlPanel.querySelector(".o_control_panel_main_buttons") ||
        controlPanel.querySelector(".o_control_panel_actions") ||
        controlPanel
    );
}

function findPreviousBreadcrumb(controlPanel) {
    const breadcrumbLinks = controlPanel.querySelectorAll(".breadcrumb-item a, .breadcrumb a");
    return breadcrumbLinks.length ? breadcrumbLinks[breadcrumbLinks.length - 1] : null;
}

function canNavigateBack(controlPanel) {
    return isDetailPage() && (Boolean(findPreviousBreadcrumb(controlPanel)) || window.history.length > 1);
}

function navigateBack(event) {
    event.preventDefault();
    event.stopPropagation();

    const controlPanel = findControlPanel();
    const previousBreadcrumb = controlPanel ? findPreviousBreadcrumb(controlPanel) : null;
    if (previousBreadcrumb) {
        previousBreadcrumb.click();
        return;
    }
    if (window.history.length > 1) {
        window.history.back();
    }
}

function ensureBackButton() {
    const controlPanel = findControlPanel();
    if (!controlPanel) {
        return;
    }

    const existingButton = controlPanel.querySelector(`.${BACK_BUTTON_CLASS}`);
    if (existingButton) {
        existingButton.hidden = !canNavigateBack(controlPanel);
        return;
    }

    const buttonHost = findButtonHost(controlPanel);
    const button = document.createElement("button");
    button.type = "button";
    button.className = `btn btn-secondary btn-sm ${BACK_BUTTON_CLASS}`;
    button.textContent = BACK_BUTTON_LABEL;
    button.title = BACK_BUTTON_TITLE;
    button.hidden = !canNavigateBack(controlPanel);
    button.addEventListener("click", navigateBack);
    buttonHost.prepend(button);
}

let scheduled = false;

function scheduleEnsureBackButton() {
    if (scheduled) {
        return;
    }
    scheduled = true;
    window.requestAnimationFrame(() => {
        scheduled = false;
        try {
            ensureBackButton();
        } catch {
            // This patch must never block the normal Odoo page if the control panel changes.
        }
    });
}

function startBackButtonPatch() {
    if (!document.body || !window.MutationObserver) {
        return;
    }
    scheduleEnsureBackButton();

    const observer = new MutationObserver(scheduleEnsureBackButton);
    observer.observe(document.body, { childList: true, subtree: true });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startBackButtonPatch, { once: true });
} else {
    startBackButtonPatch();
}
