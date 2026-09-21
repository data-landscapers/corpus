"""datasets-metadata-dc.py — writes the Data Centres field dictionary. One-off, kept for its reasoning.

The dictionary is authored here, not in a spreadsheet, for two reasons: the CSV quoting is
correct by construction, and each rename and drop from the v2 header (`v2_name`) is recorded
beside the field it produced. T2's import reads `v2_name` to migrate the master's header.

Two v2 columns are dropped, because neither held information of its own (checked against all
306 rows on 2026-09-21):
  - `ownership chain` equalled `ultimate_parent_company` in every row. It was a copy, not a chain.
  - `chinese_role` was "Construction/Equipment" wherever `chinese_involvement` was set, including
    the 17 Ownership rows, so it was a lossy copy.

`cloud_act_exposure` was relabelled on 2026-09-21 (T6) and is now set by rule. v2 judged it row by
row and disagreed with its own guidance in about a third of rows, and its "No" read "fully domestic
ownership and stack", which is false for every foreign, non-US parent. The field asks one question —
can a US order reach this data — and the rule answers it from two columns already in the row.

Columns: column, label (the table header), type, values (the allowed set for a category, or the
format), derived (blank if collected; otherwise the rule it is computed by), definition, guidance.
"""
import csv, io, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "outputs" / "datasets" / "data-centres" / "metadata.csv"

YN = "Yes; No"
UNK = "; Unknown"

