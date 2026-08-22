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
  var navSeps = Array.prototype.slice.call(
    document.querySelectorAll('.bulletin-nav__sep'));
  var count = control.querySelector('.bulletin-filter__count');

  function show(el, on) {
    if (el) { el.hidden = !on; }
  }

  function matches(item, code) {
    if (!code) { return true; }
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
          if (on) { sectionLive = true; shown++; }
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
