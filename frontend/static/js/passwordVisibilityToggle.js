(function () {
    "use strict";

    document.querySelectorAll("[data-password-toggle]").forEach((button) => {
        const input = document.getElementById(button.getAttribute("aria-controls"));
        if (!input) return;

        button.addEventListener("click", () => {
            const isVisible = input.type === "text";
            const shouldShow = !isVisible;
            const labelKey = shouldShow ? "auth.hide_password" : "auth.show_password";

            input.type = shouldShow ? "text" : "password";
            button.setAttribute("aria-pressed", String(shouldShow));
            button.setAttribute("data-i18n-aria-label", labelKey);
            if (typeof window.t === "function") {
                button.setAttribute("aria-label", window.t(labelKey));
            }
            button.querySelector("[data-password-eye]").classList.toggle("hidden", shouldShow);
            button.querySelector("[data-password-eye-off]").classList.toggle("hidden", !shouldShow);
        });
    });
})();