# (column, v2_name, label, type, values, derived, definition, guidance)
F = [
 ("facility_id", "", "ID", "id", "ISO3-NNN", "",
  "Permanent identifier for the facility.",
  "The country's ISO3 code followed by the next free number in that country. An ID is never reissued: a facility that closes keeps its ID and is marked Decommissioned."),
 ("facility_name", "", "Facility", "text", "", "",
  "The facility's name as its operator markets it.",
  "Include any site suffix the operator uses (Teraco JB1). If a facility has no public name, use '[Operator] [City]'. Use the English name, with a local-language name in brackets if that is the one commonly used."),
 ("country", "", "ISO3", "code", "ISO3 from lookups/countries.csv", "",
  "The country where the facility is.", ""),
 ("country_name", "", "Country", "text", "", "from country",
  "The country's name.", "Copied from lookups/countries.csv."),
 ("city", "", "City", "text", "", "",
  "The city or town where the facility is.",
  "Use the usual English spelling (Johannesburg, not Joburg). For a site outside a city, give the nearest city and say where the site actually is in comments."),
 ("operational_status", "", "Status", "category", "Operational; Under construction; Planned; Decommissioned" + UNK, "",
  "Whether the facility is running.",
  "Base this on the newest source you can find, preferably from the last 12 months. Status changes quickly, so record the date of that source in comments."),
 ("year_operational", "", "Year", "year", "YYYY", "",
  "The year the facility opened, or is due to open.",
  "For a facility that is Planned or Under construction, give the announced target year. Leave blank if no source gives one."),
 ("facility_type", "", "Type", "category", "Colocation/carrier-neutral; Enterprise; Government; Hyperscale; Edge; Research", "",
  "The facility's main service model.",
  "Colocation: rack space rented to many tenants. Enterprise: built for one organisation's own use. Hyperscale: built for, or by, a cloud provider at campus scale. Record the main type here and any secondary role in comments."),
 ("services_offered", "", "Services", "list", "; -separated", "",
  "The services the operator advertises at the facility.",
  "Record only what the operator advertises or documents, and do not infer services."),
 ("govt_data_hosted", "", "Government data", "category",
  "Designated national / government data centre; Hosts government data alongside commercial; No government data" + UNK, "",
  "Whether the facility hosts government data or systems.",
  "Evidence comes from government cloud contracts, procurement records and operator client lists. Name the ministries or agencies in comments where they are known."),
 ("operator_name", "", "Operator", "text", "", "",
  "The company or agency that runs the facility day to day.",
  "This may be a different entity from the owner. For a state facility, name the agency or SOE. If the operator changed recently, name the previous one in comments."),
 ("ownership_type", "", "Ownership", "category",
  "Private domestic; Private foreign; Government / SOE; Joint venture (majority domestic); Joint venture (majority foreign); PPP; Multilateral / DFI" + UNK, "",
  "Who owns the facility's equity.",
  "Judge by equity, not by who runs the site. For a joint venture, domestic and foreign mean relative to the country the facility is in."),
 ("ownership_structure_type", "", "Parent structure", "text", "", "",
  "The legal form of the ultimate parent.",
  "Describes the ultimate parent, not the operator (e.g. Public REIT; Private equity-backed group; State-owned enterprise)."),
 ("parent_company", "", "Parent", "text", "", "",
  "The operator's immediate parent company, if it has one.", "Leave blank if the operator is itself the top of the chain."),
 ("parent_hq_country", "", "Parent HQ", "code", "ISO3", "",
  "The country where the immediate parent is registered.", "Use the country of registration, not the operational HQ."),
 ("ultimate_parent_company", "", "Ultimate parent", "text", "", "",
  "The top entity in the ownership chain.",
  "Trace the chain through filings, annual reports and registries. Write '(self)' when the operator is the top of the chain. A state is named as the government that owns it."),
 ("ultimate_parent_hq_country", "", "Ultimate parent HQ", "code", "ISO3; |-separated where control is joint", "",
  "The country where the ultimate parent is registered.",
  "This field drives control_category. Where control is joint, list every country, e.g. GBR|ZWE."),
 ("major_shareholders", "major shareholders", "Major shareholders", "text", "", "",
  "The ultimate parent's largest shareholders, with their stakes.",
  "Take up to five from the latest filing (2024 or later), each giving its source. Leave blank where nothing is disclosed."),
 ("government_ownership_pct", "", "Govt stake", "text", "Percentage, with its basis", "",
  "The share of the ultimate parent held by governments, whether directly or through state funds, SOEs or state pension funds.",
  "Give the figure with how it is held, e.g. '19.44% via PIC'. Leave blank if it is not disclosed."),
 ("foreign_ownership_pct", "", "Foreign stake", "text", "Percentage, with its basis", "",
  "The share of the owning entity held from outside the facility's country.", "Leave blank if it is not disclosed."),
 ("controlling_entities", "", "Controlled by", "text", "", "",
  "The entities holding more than 25% of the equity, or effective control of the board or management.", ""),
 ("control_mechanisms", "", "Control via", "text", "", "",
  "How the controlling entities exercise control (equity, board seats, voting rights, management contract).", ""),
 ("recent_investments", "", "Recent investment", "text", "", "",
  "Major investments since 2021, giving the investor, the year and the amount.", ""),
 ("dfi_involvement", "", "DFI involvement", "text", "None identified, or the DFI and its instrument", "",
  "The development finance institutions financing the facility or its parent, and on what terms.",
  "Name the instrument (equity, debt, guarantee). Equity carrying a board seat is a governance lever; debt alone is not. Write 'None identified' when a search found none."),
 ("investment_usd", "", "Investment (USD)", "number", "Whole US dollars", "",
  "The total capital investment reported for the facility.",
  "Record the newest figure. Say in comments whether it covers the first build, an expansion or the whole campus, and give any conversion from another currency with its date."),
 ("expansion_plans", "", "Expansion", "category", "Under construction; Planned; No plans" + UNK, "",
  "Whether the facility is being expanded.", "Look for announcements from the last 24 months."),
 ("key_tenants", "", "Key tenants", "text", "", "",
  "Anchor or notable tenants who are publicly confirmed.", "Record only tenants a source names. Most tenants are confidential, and a tenant must never be inferred."),
 ("hyperscaler_relationships", "", "Hyperscaler links", "text", "", "",
  "Confirmed relationships with AWS, Microsoft Azure or Google Cloud: tenancy, on-ramp, partnership or equity.",
  "The three hyperscaler_* columns are set from this field. Write 'None identified' when a search found none."),
 ("hyperscaler_microsoft", "Microsoft", "Microsoft", "category", YN, "from hyperscaler_relationships",
  "Whether Microsoft or Azure has a confirmed relationship with the facility.",
  "Yes only where hyperscaler_relationships names a relationship that is not negated."),
 ("hyperscaler_aws", "AWS", "AWS", "category", YN, "from hyperscaler_relationships",
  "Whether Amazon Web Services has a confirmed relationship with the facility.", "As for hyperscaler_microsoft."),
 ("hyperscaler_google", "Google", "Google", "category", YN, "from hyperscaler_relationships",
  "Whether Google has a confirmed relationship with the facility, including through a subsea cable partnership such as Equiano.", "As for hyperscaler_microsoft."),
 ("hyperscaler_presence", "", "Any hyperscaler", "category", YN, "Yes if any hyperscaler_* column is Yes",
  "Whether any of the three hyperscalers has a relationship with the facility.", ""),
 ("cloud_act_exposure", "", "CLOUD Act", "category",
  "Yes (US-parented operator); Partial (US hyperscaler service on site); No (no US parent or hyperscaler service)" + UNK,
  "from ultimate_parent_hq_country and hyperscaler_*",
  "Whether the US CLOUD Act can compel access to data held at the facility, through its owner or a US cloud provider there.",
  "Set by rule, not judged: Yes when ultimate_parent_hq_country includes USA; otherwise Partial when any hyperscaler_* is Yes; otherwise No. Unknown when ultimate_parent_hq_country is blank."),
 ("chinese_involvement", "", "Chinese role", "category", "Ownership; Investment; Construction/Equipment; None identified", "",
  "The strongest form of Chinese involvement in the facility.",
  "Ownership outranks Investment, which outranks Construction/Equipment. Write 'None identified' when a search found none."),
 ("chinese_entities", "", "Chinese entities", "list", "|-separated", "",
  "The Chinese companies involved.", "Leave blank when chinese_involvement is None identified."),
 ("foreign_dependency_score", "", "Foreign dependency", "category",
  "Low; Moderate; High; Insufficient data", "from ownership_type, ultimate_parent_hq_country, open_source_stack and cloud_act_exposure",
  "A composite of how far the facility depends on foreign owners, technology and law.",
  "Low: domestic ownership, an open stack and compliance with local law. High: foreign ownership, a proprietary stack and CLOUD Act exposure. Moderate: anything between the two."),
 ("open_source_stack", "", "Open source", "category",
  "Predominantly open source; Mixed open source and proprietary; Predominantly proprietary" + UNK, "",
  "Whether the facility's software stack is mainly open source.", "Judge from cloud_platform and what the operator says about its technology."),
 ("data_residency_guarantee", "", "Data residency", "category", "Yes, contractual guarantee; Partial (some data classes); No" + UNK, "",
  "Whether the operator guarantees by contract that data stays in the country.", "Check SLAs, terms of service and government hosting contracts."),
 ("local_dp_compliance", "", "Data protection", "category", "Certified / audited compliant; Self-declared compliant; No claim" + UNK, "",
  "Whether the operator claims compliance with the country's data protection law.", "Name the law in comments (e.g. POPIA, NDPA)."),
 ("total_floor_space_sqm", "", "Floor space (m²)", "number", "Square metres", "",
  "The facility's floor space.", "Convert from square feet by dividing by 10.764. Say in comments whether the figure is the campus, the building or the white space."),
 ("rack_capacity", "", "Racks", "number", "Racks", "",
  "How many racks the facility can hold.", "Record the figure as reported, and say in comments if the source counted cabinets."),
 ("it_capacity_mw", "", "IT power (MW)", "number", "Megawatts", "",
  "The power available to IT equipment, not counting cooling and other load.",
  "If only total facility power is published, record that and say so in comments. For a phased build, give the capacity built so far and the planned total in comments."),
 ("submarine_cable_access", "", "Subsea cable", "category",
  "At or adjacent to cable landing station; Dark fibre connection to landing station; Connected via metro fibre; Landlocked/no submarine cable access" + UNK, "",
  "How the facility reaches a submarine cable landing station.", "Check submarine cable maps and the operator's connectivity specifications."),
 ("ixp_presence", "", "IXP", "category", "IXP hosted on-site; IXP connected (not hosted); No IXP connection" + UNK, "",
  "Whether an internet exchange point is hosted at the facility or connected to it.", "Check PeeringDB and Af-IX."),
 ("carrier_neutrality", "", "Carrier-neutral", "category", "Fully carrier-neutral; Limited carriers; Single carrier / captive" + UNK, "",
  "Whether tenants can choose their carrier.", "Check the operator's material and PeeringDB."),
 ("gpu_ai_capability", "", "GPU / AI", "category", "Yes, confirmed GPU/AI infrastructure; Planned; No evidence" + UNK, "",
  "Whether the facility hosts GPU or other AI accelerator infrastructure.", "Name the GPU models in comments where known (e.g. NVIDIA H100)."),
 ("server_vendors", "", "Server vendors", "list", "; -separated", "",
  "The server vendors whose hardware is deployed at the facility.", "Record only deployments that are disclosed. In colocation, tenants bring their own hardware."),
 ("cloud_platform", "", "Cloud platform", "text", "", "",
  "The platform the operator uses to deliver cloud services, or any hyperscaler on-ramp it hosts.", "Keep the operator's own platform separate from a hosted on-ramp."),
 ("security_certifications", "", "Certifications", "list", "; -separated", "",
  "The current security and management certifications held by the facility or its operator.", "Check the certification body's register where one exists. Record expiry dates in comments."),
 ("gps_coordinates", "", "Coordinates", "coordinates", "lat, lon (decimal, 4 places)", "",
  "The facility's location.", "Approximate coordinates are acceptable; say so in comments. Leave blank if the location is not known."),
 ("control_category", "", "Control", "category", "African control; Joint African/foreign control; US control; Other foreign control", "from ultimate_parent_hq_country",
  "Who controls the facility, seen from a sovereignty angle.", "Joint when control is shared between African and non-African parents."),
 ("control_confidence", "", "Control confidence", "category", "high; medium; low", "",
  "How far the sources support control_category.", "high: two or more independent sources agree. low: a single source, or sources that conflict."),
 ("control_rationale", "", "Control rationale", "text", "", "",
  "The reason for control_category, in one line.", ""),
 ("comments", "", "Comments", "text", "", "",
  "Context, caveats, conflicting sources and recent changes.", "Every approximation or conversion, and every source that disagrees, belongs here."),
 ("source_urls", "", "Sources", "list", "; -separated URLs", "",
  "The URLs of every source consulted for the row.", "Bare URLs only. A row needs at least two independent sources for control_confidence to be high."),
 ("raw_slugs", "(new)", "Catalogue records", "list", "; -separated catalogue slugs", "",
  "The catalogue records that hold this row's sources.", "Each source_urls entry that is in the catalogue appears here as its slug; those not yet held are staged for ingest."),
 ("last_verified", "(new)", "Last verified", "date", "YYYY-MM-DD", "",
  "The date the row was last checked against its sources.", "Set whenever a validation pass or a BUILD run confirms or changes the row."),
]

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["column", "v2_name", "label", "type", "values", "derived", "definition", "guidance"])
    w.writerows(F)
    OUT.write_text(buf.getvalue(), encoding="utf-8", newline="")
    print(f"{OUT}: {len(F)} fields")

if __name__ == "__main__":
    main()
