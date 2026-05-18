# Synthetic Archaeology
### BARC0053: Bartlett Architecture Skills Elective (B-Pro Courses) 25/26 — Final Assignment

**Tutor:** Ioana Drogeanu
**Student number:** 25217145
**OneDrive (large files):** <https://liveuclac-my.sharepoint.com/:f:/g/personal/ucbvxr0_ucl_ac_uk/IgDhwf4scqmuSrxvjEnf63xlAbJli6S2QKK5bCRpB_3h3Ko?e=FbxL3d>

---

## What this project is

A computational reconstruction of a city of fragmented digital remains, built by a machine that does not understand the people it preserves. Three datasets of "internet debris" are scraped, jointly vectorised, clustered for mis-classifications, expanded into fictional-inhabitant monologues by GPT-4o-mini, and translated into twenty architectural fragments assembled into a single impossible room. A sixty-plus second animation moves a camera through this room as it assembles, breathes, and dissolves.

The full thesis is in [`PROJECT_THESIS.md`](./PROJECT_THESIS.md).

---

## Repository structure

```
.
├── PROJECT_THESIS.md
├── README.md
├── requirements.txt
├── .env.example                ← copy to .env, fill in OPENAI_API_KEY
├── .gitignore
│
├── Chapter_1/                  ← Data collection + ML + visualisation
│   ├── Scraping/
│   │   ├── reddit_grief.ipynb
│   │   ├── wayback_dead_blogs.ipynb
│   │   └── loc_unidentified_photos.ipynb
│   ├── API/
│   │   └── synthetic_archaeology.ipynb   # GPT-4o-mini inhabitant monologues
│   ├── Machine_Learning/
│   │   └── distilgpt2_finetune.ipynb     # light LLM fine-tune on the project corpus
│   └── Visualising_Plotting/
│       └── visualisations.ipynb
│
├── Chapter_2/                  ← Projecting between domains
│   ├── Vectorization/
│   │   ├── text_vectorisation.ipynb      # TF-IDF vs Sentence-BERT
│   │   └── image_vectorisation.ipynb     # HOG vs CLIP
│   └── Clustering/
│       └── kmeans_misclusters.ipynb      # K=20 joint clustering, mis-cluster extraction
│
├── Chapter_3/                  ← Design tool integration
│   ├── AI_Image_Generation/    # DALL-E reference imagery for design language
│   ├── Fragments_to_Clusters/  # cluster-to-fragment metadata
│   ├── Blender/                # Python scripts + .blend files
│   ├── TouchDesigner/          # .toe files + audio
│   └── Renders/                # final video + stills
│
├── data/                       ← scraped + processed (large files go to OneDrive)
│   ├── raw/{reddit,wayback,loc}/
│   ├── processed/
│   └── generated/
│
└── docs/
    └── Bibliography.md
```

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/synthetic-archaeology.git
cd synthetic-archaeology

# 2. Python env (3.10+)
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
pip install -r requirements.txt

# 3. Secrets — never commit your key
cp .env.example .env
# then edit .env and paste your new OpenAI key on the OPENAI_API_KEY= line

# 4. Run the notebooks in order:
#    Chapter_1/Scraping/  →  Chapter_1/API/  →  Chapter_1/Machine_Learning/
#    →  Chapter_1/Visualising_Plotting/  →  Chapter_2/  →  Chapter_3/
```

---

## Workflow (continuous, end-to-end)

```
Reddit grief posts ─┐
Wayback dead blogs ─┼─→ vectorisation (TF-IDF vs SBERT, HOG vs CLIP)
LoC unidentified ──┘            │
                                ▼
                    K-means (K=20) on joint corpus
                                │
                                ▼
            20 mis-clustered cells (cross-domain confusion)
                                │
                                ▼
        GPT-4o-mini synthetic archaeology agent
        (1 fictional inhabitant + monologue per cluster)
                                │
                                ▼
        Blender Python pipeline
        ├─ Workflow A: text→geometric parameters (20 fragments)
        ├─ Workflow B: image→displacement terrain (sediment layer)
        └─ Workflow C: audio→TouchDesigner deformation (breathing core fragment)
                                │
                                ▼
        One impossible domestic interior
                                │
                                ▼
        70-second camera animation: assemble → breathe → dissolve
```

Each arrow is a real dependency: the K-means model literally drives the fragment parameters, the GPT monologues literally name each fragment, the TTS of the original Reddit posts literally drives the TouchDesigner deformation. Nothing is symbolic; everything is connected.

---

## Citations

See [`docs/Bibliography.md`](./docs/Bibliography.md) for datasets, pretrained models, third-party code, and any GPT-generated content.

---

## A note on aesthetics

This project is deliberately **not** a glitch / cyberpunk / sci-fi project. The room is supposed to feel **almost** remembered, **almost** correct, with the wrongness only legible on second viewing. The sadness is structural, not decorative.
