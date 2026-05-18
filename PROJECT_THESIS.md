# Synthetic Archaeology
### A city of mistaken memories, reconstructed by an AI that does not understand the people it preserves.

---

## Central question

> Where do a grief post on Reddit, the cached HTML of a dead personal blog, and an unidentified photograph in the Library of Congress archive land in the same mathematical space — and what architecture emerges when an AI is asked to reconstruct the human beings these fragments once belonged to?

---

## Premise

The internet is the only continuous archive humanity now maintains, but it does not preserve people. It preserves the **debris** of people: half-finished sentences, broken thumbnails, 404-ed blog posts, low-resolution scans of photographs nobody can name. As this debris accumulates, the work of holding it together is increasingly delegated to machine learning systems that compress, cluster, and complete what they cannot read.

This project treats that situation as an archaeological site. Three datasets are scraped from three different domains of digital remains:

- 250 emotional Reddit posts from communities about grief and lost media (the residue of feeling);
- 250 Wayback Machine snapshots of dead personal blogs (the residue of identity);
- 250 Library of Congress / Wikimedia Commons photographs whose subjects are unidentified or undated (the residue of seeing).

The three are projected into a shared vector space (TF-IDF compared against Sentence-BERT; HOG compared against CLIP on the image side), and a K-means model is trained to find the twenty cells where the machine most aggressively confuses one type of remains with another. These are not errors to be corrected. They are the design generators of the project.

Each of the twenty mis-clustered cells is then passed to GPT-4o-mini, which is asked to act as a synthetic archaeologist: from the three sources of debris that the machine has accidentally fused together, it must extrapolate a fictional inhabitant — a person who never existed but whom the data, read incorrectly, implies. For each inhabitant, a short interior monologue is generated. These twenty monologues are the "false memories" the system produces.

The twenty false memories are then translated into twenty architectural fragments through a Blender Python pipeline. The fragments are assembled into one room — a single domestic interior that the AI is trying, and failing, to remember. A one-minute camera animation moves through the room as it slowly assembles itself, breathes (a TouchDesigner network deforms a key fragment in real time, driven by text-to-speech audio of the original Reddit posts), and dissolves back into a point cloud.

---

## Why this is not a glitch project

The aesthetic ambition is **not** future-tech, not cyberpunk, not "data-art glitch." It is the opposite. The room must feel **almost-remembered**. The wallpaper is slightly the wrong colour because the AI averaged seventeen different living rooms. The chair is the right shape but in the wrong era. The voice describing the room is gentle, but speaks of a person who never lived. The sadness is structural: the more accurate the AI tries to be, the more clearly its inability to understand human emotion becomes legible.

This is what the project is for: to make a viewer feel, for sixty seconds, what it is like to be remembered by a system that does not know it is remembering.

---

## Technical thesis (one paragraph)

Three heterogeneous text-and-image corpora of "digital remains" are scraped, vectorised in parallel by two competing methods per modality, jointly clustered with K-means to identify the twenty most cross-domain-confused cells in the shared semantic space, expanded by a GPT-4o-mini agent into twenty fictional-inhabitant monologues, and finally compiled by three connected Blender + TouchDesigner workflows into a single architectural scene of twenty rules-generated fragments that breathe in response to synthesised speech and resolve into a sixty-second camera animation through one impossible room.

---

## Mapping to assignment requirements

| Requirement | Where it is met |
|---|---|
| Web scraping — ≥2 sites, ≥3 datasets, 200–300 elements each | `Chapter_1/Scraping/` — Reddit JSON, Wayback CDX API, LoC/Wikimedia JSON |
| Vectorisation — ≥2 methods compared with experimental discussion | `Chapter_2/Vectorization/` — TF-IDF vs Sentence-BERT (text); HOG vs CLIP (image) |
| API interaction — own script, expand / synthesise / agent | `Chapter_1/API/synthetic_archaeology.py` — GPT-4o-mini generates 20 inhabitant monologues |
| Machine learning model | `Chapter_2/Clustering/` — K-means (K=20) on joint corpus; light DistilGPT2 fine-tune for fragment captions |
| Visualisation — matplotlib + seaborn | `Chapter_1/Visualising_Plotting/` — 6 plots minimum |
| 3 different 3D conversion workflows | `Chapter_3/Blender/` (text→geometry, image→displacement) + `Chapter_3/TouchDesigner/` (audio→deformation) |
| ≥20 rule-generated fragments | `Chapter_3/Blender/fragments_from_clusters.py` — 1 cluster → 1 fragment |
| ≥2 software with explained roles | Blender (static geometry + render) + TouchDesigner (real-time audio deformation) |
| ≥1 min animation | `Chapter_3/Renders/synthetic_room_70s.mp4` |
| Public GitHub repo with notebooks containing outputs | Top of this repo |
| OneDrive folder for large data, images, animation | Linked from `README.md` |
| Citations for datasets / models / GPT / 3rd-party code | `docs/Bibliography.md` |

---

## What the viewer is supposed to feel

Not amazement. Not awe.
A small, specific kind of sadness — the same one you feel when an autocomplete finishes your dead grandmother's sentence almost correctly.
