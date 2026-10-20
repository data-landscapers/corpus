/* report-head.js — pin a place monthly's head under the site chrome.

   The head is the place's reports, the title with its PDF button and the
   sections bar (Bill, 2026-10-17): a reader on a story deep in the page can
   see which country it is and jump to another section. Measured rather than a
   CSS constant for the reason `progress-sticky.js` gives — the chrome's height
   differs by viewport — and the head's own height decides where a jumped-to
   heading must land.

   **Opt-in, like the progress table's header.** The CSS leaves the head static
   and this adds the class once it has real numbers, and declines when the head
   would take more than 40% of the viewport, where pinning it would leave too
   little room to read. With the script blocked the page reads as before. */
(function () {
  var head = document.querySelector('.report-head');
  if (!head) return;
  var root = document.documentElement, top = 0;

  function place() {
    top = 0;
    ['.site-header', '.corpus-nav'].forEach(function (sel) {
      var el = document.querySelector(sel);
      if (el && getComputedStyle(el).position === 'sticky') top += el.offsetHeight;
    });
    var fits = head.offsetHeight <= window.innerHeight * 0.4;
    root.classList.toggle('report-head-sticky', fits);
    root.style.setProperty('--report-head-top', top + 'px');
    root.style.setProperty('--report-head-clear', (top + head.offsetHeight + 12) + 'px');
  }

  /* A status report's head carries a third bar, the topics of each section
     (Bill, 2026-10-20). Show the group for the section in view and mark that
     section and topic as current, which the house style puts in black. The bar
     is held at its tallest group's height so a swap never moves the page.
     A section link shows its topics and stays put, so a reader can click
     through the sections to see what each holds; a topic link jumps. The next
     scroll hands the bar back to the section in view. */
  var bar = head.querySelector('.status-topics');
  var sections = head.querySelector('nav[aria-label="Sections in this report"]');
  var groups = bar ? bar.querySelectorAll('.status-topics__group') : [];
  var heads = document.querySelectorAll('.article-body h2[id], .article-body h3[id]');

  function mark(nav, id) {
    if (!nav) return;
    nav.querySelectorAll('a[aria-current]').forEach(function (a) { a.removeAttribute('aria-current'); });
    var a = id && nav.querySelector('a[href="#' + id + '"]');
    if (a) a.setAttribute('aria-current', 'true');
  }

  function hold() {
    var tallest = 0;
    bar.style.minHeight = '';
    var shown = [].filter.call(groups, function (g) { return !g.hidden; });
    groups.forEach(function (g) {
      groups.forEach(function (o) { o.hidden = o !== g; });
      tallest = Math.max(tallest, bar.offsetHeight);
    });
    groups.forEach(function (g) { g.hidden = shown.indexOf(g) < 0; });
    bar.style.minHeight = tallest + 'px';
  }

  var chapter = null;
  function show(id) {
    chapter = id;
    groups.forEach(function (g) { g.hidden = g.getAttribute('data-chapter') !== id; });
    mark(sections, id);
  }

  function spy() {
    // Below the pinned head, or below the site chrome where the head is not pinned.
    var line = Math.max(head.getBoundingClientRect().bottom, top) + 16, h2 = null, h3 = null;
    heads.forEach(function (h) {
      if (h.getBoundingClientRect().top > line) return;
      if (h.tagName === 'H2') { h2 = h; h3 = null; } else { h3 = h; }
    });
    var id = h2 ? h2.id : (heads[0] && heads[0].id);
    if (id !== chapter) show(id);
    mark(bar, h3 && h3.id);
  }

  if (bar && groups.length) {
    hold();
    spy();
    if (sections) sections.addEventListener('click', function (e) {
      var a = e.target.closest('a[href^="#"]'), id = a && a.getAttribute('href').slice(1);
      // A section without topics has nothing to preview, so its link jumps as before.
      if (!id || !bar.querySelector('[data-chapter="' + id + '"]')) return;
      e.preventDefault();
      show(id);
      mark(bar, null);
    });
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () { ticking = false; spy(); });
    }, { passive: true });
  }

  place();
  var pending;
  window.addEventListener('resize', function () {
    clearTimeout(pending);
    pending = setTimeout(function () { if (bar && groups.length) hold(); place(); }, 120);
  });
})();
