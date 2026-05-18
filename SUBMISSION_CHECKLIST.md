# Submission Checklist
### BARC0053 — DfPI Digital Skills 25/26

Tick items as you complete them.

---

## A. Pre-flight

- [ ] OpenAI key you pasted in chat is **revoked** at https://platform.openai.com/api-keys.
- [ ] New key sits in `.env` (only there — never anywhere else).
- [ ] `.gitignore` has `.env` on its first lines (already done in this project).

---

## B. Run order — produce all artifacts

Run notebooks **in this order** with a fresh kernel each time, so outputs land in the committed `.ipynb` files:

1. `Chapter_1/Scraping/reddit_grief.ipynb`
2. `Chapter_1/Scraping/wayback_dead_blogs.ipynb`
3. `Chapter_1/Scraping/loc_unidentified_photos.ipynb`
4. `Chapter_1/API/synthetic_archaeology.ipynb`
5. `Chapter_2/Vectorization/text_vectorisation.ipynb`
6. `Chapter_2/Vectorization/image_vectorisation.ipynb`
7. `Chapter_2/Clustering/kmeans_misclusters.ipynb`
8. `Chapter_1/Visualising_Plotting/visualisations.ipynb` ← can run any time after 7

Then in Blender:

9. `Chapter_3/Blender/fragments_from_clusters.py` (Run Script)
10. `Chapter_3/Blender/sediment_from_images.py`
11. `Chapter_3/Blender/scene_animation.py`
12. **Save** the .blend as `Chapter_3/Blender/synthetic_room.blend`
13. **Render** the 70-second animation (Eevee for speed, Cycles for quality)
14. Encode the frames to MP4:
    ```bash
    ffmpeg -framerate 30 -i Chapter_3/Renders/frames/%04d.png \
           -c:v libx264 -pix_fmt yuv420p \
           Chapter_3/Renders/synthetic_room_70s.mp4
    ```

Then for TouchDesigner:

15. From a regular terminal in the outputs folder:
    ```bash
    python Chapter_3/TouchDesigner/tts_inhabitant_monologue.py --inhabitant inhabitant_07
    ```
16. Build the TouchDesigner network per `Chapter_3/TouchDesigner/TOUCHDESIGNER_SETUP.md`.
17. Save the `.toe` file as `Chapter_3/TouchDesigner/AudioVariations.toe`.
18. (Optional) Record a 70s pass from the Render TOP for the report.

---

## C. GitHub repository — `bash setup_repo.sh`

There's a helper script at the project root. From a terminal in the outputs folder:

```bash
bash setup_repo.sh
```

This script:
1. Wipes any half-finished previous `.git/`.
2. **Security check 1** — confirms `.env` is in `.gitignore`.
3. **Security check 2** — greps every file about to be committed for the string `sk-proj`. **Aborts if any leak is found.**
4. Runs `git init`, configures your git identity (interactive if not already set), makes the first commit, prints the commit size.
5. If you have GitHub CLI (`gh`) installed: auto-creates the **public** repo and pushes.
6. If you don't: prints the three manual commands to run.

Custom invocation:

```bash
bash setup_repo.sh                        # default repo name = synthetic-archaeology
bash setup_repo.sh my-repo-name           # custom name
```

### Fully manual fallback

```bash
cd <outputs folder>
rm -rf .git
git init && git branch -M main
git config user.email "you@example.com" && git config user.name "Your Name"
git add .
git commit -m "Initial commit — Synthetic Archaeology"

# Go to https://github.com/new, create PUBLIC repo, copy the URL, then:
git remote add origin https://github.com/<your-username>/synthetic-archaeology.git
git push -u origin main
```

### After pushing — verify in browser

- [ ] `.env` is **NOT** in the repo (only `.env.example`).
- [ ] All `.ipynb` files open in GitHub's viewer with cell outputs visible.
- [ ] `Chapter_3/Renders/`, `*.blend`, etc. are not bloating the repo.
- [ ] Repo visibility = Public.

---

## D. OneDrive — `python prepare_onedrive.py`

There's a helper script that **automatically assembles the OneDrive folder** with exactly the structure the assignment requires (Part 1 datasets, image/text/sound classification, animation output, Blender/TD files). From the outputs folder:

```bash
python prepare_onedrive.py --student 25212945
```

(replace `25212945` with your real UCL student number)

This produces `OneDrive_staging/RC11_25212945_LargeFiles/` with:

```
RC11_25212945_LargeFiles/
├── README.txt
├── Part_1_Datasets/
│   ├── Text/        (reddit/, wayback/, synthetic_inhabitants/)
│   ├── Images/      (loc_unidentified/, wayback_thumbnails/)
│   └── Sound/       (inhabitant_voice.wav)
├── Chapter_2_Models/    (npy / pkl / npz)
├── Chapter_3_3D/
│   ├── Blender/         (synthetic_room.blend + breathing_fragment.obj)
│   └── TouchDesigner/   (AudioVariations.toe + audio source)
└── Chapter_3_Renders/   (synthetic_room_70s.mp4)
```

Then:

1. Open Finder, navigate to your UCL OneDrive folder.
2. Drag `OneDrive_staging/RC11_<student>_LargeFiles/` into it.
3. Wait for OneDrive to finish syncing (depends on render size — ~5 min for typical).
4. Right-click the uploaded folder → *Share* → **Anyone with the link can view**.
5. Copy the share URL and paste it into `README.md` of the GitHub repo (replace the `_to be added after upload_` line at the top), then `git commit -am "Add OneDrive link" && git push`.

---

## E. PDF report

Convert `docs/FINAL_REPORT.md` to PDF. Three options:

- **Pandoc:** `pandoc docs/FINAL_REPORT.md -o docs/RC11_<student>_REPORT.pdf --pdf-engine=xelatex`
- **Marked 2** (macOS app): open `docs/FINAL_REPORT.md`, then File → Export → PDF.
- **Word**: paste the Markdown into a fresh Word doc, format headings, export as PDF.

Before exporting, edit the top of `docs/FINAL_REPORT.md`:
- Fill in your student number on the second-to-last line of the header.
- Fill in your GitHub URL.
- Fill in your OneDrive share URL.

The PDF goes on Moodle (the submission portal). Keep a copy in `docs/`.

---

## F. Final rubric cross-check

| Requirement | Where it is met | ✓ |
|---|---|---|
| ≥ 2 websites, ≥ 3 datasets, 200–300 each | Reddit + Wayback + LoC | [ ] |
| Vectorisation ≥ 2 methods w/ experimental discussion | TF-IDF vs SBERT + HOG vs CLIP | [ ] |
| API interaction with own script | `Chapter_1/API/synthetic_archaeology.ipynb` | [ ] |
| Machine learning model | K-means K=20 + LLM agent | [ ] |
| Matplotlib / Seaborn visualisations | 8 figures + 4 embedded | [ ] |
| 3 different 3D conversion workflows | Blender A, Blender B, TouchDesigner C | [ ] |
| ≥ 20 rule-generated fragments | `fragments_from_clusters.py` builds exactly 20 | [ ] |
| ≥ 2 software with explained roles | Blender + TouchDesigner | [ ] |
| ≥ 1 min camera animation | 70 seconds at 30 fps | [ ] |
| Public GitHub repo w/ notebooks containing outputs | `setup_repo.sh` does this | [ ] |
| OneDrive folder with datasets / image / text / sound / animation / Grasshopper-TouchDesigner-Blender files | `prepare_onedrive.py` builds the exact structure | [ ] |
| Citations for data / models / GPT / 3rd-party code | `docs/Bibliography.md` | [ ] |
