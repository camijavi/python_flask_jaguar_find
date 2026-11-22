
document.addEventListener("DOMContentLoaded", () => {

    const roleInput = document.getElementById("rol");

    if (!roleInput) return;

    const role = roleInput.value.trim().toLowerCase();

    console.log("Rol recibido:", role);

    document.querySelectorAll("[data-rol]").forEach((field) => {

        const allowedRoles = field.dataset.rol.split(" ");

        const isVisible = allowedRoles.includes(role);

        field.classList.toggle("visible", isVisible);

        field.querySelectorAll("input, select").forEach((input) => {

            input.required = isVisible;

        });

    });

});
