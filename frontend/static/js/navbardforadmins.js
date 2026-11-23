const sidebar = document.getElementById("sidebar");
const toggleBtn = document.getElementById("toggleBtn");

// Recuperar el estado guardado (si estaba cerrada, se queda cerrada)
if (localStorage.getItem("sidebarCollapsed") === "true") {
  sidebar.classList.add("collapsed");
}

toggleBtn.addEventListener("click", () => {
  sidebar.classList.toggle("collapsed");
  localStorage.setItem("sidebarCollapsed", sidebar.classList.contains("collapsed"));
});