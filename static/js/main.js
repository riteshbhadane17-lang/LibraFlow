// LibraFlow global JS: dark mode toggle, toast helper, loading overlay.
document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("darkModeToggle");
  const body = document.body;

  if (localStorage.getItem("libraflow-theme") === "dark") {
    body.classList.add("dark-mode");
  }

  if (toggle) {
    toggle.addEventListener("click", () => {
      body.classList.toggle("dark-mode");
      localStorage.setItem(
        "libraflow-theme",
        body.classList.contains("dark-mode") ? "dark" : "light"
      );
    });
  }

  // Auto-dismiss Bootstrap toasts
  document.querySelectorAll(".toast").forEach((el) => {
    new bootstrap.Toast(el, { delay: 4000 }).show();
  });

  // Simple form-submit loading spinner
  document.querySelectorAll("form[data-loading]").forEach((form) => {
    form.addEventListener("submit", () => {
      const btn = form.querySelector('button[type="submit"]');
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Please wait...';
      }
    });
  });
});

// Confirm before destructive actions (delete book/member)
function confirmDelete(message) {
  return confirm(message || "Are you sure? This action cannot be undone.");
}
