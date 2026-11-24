/* Live figures for the joint sites, after Eido (weft-eido):
   - Every line is computed in the browser from an equation printed beside it.
   - Each visual channel carries exactly one named quantity (see captions).
   - With motion off, each canvas draws its settled state once.
   Figures: weft background threads, resonance cavity (two-wave figure),
   interference field of wave sources, and the style point (simplex pad). */
(function () {
  "use strict";
  var root = document.documentElement;
  var live = []; /* {draw(t), canvas} */
  var raf = 0, start = 0;

  function motionOn() { return root.getAttribute("data-motion") !== "off"; }
  function css(name) { return getComputedStyle(root).getPropertyValue(name).trim(); }
  function fit(canvas) {
    var r = canvas.getBoundingClientRect();
    var dpr = Math.min(2, window.devicePixelRatio || 1);
    var w = Math.max(320, Math.round(r.width)), h = Math.max(200, Math.round(r.height));
    if (canvas.width !== w * dpr || canvas.height !== h * dpr) { canvas.width = w * dpr; canvas.height = h * dpr; }
    var ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { ctx: ctx, w: w, h: h };
  }
  function loop(now) {
    if (!start) start = now;
    var t = (now - start) / 1000;
    live.forEach(function (f) { f.draw(t); });
    if (motionOn() && live.length) raf = requestAnimationFrame(loop);
  }
  function kick() {
    cancelAnimationFrame(raf); start = 0;
    if (motionOn() && live.length) raf = requestAnimationFrame(loop);
    else live.forEach(function (f) { f.draw(2.4); });
  }
  new MutationObserver(kick).observe(root, { attributes: true, attributeFilter: ["data-motion", "data-theme"] });
  window.addEventListener("resize", function () { live.forEach(function (f) { f.draw(2.4); }); });

  /* Weft background: y(x,t) = sum_n a_n sin(n pi x / W) cos(2 pi n f1 t + n phi_i).
     Channel map: thread height is wave height, colour crest/trough is sign,
     brightness is the style hue. Atmosphere only, no data. */
  function weft(canvas) {
    var threads = 14;
    return function (t) {
      var f = fit(canvas), ctx = f.ctx;
      ctx.clearRect(0, 0, f.w, f.h);
      var bio = css("--bio"), dig = css("--dig");
      for (var i = 0; i < threads; i++) {
        var y0 = (i + 0.5) * f.h / threads, phi = i * 0.7;
        ctx.beginPath();
        for (var x = 0; x <= f.w; x += 4) {
          var y = y0;
          for (var n = 1; n <= 3; n++) y += (7 / n) * Math.sin(n * Math.PI * x / f.w) * Math.cos(2 * Math.PI * n * 0.06 * t + n * phi);
          if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.strokeStyle = i % 2 ? dig : bio; ctx.globalAlpha = 0.35; ctx.lineWidth = 1; ctx.stroke(); ctx.globalAlpha = 1;
      }
    };
  }

  /* Resonance cavity: two waves in a ratio (Lissajous).
     x = sin(a t), y = sin(b t + d). A whole-number ratio b:a closes.
     Gold trace is openness (portal return), cyan is rigor (tomography);
     where they cross, the cavity resonates. Ratio is set by the slider. */
  function cavity(canvas, slider, out, numbers) {
    function ratio() { return slider ? parseFloat(slider.value) : 1.5; }
    return function (t) {
      var f = fit(canvas), ctx = f.ctx, cx = f.w / 2, cy = f.h / 2, R = Math.min(f.w, f.h) * 0.36;
      var b = ratio(), a = 1;
      ctx.clearRect(0, 0, f.w, f.h);
      ctx.strokeStyle = css("--line"); ctx.lineWidth = 1;
      ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(cx - R, cy); ctx.lineTo(cx + R, cy); ctx.moveTo(cx, cy - R); ctx.lineTo(cx, cy + R); ctx.stroke();
      var span = motionOn() ? Math.min(1, t / 6) : 1;
      function trace(color, phase, scale) {
        ctx.beginPath();
        var steps = 900, upto = Math.floor(steps * span);
        for (var i = 0; i <= upto; i++) {
          var s = i / steps * Math.PI * 2 * 4;
          var x = cx + Math.sin(a * s + phase) * R * scale, y = cy + Math.sin(b * s + Math.PI / 3 + phase) * R * scale;
          if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.strokeStyle = color; ctx.lineWidth = 1.6; ctx.stroke();
      }
      trace(css("--bio"), 0, 1);
      trace(css("--dig"), Math.PI / 2, 0.82);
      if (out) out.textContent = b.toFixed(3);
      if (numbers) numbers.textContent = "x = sin(t)  ·  y = sin(" + b.toFixed(3) + " t + pi/3)  ·  whole-number ratios close, others never repeat";
    };
  }

  /* Interference field: each place is a wave source.
     Amplitude is stated weight, frequency is family (shared = still fringes),
     reach is state. Value at a pixel is the sum of cos(k r - w t) / (1 + r/80).
     Drawn on a coarse grid for speed; links below the canvas carry the same choices. */
  function field(canvas, sources, numbers) {
    var img = null;
    return function (t) {
      var f = fit(canvas), ctx = f.ctx;
      var cell = 7, cols = Math.ceil(f.w / cell), rows = Math.ceil(f.h / cell);
      if (!img || img.width !== cols || img.height !== rows) img = ctx.createImageData(cols, rows);
      var dark = (root.getAttribute("data-theme") === "dark") || (!root.getAttribute("data-theme") && matchMedia("(prefers-color-scheme: dark)").matches);
      var pts = sources.map(function (s) { return { x: s.x * f.w, y: s.y * f.h, k: s.k, wgt: s.w }; });
      for (var gy = 0; gy < rows; gy++) for (var gx = 0; gx < cols; gx++) {
        var x = gx * cell, y = gy * cell, v = 0;
        for (var i = 0; i < pts.length; i++) {
          var dx = x - pts[i].x, dy = y - pts[i].y, r = Math.sqrt(dx * dx + dy * dy);
          v += pts[i].wgt * Math.cos(pts[i].k * r * 0.09 - t * 1.4) / (1 + r / 90);
        }
        var s01 = Math.max(0, Math.min(1, 0.5 + v * 0.45));
        var idx = (gy * cols + gx) * 4;
        if (dark) { img.data[idx] = 10 + s01 * 40; img.data[idx + 1] = 18 + s01 * 120; img.data[idx + 2] = 24 + s01 * 150; }
        else { img.data[idx] = 245 - s01 * 90; img.data[idx + 1] = 240 - s01 * 80; img.data[idx + 2] = 230 - s01 * 40; }
        img.data[idx + 3] = 255;
      }
      var tmp = document.createElement("canvas"); tmp.width = cols; tmp.height = rows;
      tmp.getContext("2d").putImageData(img, 0, 0);
      ctx.imageSmoothingEnabled = true; ctx.drawImage(tmp, 0, 0, f.w, f.h);
      ctx.fillStyle = css("--ink");
      pts.forEach(function (p) { ctx.beginPath(); ctx.arc(p.x, p.y, 4, 0, Math.PI * 2); ctx.fill(); });
      if (numbers) numbers.textContent = sources.length + " sources  ·  value = sum of w cos(k r - 1.4 t) / (1 + r/90)  ·  shared k = still fringes";
    };
  }

  /* Style point: barycentric weights over three presets.
     Linear values average linearly; hue averages on the circle,
     so two reds never blend into cyan (Eido aesthetic mixer). */
  var PRESETS = {
    open: { hue: 0.11, round: 10, label: "Open" },
    exact: { hue: 0.55, round: 2, label: "Exact" },
    field: { hue: 0.78, round: 5, label: "Field" }
  };
  function mixHue(weights) {
    var x = 0, y = 0;
    Object.keys(PRESETS).forEach(function (k) {
      var a = PRESETS[k].hue * Math.PI * 2;
      x += weights[k] * Math.cos(a); y += weights[k] * Math.sin(a);
    });
    var h = Math.atan2(y, x) / (Math.PI * 2);
    return h < 0 ? h + 1 : h;
  }
  function applyStyle(weights) {
    var round = 0;
    Object.keys(PRESETS).forEach(function (k) { round += weights[k] * PRESETS[k].round; });
    root.style.setProperty("--hue", mixHue(weights).toFixed(4));
    root.style.setProperty("--round", round.toFixed(1) + "px");
    try { localStorage.setItem("joint-style", JSON.stringify(weights)); } catch (e) {}
  }
  function stylePad(svg, readout) {
    var NS = "http://www.w3.org/2000/svg";
    var W = 280, H = 250, tri = [[140, 26], [34, 208], [246, 208]]; /* open, exact, field */
    var keys = ["open", "exact", "field"];
    var weights = { open: 1 / 3, exact: 1 / 3, field: 1 / 3 };
    try { var saved = JSON.parse(localStorage.getItem("joint-style") || "null"); if (saved) weights = saved; } catch (e) {}
    var poly = document.createElementNS(NS, "polygon");
    poly.setAttribute("points", tri.map(function (p) { return p.join(","); }).join(" "));
    poly.setAttribute("class", "tri"); svg.appendChild(poly);
    keys.forEach(function (k, i) {
      var tx = document.createElementNS(NS, "text");
      tx.setAttribute("x", tri[i][0]); tx.setAttribute("y", tri[i][1] + (i === 0 ? -10 : 20));
      tx.setAttribute("text-anchor", "middle"); tx.textContent = PRESETS[k].label; svg.appendChild(tx);
    });
    var pt = document.createElementNS(NS, "circle");
    pt.setAttribute("r", "9"); pt.setAttribute("class", "pt"); pt.setAttribute("tabindex", "0");
    pt.setAttribute("role", "slider"); pt.setAttribute("aria-label", "Style point. Arrow keys move it. Three weights always sum to one.");
    svg.appendChild(pt);
    function place() {
      var x = 0, y = 0;
      keys.forEach(function (k, i) { x += weights[k] * tri[i][0]; y += weights[k] * tri[i][1]; });
      pt.setAttribute("cx", x); pt.setAttribute("cy", y);
      applyStyle(weights);
      if (readout) readout.textContent = "open " + weights.open.toFixed(2) + "  ·  exact " + weights.exact.toFixed(2) + "  ·  field " + weights.field.toFixed(2) + "  ·  sum 1.00  ·  hue " + mixHue(weights).toFixed(3) + " turns";
      pt.setAttribute("aria-valuetext", readout ? readout.textContent : "");
    }
    function fromXY(mx, my) {
      var r = svg.getBoundingClientRect();
      var x = (mx - r.left) * W / r.width, y = (my - r.top) * H / r.height;
      var d = (tri[1][1] - tri[2][1]) * (tri[0][0] - tri[2][0]) + (tri[2][0] - tri[1][0]) * (tri[0][1] - tri[2][1]);
      var w0 = ((tri[1][1] - tri[2][1]) * (x - tri[2][0]) + (tri[2][0] - tri[1][0]) * (y - tri[2][1])) / d;
      var w1 = ((tri[2][1] - tri[0][1]) * (x - tri[2][0]) + (tri[0][0] - tri[2][0]) * (y - tri[2][1])) / d;
      var w2 = 1 - w0 - w1;
      var raw = [Math.max(0, w0), Math.max(0, w1), Math.max(0, w2)], s = raw[0] + raw[1] + raw[2] || 1;
      weights = { open: raw[0] / s, exact: raw[1] / s, field: raw[2] / s };
      place();
    }
    var dragging = false;
    svg.addEventListener("pointerdown", function (e) { dragging = true; svg.setPointerCapture(e.pointerId); fromXY(e.clientX, e.clientY); });
    svg.addEventListener("pointermove", function (e) { if (dragging) fromXY(e.clientX, e.clientY); });
    svg.addEventListener("pointerup", function () { dragging = false; });
    pt.addEventListener("keydown", function (e) {
      var step = 0.06, w = { open: weights.open, exact: weights.exact, field: weights.field };
      if (e.key === "ArrowUp") { w.open += step; w.exact -= step / 2; w.field -= step / 2; }
      else if (e.key === "ArrowLeft") { w.exact += step; w.open -= step / 2; w.field -= step / 2; }
      else if (e.key === "ArrowRight") { w.field += step; w.open -= step / 2; w.exact -= step / 2; }
      else if (e.key === "ArrowDown") { w.open -= step; w.exact += step / 2; w.field += step / 2; }
      else return;
      e.preventDefault();
      var raw = [Math.max(0, w.open), Math.max(0, w.exact), Math.max(0, w.field)], s = raw[0] + raw[1] + raw[2] || 1;
      weights = { open: raw[0] / s, exact: raw[1] / s, field: raw[2] / s }; place();
    });
    place();
  }

  function init() {
    var bg = document.getElementById("weft-bg");
    if (bg) live.push({ canvas: bg, draw: weft(bg) });
    var cav = document.getElementById("cavity");
    if (cav) {
      var slider = document.getElementById("ratio"), out = document.getElementById("ratio-out"), nums = document.getElementById("cavity-numbers");
      live.push({ canvas: cav, draw: cavity(cav, slider, out, nums) });
      if (slider) slider.addEventListener("input", function () { start = 0; live.forEach(function (f) { f.draw(2.4); }); });
      document.querySelectorAll("[data-ratio]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var p = btn.getAttribute("data-ratio").split("/").map(Number);
          if (slider) slider.value = String(p[0] / p[1]);
          start = 0; live.forEach(function (f) { f.draw(2.4); });
        });
      });
    }
    var fld = document.getElementById("field");
    if (fld && fld.dataset.sources) {
      try {
        var sources = JSON.parse(fld.dataset.sources);
        live.push({ canvas: fld, draw: field(fld, sources, document.getElementById("field-numbers")) });
      } catch (e) {}
    }
    var pad = document.getElementById("style-pad");
    if (pad) stylePad(pad, document.getElementById("style-readout"));
    else {
      try { var saved = JSON.parse(localStorage.getItem("joint-style") || "null"); if (saved) applyStyle(saved); } catch (e) {}
    }
    kick();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
