# Bibliography

_To be expanded as the project progresses. Every dataset, pretrained model, third-party code package, and GPT-generated artifact must be listed here._

---

## Datasets (scraped)

- **Reddit** — posts collected from `r/GriefSupport`, `r/lostmedia`, and `r/AbandonedPorn` via the public JSON endpoint (`https://www.reddit.com/r/{subreddit}/top.json`). Accessed _DATE_. Reddit Terms of Use: <https://www.redditinc.com/policies/user-agreement>.
- **Internet Archive — Wayback Machine** — historical snapshots of dead personal blog domains collected through the CDX server API (`https://web.archive.org/cdx/search/cdx`) and the snapshot endpoint. Accessed _DATE_. <https://archive.org/about/terms.php>.
- **Library of Congress — Prints & Photographs Online Catalog** — photographs filtered for "unidentified" or "no date" metadata via the JSON endpoint (`https://www.loc.gov/photos/?fo=json`). Public domain unless otherwise stated. Accessed _DATE_. <https://www.loc.gov/legal/>.
- _(Backup: Wikimedia Commons category `Unidentified subjects` — `https://commons.wikimedia.org/wiki/Category:Unidentified_subjects`. CC-BY-SA where applicable.)_

---

## Generative APIs

- **OpenAI GPT-4o-mini** — used to generate fictional inhabitant monologues from K-means cluster centroids. Custom script `Chapter_1/API/synthetic_archaeology.ipynb`. No content from OpenAI's training data is redistributed; only model completions of project-supplied prompts are stored. <https://platform.openai.com/docs/models/gpt-4o-mini>.

---

## Pretrained models

- **Sentence-BERT — all-MiniLM-L6-v2.** Reimers, N. and Gurevych, I. (2019). _Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks._ Proceedings of EMNLP 2019. <https://arxiv.org/abs/1908.10084>. Weights: <https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2>.
- **CLIP ViT-B-32.** Radford, A. et al. (2021). _Learning Transferable Visual Models From Natural Language Supervision._ Proceedings of ICML 2021. <https://arxiv.org/abs/2103.00020>. Accessed via OpenCLIP: <https://github.com/mlfoundations/open_clip>.
- **DistilGPT2.** Sanh, V. et al. (2019). _DistilBERT, a distilled version of BERT (and the DistilGPT2 derivative)._ <https://arxiv.org/abs/1910.01108>. Weights: <https://huggingface.co/distilgpt2>.

---

## Third-party Python packages

- Hunter, J.D. (2007). _Matplotlib: A 2D Graphics Environment._ <https://matplotlib.org>.
- Waskom, M. (2021). _Seaborn: Statistical Data Visualization._ <https://seaborn.pydata.org>.
- McKinney, W. (2010). _Data Structures for Statistical Computing in Python._ <https://pandas.pydata.org>.
- Harris, C.R. et al. (2020). _Array programming with NumPy._ _Nature_, 585. <https://numpy.org>.
- Pedregosa, F. et al. (2011). _scikit-learn: Machine Learning in Python._ JMLR 12. <https://scikit-learn.org>.
- van der Walt, S. et al. (2014). _scikit-image: image processing in Python._ <https://scikit-image.org> (HOG feature extractor).
- Wolf, T. et al. (2020). _Transformers: State-of-the-Art Natural Language Processing._ <https://github.com/huggingface/transformers>.
- Řehůřek, R. and Sojka, P. (2010). _Software Framework for Topic Modelling with Large Corpora_ (Gensim). <https://radimrehurek.com/gensim/>.
- Richardson, L. (2007). _BeautifulSoup._ <https://www.crummy.com/software/BeautifulSoup/>.

---

## Software

- Blender Foundation (2024). _Blender 4.x_. <https://www.blender.org>.
- Derivative (2024). _TouchDesigner 2025_. <https://derivative.ca>.

---

## Conceptual / theoretical references

- Manovich, L. (2001). _The Language of New Media._ MIT Press.
- Baudrillard, J. (1981). _Simulacra and Simulation._ Translated by Sheila Faria Glaser.
- Parikka, J. (2012). _What is Media Archaeology?_ Polity.
- Bridle, J. (2018). _New Dark Age._ Verso.
- (Dead Internet Theory — popularised online, _2021_.)

---

## Audio sources (TouchDesigner)

- Text-to-speech rendering of Reddit grief posts produced locally via _macOS `say` / Edge TTS_, used only as input audio signal for real-time geometry deformation. No external audio dataset redistributed.
