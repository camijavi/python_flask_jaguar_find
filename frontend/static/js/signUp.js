document.addEventListener("DOMContentLoaded", () => {
    const roleInput = document.getElementById("role");
    if (!roleInput) return;

    const role = roleInput.value;

    document.querySelectorAll("[data-role]").forEach((field) => {
        const allowedRoles = field.dataset.role.split(" ");
        const isVisible = allowedRoles.includes(role);

        field.style.display = isVisible ? "" : "none";

        field.querySelectorAll("input, select").forEach((input) => {
            input.required = isVisible;
        });
    });
});
