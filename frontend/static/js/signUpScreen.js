
/**
 * Visitor and Auth form validation rules and helpers.
 */

const VisitorValidation = {
    patterns: {
        cedula: /^\d{3}-\d{6}-\d{4}[A-Za-z]$/,
        cedulaRaw: /^\d{13}[A-Za-z]$/,
        phoneDigits: /^\d{8,15}$/,
        email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    },

    formatCedula(val) {
        if (!val) return "";
        const clean = val.replace(/[^0-9A-Za-z]/g, "").toUpperCase();
        if (clean.length === 14) {
            return `${clean.slice(0, 3)}-${clean.slice(3, 9)}-${clean.slice(9, 13)}${clean.slice(13)}`;
        }
        return val.trim().toUpperCase();
    },

    stripPhone(val) {
        if (!val) return "";
        return val.replace(/\D/g, "");
    },

    _t(key) {
        if (typeof window !== "undefined" && typeof window.t === "function") {
            return window.t(key);
        }
        return key;
    },

    validateFullName(val) {
        const trimmed = (val || "").trim();
        if (!trimmed) {
            return { valid: false, error: this._t("auth.validation.name_required") };
        }
        if (trimmed.length < 2) {
            return { valid: false, error: this._t("auth.validation.name_min") };
        }
        return { valid: true };
    },

    validateCedula(val) {
        const trimmed = (val || "").trim();
        if (trimmed.length < 14 || trimmed.length > 16) {
            return { valid: false, error: this._t("auth.validation.cedula_length") };
        }
        const formatted = this.formatCedula(trimmed);
        if (!formatted) {
            return { valid: false, error: this._t("auth.validation.cedula_required") };
        }
        if (!this.patterns.cedula.test(formatted)) {
            return { valid: false, error: this._t("auth.validation.cedula_invalid") };
        }
        return { valid: true, value: formatted };
    },

    validatePhone(val) {
        const digits = this.stripPhone(val);
        if (!digits) {
            return { valid: false, error: this._t("auth.validation.phone_required") };
        }
        if (!this.patterns.phoneDigits.test(digits)) {
            return { valid: false, error: this._t("auth.validation.phone_min") };
        }
        return { valid: true, value: digits };
    },

    validateEmail(val) {
        const trimmed = (val || "").trim();
        if (!trimmed) {
            return { valid: false, error: this._t("auth.validation.email_required") };
        }
        if (!this.patterns.email.test(trimmed)) {
            return { valid: false, error: this._t("auth.validation.email_invalid") };
        }
        return { valid: true, value: trimmed };
    }
};

if (typeof window !== "undefined") {
    window.VisitorValidation = VisitorValidation;
}

document.addEventListener("DOMContentLoaded", () => {
    const roleInput = document.getElementById("rol");
    if (!roleInput) return;

    const role = roleInput.value.trim().toLowerCase();

    document.querySelectorAll("[data-rol]").forEach((field) => {
        const allowedRoles = field.dataset.rol.split(" ");
        const isVisible = allowedRoles.includes(role);
        field.classList.toggle("visible", isVisible);
        field.querySelectorAll("input, select").forEach((input) => {
            input.required = isVisible;
        });
    });
});

