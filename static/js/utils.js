(function () {
  "use strict";

  window.OJ = window.OJ || {};

  OJ.getCookie = function (name) {
    const v = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
    return v ? v.pop() : "";
  };

  OJ.toast = function (message, variant) {
    const el = document.createElement("div");
    el.className = "alert alert-" + (variant || "info") + " shadow oj-toast-item";
    el.setAttribute("role", "status");
    el.textContent = message;
    let c = document.querySelector(".oj-toast-container");
    if (!c) {
      c = document.createElement("div");
      c.className = "oj-toast-container";
      document.body.appendChild(c);
    }
    c.appendChild(el);
    setTimeout(function () {
      el.classList.add("opacity-0");
      setTimeout(function () {
        el.remove();
      }, 300);
    }, 3200);
  };

  OJ.copyText = async function (text) {
    try {
      await navigator.clipboard.writeText(text);
      OJ.toast("Copied to clipboard", "success");
    } catch (e) {
      OJ.toast("Copy failed", "danger");
    }
  };

  OJ.debounce = function (fn, ms) {
    let t;
    return function () {
      const args = arguments;
      clearTimeout(t);
      t = setTimeout(function () {
        fn.apply(null, args);
      }, ms);
    };
  };
})();
