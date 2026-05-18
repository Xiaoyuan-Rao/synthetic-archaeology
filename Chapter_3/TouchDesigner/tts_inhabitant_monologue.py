"""
tts_inhabitant_monologue.py
===========================
Generate the audio that drives Workflow C in TouchDesigner.

We feed one of the GPT-generated *inhabitant monologues* (from Chapter 1.2)
through macOS's built-in `say` command and convert the result to a 16-bit
44.1 kHz WAV file that TouchDesigner's `Audio File In CHOP` reads cleanly.

The result is the project's signal premise made literal: an AI machine
voice, slightly off, reading the words of an inhabitant who never existed,
to an architecture that breathes in response. The wrongness of the voice
is by design — TTS is the audio equivalent of the *almost-right* aesthetic
the inhabitants are written in.

Run on the user's regular Python (NOT inside TouchDesigner):

    python Chapter_3/TouchDesigner/tts_inhabitant_monologue.py

Output: Chapter_3/TouchDesigner/inhabitant_voice.wav
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# -----------------------------------------------------------------------------
# Project root
# -----------------------------------------------------------------------------
def find_project_root(marker="sa_utils.py") -> Path:
    here = Path(__file__).resolve().parent
    for c in [here] + list(here.parents):
        if (c / marker).exists():
            return c
    cowork = Path.home() / "Library/Application Support/Claude/local-agent-mode-sessions"
    if cowork.exists():
        for hit in cowork.rglob(marker):
            return hit.parent
    raise FileNotFoundError("Could not find project root (sa_utils.py).")

PROJECT_ROOT = find_project_root()
MONO_DIR     = PROJECT_ROOT / "data" / "generated" / "synthetic_archaeology" / "monologues"
OUT_DIR      = PROJECT_ROOT / "Chapter_3" / "TouchDesigner"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------------
# Pick a monologue
# -----------------------------------------------------------------------------
def pick_monologue(inhabitant_id: str | None = None) -> tuple[str, Path]:
    """Return (text_after_separator, source_file). Defaults to inhabitant_01."""
    if inhabitant_id is None:
        # match a high-mixing-entropy fragment if the clusterer has run; otherwise the first inhabitant
        candidates = sorted(MONO_DIR.glob("inhabitant_*.txt"))
        if not candidates:
            raise FileNotFoundError(
                f"No monologues in {MONO_DIR}. Run Chapter_1/API/synthetic_archaeology.ipynb first."
            )
        src = candidates[0]
    else:
        src = MONO_DIR / f"{inhabitant_id}.txt"
        if not src.exists():
            raise FileNotFoundError(src)
    raw  = src.read_text(encoding="utf-8")
    # text below the --- separator is the monologue body
    if "---" in raw:
        body = raw.split("---", 1)[1].strip()
    else:
        body = raw
    return body, src


# -----------------------------------------------------------------------------
# Synthesise via macOS `say`
# -----------------------------------------------------------------------------
DEFAULT_VOICE = "Allison"   # quiet female US voice; "Karen" (AU) also works well

def synthesise(text: str, out_wav: Path, voice: str = DEFAULT_VOICE, rate: int = 175) -> None:
    """Use `say` to write an AIFF, then convert to WAV via afconvert (also bundled with macOS)."""
    aiff = out_wav.with_suffix(".aiff")
    cmd_say = [
        "say", "-v", voice, "-r", str(rate),
        "-o", str(aiff),
        "--file-format=AIFF",
        "--data-format=LEI16@22050",
        text,
    ]
    subprocess.run(cmd_say, check=True)
    if shutil.which("afconvert"):
        subprocess.run(
            ["afconvert", "-f", "WAVE", "-d", "LEI16@44100", str(aiff), str(out_wav)],
            check=True,
        )
        aiff.unlink(missing_ok=True)
    else:
        # fall back to writing the AIFF and renaming — TouchDesigner reads both
        aiff.rename(out_wav)
    print(f"  voice synthesised: {out_wav.name} ({out_wav.stat().st_size//1024} KB)")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--inhabitant", default=None, help="e.g. inhabitant_07 (defaults to inhabitant_01)")
    p.add_argument("--voice",      default=DEFAULT_VOICE)
    p.add_argument("--rate",       type=int, default=175, help="words per minute")
    p.add_argument("--out",        default=str(OUT_DIR / "inhabitant_voice.wav"))
    args = p.parse_args()

    text, src_path = pick_monologue(args.inhabitant)
    print(f"[tts] using monologue from {src_path.name}")
    print(f"[tts] {len(text.split())} words; first sentence:\n   {text.split('.')[0][:120]}...\n")

    out = Path(args.out)
    if sys.platform != "darwin":
        print("[tts] WARNING: this script uses macOS `say`. On Windows / Linux replace with edge-tts:")
        print("       pip install edge-tts && edge-tts --voice en-US-JennyNeural --text 'hello' --write-media out.mp3")
        return

    synthesise(text, out, voice=args.voice, rate=args.rate)
    print(f"\n[tts] DONE. Output → {out}")


if __name__ == "__main__":
    main()
