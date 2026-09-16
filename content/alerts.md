# The alerts pages

Read by `scripts/alerts.py`, which writes both `site/alerts/index.html` (sign up) and
`site/alerts/manage/index.html` (edit what you hold). `documentation/catalogue-alerts.md`
Part 2 is where this text was agreed, and the design record is the place to argue with it.

**Only the site's own text is here.** What Buttondown sends — the confirmation email, the
tag descriptions, the newsletter description — is typed into Buttondown's settings screens
by hand, and sits inline in Part A of the design beside the step that types it. The digest
body is built by the Worker (`workers/alerts/worker.js`) and is not prose anyone edits.

The keys `e-check`, `e-input` and `e-later` are the three `?e=` values the Worker redirects
back with, and `ok` is `?ok=1`. Renaming one means changing the Worker too.

## title

Alerts

## lede

Get an email when new documents about your countries or topics reach the catalogue. Free, weekly, and you can stop at any time.

## how

1. Pick countries, topics, or both.
2. Enter your email address.
3. Confirm from the email we send you.

You then get one email a week, on Monday, listing the new documents that match. No new documents, no email.

## what

An alert can cover up to five countries and five topics. A document matches if it is about any of the countries and any of the topics. Choose **Any** to widen either side.

You can hold up to ten alerts. They all arrive together, in one email on Monday.

An alert lists documents published in roughly the last three months as they reach the catalogue. Older documents we add to the archive are not sent; find those in the catalogue.

A region, such as West Africa, covers documents about the region as a whole, not every document about each country in it.

## site

Also send me new writing from data-landscapers.io: articles, working papers and datasets, once a week.

## several

An alert covers up to five countries and five topics. Your selection had more, so pick the ones you want below.

## manage

Every alert email has a link to change your alerts or stop them.

## manage-title

Your alerts

## manage-lede

Change the countries and topics you get alerts for, add another, or remove them all.

## manage-empty

You have no alerts set up. Add one below.

## manage-saved

Saved. Your next Monday email will use the alerts above.

## manage-none

You have no alerts left, so we will send you nothing. Your address stays on the list. To remove it, use the unsubscribe link in any email from us.

## feed

Use a feed reader? Copy this address instead. It shows the same documents and needs no email address.

## privacy

Your email address is held by Buttondown, the service that sends the alerts, and used only to send them. This site does not store it. [Buttondown's privacy policy](https://buttondown.com/legal/privacy).

## ok

Check your inbox. Click the link in the email from Data Landscapers to start your alert.

## e-check

The check that you are not a robot did not complete. Please try again.

## e-input

Pick a country, a topic or the main-site box, and check the email address.

## e-later

Something went wrong on our side. Please try again later.
