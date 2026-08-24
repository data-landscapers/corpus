/* bulletin-filter.js — the bulletin's country filter.
 *
 * After the Lab index's category filter on data-landscapers.io, which is eight lines: a
 * <select> over the distinct categories, and a change handler that sets display:none on any
 * <article> whose data-category does not match. This is longer for two reasons and neither is
 * decoration.
 *
 * **The list is nested.** The Lab's is flat — one article per row — so hiding rows is the
 * whole job. Here the items sit under Level-2 headings which sit under Level-1 headings, and a
 * filter that hides items alone leaves a page of headings with nothing under them. So a section
 * goes when every item in it has gone, a category goes when every section in it has gone, and
 * the category bar at the top loses the links that would now jump to a hidden heading.
 *
 * **An item can carry several countries, or none.** `data-places` is a space-separated list of
 * ISO3 codes, matched as a set. An item with no African country — a regional or global story —
 * is hidden by any country selection, which is correct: it is not about that country.
 *
 * The structure is read off the document rather than declared, because `bulletin.py` writes
 * headings and items as flat siblings inside `.article-body` and wrapping the sections would
 * mean nesting `markdown="1"` blocks two deep. One walk at load builds the model; every change
 * after that is a loop over it.
 *
 * Nothing here runs if the script does not load: `bulletin.py` writes the control `hidden`, and
 * removing that attribute is the first thing this does.
 */
