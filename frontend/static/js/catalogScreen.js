/**
 * catalogScreen.js
 * ================================================================================
 * LOST & FOUND CATALOG CONTROLLER (URL PARAMS, BUILDING FILTER & DETAIL MODAL)
 * ================================================================================
 * Manages:
 * - Reading URL query parameters (?building=..., ?location=..., ?item=..., ?q=...,
 *   ?category=..., ?stateId=...) and route-injected item IDs on load
 * - Building filter dropdown + prominent active building filter banner with
 *   one-click clear action to return to browsing all items
 * - Pinterest-style Item Detail Modal auto-opening on ?item=<id> or /catalog/<id>,
 *   accessible from map popups and catalog cards, with claim request submission,
 *   building filtering, 2.5D map link, shareable link copy, and admin status editing
 * - Reactive bilingual (ES / EN) re-rendering on `jaguarLanguageChanged`
 */

(function (global) {
    "use strict";

    function escapeHtml(value) {
        return String(value == null ? "" : value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function tr(key, fallbackEs, fallbackEn, params) {
        const isEs = global.JaguarI18n
            ? global.JaguarI18n.isSpanish()
            : !(global.APP_CONFIG && String(global.APP_CONFIG.currentLang || "").toLowerCase().startsWith("en"));
        const fallback = isEs ? fallbackEs : fallbackEn;
        if (typeof global.t === "function") {
            return global.t(key, fallback, params);
        }
        if (params && typeof fallback === "string") {
            let out = fallback;
            for (const [k, v] of Object.entries(params)) {
                out = out.replace(new RegExp(`\\{${k}\\}`, "g"), String(v));
            }
            return out;
        }
        return fallback;
    }

    function parsePositiveInt(raw) {
        if (raw == null) return null;
        const clean = String(raw).trim();
        if (!/^\d+$/.test(clean)) return null;
        const parsed = parseInt(clean, 10);
        return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
    }

    function resolveBuildingLabel(buildingId, fallbackName) {
        const cleanId = String(buildingId || "").trim();
        if (!cleanId) return fallbackName || "";

        if (typeof global.t === "function") {
            const translated = global.t(`nodes.${cleanId}`, "");
            if (translated && translated !== `nodes.${cleanId}`) {
                return translated;
            }
        }

        const filterSelect = global.document && global.document.getElementById("filterBuilding");
        if (filterSelect && filterSelect.options) {
            const match = Array.from(filterSelect.options).find(
                (opt) => opt.value && opt.value.toLowerCase() === cleanId.toLowerCase()
            );
            if (match && match.textContent) {
                return match.textContent.trim();
            }
        }

        return fallbackName || cleanId;
    }

    function initCatalogScreen() {
        const doc = global.document;
        if (!doc) return null;

        const root = doc.getElementById("catalogAppRoot");
        const grid = doc.getElementById("catalogGrid");
        if (!root || !grid) return null;

        const isAdmin = root.getAttribute("data-is-admin") === "true";
        const initialRouteItemId = parsePositiveInt(root.getAttribute("data-initial-item-id"));
        const defaultUserName = (root.getAttribute("data-user-name") || "").trim();
        const defaultUserContact = (root.getAttribute("data-user-contact") || "").trim();

        const loading = doc.getElementById("catalogLoading");
        const emptyState = doc.getElementById("catalogEmpty");
        const btnClearFiltersEmpty = doc.getElementById("btnClearFiltersEmpty");
        const itemsCountText = doc.getElementById("catalogItemsCount");
        const searchInput = doc.getElementById("catalogSearchInput");
        const filterBuilding = doc.getElementById("filterBuilding");
        const filterCategory = doc.getElementById("filterCategory");
        const filterState = doc.getElementById("filterState");
        const btnRefresh = doc.getElementById("btnRefreshCatalog");
        const btnOpenReport = doc.getElementById("btnOpenReportDialog");

        const activeBuildingBanner = doc.getElementById("activeBuildingFilterBanner");
        const activeBuildingLabel = doc.getElementById("activeBuildingFilterLabel");
        const btnClearBuildingFilter = doc.getElementById("btnClearBuildingFilter");

        // Item Detail Modal DOM elements
        const detailModal = doc.getElementById("itemDetailModal");
        const btnCloseDetail = doc.getElementById("btnCloseItemDetailModal");
        const btnCloseDetailError = doc.getElementById("btnCloseItemDetailError");
        const detailLoading = doc.getElementById("itemDetailLoading");
        const detailError = doc.getElementById("itemDetailError");
        const detailContent = doc.getElementById("itemDetailContent");
        const detailPhoto = doc.getElementById("detailItemPhoto");
        const detailNoPhoto = doc.getElementById("detailItemNoPhoto");
        const detailStateBadge = doc.getElementById("detailStateBadge");
        const detailCategoryBadge = doc.getElementById("detailCategoryBadge");
        const detailTicketId = doc.getElementById("detailTicketId");
        const detailTitle = doc.getElementById("detailItemTitle");
        const detailLocationBtn = doc.getElementById("btnDetailFilterBuilding");
        const detailLocationText = doc.getElementById("detailItemLocation");
        const detailDescription = doc.getElementById("detailItemDescription");
        const detailDate = doc.getElementById("detailItemDate");
        const detailReporterWrap = doc.getElementById("detailItemReporterWrap");
        const detailReporter = doc.getElementById("detailItemReporter");
        const detailResolvedWrap = doc.getElementById("detailItemResolvedWrap");
        const detailResolvedDate = doc.getElementById("detailItemResolvedDate");
        const detailCustodyBox = doc.getElementById("detailCustodyBox");
        const detailCustodyText = doc.getElementById("detailCustodyText");
        const detailSecretBox = doc.getElementById("detailSecretBox");
        const detailSecretText = doc.getElementById("detailSecretText");
        const btnDetailViewOnMap = doc.getElementById("btnDetailViewOnMap");
        const btnDetailMoreInBuilding = doc.getElementById("btnDetailMoreInBuilding");
        const btnDetailAdminEdit = doc.getElementById("btnDetailAdminEditState");
        const btnDetailCopyLink = doc.getElementById("btnDetailCopyLink");
        const detailCopyLabel = doc.getElementById("detailCopyLinkLabel");

        // Inline claim elements inside detail modal
        const btnToggleClaimForm = doc.getElementById("btnToggleClaimForm");
        const detailClaimSection = doc.getElementById("detailClaimSection");
        const detailClaimForm = doc.getElementById("detailClaimForm");
        const claimantNameInput = doc.getElementById("claimantNameInput");
        const claimantContactInput = doc.getElementById("claimantContactInput");
        const claimSecretInput = doc.getElementById("claimSecretInput");
        const btnCancelClaimForm = doc.getElementById("btnCancelClaimForm");
        const btnSubmitClaimForm = doc.getElementById("btnSubmitClaimForm");
        const detailClaimAlert = doc.getElementById("detailClaimAlert");

        let allItems = [];
        let activeDetailItem = null;
        let activeDetailItemId = null;
        let detailRequestSeq = 0;
        let copyTimer = null;

        function getCanonicalBasePath() {
            const path = (global.location && global.location.pathname) || "/lost-found-object/catalogo";
            if (/^\/admin\/items/i.test(path)) return "/admin/items";
            if (/^\/catalog(\/\d+)?\/?$/i.test(path)) return "/catalog";
            return "/lost-found-object/catalogo";
        }

        function setBuildingFilterValue(rawBuildingId) {
            if (!filterBuilding) return "";
            const clean = String(rawBuildingId || "").trim();
            if (!clean) {
                filterBuilding.value = "";
                return "";
            }
            const opts = Array.from(filterBuilding.options || []);
            const exact = opts.find((opt) => opt.value === clean);
            if (exact) {
                filterBuilding.value = exact.value;
                return exact.value;
            }
            const ciMatch = opts.find((opt) => opt.value && opt.value.toLowerCase() === clean.toLowerCase());
            if (ciMatch) {
                filterBuilding.value = ciMatch.value;
                return ciMatch.value;
            }
            const dynOpt = doc.createElement("option");
            dynOpt.value = clean;
            dynOpt.textContent = resolveBuildingLabel(clean, clean);
            dynOpt.setAttribute("data-dynamic-building", "true");
            filterBuilding.appendChild(dynOpt);
            filterBuilding.value = clean;
            return clean;
        }

        function updateBuildingFilterBanner() {
            if (!activeBuildingBanner) return;
            const selectedBuilding = filterBuilding ? filterBuilding.value.trim() : "";
            if (!selectedBuilding) {
                activeBuildingBanner.classList.add("hidden");
                if (activeBuildingLabel) activeBuildingLabel.textContent = "";
                return;
            }
            if (activeBuildingLabel) {
                activeBuildingLabel.textContent = resolveBuildingLabel(selectedBuilding, selectedBuilding);
            }
            activeBuildingBanner.classList.remove("hidden");
        }

        function hasAnyActiveFilter() {
            const b = filterBuilding ? filterBuilding.value.trim() : "";
            const c = filterCategory ? filterCategory.value.trim() : "";
            const s = filterState ? filterState.value.trim() : "";
            const q = searchInput ? searchInput.value.trim() : "";
            return Boolean(b || c || s || q);
        }

        function updateEmptyStateClearButton() {
            if (!btnClearFiltersEmpty) return;
            btnClearFiltersEmpty.classList.toggle("hidden", !hasAnyActiveFilter());
        }

        function syncBrowserUrl(options) {
            if (!global.history || typeof global.history.replaceState !== "function") return;
            const opts = options || {};
            const params = new URLSearchParams();

            const building = filterBuilding ? filterBuilding.value.trim() : "";
            const cat = filterCategory ? filterCategory.value.trim() : "";
            const state = filterState ? filterState.value.trim() : "";
            const q = searchInput ? searchInput.value.trim() : "";

            if (building) params.set("building", building);
            if (cat) params.set("category", cat);
            if (state) params.set("stateId", state);
            if (q) params.set("q", q);
            if (activeDetailItemId != null) params.set("item", String(activeDetailItemId));

            const qs = params.toString();
            const targetUrl = getCanonicalBasePath() + (qs ? `?${qs}` : "");
            if (opts.push && typeof global.history.pushState === "function") {
                global.history.pushState({ itemId: activeDetailItemId, building }, "", targetUrl);
            } else {
                global.history.replaceState({ itemId: activeDetailItemId, building }, "", targetUrl);
            }
        }

        function getStateBadge(stateId, stateName) {
            if (stateId === 1) {
                const label = escapeHtml(tr("lost_found.state_reported", "Reportado", "Reported"));
                return `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-50 text-amber-800 border border-amber-200">
                    <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>${label}
                </span>`;
            }
            if (stateId === 2) {
                const label = escapeHtml(tr("lost_found.state_custody", "En Custodia (Edif. A)", "In Custody (Bldg. A)"));
                return `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-sky-50 text-sky-800 border border-sky-200">
                    <span class="w-1.5 h-1.5 rounded-full bg-brand-500"></span>${label}
                </span>`;
            }
            if (stateId === 3) {
                const label = escapeHtml(tr("lost_found.state_claimed", "Entregado / Reclamado", "Claimed / Delivered"));
                return `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>${label}
                </span>`;
            }
            return `<span class="px-2 py-0.5 rounded-full text-xs bg-slate-100 text-slate-700">${escapeHtml(stateName || "Unknown")}</span>`;
        }

        function getCategoryBadge(cat) {
            const map = {
                electronics: {
                    label: tr("lost_found.cat_electronics", "Electrónica", "Electronics"),
                    icon: '<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>',
                },
                documents: {
                    label: tr("lost_found.cat_documents", "Documentos", "Documents"),
                    icon: '<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2"/></svg>',
                },
                personalItems: {
                    label: tr("lost_found.cat_personal", "Personal", "Personal"),
                    icon: '<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>',
                },
                clothing: {
                    label: tr("lost_found.cat_clothing", "Ropa", "Clothing"),
                    icon: '<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7l6-3 3 3 3-3 6 3v13H3V7z"/></svg>',
                },
                other: {
                    label: tr("lost_found.cat_other", "Otros", "Other"),
                    icon: '<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>',
                },
            };
            const c = map[cat] || map.other;
            return `<span class="inline-flex items-center gap-1">${c.icon}<span>${escapeHtml(c.label)}</span></span>`;
        }

        async function loadCatalog(options) {
            const opts = options || {};
            if (loading) loading.classList.remove("hidden");
            grid.classList.add("hidden");
            if (emptyState) emptyState.classList.add("hidden");

            updateBuildingFilterBanner();
            updateEmptyStateClearButton();
            if (opts.syncUrl !== false) {
                syncBrowserUrl({ push: Boolean(opts.pushHistory) });
            }

            const building = filterBuilding ? filterBuilding.value.trim() : "";
            const cat = filterCategory ? filterCategory.value.trim() : "";
            const state = filterState ? filterState.value.trim() : "";
            const q = searchInput ? searchInput.value.trim() : "";

            const apiParams = new URLSearchParams();
            if (building) apiParams.set("building", building);
            if (cat) apiParams.set("category", cat);
            if (state) apiParams.set("stateId", state);
            if (q) apiParams.set("q", q);

            const qs = apiParams.toString();
            const url = "/api/lost-found-object/items" + (qs ? `?${qs}` : "");

            try {
                const res = await global.fetch(url);
                const data = await res.json();
                if (loading) loading.classList.add("hidden");

                if (data && data.success && Array.isArray(data.items)) {
                    allItems = data.items;
                    renderCards(allItems);
                } else {
                    allItems = [];
                    renderCards([]);
                }
            } catch (e) {
                if (loading) loading.classList.add("hidden");
                allItems = [];
                renderCards([]);
            }
            return allItems;
        }

        function renderCards(items) {
            const countKey = items.length === 1 ? "lost_found.items_found_singular" : "lost_found.items_found_plural";
            const countFallbackEs = items.length === 1 ? `${items.length} objeto encontrado` : `${items.length} objetos encontrados`;
            const countFallbackEn = items.length === 1 ? `${items.length} item found` : `${items.length} items found`;
            if (itemsCountText) {
                itemsCountText.textContent = tr(countKey, countFallbackEs, countFallbackEn, { count: items.length });
            }
            grid.innerHTML = "";
            updateEmptyStateClearButton();

            if (items.length === 0) {
                if (emptyState) emptyState.classList.remove("hidden");
                grid.classList.add("hidden");
                return;
            }

            if (emptyState) emptyState.classList.add("hidden");
            grid.classList.remove("hidden");

            const viewDetailsLabel = escapeHtml(tr("lost_found.view_details", "Ver detalle", "View details"));
            const viewMapLabel = escapeHtml(tr("lost_found.view_on_map_25d", "Ver en Mapa 2.5D", "View on 2.5D Map"));
            const editStateLabel = escapeHtml(tr("lost_found.edit_ticket_state", "Editar Estado Ticket", "Edit Ticket Status"));
            const antifraudLabel = escapeHtml(tr("lost_found.antifraud_badge", "Antifraude", "Anti-fraud"));
            const custodyShortHint = escapeHtml(
                tr(
                    "lost_found.detail_custody_in_custody",
                    "En custodia en Edificio A (CAE). Presenta tu carnet o cédula.",
                    "In custody at Building A (CAE). Present your UAM ID or national ID."
                )
            );

            items.forEach((item) => {
                const card = doc.createElement("div");
                card.className = "bg-white rounded-3xl border border-slate-200/90 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-200 overflow-hidden flex flex-col";
                card.setAttribute("data-item-id", String(item.Id));

                const safeName = escapeHtml(item.ItemName);
                const safeDesc = escapeHtml(item.Description);
                const safeLocId = escapeHtml(item.Location);
                const safeLocLabel = escapeHtml(resolveBuildingLabel(item.Location, item.locationName || item.Location));
                const safeDate = escapeHtml(item.DateTimeReported ? String(item.DateTimeReported).split(" ")[0] : "");
                const mapHref = `/mapa?focus=${encodeURIComponent(item.Location)}&mode=25d`;

                const photoHtml = item.PhotoUrl
                    ? `<button type="button" data-open-item-detail="${item.Id}" class="w-full h-44 bg-slate-100 relative overflow-hidden block text-left cursor-pointer group">
                         <img src="${escapeHtml(item.PhotoUrl)}" alt="${safeName}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">
                         <div class="absolute top-3 left-3">${getStateBadge(item.LostObjectStateId, item.StateName)}</div>
                         <span class="absolute top-3 right-3 px-2.5 py-1 rounded-full text-[10px] font-extrabold bg-white/90 backdrop-blur-xs text-slate-800 shadow-xs">${getCategoryBadge(item.Category)}</span>
                       </button>`
                    : `<button type="button" data-open-item-detail="${item.Id}" class="w-full h-32 bg-gradient-to-br from-slate-100 to-slate-200 relative flex items-center justify-center cursor-pointer group">
                         <div class="w-12 h-12 rounded-2xl bg-white/80 border border-slate-200/80 flex items-center justify-center text-slate-400 group-hover:scale-105 transition-transform">
                           <svg class="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
                         </div>
                         <div class="absolute top-3 left-3">${getStateBadge(item.LostObjectStateId, item.StateName)}</div>
                         <span class="absolute top-3 right-3 px-2.5 py-1 rounded-full text-[10px] font-extrabold bg-white/90 backdrop-blur-xs text-slate-800 shadow-xs">${getCategoryBadge(item.Category)}</span>
                       </button>`;

                const actionBtn = isAdmin
                    ? `<div class="flex flex-col gap-1.5">
                         <div class="grid grid-cols-2 gap-1.5">
                           <button type="button" data-open-item-detail="${item.Id}"
                                   class="py-2 px-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs flex items-center justify-center gap-1.5 transition cursor-pointer shadow-2xs">
                             <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                             <span>${viewDetailsLabel}</span>
                           </button>
                           <button type="button" data-admin-edit-item="${item.Id}"
                                   class="py-2 px-2.5 rounded-xl bg-slate-800 hover:bg-slate-900 text-white font-bold text-xs flex items-center justify-center gap-1.5 transition cursor-pointer">
                             <svg class="w-3.5 h-3.5 text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                             <span class="truncate">${editStateLabel}</span>
                           </button>
                         </div>
                         <a href="${mapHref}"
                            class="w-full py-1.5 px-3 rounded-xl bg-slate-100 hover:bg-brand-50 border border-slate-200 text-slate-700 hover:text-brand-800 font-bold text-[11px] flex items-center justify-center gap-1.5 transition">
                           <svg class="w-3.5 h-3.5 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/></svg>
                           <span>${viewMapLabel}</span>
                         </a>
                       </div>`
                    : `<div class="space-y-1.5">
                         ${item.LostObjectStateId === 2 ? `<p class="text-[10px] text-sky-700 font-semibold bg-sky-50 px-2 py-1 rounded-lg border border-sky-100 flex items-center gap-1"><svg class="w-3 h-3 text-brand-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg><span class="line-clamp-2">${custodyShortHint}</span></p>` : ""}
                         <div class="grid grid-cols-2 gap-1.5">
                           <button type="button" data-open-item-detail="${item.Id}"
                                   class="py-2 px-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs flex items-center justify-center gap-1.5 transition cursor-pointer shadow-2xs">
                             <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                             <span>${viewDetailsLabel}</span>
                           </button>
                           <a href="${mapHref}"
                              class="py-2 px-2.5 rounded-xl bg-brand-50 hover:bg-brand-100 border border-brand-200/90 text-brand-800 font-bold text-xs flex items-center justify-center gap-1.5 transition">
                             <svg class="w-3.5 h-3.5 text-brand-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/></svg>
                             <span class="truncate">${viewMapLabel}</span>
                           </a>
                         </div>
                       </div>`;

                card.innerHTML = `
                    ${photoHtml}
                    <div class="p-5 flex-1 flex flex-col justify-between space-y-3">
                        <div>
                            <button type="button" data-open-item-detail="${item.Id}" class="text-left w-full group cursor-pointer">
                                <h3 class="font-extrabold text-base text-slate-900 group-hover:text-brand-700 leading-snug line-clamp-2 transition-colors">${safeName}</h3>
                            </button>
                            <button type="button" data-filter-building="${safeLocId}"
                                    title="${safeLocLabel}"
                                    class="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-brand-700 font-medium mt-1 max-w-full cursor-pointer transition-colors">
                                <svg class="w-3.5 h-3.5 text-brand-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                                <span class="truncate">${safeLocLabel}</span>
                            </button>
                            <p class="text-xs text-slate-600 mt-2 line-clamp-2">${safeDesc}</p>
                        </div>

                        <div class="pt-3 border-t border-slate-100 space-y-2.5">
                            <div class="flex items-center justify-between text-[11px] text-slate-400">
                                <span>${safeDate}</span>
                                ${item.hasSecretDetail ? `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold text-amber-700 bg-amber-50 border border-amber-200"><svg class="w-3 h-3 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4"/></svg><span>${antifraudLabel}</span></span>` : ""}
                            </div>
                            ${actionBtn}
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            });
        }

        // ------------------------------------------------------------------------
        // ITEM DETAIL MODAL (PINTEREST-STYLE PIN DETAIL VIEW)
        // ------------------------------------------------------------------------

        function resetClaimFormUi() {
            if (detailClaimSection) detailClaimSection.classList.add("hidden");
            if (detailClaimAlert) {
                detailClaimAlert.classList.add("hidden");
                detailClaimAlert.textContent = "";
            }
            if (claimantNameInput) claimantNameInput.value = defaultUserName;
            if (claimantContactInput) claimantContactInput.value = defaultUserContact;
            if (claimSecretInput) claimSecretInput.value = "";
            if (btnSubmitClaimForm) {
                btnSubmitClaimForm.disabled = false;
                btnSubmitClaimForm.textContent = tr("lost_found.detail_claim_submit", "Enviar solicitud de reclamo", "Submit claim request");
            }
        }

        function renderItemDetail(item) {
            if (!detailModal || !item) return;
            activeDetailItem = item;

            if (detailLoading) detailLoading.classList.add("hidden");
            if (detailError) detailError.classList.add("hidden");
            if (detailContent) detailContent.classList.remove("hidden");

            const locLabel = resolveBuildingLabel(item.Location, item.locationName || item.Location);

            if (detailTicketId) detailTicketId.textContent = `#${item.Id}`;
            if (detailTitle) detailTitle.textContent = item.ItemName || "";
            if (detailLocationText) detailLocationText.textContent = locLabel;
            if (detailLocationBtn) detailLocationBtn.setAttribute("data-building-id", item.Location || "");
            if (detailDescription) detailDescription.textContent = item.Description || "";
            if (detailDate) detailDate.textContent = item.DateTimeReported || "";

            if (detailStateBadge) detailStateBadge.innerHTML = getStateBadge(item.LostObjectStateId, item.StateName);
            if (detailCategoryBadge) detailCategoryBadge.innerHTML = getCategoryBadge(item.Category);

            if (detailPhoto && detailNoPhoto) {
                if (item.PhotoUrl) {
                    detailPhoto.src = item.PhotoUrl;
                    detailPhoto.alt = item.ItemName || "";
                    detailPhoto.classList.remove("hidden");
                    detailNoPhoto.classList.add("hidden");
                } else {
                    detailPhoto.src = "";
                    detailPhoto.classList.add("hidden");
                    detailNoPhoto.classList.remove("hidden");
                }
            }

            if (detailReporterWrap && detailReporter) {
                if (item.ReporterName) {
                    detailReporter.textContent = item.ReporterName;
                    detailReporterWrap.classList.remove("hidden");
                } else {
                    detailReporterWrap.classList.add("hidden");
                }
            }

            if (detailResolvedWrap && detailResolvedDate) {
                if (item.LostObjectStateId === 3 && item.DateTimeResolved) {
                    detailResolvedDate.textContent = item.DateTimeResolved;
                    detailResolvedWrap.classList.remove("hidden");
                } else {
                    detailResolvedWrap.classList.add("hidden");
                }
            }

            if (detailCustodyBox && detailCustodyText) {
                if (item.LostObjectStateId === 2) {
                    detailCustodyBox.className = "rounded-2xl p-3.5 text-xs font-semibold border bg-sky-50 text-sky-900 border-sky-200 flex items-start gap-2.5";
                    detailCustodyText.textContent = tr(
                        "lost_found.detail_custody_in_custody",
                        "En custodia segura en Edificio A (Oficina CAE - Planta Baja). Presenta tu carnet UAM o cédula para retirarlo.",
                        "Safely held in custody at Building A (CAE Office - Ground Floor). Present your UAM ID or national ID to collect it."
                    );
                } else if (item.LostObjectStateId === 3) {
                    detailCustodyBox.className = "rounded-2xl p-3.5 text-xs font-semibold border bg-emerald-50 text-emerald-900 border-emerald-200 flex items-start gap-2.5";
                    detailCustodyText.textContent = tr(
                        "lost_found.detail_custody_claimed",
                        "Este objeto ya fue verificado y entregado a su propietario.",
                        "This item has already been verified and returned to its owner."
                    );
                } else {
                    detailCustodyBox.className = "rounded-2xl p-3.5 text-xs font-semibold border bg-amber-50 text-amber-900 border-amber-200 flex items-start gap-2.5";
                    detailCustodyText.textContent = tr(
                        "lost_found.detail_custody_reported",
                        "Objeto reportado recientemente en el campus. Si es tuyo, solicita reclamo o acude al Edificio A (CAE).",
                        "Recently reported on campus. If it belongs to you, submit a claim or visit Building A (CAE)."
                    );
                }
            }

            if (detailSecretBox && detailSecretText) {
                if (item.SecretDetail) {
                    detailSecretText.textContent = item.SecretDetail;
                    detailSecretBox.classList.remove("hidden");
                } else if (item.hasSecretDetail) {
                    detailSecretText.textContent = tr(
                        "lost_found.detail_secret_protected",
                        "Este objeto cuenta con un detalle privado de verificación que se validará presencialmente en CAE (Edificio A).",
                        "This item has a private verification detail that will be checked in person at CAE (Building A)."
                    );
                    detailSecretBox.classList.remove("hidden");
                } else {
                    detailSecretBox.classList.add("hidden");
                }
            }

            if (btnDetailViewOnMap) {
                btnDetailViewOnMap.href = `/mapa?focus=${encodeURIComponent(item.Location)}&mode=25d`;
            }
            if (btnDetailMoreInBuilding) {
                btnDetailMoreInBuilding.setAttribute("data-building-id", item.Location || "");
            }
            if (btnToggleClaimForm) {
                const canClaim = item.LostObjectStateId !== 3;
                btnToggleClaimForm.classList.toggle("hidden", !canClaim);
            }
            if (detailCopyLabel) {
                detailCopyLabel.textContent = tr("lost_found.detail_copy_link", "Copiar enlace", "Copy link");
            }
        }

        async function openItemDetailModal(itemId, options) {
            if (!detailModal) return false;
            const parsedId = parsePositiveInt(itemId);
            if (!parsedId) return false;

            const opts = options || {};
            const reqSeq = ++detailRequestSeq;

            activeDetailItemId = parsedId;
            resetClaimFormUi();
            detailModal.classList.remove("hidden");
            if (doc.body && doc.body.classList) {
                doc.body.classList.add("overflow-hidden");
            }

            if (opts.syncUrl !== false) {
                syncBrowserUrl({ push: Boolean(opts.pushHistory) });
            }

            // Show cached item immediately if available while fetching authoritative detail
            const cached = allItems.find((it) => Number(it.Id) === parsedId);
            if (cached) {
                renderItemDetail(cached);
            } else {
                if (detailContent) detailContent.classList.add("hidden");
                if (detailError) detailError.classList.add("hidden");
                if (detailLoading) detailLoading.classList.remove("hidden");
            }

            try {
                const res = await global.fetch(`/api/lost-found-object/items/${encodeURIComponent(parsedId)}`);
                const data = await res.json();
                if (reqSeq !== detailRequestSeq) return false;

                if (res.ok && data && data.success && data.item) {
                    renderItemDetail(data.item);
                    return true;
                }

                if (!cached) {
                    activeDetailItem = null;
                    if (detailLoading) detailLoading.classList.add("hidden");
                    if (detailContent) detailContent.classList.add("hidden");
                    if (detailError) detailError.classList.remove("hidden");
                }
                return false;
            } catch (err) {
                if (reqSeq !== detailRequestSeq) return false;
                if (!cached) {
                    activeDetailItem = null;
                    if (detailLoading) detailLoading.classList.add("hidden");
                    if (detailContent) detailContent.classList.add("hidden");
                    if (detailError) detailError.classList.remove("hidden");
                }
                return false;
            }
        }

        function closeItemDetailModal(options) {
            if (!detailModal) return;
            const opts = options || {};
            detailModal.classList.add("hidden");
            if (doc.body && doc.body.classList) {
                doc.body.classList.remove("overflow-hidden");
            }
            activeDetailItem = null;
            activeDetailItemId = null;
            resetClaimFormUi();

            if (opts.syncUrl !== false) {
                syncBrowserUrl({ push: false });
            }
        }

        function applyBuildingFilter(buildingId, options) {
            setBuildingFilterValue(buildingId);
            updateBuildingFilterBanner();
            return loadCatalog(options);
        }

        function clearBuildingFilter() {
            setBuildingFilterValue("");
            updateBuildingFilterBanner();
            return loadCatalog({ syncUrl: true });
        }

        function clearAllFilters() {
            setBuildingFilterValue("");
            if (filterCategory) filterCategory.value = "";
            if (filterState) filterState.value = "";
            if (searchInput) searchInput.value = "";
            updateBuildingFilterBanner();
            return loadCatalog({ syncUrl: true });
        }

        // ------------------------------------------------------------------------
        // EVENT BINDINGS
        // ------------------------------------------------------------------------

        if (btnOpenReport) {
            btnOpenReport.addEventListener("click", () => {
                if (typeof global.openReportObjectDialog === "function") {
                    const currentBuilding = filterBuilding ? filterBuilding.value.trim() : "";
                    global.openReportObjectDialog(currentBuilding || undefined);
                }
            });
        }

        // Delegated click handler on catalog grid cards
        grid.addEventListener("click", (e) => {
            const target = e.target;
            if (!target || typeof target.closest !== "function") return;

            const detailTrigger = target.closest("[data-open-item-detail]");
            if (detailTrigger) {
                e.preventDefault();
                const id = parsePositiveInt(detailTrigger.getAttribute("data-open-item-detail"));
                if (id) openItemDetailModal(id, { syncUrl: true, pushHistory: true });
                return;
            }

            const bldgTrigger = target.closest("[data-filter-building]");
            if (bldgTrigger) {
                e.preventDefault();
                const bId = bldgTrigger.getAttribute("data-filter-building");
                if (bId) applyBuildingFilter(bId, { syncUrl: true });
                return;
            }

            if (isAdmin) {
                const adminTrigger = target.closest("[data-admin-edit-item]");
                if (adminTrigger && typeof global.openAdminStateModal === "function") {
                    e.preventDefault();
                    const id = parsePositiveInt(adminTrigger.getAttribute("data-admin-edit-item"));
                    const found = allItems.find((it) => Number(it.Id) === id);
                    if (found) {
                        global.openAdminStateModal(found.Id, found.ItemName, found.LostObjectStateId);
                    }
                }
            }
        });

        // Filter listeners
        if (searchInput) {
            searchInput.addEventListener("input", debounce(() => loadCatalog({ syncUrl: true }), 300));
        }
        if (filterBuilding) {
            filterBuilding.addEventListener("change", () => loadCatalog({ syncUrl: true }));
        }
        if (filterCategory) {
            filterCategory.addEventListener("change", () => loadCatalog({ syncUrl: true }));
        }
        if (filterState) {
            filterState.addEventListener("change", () => loadCatalog({ syncUrl: true }));
        }
        if (btnRefresh) {
            btnRefresh.addEventListener("click", () => loadCatalog({ syncUrl: false }));
        }
        if (btnClearBuildingFilter) {
            btnClearBuildingFilter.addEventListener("click", clearBuildingFilter);
        }
        if (btnClearFiltersEmpty) {
            btnClearFiltersEmpty.addEventListener("click", clearAllFilters);
        }

        // Detail modal interactions
        if (btnCloseDetail) {
            btnCloseDetail.addEventListener("click", () => closeItemDetailModal({ syncUrl: true }));
        }
        if (btnCloseDetailError) {
            btnCloseDetailError.addEventListener("click", () => closeItemDetailModal({ syncUrl: true }));
        }
        if (detailModal) {
            detailModal.addEventListener("click", (e) => {
                if (e.target === detailModal) {
                    closeItemDetailModal({ syncUrl: true });
                }
            });
        }
        doc.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && detailModal && !detailModal.classList.contains("hidden")) {
                closeItemDetailModal({ syncUrl: true });
            }
        });

        function handleFilterFromDetail(btn) {
            const bId = (btn && btn.getAttribute("data-building-id")) || (activeDetailItem && activeDetailItem.Location);
            if (!bId) return;
            closeItemDetailModal({ syncUrl: false });
            applyBuildingFilter(bId, { syncUrl: true });
        }

        if (detailLocationBtn) {
            detailLocationBtn.addEventListener("click", () => handleFilterFromDetail(detailLocationBtn));
        }
        if (btnDetailMoreInBuilding) {
            btnDetailMoreInBuilding.addEventListener("click", () => handleFilterFromDetail(btnDetailMoreInBuilding));
        }
        if (btnDetailAdminEdit && isAdmin) {
            btnDetailAdminEdit.addEventListener("click", () => {
                if (activeDetailItem && typeof global.openAdminStateModal === "function") {
                    global.openAdminStateModal(
                        activeDetailItem.Id,
                        activeDetailItem.ItemName,
                        activeDetailItem.LostObjectStateId
                    );
                }
            });
        }
        if (btnDetailCopyLink) {
            btnDetailCopyLink.addEventListener("click", async () => {
                if (activeDetailItemId == null) return;
                const origin = (global.location && global.location.origin) || "";
                const shareUrl = `${origin}/lost-found-object/catalogo?item=${encodeURIComponent(activeDetailItemId)}`;
                try {
                    if (global.navigator && global.navigator.clipboard && typeof global.navigator.clipboard.writeText === "function") {
                        await global.navigator.clipboard.writeText(shareUrl);
                    }
                    if (detailCopyLabel) {
                        detailCopyLabel.textContent = tr("lost_found.detail_link_copied", "¡Enlace copiado!", "Link copied!");
                        clearTimeout(copyTimer);
                        copyTimer = setTimeout(() => {
                            detailCopyLabel.textContent = tr("lost_found.detail_copy_link", "Copiar enlace", "Copy link");
                        }, 1800);
                    }
                } catch (_) {
                    // Clipboard unavailable in insecure context; ignore gracefully
                }
            });
        }

        // Inline claim request form inside detail modal
        if (btnToggleClaimForm && detailClaimSection) {
            btnToggleClaimForm.addEventListener("click", () => {
                const isHidden = detailClaimSection.classList.contains("hidden");
                detailClaimSection.classList.toggle("hidden", !isHidden);
                if (isHidden && claimantNameInput) {
                    claimantNameInput.focus();
                }
            });
        }
        if (btnCancelClaimForm && detailClaimSection) {
            btnCancelClaimForm.addEventListener("click", () => {
                detailClaimSection.classList.add("hidden");
                if (detailClaimAlert) detailClaimAlert.classList.add("hidden");
            });
        }
        if (detailClaimForm) {
            detailClaimForm.addEventListener("submit", async (e) => {
                e.preventDefault();
                if (!activeDetailItemId) return;

                if (detailClaimAlert) detailClaimAlert.classList.add("hidden");
                if (btnSubmitClaimForm) {
                    btnSubmitClaimForm.disabled = true;
                    btnSubmitClaimForm.textContent = tr("lost_found.detail_claim_submitting", "Enviando...", "Submitting...");
                }

                const payload = {
                    claimantName: claimantNameInput ? claimantNameInput.value.trim() : "",
                    contact: claimantContactInput ? claimantContactInput.value.trim() : "",
                    secretDetailVerification: claimSecretInput ? claimSecretInput.value.trim() : "",
                };

                try {
                    const res = await global.fetch(`/api/lost-found-object/items/${encodeURIComponent(activeDetailItemId)}/claim`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(payload),
                    });
                    const data = await res.json();
                    if (res.ok && data && data.success) {
                        if (detailClaimAlert) {
                            detailClaimAlert.className = "rounded-xl p-3 text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200";
                            detailClaimAlert.textContent = data.message || tr(
                                "lost_found.detail_custody_in_custody",
                                "Solicitud registrada. Acude al Edificio A (CAE) con tu identificación.",
                                "Claim registered. Visit Building A (CAE) with your ID."
                            );
                            detailClaimAlert.classList.remove("hidden");
                        }
                        if (claimSecretInput) claimSecretInput.value = "";
                    } else if (detailClaimAlert) {
                        detailClaimAlert.className = "rounded-xl p-3 text-xs font-semibold bg-rose-50 text-rose-800 border border-rose-200";
                        detailClaimAlert.textContent = (data && data.error) || tr("auth.connection_error", "Error de conexión.", "Connection error.");
                        detailClaimAlert.classList.remove("hidden");
                    }
                } catch (_) {
                    if (detailClaimAlert) {
                        detailClaimAlert.className = "rounded-xl p-3 text-xs font-semibold bg-rose-50 text-rose-800 border border-rose-200";
                        detailClaimAlert.textContent = tr("auth.connection_error", "Error de conexión.", "Connection error.");
                        detailClaimAlert.classList.remove("hidden");
                    }
                } finally {
                    if (btnSubmitClaimForm) {
                        btnSubmitClaimForm.disabled = false;
                        btnSubmitClaimForm.textContent = tr("lost_found.detail_claim_submit", "Enviar solicitud de reclamo", "Submit claim request");
                    }
                }
            });
        }

        // Admin state modal wiring
        if (isAdmin) {
            const adminStateModal = doc.getElementById("adminStateModal");
            const btnCloseAdminState = doc.getElementById("btnCloseAdminStateModal");
            const btnCancelAdminState = doc.getElementById("btnCancelAdminState");
            const adminStateForm = doc.getElementById("adminStateForm");
            const adminStateAlert = doc.getElementById("adminStateAlert");

            global.openAdminStateModal = function (id, name, currentStateId) {
                if (!adminStateModal) return;
                const idEl = doc.getElementById("adminStateItemId");
                const titleEl = doc.getElementById("adminStateItemTitle");
                const selectEl = doc.getElementById("adminStateSelect");
                if (idEl) idEl.value = id;
                if (titleEl) titleEl.textContent = `#${id} - ${name}`;
                if (selectEl) selectEl.value = currentStateId || 1;
                if (adminStateAlert) adminStateAlert.classList.add("hidden");
                adminStateModal.classList.remove("hidden");
            };

            function closeAdminStateModal() {
                if (adminStateModal) adminStateModal.classList.add("hidden");
            }

            if (btnCloseAdminState) btnCloseAdminState.addEventListener("click", closeAdminStateModal);
            if (btnCancelAdminState) btnCancelAdminState.addEventListener("click", closeAdminStateModal);

            if (adminStateForm) {
                adminStateForm.addEventListener("submit", async (e) => {
                    e.preventDefault();
                    const itemId = doc.getElementById("adminStateItemId").value;
                    const stateId = parseInt(doc.getElementById("adminStateSelect").value, 10);

                    try {
                        const res = await global.fetch(`/api/admin/items/${encodeURIComponent(itemId)}/state`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ stateId }),
                        });
                        const data = await res.json();
                        if (data && data.success) {
                            if (adminStateAlert) {
                                adminStateAlert.className = "rounded-xl p-3 text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200";
                                adminStateAlert.textContent = data.message;
                                adminStateAlert.classList.remove("hidden");
                            }
                            setTimeout(async () => {
                                closeAdminStateModal();
                                await loadCatalog({ syncUrl: false });
                                if (activeDetailItemId && String(activeDetailItemId) === String(itemId)) {
                                    openItemDetailModal(activeDetailItemId, { syncUrl: false });
                                }
                            }, 600);
                        } else if (adminStateAlert) {
                            adminStateAlert.className = "rounded-xl p-3 text-xs font-semibold bg-rose-50 text-rose-800 border border-rose-200";
                            adminStateAlert.textContent = (data && data.error) || "Error al actualizar estado.";
                            adminStateAlert.classList.remove("hidden");
                        }
                    } catch (_) {
                        if (adminStateAlert) {
                            adminStateAlert.className = "rounded-xl p-3 text-xs font-semibold bg-rose-50 text-rose-800 border border-rose-200";
                            adminStateAlert.textContent = tr("auth.connection_error", "Error de conexión.", "Connection error.");
                            adminStateAlert.classList.remove("hidden");
                        }
                    }
                });
            }
        }

        // Global custom events & browser history navigation
        global.addEventListener("lostObjectReported", () => loadCatalog({ syncUrl: false }));
        global.addEventListener("jaguarLanguageChanged", () => {
            updateBuildingFilterBanner();
            if (allItems) renderCards(allItems);
            if (activeDetailItem && detailModal && !detailModal.classList.contains("hidden")) {
                renderItemDetail(activeDetailItem);
            }
        });

        global.addEventListener("popstate", () => {
            applyUrlParamsFromLocation({ triggerFetch: true, syncUrl: false });
        });

        function applyUrlParamsFromLocation(options) {
            const opts = options || {};
            const search = (global.location && global.location.search) || "";
            const params = new URLSearchParams(search);

            const buildingParam = (params.get("building") || params.get("location") || "").trim();
            const qParam = (params.get("q") || params.get("search") || "").trim();
            const catParam = (params.get("category") || "").trim();
            const stateParam = (params.get("stateId") || "").trim();
            const itemParam = parsePositiveInt(params.get("item"));
            const targetItemId = itemParam || (opts.useInitialRouteItem ? initialRouteItemId : null);

            setBuildingFilterValue(buildingParam);
            if (searchInput) searchInput.value = qParam;
            if (filterCategory) filterCategory.value = catParam;
            if (filterState) filterState.value = stateParam;

            updateBuildingFilterBanner();

            let loadPromise = Promise.resolve(allItems);
            if (opts.triggerFetch !== false) {
                loadPromise = loadCatalog({ syncUrl: Boolean(opts.syncUrl) });
            }

            if (targetItemId) {
                openItemDetailModal(targetItemId, { syncUrl: false });
            } else if (detailModal && !detailModal.classList.contains("hidden")) {
                closeItemDetailModal({ syncUrl: false });
            }

            return loadPromise;
        }

        function debounce(func, wait) {
            let timeout;
            return function (...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), wait);
            };
        }

        // Initial hydration from URL query parameters (?building=..., ?item=...) or /catalog/<id>
        applyUrlParamsFromLocation({ triggerFetch: true, syncUrl: false, useInitialRouteItem: true });

        const controllerApi = {
            loadCatalog,
            openItemDetailModal,
            closeItemDetailModal,
            applyBuildingFilter,
            clearBuildingFilter,
            clearAllFilters,
            getActiveBuilding: () => (filterBuilding ? filterBuilding.value : ""),
            getActiveItemId: () => activeDetailItemId,
            getItems: () => allItems,
        };

        global.JaguarCatalog = controllerApi;
        return controllerApi;
    }

    if (typeof global !== "undefined" && global.document) {
        if (global.document.readyState === "loading") {
            global.document.addEventListener("DOMContentLoaded", initCatalogScreen);
        } else {
            initCatalogScreen();
        }
    }

    if (typeof module !== "undefined" && module.exports) {
        module.exports = {
            initCatalogScreen,
            escapeHtml,
            parsePositiveInt,
            resolveBuildingLabel,
        };
    }
})(typeof window !== "undefined" ? window : globalThis);
