#!/usr/bin/env python3
r"""study-first-write.py — a first-pass study's summaries, written from its facts.

    python scripts/study-first-write.py dataexchange
    python scripts/study-first-write.py dataexchange --dry

`maturity/documentation/maturity-study-method.md` §8, as `study-opendatause-write.py` does it,
for the studies whose ladder `study_first_ladder.py` counts. **Nothing is composed here that a
fact does not state**: each paragraph is the drafters' own fact sentences on that aspect, each
linked whole to its evidence row's `url`, the rows that set the stage first, then the rest newest
first while the paragraph stays inside its room. An aspect with nothing found says so, linked to
the fact that set the stage. The short summary is one sentence per stage from `SHORT`.

Writes, per country, `outputs/maturity/{id}/{ISO3}.md` and
`maturity/{id}/evidence/{ISO3}/short.json`. Run it after the ladder script.

Exit: 0 written, 2 the study cannot be read.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import maturity_words  # noqa: E402
import study_lib  # noqa: E402
import study_first_ladder as ladder  # noqa: E402

SINCE = "2023-10"   # three years back from the as-at, as the ladder reads it
CAPS = {15: "fifteen", 20: "twenty"}   # `study.json` -> `story_cap`, the batch's `study-calls.py --cap`
ROOM = (100, 60, 60)
# Per study: the short sentence for stages 1 to 5 ({y} the year of the fact that set it), what an
# empty aspect says for the 2nd and 3rd aspects, and the thing named in an unstaged cell.
SHORT = {
    "dataexchange": (
        ["A {y} source says government systems have no data exchange platform.",
         "A government data exchange platform was under way in {y}; none in service is on record.",
         "A government data exchange platform was in service in {y}; no source found says how many systems it connects.",
         "Ten or more bodies or systems were connected to the government exchange platform in {y}; its use is not reported.",
         "Use of the government data exchange platform was reported in {y}."],
        ["No source found since October 2023 counts ten or more institutions or systems connected.",
         "No source found since October 2023 gives a figure for the exchanges through the platform."],
        "a government data exchange platform"),
    "idverification": (
        ["A {y} source says no other system checks people against the national ID.",
         "Another system's use of the national ID was under way in {y}; none in service is on record.",
         "A service checked people against the national ID in {y}; no source found reports use in a second sector.",
         "Services in two or more sectors checked people against the national ID in {y}; no source found reports volumes.",
         "Use of the national ID by other services was reported with figures in {y}."],
        ["No source found since October 2023 shows services in two or more sectors checking against the ID.",
         "No source found since October 2023 gives a figure for verifications or counts the services relying on the ID."],
        "another system checking people against the national ID"),
    "healthexchange": (
        ["A {y} source says the country's health systems do not exchange data.",
         "An exchange between health systems was under way in {y}; none in service is on record.",
         "Two health systems exchanged data in {y}; no source found reports exchange across the health system.",
         "Health systems exchanged data across the system in {y}; no source found reports patient matching by a national identifier.",
         "Patient records were linked by a national identifier across health systems in {y}."],
        ["No source found since October 2023 says three or more health systems exchange data, or a national exchange is in service.",
         "No source found since October 2023 says patient records are linked through the national ID or a national health identifier."],
        "health systems exchanging data"),
    "educationexchange": (
        ["A {y} source says the country's education systems exchange no data.",
         "A link between education systems was under way in {y}; none in service is on record.",
         "Two education systems exchanged data in {y}; no source found reports a shared learner identifier.",
         "One learner identifier was used across education systems in {y}; no source found reports links beyond education.",
         "Learner records were linked to the national ID or another sector in {y}."],
        ["No source found since October 2023 says one learner identifier is used across education systems.",
         "No source found since October 2023 says learner records are linked to the national ID or another sector."],
        "education systems exchanging data"),
    "socialexchange": (
        ["A {y} source says social protection programmes keep separate lists with no exchange.",
         "A link between social protection systems was under way in {y}; none in service is on record.",
         "A social protection system exchanged data in {y}; no source found reports a registry shared by programmes.",
         "Two or more programmes shared one social registry in {y}; no source found reports links to another sector.",
         "The social registry was linked to the national ID and another sector in {y}."],
        ["No source found since October 2023 says two or more programmes share one registry.",
         "No source found since October 2023 says the registry is linked to the national ID and to another sector."],
        "social protection systems exchanging data"),
    "idrobustness": (
        ["A {y} source says there is no national ID system with a unique number.",
         "A national ID system was under way in {y}; none in service is on record.",
         "The national ID system was issuing unique numbers in {y}; no source found reports biometric checks.",
         "The national ID system checked people by biometrics in {y}; no certification or audit is known.",
         "The national ID system's security was certified or audited in {y}."],
        ["No source found since October 2023 says the system checks people by biometrics.",
         "No source found since October 2023 reports a certification, audit or assurance level for the system."],
        "a national ID system"),
    "idcoverage": (
        ["Fewer than a third of the population held a national ID in {y}.",
         "A third of the population or more held a national ID in {y}.",
         "Two-thirds of the population or more held a national ID in {y}.",
         "Practically everyone held a national ID in {y}; no source found reports birth and death registration at the target.",
         "Everyone held a national ID and births and deaths were registered at the target in {y}."],
        ["No source found since October 2023 counts 99.9% of the population or more holding a national ID.",
         "No source found since October 2023 puts birth registration at all births and deaths at 80% or more."],
        "a count of people holding a national ID"),
    "idmaintenance": (
        ["A {y} source says a foreign supplier runs the national ID system.",
         "A move to national operation of the ID system was under way in {y}.",
         "The national authority ran the ID system day to day in {y}; no source found says who maintains it.",
         "National staff maintained the ID system in {y}; no source found reports ownership of its code.",
         "The ID system ran in {y} on code the state owns."],
        ["No source found since October 2023 says national staff maintain the system or the foreign contract has ended.",
         "No source found since October 2023 says the system runs on code the state owns."],
        "who operates the national ID system"),
    "authentication": (
        ["A {y} source says no digital authentication service exists.",
         "An authentication or e-signature service was under way in {y}; none in service is on record.",
         "An authentication service was in use in {y}; no source found reports use across services.",
         "Authentication was used across services in {y}; no source found reports remote proof of identity by a digital ID.",
         "People could prove who they are online with a digital ID in {y}."],
        ["No source found since October 2023 says authentication is used across services or channels.",
         "No source found since October 2023 says a mobile ID, ID wallet or signed credential is in service."],
        "a digital authentication service"),
    "idfrombirth": (
        ["A {y} source says a birth creates no identity record.",
         "A unique number at birth was provided for or piloted in {y}; none given in service is on record.",
         "Children were given a unique ID number at birth registration in {y}, at least in part of the country.",
         "Every registered birth was given a unique ID number in {y}; no source found reports complete registration.",
         "All births were registered with a unique ID number in {y}."],
        ["No source found since October 2023 says every registered birth across the country receives the number.",
         "No source found since October 2023 puts birth registration at all births and deaths at 80% or more."],
        "a unique number given at birth"),
    "birthidlink": (
        ["A {y} source says the civil register and the ID system exchange no records.",
         "A link between the civil register and the ID system was under way in {y}.",
         "The civil register and the ID system were linked one way or for one event in {y}.",
         "Births and deaths passed between the civil register and the ID system in {y}; no source found reports volumes.",
         "Exchange between the civil register and the ID system was reported with figures in {y}."],
        ["No source found since October 2023 says births enrol people in the ID system and deaths retire their numbers.",
         "No source found since October 2023 gives a figure for records exchanged between the two."],
        "a link between the civil register and the ID system"),
    "idregisters": (
        ["A {y} source says public registers do not use the national ID number.",
         "A public register's use of the national ID number was under way in {y}.",
         "A public register used the national ID number in {y}; no source found reports use by three main registers.",
         "Three or more main public registers used the national ID number in {y}; no matching figures are known.",
         "Matching of public registers against the national ID was reported with figures in {y}."],
        ["No source found since October 2023 shows three or more main public registers using the national ID number.",
         "No source found since October 2023 gives a figure from checking a register against the ID."],
        "a public register using the national ID number"),
    "centralbank": (
        ["A {y} source says the central bank has no mandate over payments or e-money.",
         "The central bank's payments mandate was being set up in {y}; no licensing is on record.",
         "The central bank licensed payment providers in {y}; no source found reports a national switch it oversees.",
         "The central bank ran or oversaw a national payment switch in {y}; no source found reports a regional link.",
         "The central bank took part in a regional or continental payment system in {y}."],
        ["No source found since October 2023 says the central bank runs or oversees a national switch.",
         "No source found since October 2023 says the country takes part in PAPSS or a regional payment system."],
        "the central bank's role over payments"),
    "g2ppayments": (
        ["A {y} source says government payments to people are made in cash.",
         "Digital government payments to people were under way in {y}; none in service is on record.",
         "A government programme paid people digitally in {y}; no source found reports a second main stream.",
         "Two or more main government payment streams were digital in {y}; no source found reports checks against the ID.",
         "Government payments to people were checked against the national ID or social registry in {y}."],
        ["No source found since October 2023 shows two or more main government payment streams paid digitally.",
         "No source found since October 2023 says government payments are checked against the ID or a social registry."],
        "digital government payments to people"),
    "revenuecollection": (
        ["A {y} source says taxes or fees are paid in cash or on paper only.",
         "Electronic payment of taxes or fees was under way in {y}; none in service is on record.",
         "Some taxes or fees could be paid electronically in {y}; no source found reports the main taxes and duties.",
         "The main taxes and customs duties were filed and paid electronically in {y}; the electronic share is not reported.",
         "A figure for revenue paid electronically was reported in {y}."],
        ["No source found since October 2023 says the main taxes and customs duties are filed and paid electronically.",
         "No source found since October 2023 gives a figure for revenue paid electronically."],
        "electronic payment of taxes or fees"),
    "businesspayments": (
        ["A {y} source says public procurement runs on paper.",
         "Government e-procurement was under way in {y}; none in service is on record.",
         "A government e-procurement system was in service in {y}; no source found reports end-to-end use.",
         "Government e-procurement ran end to end in {y}; figures for its use are not reported.",
         "Figures for government e-procurement were reported in {y}."],
        ["No source found since October 2023 says e-procurement runs end to end or is required of all public bodies.",
         "No source found since October 2023 gives a figure for e-procurement."],
        "a government e-procurement system"),
    "retailpayments": (
        ["A {y} source says no mobile money or retail digital payment service is licensed.",
         "A mobile money service was starting in {y}; none in service is on record.",
         "Mobile money or e-money was in service in {y}; no source found reports payments between providers.",
         "Payments between mobile money providers or with banks were in service in {y}; no source found reports a national switch.",
         "A national switch connected mobile money wallets and bank accounts in {y}."],
        ["No source found since October 2023 says payments between providers, or between wallets and banks, are in service.",
         "No source found since October 2023 says a national switch connects wallets and bank accounts."],
        "a mobile money or e-money service"),
    "paymentsuptake": (
        ["Fewer than a quarter of adults held an account in {y}.",
         "A quarter of adults or more held an account in {y}.",
         "Over half of adults held an account in {y}.",
         "Four in five adults or more held an account in {y}; no source found reports digital payment use at that level.",
         "Four in five adults or more made or received a digital payment in {y}."],
        ["No survey held since October 2023 puts adults with an account at 79% or more.",
         "No survey held since October 2023 puts adults paying digitally at 79% or more."],
        "a survey share of adults with an account"),
    "crossborderpayments": (
        ["A {y} source says no regulated cross-border digital payment channel exists.",
         "A cross-border digital payment corridor was under way in {y}; none in service is on record.",
         "A cross-border digital payment corridor was in service in {y}; no source found reports a regional payment system link.",
         "The country took part in a regional payment system in {y}; cross-border volumes are not reported.",
         "Cross-border digital payment volumes or costs were reported in {y}."],
        ["No source found since October 2023 says the country takes part in PAPSS or a regional payment system.",
         "No source found since October 2023 gives a figure for cross-border digital payments."],
        "a cross-border digital payment channel"),
    "consumerprotection": (
        ["A {y} source says no consumer-protection rules apply to digital financial services.",
         "Consumer-protection rules for digital finance were being drafted in {y}; none in force is on record.",
         "Consumer-protection rules for digital finance were in force in {y}; no source found reports a complaints body.",
         "A body took complaints about digital financial services in {y}; enforcement is not reported.",
         "Enforcement of consumer protection in digital finance was reported in {y}."],
        ["No source found since October 2023 says a financial ombudsman or complaints unit takes complaints.",
         "No source found since October 2023 reports a fine, sanction or complaint figures."],
        "consumer-protection rules for digital finance"),
    "populationregister": (
        ["A {y} source says no population register exists.",
         "A population register was under way in {y}; none in service is on record.",
         "A population register was in service in {y}; no source found reports updating from births and deaths.",
         "Births or deaths were entered in the population register in {y}; no source found reports its use by other systems.",
         "Other systems drew on the population register in {y}."],
        ["No source found since October 2023 says births or deaths are entered in the population register.",
         "No source found since October 2023 says other systems take records from the population register."],
        "a population register"),
    "civilregister": (
        ["A {y} source says civil registration is on paper with no digital register.",
         "Digital civil registration was under way in {y}; national digital birth registration is not on record.",
         "Births were registered digitally across the country in {y}; no source found reports digital death registration.",
         "Births and deaths were registered digitally in {y}; 90% birth registration is not on record.",
         "90% or more of births were registered in {y}."],
        ["No source found since October 2023 says deaths are registered in the digital system.",
         "No source found since October 2023 puts birth registration at 90% or more."],
        "digital civil registration"),
    "addressregister": (
        ["A {y} source says there is no national addressing system.",
         "An addressing system was under way in {y}; none in service is on record.",
         "An address register or digital addressing system was in service in {y}; no source found reports national coverage.",
         "The addressing system covered the whole country in {y}; no source found reports its use by services.",
         "Other services used the national address system in {y}."],
        ["No source found since October 2023 says the addressing system covers the whole country.",
         "No source found since October 2023 says other services use the address system."],
        "a national addressing system"),
    "businessregister": (
        ["A {y} source says business registration is on paper and held locally.",
         "A digital business register was under way in {y}; online registration is not on record.",
         "Firms could register online in {y}; no source found reports a number shared with tax.",
         "A firm's registration number served the tax authority too in {y}; no source found reports a record of beneficial owners.",
         "The business register recorded beneficial owners in {y}."],
        ["No source found since October 2023 says registration gives one number shared with tax or social security.",
         "No source found since October 2023 says the register collects beneficial owners."],
        "a digital business register"),
    "socialregistry": (
        ["A {y} source says there is no social registry; programmes hold their own lists.",
         "A social registry was under way in {y}; none in service is on record.",
         "A social registry was in service in {y}; no source found reports its use by two or more programmes.",
         "Two or more programmes used the social registry in {y}; no source found reports a link to the national ID.",
         "The social registry was linked to the national ID in {y}."],
        ["No source found since October 2023 says two or more programmes use the social registry.",
         "No source found since October 2023 says the social registry is linked to the national ID."],
        "a social registry"),
    "electoralregister": (
        ["A {y} source says the voters' roll is compiled by hand for each poll.",
         "A digital voters' roll was under way in {y}; none in service is on record.",
         "The voters' roll was held digitally in {y}; voters checking it is not on record.",
         "Voters could check the digital roll in {y}; no source found reports a link to the ID or civil register.",
         "The voters' roll was drawn from or checked against the ID or civil register in {y}."],
        ["No source found since October 2023 says voters could check the roll.",
         "No source found since October 2023 says the roll is drawn from or checked against the ID or civil register."],
        "a digital voters' roll"),
    "taxregister": (
        ["A {y} source says taxpayers are registered on paper or not at all.",
         "A computerised taxpayer register was under way in {y}; none in service is on record.",
         "Taxpayers were registered on computer in {y}; no source found reports a number shared with business registration or customs.",
         "The taxpayer number was shared with business registration or customs in {y}; no source found reports a tie to the national ID.",
         "The taxpayer number was tied to the national ID in {y}."],
        ["No source found since October 2023 says the taxpayer number is shared with business registration or customs.",
         "No source found since October 2023 says the taxpayer number is tied to the national ID."],
        "a computerised taxpayer register"),
    "landregister": (
        ["A {y} source says land rights are recorded on paper or not at all.",
         "Digital land registration was under way in {y}; none in service is on record.",
         "A digital land register was in service for part of the country in {y}; no source found reports national coverage.",
         "A digital land register covered the whole country in {y}; no source found reports online services.",
         "Land searches or registrations could be made online in {y}."],
        ["No source found since October 2023 says the digital land register covers the whole country.",
         "No source found since October 2023 says land can be searched or registered online."],
        "a digital land register"),
    "socialprotection": (
        ["A {y} source says social programmes are administered on paper.",
         "A programme management information system was under way in {y}; none in service is on record.",
         "A social programme was run on an information system in {y}; no source found reports electronic payment from it.",
         "A social programme's system paid beneficiaries electronically in {y}; no source found reports one system serving several programmes.",
         "One information system served several social programmes in {y}."],
        ["No source found since October 2023 says the programme's system pays beneficiaries electronically.",
         "No source found since October 2023 says one information system serves several social programmes."],
        "a social programme management information system"),
    "justice": (
        ["A {y} source says courts keep their cases on paper.",
         "A court case management system was under way in {y}; none in service is on record.",
         "Courts managed cases electronically in {y}; online filing is not on record.",
         "Cases could be filed with the courts online in {y}; no source found reports judgments or case status open online.",
         "Court judgments or case status were open online in {y}."],
        ["No source found since October 2023 says cases can be filed with the courts online.",
         "No source found since October 2023 says judgments are published or case status can be looked up online."],
        "a court case management system"),
    "taxadmin": (
        ["A {y} source says tax returns are filed and taxes paid on paper.",
         "An electronic tax system was under way in {y}; online filing is not on record.",
         "Tax returns could be filed online in {y}; no source found reports electronic payment.",
         "Taxes could be filed online and paid electronically in {y}; no source found reports mandatory or majority online filing.",
         "Online filing was mandatory or used by most taxpayers in {y}."],
        ["No source found since October 2023 says taxes can be paid electronically through the tax authority's system.",
         "No source found since October 2023 says online filing is mandatory or used for half or more of returns."],
        "online tax filing and payment"),
    "customs": (
        ["A {y} source says customs declarations are processed on paper.",
         "An automated customs system was under way in {y}; none in service is on record.",
         "Customs declarations were processed electronically in {y}; a single window is not on record.",
         "A trade single window joined customs and other agencies in {y}; no source found reports electronic exchange with other countries.",
         "Customs exchanged data electronically with another country in {y}."],
        ["No source found since October 2023 says a trade single window is in service.",
         "No source found since October 2023 says customs exchanges data electronically with another country."],
        "an automated customs system"),
    "landadmin": (
        ["A {y} source says land administration is run on paper.",
         "A land information system was under way in {y}; none in service is on record.",
         "Land transactions were processed electronically in {y}; no source found reports a link to survey maps or valuation.",
         "The land system joined records to survey maps or valuation in {y}; no source found reports a link to tax.",
         "The land system was linked to land or property tax in {y}."],
        ["No source found since October 2023 says the land system joins records to survey maps or valuation.",
         "No source found since October 2023 says land or property tax is assessed or paid through the land system."],
        "a land information system"),
    "aigovernment": (
        ["A {y} source says no AI system is in use in public administration.",
         "AI for public administration was under way in {y}; none in service is on record.",
         "A government body used an AI system in service in {y}; AI in several bodies is not on record.",
         "AI was in service in several government bodies in {y}; no source found reports rules or a register for it.",
         "The government published rules or a register for its own use of AI in {y}."],
        ["No source found since October 2023 says AI is in service in two or more government bodies.",
         "No source found since October 2023 says the government has issued rules or a register for its own use of AI."],
        "AI in public administration"),
    "aisectoral": (
        ["A {y} source says no public sector's system uses AI.",
         "An AI tool for a public sector's system was under way in {y}; none in service is on record.",
         "An AI tool was in service in a public sector's system in {y}; AI in several sectors is not on record.",
         "AI was in service in several sectors' public systems in {y}; no source found reports measured results.",
         "Measured results of AI in a public sector's system were reported in {y}."],
        ["No source found since October 2023 says AI is in service in the public systems of two or more sectors.",
         "No source found since October 2023 reports measured results of a sectoral AI system."],
        "AI in a sector's public system"),
    "aisystems": (
        ["A {y} source says no AI model, dataset or computing is built or hosted in the country.",
         "A national AI model, dataset or computing facility was under way in {y}; none in service is on record.",
         "An AI model or dataset built in the country was in service in {y}; AI computing is not on record.",
         "AI computing was in service in the country in {y}; no source found reports its use by others.",
         "National AI computing, models or datasets were open to named users in {y}."],
        ["No source found since October 2023 says a facility with GPUs or AI accelerators is in service in the country.",
         "No source found since October 2023 says national AI computing, models or datasets are open to named users."],
        "an AI model, dataset or computing facility"),
    "aiabuse": (
        ["A {y} source says nothing addresses harms from AI.",
         "A rule or authority on harms from AI was being drafted in {y}; none in force is on record.",
         "A rule addressing a harm from AI was in force in {y}; a designated authority is not on record.",
         "A body was designated with a mandate over AI in {y}; enforcement is not on record.",
         "A rule or body against harms from AI was enforced in {y}."],
        ["No source found since October 2023 says a body is designated with a mandate over AI.",
         "No source found since October 2023 gives an enforcement or redress decision about a harm from AI."],
        "a rule or authority against harms from AI"),
    "techhubs": (
        ["A {y} source says no technology hub, incubator or park operates in the country.",
         "A technology hub or park was under way in {y}; none running programmes is on record.",
         "A hub ran a programme for startups in {y}; hubs in more than one city are not on record.",
         "Hubs ran programmes in more than one city in {y}; no source found reports a technology park with tenants.",
         "A technology park was open with tenants in {y}."],
        ["No source found since October 2023 says hubs with programmes are in service in two or more cities.",
         "No source found since October 2023 says a science or technology park is in service with tenants."],
        "a technology hub"),
    "startups": (
        ["A {y} source says no startup law, strategy or public support exists.",
         "A startup law or strategy was being prepared in {y}; none adopted is on record.",
         "A startup law or strategy was adopted by {y}; startups labelled under it are not on record.",
         "Startups were labelled under the startup law or strategy in {y}; no source found reports a public fund under it.",
         "A public fund under the startup law or strategy financed startups in {y}."],
        ["No source found since October 2023 says startups are labelled or registered under a startup law or strategy.",
         "No source found since October 2023 says a public fund under the startup law or strategy has financed startups."],
        "a startup law or strategy"),
    "civilserviceskills": (
        ["A {y} source says civil servants receive no digital-skills training.",
         "Digital-skills training for civil servants was under way in {y}; a standing programme is not on record.",
         "A digital-skills programme trained civil servants in {y}; reach across government is not on record.",
         "Digital-skills training reached civil servants across government in {y}; the share trained is not published.",
         "The share of the civil service trained in digital skills was published in {y}."],
        ["No source found since October 2023 says digital-skills training reaches civil servants across government.",
         "No source found since October 2023 gives the share of the civil service trained in digital skills."],
        "digital-skills training for civil servants"),
    "digitalskills": (
        ["A {y} source says no programme teaches the public digital skills.",
         "A national digital-skills programme was under way in {y}; how many it trained is not on record.",
         "A national digital-skills programme had trained a stated number of people by {y}; a measured share with skills is not on record.",
         "The share of people with basic digital skills was measured in {y}, below half.",
         "Half or more of adults had basic digital skills, measured in {y}."],
        ["No source found since October 2023 gives a measured share of people with basic digital skills.",
         "No source found since October 2023 gives a measured share of half or more of adults with basic digital skills."],
        "a national digital-skills programme"),
    "policyresearch": (
        ["A {y} source says no local institution researches digital policy.",
         "Research on digital policy had begun in {y}; published research by a local institution is not on record.",
         "A local institution published research on digital policy in {y}; a part in a policy process is not on record.",
         "Local research fed a digital policy process in {y}; a standing role is not on record.",
         "A local research institution held a standing role in digital policy in {y}."],
        ["No source found since October 2023 says local research fed a digital policy, law or strategy.",
         "No source found since October 2023 says a local research institution holds a standing advisory role in digital policy."],
        "research on digital policy"),
    "feedbackportals": (
        ["A {y} source says people have no digital channel to complain about public services.",
         "A digital channel for complaints about public services was under way in {y}; one in service is not on record.",
         "A digital complaints channel was in service in {y}; reach across government is not on record.",
         "A national complaints channel covered services across government in {y}; its results are not published.",
         "Results of the national complaints channel were published in {y}."],
        ["No source found since October 2023 says a complaints channel reaches services across government.",
         "No source found since October 2023 gives resolution rates, response times or a report of the cases handled."],
        "a digital channel for complaints about public services"),
    "eparticipation": (
        ["A {y} source says laws and policies are adopted with no public consultation.",
         "The government asked the public for views online in {y}; a standing online channel is not on record.",
         "A standing online channel for public comment was in service in {y}; published answers are not on record.",
         "The government published what the public said in an online consultation in {y}; a rule requiring one is not on record.",
         "A consultation was held online in {y} because a rule requires drafts to be put online for comment."],
        ["No source found since October 2023 says the government published what it was told in an online consultation.",
         "No source found since October 2023 says a rule requires drafts to be put online for public comment."],
        "online participation in making policy"),
    "disabilityaccess": (
        ["A {y} source says no law or policy addresses digital access for persons with disabilities.",
         "Work to make information and digital services accessible to persons with disabilities was under way in {y}; a rule in force is not on record.",
         "A rule in force required accessible information or digital services in {y}; delivery is not on record.",
         "Accessible digital services or assistive technology were delivered to persons with disabilities in {y}; no audit is published.",
         "An audit of how accessible public digital services are was published in {y}."],
        ["No source found since October 2023 says accessible digital services or assistive technology were delivered.",
         "No source found since October 2023 gives the results of an accessibility audit of public websites or digital services."],
        "digital accessibility for persons with disabilities"),
    "refugees": (
        ["A {y} source says refugees or displaced people are not registered or are barred from digital services.",
         "Registration or a digital service for refugees or displaced people was under way in {y}; documents issued are not on record.",
         "Refugees or displaced people were registered and documented in {y}; their access to digital services is not on record.",
         "Refugees or displaced people could use SIM cards, mobile money or digital ID in {y}; how many do is not counted.",
         "The number of refugees or displaced people using digital services was published in {y}."],
        ["No source found since October 2023 says refugees or displaced people may use SIM cards, mobile money or digital ID.",
         "No source found since October 2023 counts refugees or displaced people with a SIM, an account or a digital ID."],
        "registration of refugees and displaced people"),
    "digitaldivides": (
        ["A {y} source says no programme brings internet access to rural areas.",
         "A programme to bring internet to rural areas was under way in {y}; sites connected are not counted.",
         "A rural connectivity programme had connected a stated number of sites or people by {y}; rural and urban use is not measured.",
         "Rural and urban internet use were measured in {y}, rural use below four-fifths of urban.",
         "Rural internet use was four-fifths or more of urban in {y}."],
        ["No source found since October 2023 gives internet use in rural and in urban areas.",
         "No source found since October 2023 gives rural internet use of 80 per cent or more of the urban rate."],
        "a programme to connect rural areas"),
    "agrisatellite": (
        ["A {y} source says no farming service uses satellite data.",
         "Satellite data was being put to use in farming in {y}; a service in use is not on record.",
         "A farming service using satellite data was in use in {y}; regular published outputs are not on record.",
         "A farming service published satellite-based bulletins or maps on a schedule in {y}; how many farmers they reach is not on record.",
         "Satellite-based farming advice or alerts reached a stated number of farmers or districts in {y}."],
        ["No source found since October 2023 says a satellite-based farming service publishes on a schedule.",
         "No source found since October 2023 counts farmers or districts reached by satellite-based advice or alerts."],
        "satellite data put to use in farming"),
    "metsatellite": (
        ["A {y} source says the national weather service receives no satellite data.",
         "The national weather service was receiving or installing a satellite data stream in {y}; its use in forecasts is not on record.",
         "The national weather service used satellite data in its forecasts in {y}; warnings drawing on it are not on record.",
         "The national weather service issued warnings drawing on satellite data in {y}; ISO 9001 certification is not on record.",
         "The national weather service was ISO 9001-certified in {y}, with satellite-based warnings."],
        ["No source found since October 2023 says the weather service issues warnings drawing on satellite data.",
         "No source found since October 2023 says the weather service holds ISO 9001 certification."],
        "satellite data in the national weather service"),
    "digitalsovereignty": (
        ["A {y} source says no rule governs where state data is held.",
         "Keeping state data under national control was a stated goal in {y}; a rule in force is not on record.",
         "A rule on where state data is held was in force in {y}; national hosting of state systems is not on record.",
         "Government data or a core system was hosted in the country in {y}; contract terms on data are not on record.",
         "A government contract with a foreign provider carried terms on data or exit in {y}."],
        ["No source found since October 2023 says government data or a core system is hosted in a national data centre or cloud.",
         "No source found since October 2023 says a government contract carries terms on data jurisdiction, portability or exit."],
        "control of state data"),
    "healthmis": (
        ["A {y} source says health reporting is on paper with no national system.",
         "A health information system was under way in {y}; a national one in service is not on record.",
         "A national health information system was in service in {y}; links to other health systems are not on record.",
         "The national health information system was linked to another health system in {y}; its reporting rate is not published.",
         "The reporting rate of the national health information system was published in {y}."],
        ["No source found since October 2023 says the system is linked to surveillance, supply chain or a register.",
         "No source found since October 2023 gives the system's reporting completeness or timeliness."],
        "a national health information system"),
    "educationmis": (
        ["A {y} source says there is no education information system.",
         "An education information system was under way in {y}; a school census run through it is not on record.",
         "The school census was run through an education information system in {y}; a record for each learner is not on record.",
         "The education information system held a record for each learner in {y}; a link to the national ID is not on record.",
         "Learner records were linked to the national ID or another government system in {y}."],
        ["No source found since October 2023 says the system holds a record for each learner.",
         "No source found since October 2023 says learner records are linked to the national ID or another government system."],
        "a national education information system"),
    "egovservices": (
        ["A {y} source says no government service is available online.",
         "Government services were going online in {y}; ten or more online are not on record.",
         "Ten or more government services could be completed online in {y}; a single gateway is not on record.",
         "A single government gateway with shared sign-in was in service in {y}; its use is not published.",
         "Use of the national government services portal was published in {y}."],
        ["No source found since October 2023 says one national portal carries several ministries' services with shared sign-in.",
         "No source found since October 2023 gives users, applications or transactions through the national portal."],
        "government services online"),
}
DATING = re.compile(r"as_of|article(?:'s)? (?:publication )?date|publication date|\bdate is\b|"
                    r"document date|date used|is used as|no (?:other )?date|the date is|revision date|published year|"
                    r"gives no (?:\w+ )?date|no (?:launch )?date|undated|dated by|date .*not stated|period is used|"
                    r"^(?:but |though |with )?no .*\b(?:given|stated|named|listed)$", re.I)
OPENER = re.compile(r"^(?:the )?(?:article|document|report|page|story|piece|text|release|table|brief|assessment)"
                    r"(?: \w+)?(?: \([^)]*\))? (?:says|states|reports|notes)(?: that)? ", re.I)
ASIDE = re.compile(r"\s*\((?=[^)]*\b(?:date|dated|as_of|inferred|publication|published)\b)[^)]*\)", re.I)


def link(url: str, words: str) -> str:
    return f"[{words.replace('[', '(').replace(']', ')')}](<{url}>)"


def clean(fact: str) -> str:
    fact = ASIDE.sub("", fact)
    parts = [p.strip() for p in re.split(r";\s+|(?<!\bi\.e\.)(?<!\be\.g\.)(?<=[a-z0-9)]\.)\s+(?=[A-Z])", fact.strip()) if p.strip()]
    kept = [p for p in parts if not DATING.search(p.rstrip("."))] or parts[:1]
    text = OPENER.sub("", "; ".join(p.rstrip(".;,") for p in kept))
    return text[:1].upper() + text[1:]


def sentences(rows: list[dict], first: list[str], room: int) -> list[str]:
    order = [r for i in first for r in rows if r["row_id"] == i]
    order += sorted((r for r in rows if r["row_id"] not in first),
                    key=lambda r: (r["as_of"], r["row_id"]), reverse=True)
    out, n, seen = [], 0, set()
    for r in order:
        s = clean(r["fact"])
        if s in seen or (out and n + len(s.split()) > room):
            continue
        seen.add(s)
        if (r["as_of"] + "-12")[:7] < SINCE:   # a year stands for its last month, as the ladder reads it
            s += f" ({r['as_of'][:4]}, before the three-year window)"
        out.append(link(r["url"], s) + ".")
        n += len(s.split())
    return out


def write(study: dict, iso: str, country: str, dry: bool) -> str:
    sid = study["id"]
    shorts, empties, thing = SHORT[sid]
    sub = study["sub_indicators"][0]
    here = study_lib.study_dir(sid)
    folder = os.path.join(here, "evidence", iso)
    try:
        with open(os.path.join(folder, "stage.json"), encoding="utf-8") as fh:
            cell = json.load(fh)["cells"][0]
    except OSError:
        raise study_lib.StudyError(f"{iso}: no stage.json; run the ladder script first")
    path = os.path.join(folder, "evidence.csv")
    rows = study_lib.read_csv(path) if os.path.exists(path) else []
    rows, _ = ladder.correct(rows, [f for f in study_lib.read_csv(os.path.join(here, "corrections.csv"))
                                    if f["iso3"] == iso])
    path = os.path.join(folder, "systems.csv")
    systems = study_lib.read_csv(path) if os.path.exists(path) else []
    urls = {r["slug"]: r["url"] for r in study_lib.read_csv(os.path.join(folder, "readlist.csv"))}
    noted, seen = [], set()
    for s in systems:
        url, words = urls.get(s["sources"].split(";")[0], ""), s["system"].strip()
        if url and words and words.lower() not in seen and len(noted) < 6 and s["class"] != sub["class"]:
            seen.add(words.lower())
            noted.append(link(url, words))
    src = [i for i in cell["stage_sources"].split(";") if i]
    parts = [f"# {country}", "", f"## {sub['label']}", ""]
    if cell["stage"].isdigit():
        top = next(r for r in rows if r["row_id"] == src[0])
        used = False
        for k, a in enumerate(study["aspects"]):
            mine = [r for r in rows if r["aspect"] == a["key"]]
            ids = {r["row_id"] for r in mine}
            body = sentences(mine, [i for i in src if i in ids], ROOM[k])
            if body and src[0] in ids:
                used = True
            if not body:
                lead = empties[k - 1] if k else f"No source found says {thing} is under way or in service."
                near = link(top["url"], clean(top["fact"])) if not used else link(top["url"], "the one given above")
                body = [f"{lead} The nearest held fact: {near}."]
                used = True
            if k == 0 and int(cell["stage"]) >= 4 and not any(r["value"] == ladder.firsts(study)[0] for r in mine):
                body.append("A later answer places the country above that step.")   # method §3.3
            parts += [f"**{a['name']}.** " + " ".join(body), ""]
        words = len(re.sub(r"\(<[^>]*>\)", "", " ".join(parts[4:])).split())
        if words < 120:   # few facts held: say so in the first paragraph, as the statistics law study did
            n = len(rows)
            parts[4] += (" It is the only fact" if n == 1 else f" {n} facts are") + " held on the subject"                 + ": no news story or official notice read for this study says more about it, " + ("the documents the earlier cell cited were not read" if "story_cap" in study else "the documents the earlier cell cited included") + ", and the systems themselves were not examined."
            if len(re.sub(r"\(<[^>]*>\)", "", " ".join(parts[4:])).split()) < 120:
                parts[4] += (f" This is a first pass, which read at most {CAPS.get(study.get('story_cap', 15), study.get('story_cap', 15))} stories a country; the nightly"
                             " deep dive reads further and may move the stage either way.")
        short = shorts[int(cell["stage"]) - 1].format(y=top["as_of"][:4])
    elif cell["stage"] == "unplaced":
        short = f"Nothing found since 2023 names {thing}, so no stage is set."
    else:
        short = f"Nothing found names {thing} or says there is none, so no stage is set."
    parts += [maturity_words.ALSO_ON_FILE_LABEL + ". " + ("; ".join(noted) + "." if noted else maturity_words.NONE_FOUND), "",
              maturity_words.NOT_FOUND_LABEL + ". " + (cell["gaps"] or "Nothing further is asked of this indicator."), ""]
    if not dry:
        out = study_lib.out_dir(sid)
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, iso + ".md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(maturity_words.rewrite("\n".join(parts)))
        with open(os.path.join(folder, "short.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump({sub["key"]: maturity_words.rewrite(short)}, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    return cell["stage"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Write a first-pass study's summaries.")
    ap.add_argument("study", choices=sorted(SHORT))
    ap.add_argument("--dry", action="store_true", help="check, write nothing")
    a = ap.parse_args(argv)
    try:
        study = study_lib.load(a.study)
        names = study_lib.countries()
        for iso in sorted(names):
            write(study, iso, names[iso]["name"], a.dry)
    except study_lib.StudyError as e:
        print(f"study-first-write: {e}")
        return 2
    print(f"study-first-write: {a.study}, {len(names)} countries" + (" (dry run, nothing written)." if a.dry else " written."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
