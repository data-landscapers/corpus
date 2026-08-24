# The countries page

Read by `scripts/home.py` for `site/countries/`, where the 54-box matrix went on 2026-08-24 (Bill).

The page's intro is `countries-intro` in `home.md`, which the home page's Countries section also uses — one paragraph, one home. Only the caveat under the matrix lives here, because the matrix does.

It lived in `home.md` until 2026-08-24, when it was deleted there in the same edit that trimmed that file back to the section intros — correctly, since the boxes it explains had already left the home page, but `home.py` was still asking for it, so `build_countries()` stopped short with a missing-key error until it landed here.

## caveat

Sources held per country. A source tagged to several countries is counted under each, so these sum to more than the country total above: they measure coverage, not documents.
