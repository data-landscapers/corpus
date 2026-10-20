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
  var root = document.documentElement;

  function place() {
    var top = 0;
    ['.site-header', '.corpus-nav'].forEach(function (sel) {
      var el = document.querySelector(sel);
      if (el && getComputedStyle(el).position === 'sticky') top += el.offsetHeight;
    });
    var fits = head.offsetHeight <= window.innerHeight * 0.4;
    root.classList.toggle('report-head-sticky', fits);
    root.style.setProperty('--report-head-top', top + 'px');
    root.style.setProperty('--report-head-clear', (top + head.offsetHeight + 12) + 'px');
  }

  place();
  var pending;
  window.addEventListener('resize', function () {
    clearTimeout(pending);
    pending = setTimeout(place, 120);
  });
})();
