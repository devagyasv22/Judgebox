(function () {
  "use strict";

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    try {
      localStorage.setItem("oj-theme", theme);
    } catch (e) {}
  }

  function initTheme() {
    let t = "dark";
    try {
      t = localStorage.getItem("oj-theme") || "dark";
    } catch (e) {}
    applyTheme(t === "light" ? "light" : "dark");
    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const cur = document.documentElement.getAttribute("data-theme") || "dark";
        applyTheme(cur === "dark" ? "light" : "dark");
      });
    });
  }

  document.addEventListener("DOMContentLoaded", initTheme);

  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      const submitBtn = document.querySelector("[data-submit-code]");
      if (submitBtn) {
        e.preventDefault();
        submitBtn.click();
      }
    }
  });
})();
