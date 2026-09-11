## Introduction
Many of the decisions made by Corpus are based on the various lookup tables listed here. It allows for significant configuration changes to search and classification without interfering with the underlying code.

<!-- A "table:" comment below names a CSV, and optionally the columns to show; the page draws that table from the file at build time (scripts/methodology.py, lookup_tables). Edit the file, not a copy here. -->

## Countries
<!-- table: lookups/countries.csv -->

## Topics
<!-- table: lookups/taxonomy.csv -->

## Indicators
<!-- table: lookups/indicators.csv | indicator_id, Topic L1, Topic, Progress indicator -->

## Progress Categories
| Value             | Meaning                                                                       |
| ----------------- | ----------------------------------------------------------------------------- |
| Movement          | Some form of progress, however minor, has been recorded                       |
| Stalled           | A stated target passed without delivery                                       |
| Regressed         | An instrument was withdrawn or neutralised, or a reported position worsened   |
| Mixed             | The indicator's instruments moved in different directions in the period       |
| No change         | The repository holds a standing position and nothing in the period touched it |
| No evidence       | The repository holds nothing on this indicator at all                         |
| Baseline not held | There is evidence of movement but no baseline to compare it against           |

A value may carry a qualifying clause after a comma, as in *Movement, regulations still pending*.

## Daily journals
<!-- table: outputs/vocab/sweep-daily.csv -->

## National newspapers
<!-- table: outputs/vocab/sweep-newspapers.csv -->

## Academic journals
<!-- table: outputs/vocab/sweep-journals.csv -->

## NGOs and think-tanks
<!-- table: outputs/vocab/sweep-thinktanks.csv -->

## Financiers
<!-- table: outputs/vocab/sweep-financiers.csv -->

## Regional institutions
<!-- table: outputs/vocab/sweep-regional-orgs.csv -->

## Catalogue metadata
<!-- table: site/metadata/catalogue-metadata.csv -->

## Non-state finance metadata
<!-- table: site/metadata/non-state-finance-metadata.csv -->
