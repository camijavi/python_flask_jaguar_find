/**
 * ================================================================================
 * FORMDRAFTMANAGER.JS - SCOPED SESSIONSTORAGE FORM DRAFT PERSISTENCE
 * ================================================================================
 * Persists in-progress form and navigation inputs in sessionStorage (with an
 * in-memory fallback when storage is restricted), automatically rehydrates them
 * on load/reload, and clears stored draft data once a form is successfully
 * submitted or explicitly reset.
 *
 * Security:
 * - Password inputs (`type="password"`) and file inputs (`type="file"`) are
 *   strictly excluded from sessionStorage persistence. Password values remain
 *   preserved in DOM memory across reactive (non-reloading) language switches.
 * ================================================================================
 */

(function (global) {
    "use strict";

    const STORAGE_PREFIX = "jaguar_form_draft:";
    const EXCLUDED_INPUT_TYPES = new Set([
        "password",
        "file",
        "submit",
        "button",
        "reset",
        "image",
    ]);

    const memoryFallback = new Map();
    const registry = new Map();
    let listenersBound = false;

    function getStorageKey(draftKey) {
        return STORAGE_PREFIX + String(draftKey || "").trim();
    }

    function readRaw(storageKey) {
        try {
            if (global.sessionStorage) {
                const val = global.sessionStorage.getItem(storageKey);
                if (val !== null) return val;
            }
        } catch (_) {
            // Fall back to in-memory storage when sessionStorage is blocked
        }
        return memoryFallback.has(storageKey) ? memoryFallback.get(storageKey) : null;
    }

    function writeRaw(storageKey, serialized) {
        memoryFallback.set(storageKey, serialized);
        try {
            if (global.sessionStorage) {
                global.sessionStorage.setItem(storageKey, serialized);
            }
        } catch (_) {
            // Keep in-memory copy when sessionStorage quota/privacy throws
        }
    }

    function removeRaw(storageKey) {
        memoryFallback.delete(storageKey);
        try {
            if (global.sessionStorage) {
                global.sessionStorage.removeItem(storageKey);
            }
        } catch (_) {
            // Ignore storage removal errors
        }
    }

    function listStorageKeys() {
        const keys = new Set(memoryFallback.keys());
        try {
            if (global.sessionStorage) {
                for (let i = 0; i < global.sessionStorage.length; i++) {
                    const k = global.sessionStorage.key(i);
                    if (k && k.startsWith(STORAGE_PREFIX)) {
                        keys.add(k);
                    }
                }
            }
        } catch (_) {
            // Ignore storage enumeration errors
        }
        return Array.from(keys);
    }

    function getDraft(draftKey) {
        if (!draftKey) return null;
        const raw = readRaw(getStorageKey(draftKey));
        if (!raw) return null;
        try {
            const parsed = JSON.parse(raw);
            return parsed && typeof parsed === "object" ? parsed : null;
        } catch (_) {
            removeRaw(getStorageKey(draftKey));
            return null;
        }
    }

    function setDraft(draftKey, payload) {
        if (!draftKey) return;
        const storageKey = getStorageKey(draftKey);
        if (payload == null) {
            removeRaw(storageKey);
            return;
        }
        try {
            writeRaw(storageKey, JSON.stringify(payload));
        } catch (_) {
            // Ignore serialization errors
        }
    }

    function clear(draftKey) {
        if (!draftKey) return;
        removeRaw(getStorageKey(draftKey));
    }

    function clearByPrefix(prefix) {
        const fullPrefix = getStorageKey(prefix || "");
        listStorageKeys().forEach((k) => {
            if (k.startsWith(fullPrefix)) {
                removeRaw(k);
            }
        });
    }

    function hasDraft(draftKey) {
        return getDraft(draftKey) !== null;
    }

    function isElementEligible(el, excludeSet, includeHiddenSet) {
        if (!el || !el.tagName) return false;
        const tag = el.tagName.toUpperCase();
        if (tag !== "INPUT" && tag !== "SELECT" && tag !== "TEXTAREA") return false;

        const fieldKey = el.id || el.name;
        if (!fieldKey) return false;
        if (excludeSet.has(fieldKey) || (el.name && excludeSet.has(el.name)) || (el.id && excludeSet.has(el.id))) {
            return false;
        }
        if (el.getAttribute("data-draft-ignore") === "true") return false;

        if (tag === "INPUT") {
            const type = String(el.type || "text").toLowerCase();
            if (EXCLUDED_INPUT_TYPES.has(type)) return false;
            if (type === "hidden" && !includeHiddenSet.has(fieldKey) && !(el.name && includeHiddenSet.has(el.name))) {
                return false;
            }
        }
        return true;
    }

    function getSelectDefaultValue(selectEl) {
        if (!selectEl || !selectEl.options || selectEl.options.length === 0) return "";
        for (let i = 0; i < selectEl.options.length; i++) {
            if (selectEl.options[i].defaultSelected) {
                return selectEl.options[i].value;
            }
        }
        return selectEl.options[0].value;
    }

    function readFormValues(formEl, excludeSet, includeHiddenSet) {
        const fields = {};
        let hasMeaningfulValue = false;
        const controls = formEl.querySelectorAll("input, select, textarea");

        controls.forEach((el) => {
            if (!isElementEligible(el, excludeSet, includeHiddenSet)) return;
            const tag = el.tagName.toUpperCase();
            const type = tag === "INPUT" ? String(el.type || "text").toLowerCase() : tag.toLowerCase();
            const key = type === "radio" ? (el.name || el.id) : (el.id || el.name);

            if (type === "checkbox") {
                fields[key] = Boolean(el.checked);
                if (el.checked !== Boolean(el.defaultChecked)) {
                    hasMeaningfulValue = true;
                }
            } else if (type === "radio") {
                if (el.checked) {
                    fields[key] = el.value;
                    if (!el.defaultChecked) {
                        hasMeaningfulValue = true;
                    }
                }
            } else if (tag === "SELECT") {
                fields[key] = el.value;
                if (el.value !== getSelectDefaultValue(el)) {
                    hasMeaningfulValue = true;
                }
            } else {
                fields[key] = el.value;
                if (String(el.value || "").length > 0) {
                    hasMeaningfulValue = true;
                }
            }
        });

        if (!hasMeaningfulValue) return null;
        return { fields, updatedAt: Date.now() };
    }

    function restoreFormValues(formEl, draft, excludeSet, includeHiddenSet) {
        if (!draft || !draft.fields || typeof draft.fields !== "object") {
            return { restored: false, fields: [] };
        }

        const restoredKeys = [];
        const controls = formEl.querySelectorAll("input, select, textarea");

        controls.forEach((el) => {
            if (!isElementEligible(el, excludeSet, includeHiddenSet)) return;
            const tag = el.tagName.toUpperCase();
            const type = tag === "INPUT" ? String(el.type || "text").toLowerCase() : tag.toLowerCase();
            const key = type === "radio" ? (el.name || el.id) : (el.id || el.name);

            if (!Object.prototype.hasOwnProperty.call(draft.fields, key)) return;
            const savedVal = draft.fields[key];

            if (type === "checkbox") {
                el.checked = Boolean(savedVal);
                restoredKeys.push(key);
            } else if (type === "radio") {
                el.checked = el.value === String(savedVal);
                if (el.checked) restoredKeys.push(key);
            } else if (tag === "SELECT") {
                const strVal = String(savedVal == null ? "" : savedVal);
                const exists = Array.from(el.options || []).some((opt) => opt.value === strVal);
                if (exists) {
                    el.value = strVal;
                    restoredKeys.push(key);
                }
            } else {
                el.value = String(savedVal == null ? "" : savedVal);
                restoredKeys.push(key);
            }
        });

        return { restored: restoredKeys.length > 0, fields: restoredKeys };
    }

    function bindGlobalLifecycle() {
        if (listenersBound || typeof global.addEventListener !== "function") return;
        listenersBound = true;
        global.addEventListener("pagehide", function () {
            saveAll();
        });
    }

    function registerForm(formOrId, options) {
        const opts = options || {};
        const formEl = typeof formOrId === "string"
            ? (global.document && global.document.getElementById(formOrId))
            : formOrId;
        if (!formEl) return null;

        const draftKey = opts.draftKey || formEl.id || (global.location ? global.location.pathname : "form");
        const excludeSet = new Set(opts.excludeFields || []);
        const includeHiddenSet = new Set(opts.includeHiddenFields || []);

        // Clean up any previous listeners for the same key
        if (registry.has(draftKey)) {
            const prev = registry.get(draftKey);
            if (prev && typeof prev.destroy === "function") prev.destroy();
        }

        const save = () => {
            const payload = readFormValues(formEl, excludeSet, includeHiddenSet);
            setDraft(draftKey, payload);
            return payload;
        };

        const restore = () => {
            const draft = getDraft(draftKey);
            const result = restoreFormValues(formEl, draft, excludeSet, includeHiddenSet);
            if (result.restored && typeof opts.onRestore === "function") {
                try {
                    opts.onRestore(draft.fields, result.fields);
                } catch (_) {
                    // Protect restore lifecycle from callback errors
                }
            }
            return result;
        };

        const clearDraft = () => clear(draftKey);

        const handleInput = () => save();
        formEl.addEventListener("input", handleInput);
        formEl.addEventListener("change", handleInput);

        const destroy = () => {
            formEl.removeEventListener("input", handleInput);
            formEl.removeEventListener("change", handleInput);
            registry.delete(draftKey);
        };

        const entry = {
            draftKey,
            save,
            restore,
            clear: clearDraft,
            getDraft: () => getDraft(draftKey),
            destroy,
        };

        registry.set(draftKey, entry);
        bindGlobalLifecycle();

        if (opts.autoRestore !== false) {
            restore();
        }

        return entry;
    }

    function registerCustom(draftKey, handlers) {
        if (!draftKey || !handlers) return null;

        if (registry.has(draftKey)) {
            const prev = registry.get(draftKey);
            if (prev && typeof prev.destroy === "function") prev.destroy();
        }

        const save = () => {
            if (typeof handlers.read !== "function") return null;
            const payload = handlers.read();
            setDraft(draftKey, payload);
            return payload;
        };

        const restore = () => {
            const draft = getDraft(draftKey);
            if (draft !== null && typeof handlers.restore === "function") {
                try {
                    handlers.restore(draft);
                    return { restored: true, data: draft };
                } catch (_) {
                    return { restored: false, data: null };
                }
            }
            return { restored: false, data: null };
        };

        const clearDraft = () => clear(draftKey);

        const entry = {
            draftKey,
            save,
            restore,
            clear: clearDraft,
            getDraft: () => getDraft(draftKey),
            destroy: () => registry.delete(draftKey),
        };

        registry.set(draftKey, entry);
        bindGlobalLifecycle();

        if (handlers.autoRestore !== false) {
            restore();
        }

        return entry;
    }

    function save(draftKey) {
        const entry = registry.get(draftKey);
        return entry ? entry.save() : null;
    }

    function saveAll() {
        registry.forEach((entry) => {
            try {
                entry.save();
            } catch (_) {
                // Continue saving remaining registered forms
            }
        });
    }

    const api = {
        STORAGE_PREFIX,
        getStorageKey,
        getDraft,
        setDraft,
        hasDraft,
        clear,
        clearByPrefix,
        registerForm,
        registerCustom,
        save,
        saveAll,
    };

    if (typeof global !== "undefined") {
        global.JaguarFormDrafts = api;
    }
    if (typeof module !== "undefined" && module.exports) {
        module.exports = api;
    }
})(typeof window !== "undefined" ? window : globalThis);