(function () {
  'use strict';

  var body = document.querySelector('.article-body');
  var control = document.querySelector('.bulletin-filter');
  var select = document.getElementById('bulletin-country');
  if (!body || !control || !select) { return; }

  /* One walk over `.article-body`'s children, in document order. A group is an <h2> and the
   * sections under it; a section is an <h3> and the `.bulletin-item` divs under it. Items
   * before any heading — there are none today, but a lead paragraph would be one — are left
   * alone by belonging to no section. */
  var groups = [];
  var group = null;
  var section = null;

  Array.prototype.forEach.call(body.children, function (el) {
    if (el.tagName === 'H2') {
      group = { heading: el, sections: [] };
      groups.push(group);
      section = null;
    } else if (el.tagName === 'H3') {
      section = { heading: el, items: [] };
      if (group) { group.sections.push(section); }
    } else if (el.classList && el.classList.contains('bulletin-item')) {
      /* A group may hold items with no <h3> of its own — `Not topic-specific` is one — so the
       * items hang off a section with a null heading rather than off nothing. */
      if (group && !section) {
        section = { heading: null, items: [] };
        group.sections.push(section);
      }
      if (section) { section.items.push(el); }
    }
  });

  var navLinks = Array.prototype.slice.call(
    document.querySelectorAll('.bulletin-nav a'));
  // `.article-toc__sep` since 2026-08-24: the bar took the site-wide jump-nav
  // classes when that idiom moved into main.css. `.bulletin-nav` stays on the
  // <nav> as this page's own hook, which is what scopes the query.
  //
  // Both names are matched because this script is served to a page that may have
  // been built before the rename — the bulletin markdown on disk turns over on
  // the next sweep, not on deploy. Drop the second selector when the matching
  // block in report.css goes; they retire together.
  var navSeps = Array.prototype.slice.call(
    document.querySelectorAll('.bulletin-nav .article-toc__sep, .bulletin-nav__sep'));
  var count = control.querySelector('.bulletin-filter__count');

  function show(el, on) {
    if (el) { el.hidden = !on; }
  }

  /* Unfiltered, everything shows: the cross-references are part of reading the document top to
   * bottom, saying an item belongs under this topic too and pointing at where it is written
   * out. Filtered to one country they are noise — the reader has asked for that country's
   * items, and a signpost is not an item. So a selection shows summaries only, which also makes
   * the count the number of items rather than the number of places they are mentioned:
   * Eswatini's single item appears in two Level-2 sections and was counted twice. */
  function matches(item, code) {
    if (!code) { return true; }
    if (item.classList.contains('bulletin-item--xref')) { return false; }
    var places = (item.getAttribute('data-places') || '').split(/\s+/);
    return places.indexOf(code) !== -1;
  }

  /* The separators sit between the links as siblings, so which of them belong on the page
   * depends on which links survived. Hide them all, then put one back between each pair of
   * consecutive visible links — the first separator that lies between them in document order. */
  function repunctuate() {
    navSeps.forEach(function (s) { s.hidden = true; });
    var visible = navLinks.filter(function (a) { return !a.hidden; });
    for (var i = 0; i < visible.length - 1; i++) {
      for (var j = 0; j < navSeps.length; j++) {
        var after = visible[i].compareDocumentPosition(navSeps[j])
          & Node.DOCUMENT_POSITION_FOLLOWING;
        var before = visible[i + 1].compareDocumentPosition(navSeps[j])
          & Node.DOCUMENT_POSITION_PRECEDING;
        if (after && before) { navSeps[j].hidden = false; break; }
      }
    }
  }

  function apply(code) {
    var shown = 0;
    groups.forEach(function (g) {
      var groupLive = false;
      g.sections.forEach(function (s) {
        var sectionLive = false;
        s.items.forEach(function (item) {
          var on = matches(item, code);
          show(item, on);
          if (on) {
            sectionLive = true;
            shown++;
            /* The `Also under …` tail of a summary goes with the cross-references it names.
             * It is the same signpost in sentence form, and under a selection it was making
             * two claims that had stopped being true: its links jumped to Level-2 headings
             * this filter had just hidden, and the sentence said the item appears in sections
             * it had at that moment been filtered out of. Hidden with the item shown rather
             * than the item hidden, because it is a tail of the summary and the summary
             * stays. */
            var also = item.querySelector('.bulletin-item__also');
            if (also) { also.hidden = !!code; }
          }
        });
        show(s.heading, sectionLive);
        if (sectionLive) { groupLive = true; }
      });
      show(g.heading, groupLive);
      /* The bar's links are matched to their headings by the id they jump to, which is the one
       * thing the two are guaranteed to agree on — `bulletin.py` builds both from the same
       * slug, and a link to a hidden heading is a jump that appears to do nothing. */
      navLinks.forEach(function (a) {
        if (a.getAttribute('href') === '#' + g.heading.id) { a.hidden = !groupLive; }
      });
    });
    repunctuate();

    if (count) {
      count.textContent = code
        ? shown + (shown === 1 ? ' entry' : ' entries')
        : '';
    }
  }

  select.addEventListener('change', function () { apply(this.value); });
  control.hidden = false;
})();

/* The mini-archive picker in the colophon — the last week of bulletin PDFs
 * (documentation/bulletin-archive.md). Separate closure because it is a separate feature and
 * shares nothing with the filter above; one file because it is one page's behaviour and a
 * second request costs more than the twenty lines save.
 *
 * `render.py` writes the options from `editions.json`, so there is nothing to fetch and the
 * picker is correct in a local preview as well as on the site. All this adds is the navigation
 * a <select> cannot do by itself — which is also why it renders `hidden` and is unhidden here:
 * without the script the reader keeps the current PDF, named two rows above, and is not offered
 * a control that does nothing.
 *
 * Every value is a dated filename resolved against the page's own directory, so §9's *no
 * undated download URL exists at all* is untouched and nothing here can navigate off-site. */
(function () {
  'use strict';

  var picker = document.getElementById('bulletin-editions');
  if (!picker) { return; }

  picker.addEventListener('change', function () {
    var file = this.value;
    /* Belt and braces on a value that should only ever be a filename this build wrote: a
     * slash, a scheme or a parent segment is not one, and refusing is cheaper than reasoning
     * about what a page could be made to link to. */
    if (!file || /[/\\:]/.test(file) || file.indexOf('..') !== -1) { return; }
    window.location.href = file;
  });

  picker.hidden = false;
})();
