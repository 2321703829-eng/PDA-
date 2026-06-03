/** @odoo-module **/

const SYSTEM_TITLE = "\u5929\u67a2\u79d1\u6280\u7269\u6d41\u7cfb\u7edf";
const LEGACY_SYSTEM_TITLE = "\u5929\u67a2\u79d1\u6280\u4f01\u4e1a\u7cfb\u7edf";
const PROFILE_URL = "/my/profile";

const LABELS = new Map([
    [LEGACY_SYSTEM_TITLE, SYSTEM_TITLE],
    ["New", "\u65b0\u5efa"],
    ["Create", "\u65b0\u5efa"],
    ["Edit", "\u7f16\u8f91"],
    ["Save", "\u4fdd\u5b58"],
    ["Discard", "\u53d6\u6d88"],
    ["Cancel", "\u53d6\u6d88"],
    ["Delete", "\u5220\u9664"],
    ["Import", "\u5bfc\u5165"],
    ["Export", "\u5bfc\u51fa"],
    ["Print", "\u6253\u5370"],
    ["Action", "\u64cd\u4f5c"],
    ["Actions", "\u64cd\u4f5c"],
    ["Search...", "\u641c\u7d22..."],
    ["My Company", "\u5929\u67a2\u79d1\u6280"],
    ["Administrator", "\u7ba1\u7406\u5458"],
    ["Preferences", "\u4e2a\u4eba\u8bbe\u7f6e"],
    ["My Profile", "\u4e2a\u4eba\u4e2d\u5fc3"],
    ["Documentation", "\u5e2e\u52a9\u6587\u6863"],
    ["Support", "\u6280\u672f\u652f\u6301"],
    ["Shortcuts", "\u5feb\u6377\u952e"],
    ["Log out", "\u9000\u51fa\u767b\u5f55"],
    ["Logout", "\u9000\u51fa\u767b\u5f55"],
    ["My Preferences", "\u4e2a\u4eba\u8bbe\u7f6e"],
    ["My Odoo.com account", "\u6211\u7684 Odoo.com \u8d26\u6237"],
]);

const PATCH_SELECTOR = [
    ".o_main_navbar a",
    ".o_main_navbar button",
    ".o_main_navbar span",
    ".o_control_panel button",
    ".o_control_panel a",
    ".o_cp_buttons button",
    ".o_cp_buttons a",
    ".modal-footer button",
    ".modal-footer a",
    ".dropdown-menu .dropdown-item",
    ".o_user_menu .dropdown-item",
    ".o_switch_company_menu .dropdown-item",
].join(",");

const USER_MENU_HIDE_LABELS = [
    "\u5e2e\u52a9",
    "\u5feb\u6377\u952e",
    "\u7ebf\u4e0a",
    "\u6280\u672f\u652f\u6301",
    "\u5e2e\u52a9\u6587\u6863",
    "\u4e2a\u4eba\u8bbe\u7f6e",
    "\u504f\u597d\u8bbe\u7f6e",
    "\u6211\u7684 Odoo.com \u8d26\u6237",
    "Help",
    "Shortcuts",
    "Online",
    "Support",
    "Documentation",
    "My Preferences",
    "Preferences",
    "My Odoo.com",
];

const LOGOUT_LABELS = [
    "\u767b\u51fa",
    "\u9000\u51fa\u767b\u5f55",
    "Log out",
    "Logout",
];

function normalizeText(value) {
    return (value || "").replace(/\s+/g, " ").trim();
}

function setText(el, text) {
    if (el && normalizeText(el.textContent) !== text) {
        el.textContent = text;
    }
}

function translateElement(el) {
    if (!el || el.children.length > 1) {
        return;
    }
    const raw = (el.textContent || "").trim();
    const translated = LABELS.get(raw);
    if (translated && raw !== translated) {
        el.textContent = translated;
    }
    const title = el.getAttribute("title");
    if (title && LABELS.has(title.trim())) {
        el.setAttribute("title", LABELS.get(title.trim()));
    }
}

function hideNativeOdooLinks(root) {
    root.querySelectorAll('a[href*="odoo.com"], a[href*="/documentation"]').forEach((el) => {
        const menu = el.closest(".o_user_menu, .dropdown-menu");
        if (menu) {
            el.style.display = "none";
        }
    });
}

function patchBrandText(root) {
    document.title = SYSTEM_TITLE;
    root.querySelectorAll(".o_main_navbar .o_menu_brand, .o_main_navbar .o_menu_toggle .o_menu_brand, .o_logistics_home_identity span").forEach((el) => {
        if (el.classList.contains("o_logistics_home_identity_mark")) {
            return;
        }
        const text = normalizeText(el.textContent);
        if (text === LEGACY_SYSTEM_TITLE) {
            setText(el, SYSTEM_TITLE);
        }
        if (normalizeText(el.textContent) === SYSTEM_TITLE) {
            el.classList.add("o_tianshu_brand_text_fixed");
            el.style.setProperty("color", "#12161c", "important");
            el.style.setProperty("opacity", "1", "important");
            el.style.setProperty("text-shadow", "none", "important");
            el.querySelectorAll("*").forEach((child) => {
                child.style.setProperty("color", "#12161c", "important");
                child.style.setProperty("opacity", "1", "important");
                child.style.setProperty("text-shadow", "none", "important");
            });
        }
    });
}

