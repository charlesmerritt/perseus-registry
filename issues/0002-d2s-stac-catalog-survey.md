---
title: What does the D2S STAC catalog actually contain and expose?
labels: [wayfinder:research]
parent: 1
blocked_by: []
assignee:
status: open
---

## Question

Survey `https://stac.d2s.org/api/v1/` (and the D2S docs) to establish: the list of collections and their IDs; whether TreeMap, LiDAR, canopy-height, and biomass products referenced in `sources/objective2-tracker.csv` exist there and under what IDs; which STAC fields and extensions collections carry (title, description, license, providers, keywords, extent, links, DOIs); whether items/collections are public or need auth; whether the API is stable enough to fetch at static-site build time. Output: a fact sheet a Dataset record schema can be designed against, with real example IDs.
