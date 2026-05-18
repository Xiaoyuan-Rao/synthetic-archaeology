"""
prepare_onedrive.py
====================
Build the OneDrive submission folder by copying / linking everything that is
too large for GitHub or that the assignment explicitly wants in OneDrive.

Assignment requirement for OneDrive:
  • Part 1 — all datasets
  • Image / text / sound classification folders
  • Animation output
  • Grasshopper / TouchDesigner / Blender files

Run from the project root:
    python prepare_onedrive.py
    python prepare_onedrive.py --student 25212945      # optional, used to name the top folder
    python prepare_onedrive.py --link                  # use symlinks instead of copies (faster, saves disk)

The script writes everything to ./OneDrive_staging/RC11_<student>_LargeFiles/
which is .gitignored. Once it finishes, you drag that folder into your UCL
OneDrive and right-click → Share → 'Anyone with the link can view'.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

# -----------------------------------------------------------------------------
# Project locations
# -----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_RAW       = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_GENERATED = PROJECT_ROOT / "data" / "generated"
CHAPTER_3      = PROJECT_ROOT / "Chapter_3"
RENDERS        = CHAPTER_3 / "Renders"


def copy_or_link(src: Path, dst: Path, use_link: bool, verbose: bool = True) -> bool:
    """Copy or symlink src into dst. Skips missing sources. Returns True if something was placed."""
    if not src.exists():
        if verbose:
            print(f"  · skip (missing): {src.relative_to(PROJECT_ROOT) if src.is_relative_to(PROJECT_ROOT) else src}")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        if dst.is_symlink() or dst.is_file():
            dst.unlink()
        else:
            shutil.rmtree(dst)
    if use_link and src.is_file():
        # symlinks for individual files; directories are copied below for clarity
        os.symlink(src.resolve(), dst)
        if verbose: print(f"  ↪ link  {src.relative_to(PROJECT_ROOT)}  →  {dst.name}")
    elif src.is_dir():
        # always full-copy directories so OneDrive can sync them
        shutil.copytree(src, dst, dirs_exist_ok=True)
        n = sum(1 for _ in dst.rglob("*") if _.is_file())
        if verbose: print(f"  ⇒ copy  {src.relative_to(PROJECT_ROOT)}/  ({n} files)")
    else:
        shutil.copy2(src, dst)
        kb = dst.stat().st_size // 1024
        if verbose: print(f"  ⇒ copy  {src.relative_to(PROJECT_ROOT)}  ({kb} KB)")
    return True


def build_structure(out_dir: Path, use_link: bool) -> None:
    """
    Final folder layout:

      RC11_<student>_LargeFiles/
        ├── README.txt
        ├── Part_1_Datasets/
        │     ├── Text/
        │     │     ├── reddit/
        │     │     ├── wayback/
        │     │     └── synthetic_inhabitants/
        │     ├── Images/
        │     │     ├── loc_unidentified/
        │     │     └── wayback_thumbnails/
        │     └── Sound/
        │           └── inhabitant_voice.wav
        ├── Chapter_2_Models/
        │     └── (npy / pkl files from data/processed)
        ├── Chapter_3_3D/
        │     ├── Blender/
        │     │     ├── synthetic_room.blend
        │     │     └── breathing_fragment.obj
        │     └── TouchDesigner/
        │           ├── AudioVariations.toe
        │           └── inhabitant_voice.wav
        └── Chapter_3_Renders/
              ├── synthetic_room_70s.mp4
              └── frames/ (optional)
    """
    print(f"\nBuilding OneDrive folder at: {out_dir}\n")
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---------- Part 1 — datasets ----------
    print("Part 1 — Text datasets:")
    text_dir = out_dir / "Part_1_Datasets" / "Text"
    copy_or_link(DATA_RAW / "reddit",  text_dir / "reddit",  use_link=False)
    copy_or_link(DATA_RAW / "wayback", text_dir / "wayback", use_link=False)
    copy_or_link(DATA_GENERATED / "synthetic_archaeology",
                 text_dir / "synthetic_inhabitants", use_link=False)

    print("\nPart 1 — Image datasets:")
    img_dir = out_dir / "Part_1_Datasets" / "Images"
    copy_or_link(DATA_RAW / "loc",       img_dir / "loc_unidentified",  use_link=False)
    copy_or_link(DATA_RAW / "wayback" / "thumbnails", img_dir / "wayback_thumbnails", use_link=False)

    print("\nPart 1 — Sound:")
    sound_dir = out_dir / "Part_1_Datasets" / "Sound"
    sound_dir.mkdir(parents=True, exist_ok=True)
    copy_or_link(CHAPTER_3 / "TouchDesigner" / "inhabitant_voice.wav",
                 sound_dir / "inhabitant_voice.wav", use_link)
    # also any individual monologue audio you generated
    for wav in (CHAPTER_3 / "TouchDesigner").glob("*.wav"):
        if wav.name != "inhabitant_voice.wav":
            copy_or_link(wav, sound_dir / wav.name, use_link)

    # ---------- Chapter 2 — large model artefacts ----------
    print("\nChapter 2 — saved model arrays (npy / pkl):")
    ch2_dir = out_dir / "Chapter_2_Models"
    for f in sorted(DATA_PROCESSED.glob("*")):
        if f.suffix in {".npy", ".pkl", ".npz"}:
            copy_or_link(f, ch2_dir / f.name, use_link)

    # ---------- Chapter 3 — Blender + TouchDesigner ----------
    print("\nChapter 3 — Blender / TouchDesigner project files:")
    ch3_blender = out_dir / "Chapter_3_3D" / "Blender"
    for f in sorted((CHAPTER_3 / "Blender").glob("*")):
        if f.suffix in {".blend", ".blend1", ".obj", ".fbx"} and f.is_file():
            copy_or_link(f, ch3_blender / f.name, use_link)

    ch3_td = out_dir / "Chapter_3_3D" / "TouchDesigner"
    for f in sorted((CHAPTER_3 / "TouchDesigner").glob("*")):
        if f.suffix in {".toe", ".wav", ".mp3", ".aiff"} and f.is_file():
            copy_or_link(f, ch3_td / f.name, use_link)

    # ---------- Chapter 3 — renders ----------
    print("\nChapter 3 — Renders:")
    ch3_renders = out_dir / "Chapter_3_Renders"
    ch3_renders.mkdir(parents=True, exist_ok=True)
    if RENDERS.exists():
        for f in sorted(RENDERS.glob("*")):
            if f.is_file() and f.suffix in {".mp4", ".mov", ".png", ".jpg"}:
                copy_or_link(f, ch3_renders / f.name, use_link)
        # optionally include the PNG frame sequence
        frames = RENDERS / "frames"
        if frames.exists() and frames.is_dir():
            n = sum(1 for _ in frames.iterdir() if _.is_file())
            if n > 0:
                copy_or_link(frames, ch3_renders / "frames", use_link=False)

    # ---------- README in the OneDrive folder ----------
    (out_dir / "README.txt").write_text(
        "Synthetic Archaeology — BARC0053 25/26 Final Assignment\n"
        "Large files referenced by the GitHub repository.\n\n"
        "Folder structure:\n"
        "  Part_1_Datasets/Text/      — scraped CSVs + raw JSON dumps + monologues\n"
        "  Part_1_Datasets/Images/    — LoC unidentified-subject photographs\n"
        "  Part_1_Datasets/Sound/     — TTS inhabitant voice recording(s)\n"
        "  Chapter_2_Models/          — saved embedding matrices (.npy) and vectoriser (.pkl)\n"
        "  Chapter_3_3D/Blender/      — synthetic_room.blend, breathing_fragment.obj\n"
        "  Chapter_3_3D/TouchDesigner/ — AudioVariations.toe + audio source\n"
        "  Chapter_3_Renders/         — synthetic_room_70s.mp4 (the final >1 min animation)\n\n"
        "GitHub repository (source code, notebooks, small CSVs, figures):\n"
        "  https://github.com/<your-username>/synthetic-archaeology\n",
        encoding="utf-8",
    )
    print("\n  ⇒ wrote README.txt at the OneDrive folder root")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--student", default="STUDENT-ID", help="your UCL student number, used to name the top folder")
    p.add_argument("--link", action="store_true", help="symlink files instead of copying (saves disk, but symlinks won't sync into OneDrive)")
    p.add_argument("--out",   default=None, help="override the staging directory location")
    args = p.parse_args()

    staging_root = Path(args.out) if args.out else PROJECT_ROOT / "OneDrive_staging"
    out_dir      = staging_root / f"RC11_{args.student}_LargeFiles"

    if args.link:
        print("⚠  --link mode: files will be symlinked into the staging folder.")
        print("   This is fast and saves disk space, but OneDrive's desktop client")
        print("   will NOT upload through symlinks. Use this only for inspecting the")
        print("   structure; re-run WITHOUT --link before actually uploading.\n")

    build_structure(out_dir, use_link=args.link)

    # Summary
    total = sum(f.stat().st_size for f in out_dir.rglob("*") if f.is_file())
    nfiles = sum(1 for f in out_dir.rglob("*") if f.is_file())
    print(f"\n=== DONE ===")
    print(f"  Staging folder: {out_dir}")
    print(f"  Files: {nfiles}   Size: {total/1024/1024:.1f} MB")
    print()
    print(f"Next step:")
    print(f"  Open Finder, navigate to your UCL OneDrive folder,")
    print(f"  then drag {out_dir.name} into it.")
    print(f"  Right-click → Share → 'Anyone with the link can view'.")
    print(f"  Paste the share URL into the README.md of the GitHub repo.")


if __name__ == "__main__":
    main()