function isLogoutItem(item) {
    const text = normalizeText(item.textContent);
    return LOGOUT_LABELS.some((label) => text.includes(label));
}

function isProfileItem(item) {
    const href = item.getAttribute("href") || "";
    const text = normalizeText(item.textContent);
    return href.includes(PROFILE_URL) || text.includes("\u4e2a\u4eba\u4e2d\u5fc3");
}

function shouldHideUserMenuItem(item) {
    const href = item.getAttribute("href") || "";
    const text = normalizeText(item.textContent);
    return href.includes("odoo.com")
        || href.includes("/documentation")
        || USER_MENU_HIDE_LABELS.some((label) => text.includes(label));
}

function createProfileItem() {
    const item = document.createElement("a");
    item.className = "dropdown-item o_tianshu_profile_link";
    item.href = PROFILE_URL;
    item.textContent = "\u4e2a\u4eba\u4e2d\u5fc3";
    return item;
}

function patchUserMenus(root) {
    root.querySelectorAll(".dropdown-menu, .o-dropdown--menu").forEach((menu) => {
        const items = Array.from(menu.querySelectorAll("a, button, .dropdown-item"))
            .filter((item) => normalizeText(item.textContent));
        if (!items.some(isLogoutItem)) {
            return;
        }

        menu.classList.add("o_tianshu_user_menu_clean");
        let logoutItem = null;
        let profileItem = null;

        items.forEach((item) => {
            if (isLogoutItem(item)) {
                logoutItem = item;
                item.classList.remove("o_tianshu_menu_item_hidden");
                item.style.display = "";
                setText(item, "\u9000\u51fa\u767b\u5f55");
                return;
            }
            if (isProfileItem(item)) {
                profileItem = item;
                item.classList.remove("o_tianshu_menu_item_hidden");
                item.style.display = "";
                setText(item, "\u4e2a\u4eba\u4e2d\u5fc3");
                return;
            }
            if (shouldHideUserMenuItem(item)) {
                item.classList.add("o_tianshu_menu_item_hidden");
                item.style.display = "none";
            }
        });

        if (!profileItem && logoutItem) {
            const created = createProfileItem();
            logoutItem.parentElement?.insertBefore(created, logoutItem);
        }
    });
}

function dedupeAvatarButtons() {
    const systray = document.querySelector(".o_main_navbar .o_menu_systray");
    if (!systray) {
        return;
    }

    function directSystrayItem(el) {
        let node = el;
        while (node?.parentElement && node.parentElement !== systray) {
            node = node.parentElement;
        }
        return node?.parentElement === systray ? node : null;
    }

    const explicitUserMenus = Array.from(systray.querySelectorAll(".o_user_menu"))
        .map(directSystrayItem)
        .filter(Boolean);

    const candidates = Array.from(systray.children).filter((item) => {
        if (item.classList.contains("o_tianshu_home_systray")) {
            return false;
        }
        const text = normalizeText(item.textContent).replace(/[●•]/g, "");
        const hasAvatar = item.querySelector(".o_avatar, .o_user_avatar, img[src*='avatar'], img[alt='User']");
        const hasUserMenu = item.matches(".o_user_menu") || item.querySelector(".o_user_menu");
        const looksLikeInitialButton = /^[A-Z]$/i.test(text) && item.querySelector("button, .dropdown-toggle, .o-dropdown");
        return hasUserMenu || (hasAvatar && text.length <= 3) || looksLikeInitialButton;
    });

    const uniqueCandidates = Array.from(new Set([...explicitUserMenus, ...candidates]));
    uniqueCandidates.forEach((item) => item.classList.remove("o_tianshu_hide_duplicate_avatar"));
    if (uniqueCandidates.length > 1) {
        uniqueCandidates.slice(0, -1).forEach((item) => item.classList.add("o_tianshu_hide_duplicate_avatar"));
    }
}

function patch(root = document) {
    if (!document.body) {
        return;
    }
    document.body.classList.add("o_kebi_visual_polish");
    patchBrandText(root);
    root.querySelectorAll(PATCH_SELECTOR).forEach(translateElement);
    hideNativeOdooLinks(root);
    patchUserMenus(root);
    dedupeAvatarButtons();
}

let scheduled = false;
function schedulePatch(root = document) {
    if (scheduled) {
        return;
    }
    scheduled = true;
    window.requestAnimationFrame(() => {
        scheduled = false;
        patch(root);
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => patch());
} else {
    patch();
}

new MutationObserver((mutations) => {
    for (const mutation of mutations) {
        if (mutation.addedNodes.length) {
            schedulePatch(document);
            break;
        }
    }
}).observe(document.documentElement, { childList: true, subtree: true });
