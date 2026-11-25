/**
 * ================================================================================
 * I18NMANAGER.JS - REACTIVE CLIENT-SIDE LANGUAGE SWITCHER & DOM TRANSLATOR
 * ================================================================================
 * Updates session language via /api/i18n/set-language/<lang> and applies
 * translations across the active DOM without triggering a full page reload.
 *
 * Features:
 * - Intercepts clicks on `[data-lang-switch]` toggles (progressive enhancement
 *   over the server `/set-language/<lang>` route).
 * - Saves all registered form drafts via `window.JaguarFormDrafts.saveAll()`
 *   before switching so inputs are protected both in-memory and in sessionStorage.
 * - Updates `<title data-i18n>`, `[data-i18n]`, `[data-i18n-placeholder]`,
 *   `[data-i18n-title]`, `[data-i18n-aria-label]`, and `[data-i18n-es]/[data-i18n-en]`.
 * - Dispatches `jaguarLanguageChanged` so dynamic modules (auth validation,
 *   map navigation, catalog cards, GPS panels) re-translate in place.
 * ================================================================================
 */

(function (global) {
    "use strict";

    let latestRequestSeq = 0;
    let clickDelegationBound = false;

    function normalizeLang(lang) {
        const clean = String(lang || "").trim().toLowerCase();
        return clean.startsWith("sp") || clean.startsWith("es") ? "spa" : "eng";
    }

    function getLang() {
        if (global.APP_CONFIG && global.APP_CONFIG.currentLang) {
            return normalizeLang(global.APP_CONFIG.currentLang);
        }
        if (global.document && global.document.documentElement && global.document.documentElement.lang) {
            return normalizeLang(global.document.documentElement.lang);
        }
        return "eng";
    }

    function isSpanish() {
        return getLang() === "spa";
    }

    function pick(esText, enText) {
        return isSpanish() ? esText : enText;
    }

    function resolveRaw(dict, keyPath) {
        if (!dict || !keyPath) return null;
        const keys = String(keyPath).split(".");
        let curr = dict;
        for (const k of keys) {
            if (curr && typeof curr === "object" && Object.prototype.hasOwnProperty.call(curr, k)) {
                curr = curr[k];
            } else {
                return null;
            }
        }
        return curr !== undefined ? curr : null;
    }

    function resolveFromDict(dict, keyPath) {
        const curr = resolveRaw(dict, keyPath);
        return typeof curr === "string" ? curr : null;
    }

    function getRaw(keyPath, defaultValue) {
        const found = resolveRaw(global.APP_TRANSLATIONS, keyPath);
        return found !== null ? found : (defaultValue !== undefined ? defaultValue : null);
    }

    function formatTemplate(text, params) {
        if (!params || typeof text !== "string") return text;
        let out = text;
        for (const [k, v] of Object.entries(params)) {
            out = out.replace(new RegExp(`\\{${k}\\}`, "g"), String(v));
        }
        return out;
    }

    function translate(keyPath, defaultText, params) {
        let fallback = defaultText;
        let fmtParams = params;
        // Allow calling t("some.key", { count: 3 }) without a hardcoded fallback string
        if (defaultText && typeof defaultText === "object" && params === undefined) {
            fmtParams = defaultText;
            fallback = undefined;
        }
        if (!keyPath) return formatTemplate(fallback || "", fmtParams);
        const found = resolveFromDict(global.APP_TRANSLATIONS, keyPath);
        const raw = found !== null ? found : (fallback !== undefined && fallback !== null ? fallback : keyPath);
        return formatTemplate(String(raw), fmtParams);
    }

    function updateSwitcherControls(activeLang, root) {
        const doc = root || global.document;
        if (!doc || typeof doc.querySelectorAll !== "function") return;

        doc.querySelectorAll("[data-lang-switch]").forEach((el) => {
            const btnLang = normalizeLang(el.getAttribute("data-lang-switch"));
            const isActive = btnLang === activeLang;
            el.setAttribute("aria-pressed", isActive ? "true" : "false");
            if (isActive) {
                el.setAttribute("aria-current", "true");
                el.classList.add("bg-white", "text-slate-900", "shadow-xs");
                el.classList.remove("text-slate-500", "hover:text-slate-800");
            } else {
                el.removeAttribute("aria-current");
                el.classList.remove("bg-white", "text-slate-900", "shadow-xs");
                el.classList.add("text-slate-500", "hover:text-slate-800");
            }
        });
    }

    function applyTranslations(lang, root) {
        const activeLang = normalizeLang(lang || getLang());
        const doc = root || global.document;
        if (!doc) return;

        if (doc === global.document && doc.documentElement) {
            doc.documentElement.lang = activeLang;
        }

        const isSpa = activeLang === "spa";

        if (doc === global.document && doc.head) {
            const titleEl = doc.head.querySelector("title[data-i18n]");
            if (titleEl) {
                const titleKey = titleEl.getAttribute("data-i18n");
                const resolved = resolveFromDict(global.APP_TRANSLATIONS, titleKey);
                if (resolved !== null) {
                    doc.title = resolved;
                    titleEl.textContent = resolved;
                }
            } else {
                const bilingualTitleEl = doc.head.querySelector("title[data-i18n-es][data-i18n-en]");
                if (bilingualTitleEl) {
                    const nextTitle = isSpa
                        ? bilingualTitleEl.getAttribute("data-i18n-es")
                        : bilingualTitleEl.getAttribute("data-i18n-en");
                    if (nextTitle) {
                        doc.title = nextTitle;
                        bilingualTitleEl.textContent = nextTitle;
                    }
                }
            }
        }

        if (typeof doc.querySelectorAll === "function") {
            doc.querySelectorAll("[data-i18n]").forEach((el) => {
                if (el.tagName && el.tagName.toUpperCase() === "TITLE") return;
                const key = el.getAttribute("data-i18n");
                const resolved = resolveFromDict(global.APP_TRANSLATIONS, key);
                if (resolved !== null) {
                    el.textContent = resolved;
                }
            });

            doc.querySelectorAll("[data-i18n-es][data-i18n-en]").forEach((el) => {
                if (el.tagName && el.tagName.toUpperCase() === "TITLE") return;
                el.textContent = isSpa ? el.getAttribute("data-i18n-es") : el.getAttribute("data-i18n-en");
            });

            doc.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
                const key = el.getAttribute("data-i18n-placeholder");
                const resolved = resolveFromDict(global.APP_TRANSLATIONS, key);
                if (resolved !== null) {
                    el.setAttribute("placeholder", resolved);
                    if ("placeholder" in el) el.placeholder = resolved;
                }
            });

            doc.querySelectorAll("[data-i18n-title]").forEach((el) => {
                const key = el.getAttribute("data-i18n-title");
                const resolved = resolveFromDict(global.APP_TRANSLATIONS, key);
                if (resolved !== null) {
                    el.setAttribute("title", resolved);
                }
            });

            doc.querySelectorAll("[data-i18n-aria-label]").forEach((el) => {
                const key = el.getAttribute("data-i18n-aria-label");
                const resolved = resolveFromDict(global.APP_TRANSLATIONS, key);
                if (resolved !== null) {
                    el.setAttribute("aria-label", resolved);
                }
            });

            doc.querySelectorAll("[data-i18n-label]").forEach((el) => {
                const key = el.getAttribute("data-i18n-label");
                const resolved = resolveFromDict(global.APP_TRANSLATIONS, key);
                if (resolved !== null) {
                    el.setAttribute("label", resolved);
                    if ("label" in el) el.label = resolved;
                }
            });

            doc.querySelectorAll("[data-i18n-alt]").forEach((el) => {
                const key = el.getAttribute("data-i18n-alt");
                const resolved = resolveFromDict(global.APP_TRANSLATIONS, key);
                if (resolved !== null) {
                    el.setAttribute("alt", resolved);
                }
            });

            doc.querySelectorAll("[data-i18n-value]").forEach((el) => {
                const key = el.getAttribute("data-i18n-value");
                const resolved = resolveFromDict(global.APP_TRANSLATIONS, key);
                if (resolved !== null) {
                    el.setAttribute("value", resolved);
                    if ("value" in el) el.value = resolved;
                }
            });
        }

        updateSwitcherControls(activeLang, doc);
    }

    async function setLanguage(targetLang, options) {
        const opts = options || {};
        const cleanLang = normalizeLang(targetLang);
        const previousLang = getLang();

        // Always snapshot form drafts before any language transition
        if (global.JaguarFormDrafts && typeof global.JaguarFormDrafts.saveAll === "function") {
            global.JaguarFormDrafts.saveAll();
        }

        if (cleanLang === previousLang && !opts.force) {
            updateSwitcherControls(cleanLang);
            return {
                success: true,
                language: cleanLang,
                previousLang,
                unchanged: true,
            };
        }

        const seq = ++latestRequestSeq;

        try {
            const res = await global.fetch(`/api/i18n/set-language/${encodeURIComponent(cleanLang)}`, {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    Accept: "application/json",
                },
            });

            if (!res.ok) {
                throw new Error(`HTTP ${res.status}`);
            }

            const data = await res.json();
            let translations = data && data.translations && typeof data.translations === "object"
                ? data.translations
                : null;

            if (!translations) {
                const dictRes = await global.fetch(`/api/i18n/translations/${encodeURIComponent(cleanLang)}`, {
                    credentials: "same-origin",
                    headers: { Accept: "application/json" },
                });
                if (!dictRes.ok) {
                    throw new Error(`HTTP ${dictRes.status}`);
                }
                const dictData = await dictRes.json();
                translations = (dictData && dictData.translations) || {};
            }

            // Ignore out-of-order responses from rapid consecutive clicks
            if (seq !== latestRequestSeq) {
                return { success: false, stale: true, language: cleanLang };
            }

            global.APP_CONFIG = global.APP_CONFIG || {};
            global.APP_CONFIG.currentLang = cleanLang;
            global.APP_TRANSLATIONS = translations;

            applyTranslations(cleanLang);

            if (typeof global.dispatchEvent === "function" && typeof global.CustomEvent === "function") {
                global.dispatchEvent(new global.CustomEvent("jaguarLanguageChanged", {
                    detail: {
                        lang: cleanLang,
                        previousLang,
                        translations,
                    },
                }));
            }

            return {
                success: true,
                language: cleanLang,
                previousLang,
                translations,
            };
        } catch (err) {
            if (global.console && typeof global.console.warn === "function") {
                global.console.warn("Reactive language switch failed:", err);
            }
            return {
                success: false,
                error: err,
                language: previousLang,
            };
        }
    }

    function bindSwitcherDelegation() {
        if (clickDelegationBound || !global.document || typeof global.document.addEventListener !== "function") {
            return;
        }
        clickDelegationBound = true;

        global.document.addEventListener("click", function (e) {
            const trigger = e.target && typeof e.target.closest === "function"
                ? e.target.closest("[data-lang-switch]")
                : null;
            if (!trigger) return;

            // Allow modifier-click (open in new tab) to behave normally
            if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;

            e.preventDefault();
            const targetLang = trigger.getAttribute("data-lang-switch");
            if (targetLang) {
                setLanguage(targetLang);
            }
        });
    }

    // Export global helpers
    const api = {
        normalizeLang,
        getLang,
        isSpanish,
        pick,
        t: translate,
        get: getRaw,
        resolve: getRaw,
        applyTranslations,
        updateSwitcherControls,
        setLanguage,
    };

    if (typeof global !== "undefined") {
        global.JaguarI18n = api;
        global.t = translate;
        bindSwitcherDelegation();
    }
    if (typeof module !== "undefined" && module.exports) {
        module.exports = api;
    }
})(typeof window !== "undefined" ? window : globalThis);
