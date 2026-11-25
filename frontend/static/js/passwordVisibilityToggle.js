(function () {
    "use strict";

    const labels = {
        "auth.show_password": {
            es: "Mostrar contraseña",
            en: "Show password"
        },
        "auth.hide_password": {
            es: "Ocultar contraseña",
            en: "Hide password"
        }
    };

    document.querySelectorAll("[data-password-toggle]").forEach((button) => {
        const input = document.getElementById(button.getAttribute("aria-controls"));
        if (!input) return;

        button.addEventListener("click", () => {
            const isVisible = input.type === "text";
            const shouldShow = !isVisible;
            const labelKey = shouldShow ? "auth.hide_password" : "auth.show_password";
            const label = labels[labelKey];
            const isSpanish = document.documentElement.lang === "spa";

            input.type = shouldShow ? "text" : "password";
            button.setAttribute("aria-pressed", String(shouldShow));
            button.setAttribute("data-i18n-aria-label", labelKey);
            button.setAttribute("aria-label", window.t
                ? window.t(labelKey, isSpanish ? label.es : label.en)
                : (isSpanish ? label.es : label.en));
            button.querySelector("[data-password-eye]").classList.toggle("hidden", shouldShow);
            button.querySelector("[data-password-eye-off]").classList.toggle("hidden", !shouldShow);
        });
    });
})();
