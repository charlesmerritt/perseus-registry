---
title: What does the D2S STAC catalog actually contain and expose?
labels: [wayfinder:research]
parent: 1
blocked_by: []
assignee: claude (research subagent)
status: closed
---

## Question

Survey `https://stac.d2s.org/api/v1/` (and the D2S docs) to establish: the list of collections and their IDs; whether TreeMap, LiDAR, canopy-height, and biomass products referenced in `sources/objective2-tracker.csv` exist there and under what IDs; which STAC fields and extensions collections carry (title, description, license, providers, keywords, extent, links, DOIs); whether items/collections are public or need auth; whether the API is stable enough to fetch at static-site build time. Output: a fact sheet a Dataset record schema can be designed against, with real example IDs.

## Context

Findings: branch `research/d2s-stac-catalog-survey`, file `research/d2s-stac-catalog-survey.md`.

## Resolution

The D2S STAC API is public, fast, and suitable as the read-only source for Dataset metadata at static-site build time.

- 60 public collections. 43 use UUID IDs (= D2S Project IDs; their Item IDs = D2S data-product IDs); 17 use slugs (`3dep`, `indiana-lidar-ndhm`, ...). A Dataset reference must accept both.
- Real IDs for seeding: TreeMap `f8934dd1-75c0-4fa0-9c75-b29c8e4c7dc1` (64 items 2016/2020/2022, DOI 10.2737/RDS-2025-0032); biomass `22913402-...` (Maine 2023), `bfff8c87-...` (Howland), `e1cdddec-...` (BigMap); LiDAR `indiana-lidar-*`, `3dep`, `templ`, `martell-forest-benchmark-data`. Penobscot collections are marked UNOFFICIAL/test. No canopy-height collection yet (O2-17 has nothing in STAC).
- Metadata is thin: title/description/license/extent always present; `sci:doi` on 23 (needs normalizing); `contacts` on 34 (often personal emails, so think before republishing); keywords/providers almost never. Registry-side fields (variables, responsible project) fill a real gap.
- No auth for reads; CORS `*`; one GET of `/collections?limit=100` takes ~0.3 s. Items paginate by token with no totals. No caching headers; `q=` search broken. Builds should keep a cached snapshot and degrade gracefully when a collection disappears or is unpublished.
- Writes exist (API-key header) but are out of scope.
