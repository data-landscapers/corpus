# The Finance page

`site/finance/index.html`, built by `scripts/finance.py`. Two sections: non-state finance, which has data behind it, and national budgets, which does not yet.

The first block is what a reader meets before 1,257 rows of commitments, and it has to say three things: what a row is, what the money figures do and do not mean, and why the totals cannot be read as a market size. The second block has one job — to say plainly that the domestic side is not here yet and what that leaves missing — because a heading with nothing under it reads as an oversight unless it says otherwise.

Draft wording. This is the part to rewrite.

The two `dataset-*` blocks are not shown on the page: they are the descriptions in the `Dataset` structured data `finance.py` and `country.py` write into the head, which is what a reader meets in a dataset search before they have clicked anything. They live here because they are prose a reader reads. Each has to carry on its own the caveat the page spends a paragraph on — these are **commitments**, not disbursements, and a total of them is not a market size — because whoever sees one has not seen the page. Keep them between 50 and 5,000 characters, which is what a dataset search will take.

## page-intro

**It is currently impossible to calculate total investments into digital transformation.** There are three main reasons for this. Firstly no one has integrated non-state finance data with national budgets, expenditure and audits. Secondly no one has attempted to align the full spectrum of cross-border and domestic, public and private investment. Thirdly, with the  exception of the World Bank, no investors have attempted to adopt a common modern taxonomy that classifies investments in categories compatible with digital transformation. 

**Over the next year we aim to fill this vacuum.** Data on national budgets is currently not available and will be published when deep dives into national budget documentation is complete.

## non-state-intro

This table documents money committed to Africa's digital sector by financiers other than the state: bilateral and multilateral donors, development finance institutions, foundations, private investors, vendors and operators and private. One row per commitment, each tagged to a single recipient country, so the figures sum without double-counting.

**These are commitments, not disbursements.** This is because of the availability of data. A value in the table is the amount announced, in the year it was announced, converted from the announcing party's own currency at a dated rate — and a multi-year commitment sits wholly in its start year rather than being spread across the years it will be spent in. Money announced is not money arrived. We have insufficient evidence on which commitments were honoured. 

While we take pains to avoid double counting **do not attempt a simple aggregation of this table** without understanding the different instruments, financiers and beneficiary types.

The data is sourced from the International Aid Transparency Initiative's datastore, investor's own published portfolio's, press announcements and the media in general.

## non-state-table-note

Click any row to open the full record. Sort on any column heading, filter with the dropdowns, and search across every field whether or not it is shown. The regional codes are recipients in their own right, not aggregates of the countries beside them.

## budgets-intro

What a government commits from its own budget is the other half of the picture, and the more important half: domestic spending is where a state's actual priorities are visible, and where external finance either is or is not being matched.

**Nothing is published here yet.** The repository holds budget extracts for a number of countries, but not enough of them, and not on a consistent enough basis, to put a table on a public page without it being read as a comparison it cannot support — budget documents differ by country in what they call a line, which years they cover and whether the figure is an allocation, a revision or an outturn. Publishing them side by side before that is settled would produce exactly the false precision this section exists to avoid.

Until then, the per-country reports carry what is held, stated as what it is.

## dataset-all

Every non-state financial commitment to Africa's digital sector held by Data Landscapers, as a single table: the recipient country, the financier, the year the finance was approved and the year the activity ends, the sector and instrument, the committed amount in millions of US dollars with its basis and a quality assessment, the status, the recipient organisation, the original currency amount, the financier's own project identifier and IATI activity identifier where published, and the public source each row rests on. The amounts are commitments rather than disbursements, because disbursement data is largely unavailable, so a total of them is what was promised and not what was spent — it is not a measure of market size. The subjects covered are digital transformation, digital public infrastructure and data governance. Domestic budget appropriations are not in this table.

## dataset-place

Every non-state financial commitment to the digital sector in {name} held by Data Landscapers, as a single table: the financier, the year the finance was approved and the year the activity ends, the sector and instrument, the committed amount in millions of US dollars with its basis and a quality assessment, the status, the recipient organisation, the original currency amount, the financier's own project identifier and IATI activity identifier where published, and the public source each row rests on. The amounts are commitments rather than disbursements, because disbursement data is largely unavailable, so a total of them is what was promised to {name} and not what was spent there — it is not a measure of market size. The subjects covered are digital transformation, digital public infrastructure and data governance. Domestic budget appropriations are not in this table. This is the {name} cut of the full Data Landscapers non-state finance table.
