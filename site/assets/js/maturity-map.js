/* maturity-map.js — the Maturity Assessment map at /maturity/.
 *
 * Built by scripts/maturity-site.py; the spec is maturity/documentation/output-spec-v2.md.
 * Everything shown comes from data/maturity.json; this file only draws it.
 * The address keeps the state: /maturity/#<indicator_id>|<ISO3>.
 */
(function () {
  "use strict";

  var ISLANDS = { CPV: [-28, 0], COM: [24, -6], MUS: [0, 22], SYC: [0, 22], STP: [-26, 6] };
  var NOT_ASSESSED = { ESH: true };
  var CLICK_DELAY = 0;

  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  };

  var data, geo, state = { indicator: null, country: null };
  var svg, gCountries, gIslands, path;

  Promise.all([
    fetch("data/maturity.json").then(function (r) { return r.json(); }),
    fetch("data/africa.json").then(function (r) { return r.json(); })
  ]).then(function (res) {
    data = res[0]; geo = res[1];
    readHash();
    buildControls();
    buildMap();
    buildLegend();
    window.addEventListener("resize", debounce(buildMap, 150));
    window.addEventListener("hashchange", function () { readHash(); syncControls(); render(); });
    render();
  }).catch(function (e) {
    $("mat-map").innerHTML = '<p class="mat-error">The map could not load its data.</p>';
    if (window.console) console.error(e);
  });

  /* ---------- state ---------- */

  function firstStudied() {
    for (var i = 0; i < data.topics.length; i++)
      for (var j = 0; j < data.topics[i].indicators.length; j++)
        if (data.topics[i].indicators[j].studied) return data.topics[i].indicators[j].id;
    return null;
  }

  function readHash() {
    var h = decodeURIComponent((location.hash || "").slice(1)).split("|");
    state.indicator = data.indicators[h[0]] ? h[0] : (state.indicator || firstStudied());
    state.country = h[1] && data.countries[h[1]] ? h[1] : (h[0] && data.indicators[h[0]] ? null : state.country);
  }

  function writeHash() {
    var h = "#" + state.indicator + (state.country ? "|" + state.country : "");
    if (location.hash !== h) history.replaceState(null, "", h);
  }

  function cell(iso) {
    var c = (data.cells[state.indicator] || {})[iso];
    return c || { stage: null, state: "no evidence", short: "", summary: "" };
  }

  function stageInfo(c) {
    return c.stage ? data.stages[c.stage - 1] : data.grey;
  }

  function stageText(c) {
    if (c.stage) { var s = data.stages[c.stage - 1]; return "Stage " + s.n + " · " + s.label; }
    return c.state === "unplaced" ? "Unplaced" : "No evidence";
  }

  /* ---------- controls ---------- */

  function topicOf(id) {
    for (var i = 0; i < data.topics.length; i++)
      for (var j = 0; j < data.topics[i].indicators.length; j++)
        if (data.topics[i].indicators[j].id === id) return data.topics[i];
    return data.topics[0];
  }

  function buildControls() {
    var ts = $("mat-topic");
    ts.innerHTML = data.topics.map(function (t, i) {
      return '<option value="' + i + '"' + (t.studied ? "" : " disabled") + ">" +
        esc(t.name) + (t.studied ? "" : " — not yet studied") + "</option>";
    }).join("");
    ts.addEventListener("change", function () {
      var t = data.topics[+ts.value];
      var first = t.indicators.filter(function (i) { return i.studied; })[0];
      if (first) { state.indicator = first.id; fillIndicators(t); render(); }
    });
    $("mat-indicator").addEventListener("change", function (e) {
      state.indicator = e.target.value; render();
    });
    syncControls();
  }

  function fillIndicators(t) {
    $("mat-indicator").innerHTML = t.indicators.map(function (i) {
      return '<option value="' + esc(i.id) + '"' + (i.studied ? "" : " disabled") +
        (i.id === state.indicator ? " selected" : "") + ">" + esc(i.label) +
        (i.studied ? "" : " — not yet studied") + "</option>";
    }).join("");
  }

  function syncControls() {
    var t = topicOf(state.indicator);
    $("mat-topic").value = String(data.topics.indexOf(t));
    fillIndicators(t);
  }

  /* ---------- map ---------- */

  function buildMap() {
    var box = $("mat-map");
    var w = box.clientWidth, h = box.clientHeight;
    if (!w || !h) return;
    placeChanges();
    d3.select(box).select("svg").remove();
    svg = d3.select(box).insert("svg", ":first-child")
      .attr("viewBox", "0 0 " + w + " " + h).attr("role", "img")
      .attr("aria-label", "Map of Africa coloured by maturity stage");
    var proj = d3.geoMercator().fitExtent([[8, 8], [w - 8, h - 8]], geo);
    path = d3.geoPath(proj);

    gCountries = svg.append("g");
    gCountries.selectAll("path").data(geo.features).enter().append("path")
      .attr("d", path)
      .attr("class", function (f) { return "mat-country" + (NOT_ASSESSED[f.properties.iso3] ? " is-off" : ""); })
      .each(function (f) { if (!NOT_ASSESSED[f.properties.iso3]) wire(d3.select(this), f.properties.iso3); });

    gIslands = svg.append("g");
    geo.features.forEach(function (f) {
      var iso = f.properties.iso3, off = ISLANDS[iso];
      if (!off) return;
      var c = path.centroid(f);
      var circ = gIslands.append("circle")
        .datum(f).attr("class", "mat-island")
        .attr("cx", Math.max(10, Math.min(w - 10, c[0] + off[0])))
        .attr("cy", Math.max(10, Math.min(h - 10, c[1] + off[1]))).attr("r", 8);
      wire(circ, iso);
    });
    paint();
  }

  function wire(sel, iso) {
    var timer = null;
    sel.attr("tabindex", 0).attr("data-iso", iso)
      .attr("aria-label", data.countries[iso] || iso)
      .on("mousemove", function (ev) { showTip(ev, iso); })
      .on("mouseleave", hideTip)
      .on("click", function () {
        clearTimeout(timer);
        timer = setTimeout(function () { select(iso); }, CLICK_DELAY);
      })
      .on("dblclick", function (ev) {
        ev.preventDefault(); clearTimeout(timer); openReport(iso);
      })
      .on("keydown", function (ev) {
        if (ev.key === "Enter") { ev.shiftKey ? openReport(iso) : select(iso); }
      })
      .on("focus", function () { var b = this.getBoundingClientRect(); showTip({ clientX: b.left + b.width / 2, clientY: b.top + b.height / 2 }, iso); })
      .on("blur", hideTip);
  }

  function paint() {
    if (!svg) return;
    var fill = function (f) {
      var iso = f.properties.iso3;
      return NOT_ASSESSED[iso] ? data.grey.color : stageInfo(cell(iso)).color;
    };
    gCountries.selectAll("path").attr("fill", fill)
      .classed("is-selected", function (f) { return f.properties.iso3 === state.country; });
    gIslands.selectAll("circle").attr("fill", fill)
      .classed("is-selected", function (f) { return f.properties.iso3 === state.country; });
    gCountries.selectAll("path.is-selected").raise();
  }

  /* The changes box sits in the Atlantic on a wide screen and under the sidebar on a narrow one. */
  function placeChanges() {
    var ch = $("mat-changes"), narrow = window.innerWidth <= 960;
    var home = narrow ? document.querySelector(".mat-side") : $("mat-map");
    if (ch.parentNode !== home) home.appendChild(ch);
  }

  function openReport(iso) {
    location.href = "countries/" + iso.toLowerCase() + "/#" + state.indicator;
  }

  function select(iso) {
    state.country = iso; render();
    if (window.innerWidth <= 960) $("mat-side-country").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  /* ---------- tooltip ---------- */

  function showTip(ev, iso) {
    var c = cell(iso), tip = $("mat-tooltip"), s = stageInfo(c);
    tip.innerHTML = '<div class="mat-tip__name">' + esc(data.countries[iso] || iso) + "</div>" +
      '<span class="mat-chip" style="background:' + s.color + ";color:" + s.ink + '">' + esc(stageText(c)) + "</span>" +
      '<p class="mat-tip__short">' + esc(c.short || "Nothing held.") + "</p>" +
      '<p class="mat-tip__cta">Click for detail · double-click for the report</p>';
    tip.hidden = false;
    var pad = 14, tw = tip.offsetWidth, th = tip.offsetHeight;
    var x = ev.clientX + pad, y = ev.clientY + pad;
    if (x + tw > window.innerWidth - 8) x = ev.clientX - tw - pad;
    if (y + th > window.innerHeight - 8) y = ev.clientY - th - pad;
    tip.style.left = Math.max(8, x) + "px";
    tip.style.top = Math.max(8, y) + "px";
  }

  function hideTip() { $("mat-tooltip").hidden = true; }

  /* ---------- legend, sidebar, changes ---------- */

  function buildLegend() {
    var items = data.stages.map(function (s) {
      return '<li><span class="mat-sw" style="background:' + s.color + '"></span><b>' + s.n + " " + esc(s.label) +
        "</b> " + esc(s.desc) + "</li>";
    });
    items.push('<li><span class="mat-sw" style="background:' + data.grey.color + '"></span><b>' +
      esc(data.grey.label) + "</b> " + esc(data.grey.desc) + "</li>");
    $("mat-legend").innerHTML = "<ul>" + items.join("") + "</ul>";
  }

  function renderIndicator() {
    var ind = data.indicators[state.indicator];
    var lad = ind.ladder.map(function (l) {
      var s = l.n ? data.stages[l.n - 1] : data.grey;
      return '<li><span class="mat-sw" style="background:' + s.color + '"></span><b>' +
        (l.n ? l.n + " " + esc(s.label) : "") + "</b> " + esc(l.text) + "</li>";
    }).join("");
    $("mat-side-indicator").innerHTML =
      '<p class="mat-side__kicker">' + esc(ind.topic) + "</p>" +
      "<h2>" + esc(ind.label) + "</h2>" +
      '<ul class="mat-ladder">' + lad + "</ul>" +
      '<a class="mat-btn" href="../methodology/maturity/#' + esc(state.indicator) + '">Methodology for this indicator</a>';
    $("mat-method").href = "../methodology/maturity/#" + state.indicator;
  }

  function renderCountry() {
    var box = $("mat-side-country"), iso = state.country;
    if (!iso) { box.innerHTML = '<p class="mat-side__empty">Select a country.</p>'; return; }
    var c = cell(iso), s = stageInfo(c);
    var moved = c.reassessed ? "Reassessed " + c.reassessed : (c.moved || "First assessment");
    box.innerHTML =
      "<h2>" + esc(data.countries[iso] || iso) + "</h2>" +
      '<p class="mat-side__meta"><span class="mat-chip" style="background:' + s.color + ";color:" + s.ink + '">' +
      esc(stageText(c)) + "</span>" +
      "<span><b>Last assessed</b> " + esc(c.assessed || "—") + "</span>" +
      "<span><b>Stage last moved</b> " + esc(moved) + "</span></p>" +
      '<p class="mat-side__short">' + esc(c.short || "Nothing held.") + "</p>" +
      '<div class="mat-side__long">' + (c.summary || "") + "</div>" +
      '<a class="mat-btn mat-btn--primary" href="countries/' + iso.toLowerCase() + "/#" + esc(state.indicator) +
      '">View in country report</a>';
    box.scrollTop = 0;
  }

  function renderChanges() {
    var list = data.changes[state.indicator] || [];
    var body = list.length ? "<ul>" + list.map(function (ch) {
      return "<li><b>" + esc(data.countries[ch.iso3] || ch.iso3) + "</b> stage " + ch.from + " → " + ch.to +
        " <span>(" + esc(ch.month) + ")</span></li>";
    }).join("") + "</ul>" : "<p>No stage changes in the past six months.</p>";
    $("mat-changes").innerHTML = "<h3>Changes in the past six months</h3>" + body;
  }

  function render() {
    writeHash();
    renderIndicator();
    renderCountry();
    renderChanges();
    paint();
  }

  function debounce(fn, ms) {
    var t; return function () { clearTimeout(t); t = setTimeout(fn, ms); };
  }
})();
