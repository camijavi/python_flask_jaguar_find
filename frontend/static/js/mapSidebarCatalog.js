/**
 * mapSidebarCatalog.js
 * ================================================================================
 * MAP SIDEBAR LOST & FOUND OBJECTS CATALOG CONTROLLER
 * ================================================================================
 * Powers the Lost & Found Objects Catalog tab inside the Campus Map sidebar:
 * - Fetches and filters lost & found items via /api/lost-found-object/items
 * - Renders responsive catalog cards optimized for mobile drawer & desktop sidebar
 * - Opens the shared responsive Item Detail Dialog (#itemDetailModal) when a card
 *   is selected, fetching authoritative details from /api/lost-found-object/items/<id>
 * - Supports inline claim request submission, shareable link copy, admin custody
 *   status editing, filtering by building, and focusing the item's building directly
 *   on the live 2D / 2.5D campus map
 * - Automatically updates on `lostObjectReported` and `jaguarLanguageChanged`
 * ================================================================================
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

    function sanitizePhotoUrl(rawUrl) {
        if (!rawUrl) return "";
        const trimmed = String(rawUrl).trim();
        if (
            trimmed.startsWith("/") ||
            /^https?:\/\//i.test(trimmed) ||
            /^data:image\/(png|jpe?g|gif|webp);base64,/i.test(trimmed)
        ) {
            return trimmed;
        }
        return "";
    }

    function tr(key, params) {
        if (typeof global.t === "function") {
            return global.t(key, undefined, params);
        }
        return key;
    }

    function parsePositiveInt(raw) {
        if (raw == null) return null;
        const clean = String(raw).trim();
        if (!/^\d+$/.test(clean)) return null;
        const parsed = parseInt(clean, 10);
        return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
    }

    function debounce(fn, waitMs) {
        let timer = null;
        return function (...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), waitMs);
        };
    }

    function initMapSidebarCatalog() {
        const doc = global.document;
        if (!doc) return null;

        const root = doc.getElementById("sidebarLostFoundComponent");
        const listEl = doc.getElementById("sidebarCatalogList");
        if (!root || !listEl) return null;

        const isAdmin = root.getAttribute("data-is-admin") === "true";
        const defaultUserName = (root.getAttribute("data-user-name") || "").trim();
        const defaultUserContact = (root.getAttribute("data-user-contact") || "").trim();

        // Sidebar panel controls
        const countBadge = doc.getElementById("sidebarCatalogCountBadge");
        const tabBadge = doc.getElementById("sidebarTabCatalogBadge");
        const searchInput = doc.getElementById("sidebarCatalogSearchInput");
        const btnClearSearch = doc.getElementById("btnSidebarClearSearch");
        const categorySelect = doc.getElementById("sidebarCatalogCategory");
        const stateSelect = doc.getElementById("sidebarCatalogState");
        const buildingSelect = doc.getElementById("sidebarCatalogBuilding");
        const btnRefresh = doc.getElementById("btnSidebarCatalogRefresh");
        const refreshIcon = doc.getElementById("sidebarCatalogRefreshIcon");
        const btnReport = doc.getElementById("btnSidebarReportObject");
        const btnCloseSidebar = doc.getElementById("btnCloseCatalogSidebar");
        const activeFilterBar = doc.getElementById("sidebarCatalogActiveFilterBar");
        const activeFilterLabel = doc.getElementById("sidebarCatalogActiveFilterLabel");
        const btnClearFilters = doc.getElementById("btnSidebarClearFilters");
        const btnClearFiltersEmpty = doc.getElementById("btnSidebarClearFiltersEmpty");
        const btnRetry = doc.getElementById("btnSidebarCatalogRetry");

        const loadingEl = doc.getElementById("sidebarCatalogLoading");
        const errorEl = doc.getElementById("sidebarCatalogError");
        const emptyEl = doc.getElementById("sidebarCatalogEmpty");

        // Shared Item Detail Dialog elements
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

        // Inline claim elements inside dialog
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
        let lastFocusedTrigger = null;
        let listRequestSeq = 0;
        let detailRequestSeq = 0;
        let copyTimer = null;
        let hasLoadedOnce = false;
        let lastFetchFailed = false;

        function resolveBuildingLabel(buildingId, fallbackName) {
            const cleanId = String(buildingId || "").trim();
            if (!cleanId) return fallbackName || "";

            if (typeof global.t === "function") {
                const translated = global.t(`nodes.${cleanId}`, "");
                if (translated && translated !== `nodes.${cleanId}`) {
                    return translated;
                }
            }

            if (buildingSelect && buildingSelect.options) {
                const match = Array.from(buildingSelect.options).find(
                    (opt) => opt.value && opt.value.toLowerCase() === cleanId.toLowerCase()
                );
                if (match && match.textContent) {
                    return match.textContent.trim();
                }
            }

            return fallbackName || cleanId;
        }

        function setBuildingFilterValue(rawBuildingId) {
            if (!buildingSelect) return "";
            const clean = String(rawBuildingId || "").trim();
            if (!clean) {
                buildingSelect.value = "";
                return "";
            }
            const opts = Array.from(buildingSelect.options || []);
            const exact = opts.find((opt) => opt.value === clean);
            if (exact) {
                buildingSelect.value = exact.value;
                return exact.value;
            }
            const ciMatch = opts.find((opt) => opt.value && opt.value.toLowerCase() === clean.toLowerCase());
            if (ciMatch) {
                buildingSelect.value = ciMatch.value;
                return ciMatch.value;
            }
            const dynOpt = doc.createElement("option");
            dynOpt.value = clean;
            dynOpt.textContent = resolveBuildingLabel(clean, clean);
            dynOpt.setAttribute("data-dynamic-building", "true");
            buildingSelect.appendChild(dynOpt);
            buildingSelect.value = clean;
            return clean;
        }

        function hasAnyActiveFilter() {
            const b = buildingSelect ? buildingSelect.value.trim() : "";
            const c = categorySelect ? categorySelect.value.trim() : "";
            const s = stateSelect ? stateSelect.value.trim() : "";
            const q = searchInput ? searchInput.value.trim() : "";
            return Boolean(b || c || s || q);
        }

        function updateFilterIndicators() {
            const q = searchInput ? searchInput.value.trim() : "";
            const b = buildingSelect ? buildingSelect.value.trim() : "";
            const c = categorySelect ? categorySelect.value.trim() : "";
            const s = stateSelect ? stateSelect.value.trim() : "";
            const anyActive = Boolean(q || b || c || s);

            if (btnClearSearch) {
                btnClearSearch.classList.toggle("hidden", !q);
            }
            if (btnClearFiltersEmpty) {
                btnClearFiltersEmpty.classList.toggle("hidden", !anyActive);
            }
            if (activeFilterBar && activeFilterLabel) {
                if (!anyActive) {
                    activeFilterBar.classList.add("hidden");
                    activeFilterLabel.textContent = "";
                } else {
                    const parts = [];
                    if (b) parts.push(resolveBuildingLabel(b, b));
                    if (c) parts.push(getCategoryMeta(c).label);
                    if (s) parts.push(getStateShortLabel(parseInt(s, 10)));
                    if (q) parts.push(`"${q}"`);
                    activeFilterLabel.textContent = parts.join(" · ");
                    activeFilterBar.classList.remove("hidden");
                }
            }
        }

        function getStateShortLabel(stateId, stateName) {
            if (stateId === 1) return tr("lost_found.state_reported");
            if (stateId === 2) return tr("lost_found.state_custody");
            if (stateId === 3) return tr("lost_found.state_claimed");
            return stateName || tr("lost_found.state_reported");
        }

        function getStateBadge(stateId, stateName, compact) {
            const padCls = compact ? "px-2 py-0.5 text-[10px]" : "px-2.5 py-1 text-[11px]";
            const label = escapeHtml(getStateShortLabel(stateId, stateName));
            if (stateId === 1) {
                return `<span class="inline-flex items-center gap-1 ${padCls} rounded-full font-bold bg-amber-50 text-amber-800 border border-amber-200 leading-tight max-w-full truncate">
                    <span class="w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0"></span><span class="truncate">${label}</span>
                </span>`;
            }
            if (stateId === 2) {
                return `<span class="inline-flex items-center gap-1 ${padCls} rounded-full font-bold bg-sky-50 text-sky-800 border border-sky-200 leading-tight max-w-full truncate">
                    <span class="w-1.5 h-1.5 rounded-full bg-brand-500 shrink-0"></span><span class="truncate">${label}</span>
                </span>`;
            }
            if (stateId === 3) {
                return `<span class="inline-flex items-center gap-1 ${padCls} rounded-full font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 leading-tight max-w-full truncate">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0"></span><span class="truncate">${label}</span>
                </span>`;
            }
            return `<span class="inline-flex items-center ${padCls} rounded-full font-bold bg-slate-100 text-slate-700 leading-tight">${label}</span>`;
        }

        function getCategoryMeta(cat) {
            const map = {
                electronics: {
                    label: tr("lost_found.cat_electronics"),
                    icon: '<svg class="w-3 h-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>',
                    thumbIcon: '<svg class="w-6 h-6 text-brand-600/80" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>',
                },
                documents: {
                    label: tr("lost_found.cat_documents"),
                    icon: '<svg class="w-3 h-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2"/></svg>',
                    thumbIcon: '<svg class="w-6 h-6 text-brand-600/80" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0"/></svg>',
                },
                personalItems: {
                    label: tr("lost_found.cat_personal"),
                    icon: '<svg class="w-3 h-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>',
                    thumbIcon: '<svg class="w-6 h-6 text-brand-600/80" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>',
                },
                clothing: {
                    label: tr("lost_found.cat_clothing"),
                    icon: '<svg class="w-3 h-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7l6-3 3 3 3-3 6 3v13H3V7z"/></svg>',
                    thumbIcon: '<svg class="w-6 h-6 text-brand-600/80" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 7l6-3 3 3 3-3 6 3v13H3V7z"/></svg>',
                },
                other: {
                    label: tr("lost_found.cat_other"),
                    icon: '<svg class="w-3 h-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>',
                    thumbIcon: '<svg class="w-6 h-6 text-brand-600/80" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>',
                },
            };
            return map[cat] || map.other;
        }

        function getCategoryBadge(cat) {
            const c = getCategoryMeta(cat);
            return `<span class="inline-flex items-center gap-1">${c.icon}<span class="truncate">${escapeHtml(c.label)}</span></span>`;
        }

        function updateCountBadges(count) {
            const key = count === 1 ? "lost_found.sidebar_items_short_singular" : "lost_found.sidebar_items_short_plural";
            if (countBadge) {
                countBadge.textContent = tr(key, { count });
            }
            if (tabBadge && !hasAnyActiveFilter()) {
                tabBadge.textContent = count > 99 ? "99+" : String(count);
                tabBadge.classList.toggle("hidden", count === 0);
            }
        }

        function highlightSelectedCard(itemId) {
            if (!listEl || typeof listEl.querySelectorAll !== "function") return;
            listEl.querySelectorAll("[data-open-sidebar-item]").forEach((card) => {
                const isSelected = itemId != null && String(card.getAttribute("data-open-sidebar-item")) === String(itemId);
                card.classList.toggle("ring-2", isSelected);
                card.classList.toggle("ring-brand-500", isSelected);
                card.classList.toggle("border-brand-400", isSelected);
                card.classList.toggle("bg-brand-50/30", isSelected);
            });
        }

        async function loadCatalog() {
            const reqSeq = ++listRequestSeq;
            updateFilterIndicators();

            if (loadingEl) loadingEl.classList.remove("hidden");
            if (errorEl) errorEl.classList.add("hidden");
            if (emptyEl) emptyEl.classList.add("hidden");
            listEl.classList.add("hidden");
            if (refreshIcon) refreshIcon.classList.add("animate-spin");

            const building = buildingSelect ? buildingSelect.value.trim() : "";
            const cat = categorySelect ? categorySelect.value.trim() : "";
            const state = stateSelect ? stateSelect.value.trim() : "";
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
                if (reqSeq !== listRequestSeq) return allItems;

                if (loadingEl) loadingEl.classList.add("hidden");
                if (refreshIcon) refreshIcon.classList.remove("animate-spin");

                if (res.ok && data && data.success && Array.isArray(data.items)) {
                    hasLoadedOnce = true;
                    lastFetchFailed = false;
                    allItems = data.items;
                    renderCards(allItems);
                } else {
                    lastFetchFailed = true;
                    allItems = [];
                    updateCountBadges(0);
                    if (errorEl) errorEl.classList.remove("hidden");
                }
            } catch (_) {
                if (reqSeq !== listRequestSeq) return allItems;
                lastFetchFailed = true;
                allItems = [];
                if (loadingEl) loadingEl.classList.add("hidden");
                if (refreshIcon) refreshIcon.classList.remove("animate-spin");
                updateCountBadges(0);
                if (errorEl) errorEl.classList.remove("hidden");
            }
            return allItems;
        }

        function renderCards(items) {
            updateCountBadges(items.length);
            updateFilterIndicators();
            listEl.innerHTML = "";

            if (items.length === 0) {
                listEl.classList.add("hidden");
                if (emptyEl) emptyEl.classList.remove("hidden");
                return;
            }

            if (emptyEl) emptyEl.classList.add("hidden");
            listEl.classList.remove("hidden");

            const viewDetailsLabel = escapeHtml(tr("lost_found.view_details"));
            const locateLabel = escapeHtml(tr("lost_found.sidebar_locate_on_map"));
            const antifraudLabel = escapeHtml(tr("lost_found.antifraud_badge"));

            items.forEach((item) => {
                const card = doc.createElement("article");
                card.className = "sidebar-catalog-card group bg-white rounded-2xl border border-slate-200/90 p-2.5 sm:p-3 shadow-2xs cursor-pointer transition-all focus:outline-hidden focus:ring-2 focus:ring-brand-500/40";
                card.setAttribute("role", "button");
                card.setAttribute("tabindex", "0");
                card.setAttribute("data-item-id", String(item.Id));
                card.setAttribute("data-open-sidebar-item", String(item.Id));

                const safeName = escapeHtml(item.ItemName);
                const safeDesc = escapeHtml(item.Description);
                const safeLocId = escapeHtml(item.Location);
                const safeLocLabel = escapeHtml(resolveBuildingLabel(item.Location, item.locationName || item.Location));
                const safeDate = escapeHtml(item.DateTimeReported ? String(item.DateTimeReported).split(" ")[0] : "");
                const safePhoto = sanitizePhotoUrl(item.PhotoUrl);
                const catMeta = getCategoryMeta(item.Category);

                card.setAttribute("aria-label", `${item.ItemName || ""} — ${resolveBuildingLabel(item.Location, item.locationName || item.Location)}`);

                const thumbHtml = safePhoto
                    ? `<div class="w-16 h-16 sm:w-[70px] sm:h-[70px] rounded-xl overflow-hidden shrink-0 border border-slate-200/80 bg-slate-100 relative">
                           <img src="${escapeHtml(safePhoto)}" alt="${safeName}" loading="lazy" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">
                       </div>`
                    : `<div class="w-16 h-16 sm:w-[70px] sm:h-[70px] rounded-xl shrink-0 border border-slate-200/80 bg-gradient-to-br from-brand-50 to-slate-100 flex items-center justify-center">
                           ${catMeta.thumbIcon}
                       </div>`;

                const secretBadgeHtml = item.hasSecretDetail
                    ? `<span title="${antifraudLabel}" class="inline-flex items-center justify-center w-5 h-5 rounded-full text-amber-700 bg-amber-50 border border-amber-200 shrink-0">
                           <svg class="w-2.5 h-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4"/></svg>
                       </span>`
                    : "";

                card.innerHTML = `
                    <div class="flex items-start gap-2.5 sm:gap-3">
                        ${thumbHtml}
                        <div class="min-w-0 flex-1">
                            <div class="flex items-center justify-between gap-1.5 mb-1">
                                <div class="min-w-0 flex-1">${getStateBadge(item.LostObjectStateId, item.StateName, true)}</div>
                                ${safeDate ? `<span class="text-[10px] text-slate-400 font-medium shrink-0">${safeDate}</span>` : ""}
                            </div>
                            <h4 class="font-extrabold text-xs sm:text-[13px] text-slate-900 group-hover:text-brand-700 leading-snug line-clamp-1 transition-colors">${safeName}</h4>
                            <div class="flex items-center gap-1 text-[11px] text-slate-500 font-medium mt-0.5 min-w-0">
                                <svg class="w-3 h-3 text-brand-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                                <span class="truncate">${safeLocLabel}</span>
                            </div>
                            <p class="text-[11px] text-slate-600 mt-1 line-clamp-2 leading-snug">${safeDesc}</p>
                        </div>
                    </div>
                    <div class="mt-2 pt-2 border-t border-slate-100 flex items-center justify-between gap-2">
                        <div class="flex items-center gap-1.5 min-w-0">
                            <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-600 max-w-[140px]">
                                ${getCategoryBadge(item.Category)}
                            </span>
                            ${secretBadgeHtml}
                        </div>
                        <div class="flex items-center gap-1.5 shrink-0">
                            <button type="button"
                                    data-locate-building="${safeLocId}"
                                    title="${locateLabel}"
                                    aria-label="${locateLabel}: ${safeLocLabel}"
                                    class="w-7 h-7 rounded-lg bg-slate-50 hover:bg-brand-50 border border-slate-200 hover:border-brand-300 text-slate-500 hover:text-brand-700 flex items-center justify-center transition-colors cursor-pointer">
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/></svg>
                            </button>
                            <span class="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-brand-50 group-hover:bg-brand-600 text-brand-700 group-hover:text-white border border-brand-200/80 group-hover:border-brand-600 text-[10.5px] font-extrabold transition-colors">
                                <span>${viewDetailsLabel}</span>
                                <svg class="w-3 h-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M9 5l7 7-7 7"/></svg>
                            </span>
                        </div>
                    </div>
                `;
                listEl.appendChild(card);
            });

            if (activeDetailItemId != null) {
                highlightSelectedCard(activeDetailItemId);
            }
        }

        // ------------------------------------------------------------------------
        // LIVE CAMPUS MAP FOCUS HELPER
        // ------------------------------------------------------------------------
        function focusLocationOnMap(locationId) {
            const cleanId = String(locationId || "").trim();
            if (!cleanId) return false;

            const pins =
                global.JaguarLostFoundMap && typeof global.JaguarLostFoundMap.getActivePins === "function"
                    ? global.JaguarLostFoundMap.getActivePins()
                    : [];
            const matchPin = Array.isArray(pins)
                ? pins.find((p) => p && p.locationNodeId && p.locationNodeId.toLowerCase() === cleanId.toLowerCase())
                : null;

            const bldgMap = global.CAMPUS_BUILDINGS || {};
            const exactBldgKey =
                bldgMap[cleanId]
                    ? cleanId
                    : Object.keys(bldgMap).find((k) => k.toLowerCase() === cleanId.toLowerCase());
            const bldgData = exactBldgKey ? bldgMap[exactBldgKey] : null;

            if (global.campus25dController && typeof global.campus25dController.focusBuilding === "function") {
                global.campus25dController.focusBuilding(exactBldgKey || cleanId, {
                    zoom: 2.85,
                    animate: true,
                    showPopover: !matchPin,
                });
                if (matchPin && global.JaguarLostFoundMap && typeof global.JaguarLostFoundMap.showPinPopover === "function") {
                    global.JaguarLostFoundMap.showPinPopover(matchPin);
                }
            } else if (matchPin && global.JaguarLostFoundMap && typeof global.JaguarLostFoundMap.showPinPopover === "function") {
                global.JaguarLostFoundMap.showPinPopover(matchPin);
            } else if (bldgData && typeof global.showBuildingPopover === "function") {
                global.showBuildingPopover(bldgData, bldgData.anchor);
            }

            // On mobile / tablet (< 1024px), dismiss the offcanvas sidebar drawer so the map focus is visible immediately
            if (global.innerWidth < 1024 && typeof global.toggleNavigateMapSidebar === "function") {
                global.toggleNavigateMapSidebar(false);
            }
            return true;
        }

        // ------------------------------------------------------------------------
        // ITEM DETAIL DIALOG CONTROLLER
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
                btnSubmitClaimForm.textContent = tr("lost_found.detail_claim_submit");
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

            if (detailStateBadge) detailStateBadge.innerHTML = getStateBadge(item.LostObjectStateId, item.StateName, false);
            if (detailCategoryBadge) detailCategoryBadge.innerHTML = getCategoryBadge(item.Category);

            if (detailPhoto && detailNoPhoto) {
                const safePhoto = sanitizePhotoUrl(item.PhotoUrl);
                if (safePhoto) {
                    detailPhoto.src = safePhoto;
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
                    detailCustodyText.textContent = tr("lost_found.detail_custody_in_custody");
                } else if (item.LostObjectStateId === 3) {
                    detailCustodyBox.className = "rounded-2xl p-3.5 text-xs font-semibold border bg-emerald-50 text-emerald-900 border-emerald-200 flex items-start gap-2.5";
                    detailCustodyText.textContent = tr("lost_found.detail_custody_claimed");
                } else {
                    detailCustodyBox.className = "rounded-2xl p-3.5 text-xs font-semibold border bg-amber-50 text-amber-900 border-amber-200 flex items-start gap-2.5";
                    detailCustodyText.textContent = tr("lost_found.detail_custody_reported");
                }
            }

            if (detailSecretBox && detailSecretText) {
                if (item.SecretDetail) {
                    detailSecretText.textContent = item.SecretDetail;
                    detailSecretBox.classList.remove("hidden");
                } else if (item.hasSecretDetail) {
                    detailSecretText.textContent = tr("lost_found.detail_secret_protected");
                    detailSecretBox.classList.remove("hidden");
                } else {
                    detailSecretBox.classList.add("hidden");
                }
            }

            if (btnDetailViewOnMap) {
                btnDetailViewOnMap.href = `/mapa?focus=${encodeURIComponent(item.Location || "")}&mode=25d`;
                btnDetailViewOnMap.setAttribute("data-focus-location", item.Location || "");
            }
            if (btnDetailMoreInBuilding) {
                btnDetailMoreInBuilding.setAttribute("data-building-id", item.Location || "");
            }
            if (btnToggleClaimForm) {
                const canClaim = item.LostObjectStateId !== 3;
                btnToggleClaimForm.classList.toggle("hidden", !canClaim);
            }
            if (detailCopyLabel) {
                detailCopyLabel.textContent = tr("lost_found.detail_copy_link");
            }
        }

        async function openItemDetailModal(itemId, triggerEl) {
            if (!detailModal) return false;
            const parsedId = parsePositiveInt(itemId);
            if (!parsedId) return false;

            const reqSeq = ++detailRequestSeq;
            activeDetailItemId = parsedId;
            lastFocusedTrigger = triggerEl || null;
            highlightSelectedCard(parsedId);
            resetClaimFormUi();
            detailModal.classList.remove("hidden");

            const cached = allItems.find((it) => Number(it.Id) === parsedId);
            if (cached) {
                renderItemDetail(cached);
            } else {
                if (detailContent) detailContent.classList.add("hidden");
                if (detailError) detailError.classList.add("hidden");
                if (detailLoading) detailLoading.classList.remove("hidden");
            }

            if (btnCloseDetail && typeof btnCloseDetail.focus === "function") {
                setTimeout(() => btnCloseDetail.focus(), 0);
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
            } catch (_) {
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

        function closeItemDetailModal() {
            if (!detailModal) return;
            detailModal.classList.add("hidden");
            activeDetailItem = null;
            activeDetailItemId = null;
            highlightSelectedCard(null);
            resetClaimFormUi();
            if (lastFocusedTrigger && typeof lastFocusedTrigger.focus === "function") {
                try {
                    lastFocusedTrigger.focus();
                } catch (_) {
                    // ignore if detached
                }
                lastFocusedTrigger = null;
            }
        }

        function applyBuildingFilter(buildingId) {
            setBuildingFilterValue(buildingId);
            if (typeof global.setSidebarActiveTab === "function") {
                global.setSidebarActiveTab("catalog");
            }
            return loadCatalog();
        }

        function clearAllFilters() {
            setBuildingFilterValue("");
            if (categorySelect) categorySelect.value = "";
            if (stateSelect) stateSelect.value = "";
            if (searchInput) searchInput.value = "";
            return loadCatalog();
        }

        // ------------------------------------------------------------------------
        // EVENT BINDINGS
        // ------------------------------------------------------------------------
        listEl.addEventListener("click", (e) => {
            const target = e.target;
            if (!target || typeof target.closest !== "function") return;

            const locateBtn = target.closest("[data-locate-building]");
            if (locateBtn) {
                e.preventDefault();
                e.stopPropagation();
                const locId = locateBtn.getAttribute("data-locate-building");
                if (locId) focusLocationOnMap(locId);
                return;
            }

            const card = target.closest("[data-open-sidebar-item]");
            if (card) {
                e.preventDefault();
                const id = parsePositiveInt(card.getAttribute("data-open-sidebar-item"));
                if (id) openItemDetailModal(id, card);
            }
        });

        listEl.addEventListener("keydown", (e) => {
            if (e.key !== "Enter" && e.key !== " ") return;
            const target = e.target;
            if (!target || typeof target.closest !== "function") return;
            if (target.closest("[data-locate-building]")) return;

            const card = target.closest("[data-open-sidebar-item]");
            if (card) {
                e.preventDefault();
                const id = parsePositiveInt(card.getAttribute("data-open-sidebar-item"));
                if (id) openItemDetailModal(id, card);
            }
        });

        if (searchInput) {
            searchInput.addEventListener("input", () => {
                if (btnClearSearch) btnClearSearch.classList.toggle("hidden", !searchInput.value.trim());
            });
            searchInput.addEventListener("input", debounce(() => loadCatalog(), 280));
        }
        if (btnClearSearch && searchInput) {
            btnClearSearch.addEventListener("click", () => {
                searchInput.value = "";
                btnClearSearch.classList.add("hidden");
                loadCatalog();
                searchInput.focus();
            });
        }
        if (categorySelect) categorySelect.addEventListener("change", () => loadCatalog());
        if (stateSelect) stateSelect.addEventListener("change", () => loadCatalog());
        if (buildingSelect) buildingSelect.addEventListener("change", () => loadCatalog());
        if (btnRefresh) btnRefresh.addEventListener("click", () => loadCatalog());
        if (btnRetry) btnRetry.addEventListener("click", () => loadCatalog());
        if (btnClearFilters) btnClearFilters.addEventListener("click", clearAllFilters);
        if (btnClearFiltersEmpty) btnClearFiltersEmpty.addEventListener("click", clearAllFilters);

        if (btnReport) {
            btnReport.addEventListener("click", () => {
                if (typeof global.openReportObjectDialog === "function") {
                    const currentBuilding = buildingSelect ? buildingSelect.value.trim() : "";
                    global.openReportObjectDialog(currentBuilding || undefined);
                }
            });
        }

        if (btnCloseSidebar) {
            btnCloseSidebar.addEventListener("click", () => {
                if (typeof global.toggleNavigateMapSidebar === "function") {
                    global.toggleNavigateMapSidebar(false);
                }
            });
        }

        // Dialog dismissal
        if (btnCloseDetail) btnCloseDetail.addEventListener("click", closeItemDetailModal);
        if (btnCloseDetailError) btnCloseDetailError.addEventListener("click", closeItemDetailModal);
        if (detailModal) {
            detailModal.addEventListener("click", (e) => {
                if (e.target === detailModal) {
                    closeItemDetailModal();
                }
            });
        }

        // Focus building directly on the live map from inside the dialog
        if (btnDetailViewOnMap) {
            btnDetailViewOnMap.addEventListener("click", (e) => {
                const targetLoc =
                    btnDetailViewOnMap.getAttribute("data-focus-location") ||
                    (activeDetailItem && activeDetailItem.Location);
                if (!targetLoc) return;
                e.preventDefault();
                closeItemDetailModal();
                focusLocationOnMap(targetLoc);
            });
        }

        function handleFilterFromDetail(btn) {
            const bId = (btn && btn.getAttribute("data-building-id")) || (activeDetailItem && activeDetailItem.Location);
            if (!bId) return;
            closeItemDetailModal();
            applyBuildingFilter(bId);
        }

        if (detailLocationBtn) {
            detailLocationBtn.addEventListener("click", () => handleFilterFromDetail(detailLocationBtn));
        }
        if (btnDetailMoreInBuilding) {
            btnDetailMoreInBuilding.addEventListener("click", () => handleFilterFromDetail(btnDetailMoreInBuilding));
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
                        detailCopyLabel.textContent = tr("lost_found.detail_link_copied");
                        clearTimeout(copyTimer);
                        copyTimer = setTimeout(() => {
                            detailCopyLabel.textContent = tr("lost_found.detail_copy_link");
                        }, 1800);
                    }
                } catch (_) {
                    // Clipboard unavailable; ignore gracefully
                }
            });
        }

        // Inline claim request form inside dialog
        if (btnToggleClaimForm && detailClaimSection) {
            btnToggleClaimForm.addEventListener("click", () => {
                const isHidden = detailClaimSection.classList.contains("hidden");
                detailClaimSection.classList.toggle("hidden", !isHidden);
                if (isHidden && claimantNameInput && typeof claimantNameInput.focus === "function") {
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
                    btnSubmitClaimForm.textContent = tr("lost_found.detail_claim_submitting");
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
                            detailClaimAlert.textContent = data.message || tr("lost_found.detail_custody_in_custody");
                            detailClaimAlert.classList.remove("hidden");
                        }
                        if (claimSecretInput) claimSecretInput.value = "";
                    } else if (detailClaimAlert) {
                        detailClaimAlert.className = "rounded-xl p-3 text-xs font-semibold bg-rose-50 text-rose-800 border border-rose-200";
                        detailClaimAlert.textContent = (data && data.error) || tr("auth.connection_error");
                        detailClaimAlert.classList.remove("hidden");
                    }
                } catch (_) {
                    if (detailClaimAlert) {
                        detailClaimAlert.className = "rounded-xl p-3 text-xs font-semibold bg-rose-50 text-rose-800 border border-rose-200";
                        detailClaimAlert.textContent = tr("auth.connection_error");
                        detailClaimAlert.classList.remove("hidden");
                    }
                } finally {
                    if (btnSubmitClaimForm) {
                        btnSubmitClaimForm.disabled = false;
                        btnSubmitClaimForm.textContent = tr("lost_found.detail_claim_submit");
                    }
                }
            });
        }

        // Admin custody state editor wiring (admins only)
        const adminStateModal = isAdmin ? doc.getElementById("adminStateModal") : null;
        if (isAdmin && adminStateModal) {
            const btnCloseAdminState = doc.getElementById("btnCloseAdminStateModal");
            const btnCancelAdminState = doc.getElementById("btnCancelAdminState");
            const adminStateForm = doc.getElementById("adminStateForm");
            const adminStateAlert = doc.getElementById("adminStateAlert");

            global.openAdminStateModal = function (id, name, currentStateId) {
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
                adminStateModal.classList.add("hidden");
            }

            if (btnCloseAdminState) btnCloseAdminState.addEventListener("click", closeAdminStateModal);
            if (btnCancelAdminState) btnCancelAdminState.addEventListener("click", closeAdminStateModal);
            adminStateModal.addEventListener("click", (e) => {
                if (e.target === adminStateModal) closeAdminStateModal();
            });

            if (btnDetailAdminEdit) {
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
                                await loadCatalog();
                                if (global.JaguarLostFoundMap && typeof global.JaguarLostFoundMap.refreshPins === "function") {
                                    global.JaguarLostFoundMap.refreshPins();
                                }
                                if (activeDetailItemId && String(activeDetailItemId) === String(itemId)) {
                                    openItemDetailModal(activeDetailItemId);
                                }
                            }, 550);
                        } else if (adminStateAlert) {
                            adminStateAlert.className = "rounded-xl p-3 text-xs font-semibold bg-rose-50 text-rose-800 border border-rose-200";
                            adminStateAlert.textContent = (data && data.error) || tr("lost_found.state_update_error");
                            adminStateAlert.classList.remove("hidden");
                        }
                    } catch (_) {
                        if (adminStateAlert) {
                            adminStateAlert.className = "rounded-xl p-3 text-xs font-semibold bg-rose-50 text-rose-800 border border-rose-200";
                            adminStateAlert.textContent = tr("auth.connection_error");
                            adminStateAlert.classList.remove("hidden");
                        }
                    }
                });
            }
        }

        // Escape key handling (closes top-most dialog cleanly without dismissing sidebar)
        doc.addEventListener("keydown", (e) => {
            if (e.key !== "Escape") return;
            if (adminStateModal && !adminStateModal.classList.contains("hidden")) {
                adminStateModal.classList.add("hidden");
                return;
            }
            if (detailModal && !detailModal.classList.contains("hidden")) {
                closeItemDetailModal();
            }
        });

        // Reactive synchronization with global events
        global.addEventListener("lostObjectReported", () => loadCatalog());
        global.addEventListener("jaguarSidebarTabChanged", (e) => {
            const tab = e && e.detail && e.detail.tab;
            if (tab === "catalog" && (!hasLoadedOnce || lastFetchFailed)) {
                loadCatalog();
            }
        });
        global.addEventListener("jaguarLanguageChanged", () => {
            if (buildingSelect && buildingSelect.options) {
                Array.from(buildingSelect.options).forEach((opt) => {
                    if (opt.getAttribute && opt.getAttribute("data-dynamic-building") === "true") {
                        opt.textContent = resolveBuildingLabel(opt.value, opt.value);
                    }
                });
            }
            if (hasLoadedOnce && !lastFetchFailed) {
                renderCards(allItems);
            } else {
                updateCountBadges(allItems.length);
                updateFilterIndicators();
            }
            if (activeDetailItem && detailModal && !detailModal.classList.contains("hidden")) {
                renderItemDetail(activeDetailItem);
            }
        });

        // Initial catalog load so count badge & cards are immediately ready
        loadCatalog();

        const controllerApi = {
            loadCatalog,
            openItemDetailModal,
            closeItemDetailModal,
            applyBuildingFilter,
            clearAllFilters,
            focusLocationOnMap,
            getItems: () => allItems,
            getActiveItemId: () => activeDetailItemId,
        };

        global.JaguarMapSidebarCatalog = controllerApi;
        return controllerApi;
    }

    if (typeof global !== "undefined" && global.document) {
        if (global.document.readyState === "loading") {
            global.document.addEventListener("DOMContentLoaded", initMapSidebarCatalog);
        } else {
            initMapSidebarCatalog();
        }
    }

    if (typeof module !== "undefined" && module.exports) {
        module.exports = {
            initMapSidebarCatalog,
            escapeHtml,
            sanitizePhotoUrl,
            parsePositiveInt,
        };
    }
})(typeof window !== "undefined" ? window : globalThis);
