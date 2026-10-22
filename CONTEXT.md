# Perseus Research Registry

A structured, portable inventory of the consortium's research activities and the relationships between them. It complements FDIS (what data means) and D2S STAC (where spatial datasets live) by answering: what is everyone working on, how does it relate, and where can I find it?

## Language

**Perseus**:
The multi-institutional consortium whose research the registry catalogs.

**FDIS**:
The consortium's shared data standard. Split into Core (scientific data contract), Registry Profile (this registry's record types and relationships), and Publication Profile (STAC metadata, citation, provenance).
_Avoid_: using "FDIS" alone to mean the registry

**Objective**:
One of Perseus's four top-level research areas: 1 Measurement, 2 Modeling, 3 Management, 4 Mindset.

**Task**:
A numbered subdivision of an Objective (e.g. 2.1 Landowner Optimization, 2.4 Data Visualization). A Research Project has one primary Task and may support others.

**Research Project**:
A consortium work package, research question, or effort: the unit of "what someone is working on". Belongs to one Objective via its primary Task. Has a lifecycle status independent of any dataset's publication status.
_Avoid_: Project (ambiguous with D2S Project), Workstream (the tracker's synonym)

**Integration Level**:
How strongly a Research Project connects to an Objective: N/A, Informational, Collaborative, Integrated, or Discuss (connection suspected, not yet confirmed).

**D2S Project**:
Data to Science's own concept: a geographic area plus its associated UAS data. The registry never redefines it and only links to one.

**Software**:
A model, tool, or library a Research Project develops or uses. One record type distinguished by `kind: model | tool | library`.
_Avoid_: treating Model and Tool as separate record types

**Dataset**:
A registry record that points at an authoritative STAC Collection or Item; the registry holds only research-side facts (responsible project, role, access status), never duplicate spatial metadata.

**Institution**:
An organization or team participating in the consortium.

**Publication**:
A citable output: paper, report, documentation, or release, usually with a DOI.

**Registry Record**:
One YAML file describing one entity of the above types, identified by a persistent ID (e.g. `perseus:spatial-forest-forecasting`) that never changes when titles or leads change.

## Relationships

- A **Research Project** is led by one **Institution** and may have collaborating **Institutions**
- A **Research Project** develops or uses **Software**
- **Software** consumes and produces **Datasets**
- A **Dataset** references exactly one STAC Collection or Item in D2S
- A **Publication** is associated with **Research Projects** and **Datasets**

## Flagged ambiguities

- "Project" was used for both the consortium's work packages and D2S's area-plus-imagery concept. Resolved: **Research Project** vs **D2S Project**.
- "Model or tool" resolved into a single **Software** type with a `kind`.
