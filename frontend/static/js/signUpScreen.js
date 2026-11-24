
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

    validateFullName(val, isEs = true) {
        const trimmed = (val || "").trim();
        if (!trimmed) {
            return { valid: false, error: isEs ? "El nombre completo es obligatorio." : "Full name is required." };
        }
        if (trimmed.length < 2) {
            return { valid: false, error: isEs ? "El nombre debe tener al menos 2 caracteres." : "Full name must be at least 2 characters." };
        }
        return { valid: true };
    },

    validateCedula(val, isEs = true) {
        const formatted = this.formatCedula(val);
        if (!formatted) {
            return { valid: false, error: isEs ? "La cédula de identidad es obligatoria." : "National ID is required." };
        }
        if (!this.patterns.cedula.test(formatted)) {
            return { valid: false, error: isEs ? "Formato de cédula inválido. Debe ser: 001-000000-0000A." : "Invalid National ID format. Expected format: 001-000000-0000A." };
        }
        return { valid: true, value: formatted };
    },

    validatePhone(val, isEs = true) {
        const digits = this.stripPhone(val);
        if (!digits) {
            return { valid: false, error: isEs ? "El número de teléfono es obligatorio." : "Phone number is required." };
        }
        if (!this.patterns.phoneDigits.test(digits)) {
            return { valid: false, error: isEs ? "El teléfono debe contener solo dígitos (mínimo 8 dígitos)." : "Phone number must contain digits only (minimum 8 digits)." };
        }
        return { valid: true, value: digits };
    },

    validateEmail(val, isEs = true) {
        const trimmed = (val || "").trim();
        if (!trimmed) {
            return { valid: false, error: isEs ? "El correo electrónico es obligatorio." : "Email is required." };
        }
        if (!this.patterns.email.test(trimmed)) {
            return { valid: false, error: isEs ? "Ingresa un correo electrónico válido (ej. usuario@dominio.com)." : "Enter a valid email address (e.g. user@domain.com)." };
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

