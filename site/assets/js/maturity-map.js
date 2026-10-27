/* maturity-map.js — the Maturity Assessment map at /maturity/.
 *
 * Built by scripts/maturity-site.py; the spec is maturity/documentation/output-spec-v2.md.
 * Everything shown comes from data/maturity.json; this file only draws it.
 * The address keeps the state: /maturity/#<indicator_id>|<ISO3>.
 */
(function () {
  "use strict";

  /* Island states: where the circle sits [lon, lat], and its nudge off the coast in px. */
  var ISLANDS = { CPV: [[-23.6, 15.9], [-14, 0]], COM: [[43.5, -11.8], [22, -4]], MUS: [[57.55, -20.25], [0, 16]],
                  SYC: [[55.45, -4.65], [0, 16]], STP: [[6.6, 0.3], [-22, 6]] };
  /* The frame the map is fitted to: the continent and its islands, not Prince Edward or Rodrigues. */
  var FRAME = { type: "MultiPoint", coordinates: [[-25.5, 37.6], [58.5, 37.6], [-25.5, -35.2], [58.5, -35.2]] };
  /* The most of the row the map may take on a wide screen; the sidebar has the rest. */
  var MAP_SHARE = 0.44;
  var NOT_ASSESSED = { ESH: true };
  var CLICK_DELAY = 0;

  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  };

  var data, geo, state = { indicator: null, country: null };
  var svg, gCountries, gIslands, path, pressed = 0;

  Promise.all([
    fetch("data/maturity.json").then(function (r) { return r.json(); }),
    fetch("data/africa.json").then(function (r) { return r.json(); })
  ]).then(function (res) {
    data = res[0]; geo = res[1];
    readHash();
    buildControls();
    buildLegend();
    buildMap();
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
    /* A bookmark from before 2026-10-19 carries a description after the id: keep the id. */
    if (h[0] && !data.indicators[h[0]])
      for (var id in data.indicators) if (h[0].indexOf(id + "-") === 0) { h[0] = id; break; }
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
    return c.stage ? data.stages[c.stage - 1] : c.state === "unplaced" ? data.grey : data.blank;
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

  /* Chapter limits Topic, and Topic limits Indicator. What is not yet studied is greyed out and
     cannot be chosen; the grey says so, and no option carries words for it. */
  function buildControls() {
    var cs = $("mat-chapter"), ts = $("mat-topic"), chapters = [];
    data.topics.forEach(function (t) { if (chapters.indexOf(t.group) < 0) chapters.push(t.group); });
    cs.innerHTML = chapters.map(function (c) {
      var studied = data.topics.some(function (t) { return t.group === c && t.studied; });
      return '<option value="' + esc(c) + '"' + (studied ? "" : " disabled") + ">" + esc(c) + "</option>";
    }).join("");
    var openTopic = function (t) {
      var first = t && t.indicators.filter(function (i) { return i.studied; })[0];
      if (first) { state.indicator = first.id; syncControls(); render(); }
    };
    cs.addEventListener("change", function () {
      openTopic(data.topics.filter(function (t) { return t.group === cs.value && t.studied; })[0]);
    });
    ts.addEventListener("change", function () { openTopic(data.topics[+ts.value]); });
    $("mat-indicator").addEventListener("change", function (e) {
      state.indicator = e.target.value; render();
    });
    syncControls();
  }

  function fillIndicators(t) {
    $("mat-indicator").innerHTML = t.indicators.map(function (i) {
      return '<option value="' + esc(i.id) + '"' + (i.studied ? "" : " disabled") +
        (i.id === state.indicator ? " selected" : "") + ">" + esc(i.label) + "</option>";
    }).join("");
  }

  function syncControls() {
    var t = topicOf(state.indicator);
    $("mat-chapter").value = t.group;
    $("mat-topic").innerHTML = data.topics.map(function (o, i) {
      return o.group !== t.group ? "" : '<option value="' + i + '"' + (o.studied ? "" : " disabled") + ">" +
        esc(o.name) + "</option>";
    }).join("");
    $("mat-topic").value = String(data.topics.indexOf(t));
    fillIndicators(t);
  }

  /* ---------- map ---------- */

  function buildMap() {
    var box = $("mat-map"), body = document.querySelector(".mat-body");
    var narrow = window.innerWidth <= 960;
    placeChanges();
    /* The map column is as wide as the map and no wider, so the islands sit at its edges and the
       sidebar takes the rest (Bill, 2026-10-13): the width comes from the height the screen
       leaves, capped at MAP_SHARE of the row. A phone gives the map the full width. */
    var top = box.getBoundingClientRect().top + window.scrollY;
    var ref = d3.geoPath(d3.geoMercator().fitWidth(1000, FRAME)).bounds(FRAME);
    var ratio = (ref[1][1] - ref[0][1]) / 1000;
    var w, rowH = 0;
    if (narrow) body.style.gridTemplateColumns = "";
    else {
      /* The row ends where the footer starts, so the page does not scroll: the sidebar has that
         whole height, and the map what the legend leaves of it. Twice, because the legend
         rewraps when the column's width moves. */
      var foot = document.querySelector(".site-footer"), legend = $("mat-legend");
      var pad = parseFloat(getComputedStyle(document.querySelector(".mat-wrap")).paddingBottom) || 0;
      rowH = Math.max(380, window.innerHeight - top - pad - (foot ? foot.offsetHeight : 0));
      for (var pass = 0; pass < 2; pass++) {
        var maxH = Math.max(320, rowH - (legend.getBoundingClientRect().bottom - box.getBoundingClientRect().bottom));
        w = Math.round(Math.min(body.clientWidth * MAP_SHARE, (maxH - 16) / ratio + 16));
        body.style.gridTemplateColumns = w + "px minmax(0, 1fr)";
      }
    }
    w = box.clientWidth;
    if (!w) return;
    /* The box takes the map's own height, so there is no blank band under the continent. */
    var proj = d3.geoMercator().fitWidth(w - 16, FRAME);
    var b = d3.geoPath(proj).bounds(FRAME), h = Math.ceil(b[1][1] - b[0][1]) + 16;
    proj.translate([proj.translate()[0] + 8, proj.translate()[1] + 8]);
    box.style.height = h + "px";
    d3.select(box).select("svg").remove();
    svg = d3.select(box).insert("svg", ":first-child")
      .attr("viewBox", "0 0 " + w + " " + h).attr("role", "img")
      .attr("aria-label", "Map of Africa coloured by maturity stage");
    path = d3.geoPath(proj);

    gCountries = svg.append("g");
    gCountries.selectAll("path").data(geo.features).enter().append("path")
      .attr("d", path)
      .attr("class", function (f) { return "mat-country" + (NOT_ASSESSED[f.properties.iso3] ? " is-off" : ""); })
      .each(function (f) { if (!NOT_ASSESSED[f.properties.iso3]) wire(d3.select(this), f.properties.iso3); });

    gIslands = svg.append("g");
    geo.features.forEach(function (f) {
      var iso = f.properties.iso3, isl = ISLANDS[iso];
      if (!isl) return;
      var c = proj(isl[0]), off = isl[1];
      var circ = gIslands.append("circle")
        .datum(f).attr("class", "mat-island")
        .attr("cx", Math.max(10, Math.min(w - 10, c[0] + off[0])))
        .attr("cy", Math.max(10, Math.min(h - 10, c[1] + off[1]))).attr("r", 8);
      wire(circ, iso);
    });
    var side = document.querySelector(".mat-side");
    side.style.height = narrow ? "" : Math.max(rowH, document.querySelector(".mat-mapcol").offsetHeight) + "px";
    paint();
  }

  function wire(sel, iso) {
    var timer = null;
    sel.attr("tabindex", 0).attr("data-iso", iso)
      .attr("aria-label", data.countries[iso] || iso)
      /* The tooltip is the mouse's and the keyboard's. A tap moves a pointer and takes focus too,
         and would show it over the country's details (spec section 5 gives a phone no tooltip);
         so a move counts only from a mouse, and a focus only when no pointer has just pressed. */
      .on("pointermove", function (ev) { if (ev.pointerType === "mouse") showTip(ev, iso); })
      .on("pointerleave", hideTip)
      .on("pointerdown", function () { pressed = Date.now(); })
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
      .on("focus", function () { if (Date.now() - pressed < 1000) return; var b = this.getBoundingClientRect(); showTip({ clientX: b.left + b.width / 2, clientY: b.top + b.height / 2 }, iso); })
      .on("blur", hideTip);
  }

  function paint() {
    if (!svg) return;
    var fill = function (f) {
      var iso = f.properties.iso3;
      return NOT_ASSESSED[iso] ? data.grey.color : stageInfo(cell(iso)).color;
    };
    /* No evidence is unfilled, so it needs a border the white outline does not give it. */
    var blank = function (f) {
      var iso = f.properties.iso3;
      return !NOT_ASSESSED[iso] && stageInfo(cell(iso)) === data.blank;
    };
    gCountries.selectAll("path").attr("fill", fill).classed("is-blank", blank)
      .classed("is-selected", function (f) { return f.properties.iso3 === state.country; });
    gIslands.selectAll("circle").attr("fill", fill)
      .classed("is-selected", function (f) { return f.properties.iso3 === state.country; });
    gCountries.selectAll("path.is-selected").raise();
  }

  /* The changes box sits in the South Atlantic on a wide screen and under the sidebar on a narrow one. */
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
      '<span class="mat-chip' + (s === data.blank ? " mat-chip--blank" : "") + '" style="background:' + s.color + ";color:" + s.ink + '">' + esc(stageText(c)) + "</span>" +
      '<p class="mat-tip__short">' + esc(c.short || "Nothing found.") + "</p>" +
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
      return '<li title="' + esc(s.desc) + '"><span class="mat-sw" style="background:' + s.color + '"></span>' +
        s.n + " " + esc(s.label) + "</li>";
    });
    [data.grey, data.blank].forEach(function (g) {
      items.push('<li title="' + esc(g.desc) + '"><span class="mat-sw" style="background:' + g.color +
        '"></span>' + esc(g.label) + "</li>");
    });
    $("mat-legend").innerHTML = "<ul>" + items.join("") + "</ul>";
  }

  function renderIndicator() {
    var ind = data.indicators[state.indicator];
    var lad = ind.ladder.map(function (l) {
      var s = l.n ? data.stages[l.n - 1] : data.grey;
      return '<li><span class="mat-sw" style="background:' + s.color + '"></span><b>' +
        (l.n ? l.n + " " + esc(s.label) : "") + "</b><span>" + esc(l.text) + "</span></li>";
    }).join("");
    $("mat-side-indicator").innerHTML =
      /* The dropdowns already name the indicator, so the box says only what it holds. */
      '<div class="mat-side__head"><div class="mat-side__row"><h2 class="mat-side__kicker">Criteria</h2>' +
      '<a class="mat-btn mat-btn--primary" href="../methodology/maturity/#' + esc(state.indicator) +
      '">Methodology for this indicator</a></div>' +
      /* The norm, cut to three lines by the stylesheet; the whole of it is on the methodology page. */
      (ind.norm ? '<div class="mat-norm">' + ind.norm + "</div>" : "") + "</div>" +
      '<ul class="mat-ladder">' + lad + "</ul>";
    var norm = document.querySelector("#mat-side-indicator .mat-norm");
    if (norm) norm.title = norm.textContent;
    $("mat-method").href = "../methodology/maturity/#" + state.indicator;
    /* After launch the button is a link to the selected indicator's dated edition. */
    var file = data.launched && data.downloads[state.indicator], one = $("mat-dl-one");
    if (data.launched) { one.hidden = !file; if (file) one.href = file; }
  }

  function renderCountry() {
    var box = $("mat-side-country"), iso = state.country;
    box.classList.toggle("is-empty", !iso);
    if (!iso) { box.innerHTML = '<p class="mat-side__empty">Select a country.</p>'; return; }
    var c = cell(iso), s = stageInfo(c);
    var moved = c.reassessed ? "Reassessed " + c.reassessed : (c.moved || "First assessment");
    /* The status report opens at the indicator's topic where it holds that topic, else at its top. */
    var held = data.status && data.status[iso], ind = data.indicators[state.indicator] || {};
    var at = held && [ind.anchor, ind.chapter].filter(function (a) { return a && held.indexOf(a) >= 0; })[0];
    var statusLink = held ? '<a class="mat-btn mat-btn--primary" href="../reports/' + iso + "/" + iso + "-status.html" +
      (at ? "#" + esc(at) : "") + '">Country status report</a>' : "";
    box.innerHTML =
      '<div class="mat-side__head"><div class="mat-side__name"><h2>' + esc(data.countries[iso] || iso) + "</h2>" +
      '<span class="mat-chip' + (s === data.blank ? " mat-chip--blank" : "") + '" style="background:' + s.color + ";color:" + s.ink + '">' +
      esc(stageText(c)) + "</span></div>" +
      '<div class="mat-side__row"><p class="mat-side__meta"><span><b>Last assessed</b> ' + esc(c.assessed || "—") + "</span>" +
      "<span><b>Stage last moved</b> " + esc(moved) + "</span></p>" +
      '<span class="mat-side__btns"><a class="mat-btn mat-btn--primary" href="countries/' + iso.toLowerCase() + "/#" +
      esc(state.indicator) + '">Country maturity report</a>' + statusLink + "</span></div></div>" +
      '<p class="mat-side__short">' + esc(c.short || "Nothing found.") + "</p>" +
      '<div class="mat-side__long">' + (c.summary || "") + "</div>";
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
