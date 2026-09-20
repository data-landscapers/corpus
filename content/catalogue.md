# The catalogue page

Read by `scripts/catalogue.py`. One page, ~9,400 records, and the only surface on the site where a reader meets the repository as a whole rather than a compiled view of it.

The lede has to do two things at once: say what the catalogue is, and say what it is not — it holds metadata and links, never the bodies of other people's sources, and a reader who expects full text should learn that here rather than after a click.

The filter and empty-state strings are inside the page's JavaScript and have not moved here.

`dataset-description` is not shown on the page at all: it is the description in the `Dataset` block `catalogue.py` writes into the head, which is what a reader meets in Google Dataset Search before they have clicked anything. It lives here because it is prose a reader reads, and it has one job the lede does not — the reader seeing it has not seen the page yet, so it must say on its own that this is metadata and links and never the body of anyone else's source. Dataset Search wants between 50 and 5,000 characters.

## lede

All the reports on this site have been built from the documents listed in this catalogue. No other sources are used. To maintain the site the full text is maintained in a private repository - private because publishing it would involve copyright infringements. The catalogue gives you access to the original, published documents. For details of how the material is classified please go to the Methodology page.

## dataset-description

Every document the Data Landscapers Corpus holds on digital transformation, digital public infrastructure and data governance across Africa, as a single table: title, publisher, author, publication date and its precision, the countries and regions covered, the subjects from the Corpus taxonomy, the organisations and people tagged, the date the document entered the repository, and the publisher's own link. It is a catalogue of metadata and links — it does not contain the text of the documents themselves, each of which stays with its publisher at the URL given. Every claim in the country, region and topic reports on this site rests on a record in it.
