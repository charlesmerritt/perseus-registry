---
title: How are relationships between records represented, and which record owns each link?
labels: [wayfinder:grilling]
parent: 1
blocked_by: [3, 4]
assignee: chazm
status: open
---

## Question

Decide whether links are embedded in records (a Research Project lists its Software and Datasets; Software lists what it consumes and produces) or held as separate relationship records; which side is authoritative for each link type, with the inverse generated statically; the relation vocabulary (from the prior-art ticket); how Integration Level per Objective is modelled; and how a link to a not-yet-registered thing (e.g. 'Objective 3 survey results', 'FIA') is represented. Test against tracker rows such as O2-04 → O2-01/O2-05 and O2-16 → many.
