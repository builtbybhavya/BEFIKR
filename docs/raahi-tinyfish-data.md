# TinyFish data for Raahi and Safe Spots

## Import public places into Safe Spots

1. Sign in with an admin account and open **Profile → Open admin console → Places**. Follow the [README](../README.md#start-locally) to create a local admin account if needed.
2. Copy the Delhi place prompt into [TinySet](https://agent.tinyfish.chat/playground/datasets), check the proposed columns, build a dataset, and export the CSV. TinySet creates a snapshot of public sources. Check the cost shown in TinyFish before starting a build. [TinySet overview](https://www.tinyfish.chat/blog/inside-tinyset)
3. Upload the CSV in **Places**. Required columns are `name`, `category`, `address`, `latitude`, `longitude`, and `source_url`. Optional columns are `phone`, `source_date`, and `dataset_id`. The importer accepts up to 250 candidates per file.
4. Open the source for each candidate and verify the name, category, address, and map position before approving it. Approved directory listings appear in nearby Safe Spot searches after the user confirms their location. The listing includes its source and review date. Opening hours and service availability still need to be checked with the venue.

Supported categories are `police`, `hospital`, `park`, `public_space`, `restaurant`, and `cafe`. Keep searches focused on public venues and official contact numbers. Users can find these records under the **BEFIKR directory** filter after confirming a pin.

## Research sources for Raahi

Copy the Raahi research prompt from **Places** into [TinyResearch](https://agent.tinyfish.chat/playground/research). It asks for official sources covering street lighting, footpaths, crossings, transit access, and aggregate safety data, with dates, coverage, spatial precision, access, and terms. Review each result before connecting a dataset to the route engine. [TinyResearch overview](https://www.tinyfish.chat/blog/introducing-tinyresearch-and-tinyset)

| Source | What to evaluate |
| --- | --- |
| [Delhi Open Transit Data](https://otd.delhi.gov.in/documentation/) | Published GTFS stop coordinates for transit proximity. Bus schedule times are approximate. |
| [Delhi Transport Department road safety report](https://transport.delhi.gov.in/sites/default/files/2023-08/road_safety_data_to_action_report.pdf) | Historical fatal traffic crash locations from 2019–2021 for traffic safety context. |
| [Safetipin project summaries](https://safetyscore.safetipin.com/projects) | Delhi audit coverage for lighting and walkpaths. Check access to individual audit records, reuse terms, and dates with the publisher. |

The app uses imported place records for discovery. Connecting any research dataset to Raahi's route ranking requires a source with suitable geographic coverage, reuse terms, and enough detail to match the walking route.
