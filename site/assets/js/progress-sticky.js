/* progress-sticky.js — park the progress table's header below the site chrome.

   The same measurement `datatable.js` makes at `placeSticky()`, for the same
   reason its own comment gives: the two sticky bars differ in height by page and
   by viewport width — the Corpus nav wraps to two rows on a narrow window — so a
   CSS constant is wrong on whichever width it was not measured at. Measured, the
   header parks exactly under the chrome at every size.

   **Sticky is opt-in, added here rather than defaulted in the stylesheet.** An
   offset that is too small is worse than none at all: the header slides under the
   nav and the six count columns lose their labels with nothing on screen to say
   why. So the CSS leaves the header static and this adds the class once it has a
   real number. With the script blocked the table reads exactly as it does without
   it, minus a convenience — the counts were never behind the script, only the
   pinning is. */
(function () {
  var table = document.querySelector('.progress-table');
  if (!table) return;

  function place() {
    var top = 0;
    ['.site-header', '.corpus-nav'].forEach(function (sel) {
      var el = document.querySelector(sel);
      if (el && getComputedStyle(el).position === 'sticky') top += el.offsetHeight;
    });
    table.style.setProperty('--progress-top', top + 'px');
    document.documentElement.classList.add('progress-sticky');
  }

  place();
  var pending;
  window.addEventListener('resize', function () {
    clearTimeout(pending);
    pending = setTimeout(place, 120);
  });
})();
