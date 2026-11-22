/* Theme, motion and reveal for the joint sites. No dependencies. */
(function () {
  "use strict";
  var root = document.documentElement;

  function themeBtn() { return document.querySelector("[data-theme-toggle]"); }
  function motionBtn() { return document.querySelector("[data-motion-toggle]"); }
  function isDark() {
    var t = root.getAttribute("data-theme");
    if (t) return t === "dark";
    return !!(window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches);
  }
  function syncLabels() {
    var tb = themeBtn(), mb = motionBtn();
    if (tb) {
      tb.setAttribute("aria-label", "Theme: " + (isDark() ? "dark" : "light") + ". Activate to switch.");
      var el = tb.querySelector(".t-txt"); if (el) el.textContent = isDark() ? "Dark" : "Light";
    }
    if (mb) {
      var on = root.getAttribute("data-motion") !== "off";
      mb.setAttribute("aria-pressed", on ? "true" : "false");
      mb.setAttribute("aria-label", "Motion: " + (on ? "on" : "off") + ". Activate to switch.");
      var mel = mb.querySelector(".t-txt"); if (mel) mel.textContent = on ? "Motion" : "Still";
    }
  }
  document.addEventListener("click", function (e) {
    var t = e.target.closest && e.target.closest("[data-theme-toggle]");
    if (t) {
      var next = isDark() ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("joint-theme", next); } catch (err) {}
      syncLabels();
      return;
    }
    var m = e.target.closest && e.target.closest("[data-motion-toggle]");
    if (m) {
      var cur = root.getAttribute("data-motion") !== "off";
      root.setAttribute("data-motion", cur ? "off" : "on");
      try { localStorage.setItem("joint-motion", cur ? "off" : "on"); } catch (err) {}
      syncLabels();
      if (!cur) revealAll();
    }
  });

  /* Reveal blocks as a slow wavefront reaches them: delay grows with
     distance from the top of the viewport, capped, so reading order wins. */
  var revealed = false;
  function revealAll() {
    document.querySelectorAll("[data-reveal]").forEach(function (el) { el.classList.add("in"); });
    revealed = true;
  }
  function initReveal() {
    var els = Array.prototype.slice.call(document.querySelectorAll("[data-reveal]"));
    if (!els.length) return;
    if (root.getAttribute("data-motion") === "off" || !("IntersectionObserver" in window)) { revealAll(); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var rect = en.target.getBoundingClientRect();
        var delay = Math.min(420, Math.max(0, rect.top * 0.35));
        setTimeout(function () { en.target.classList.add("in"); }, delay);
        io.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    els.forEach(function (el) { io.observe(el); });
    setTimeout(function () { if (!revealed) revealAll(); }, 4000);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function () { syncLabels(); initReveal(); });
  else { syncLabels(); initReveal(); }
})();
