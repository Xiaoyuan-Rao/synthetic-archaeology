# Chapter 3.3 — TouchDesigner Workflow C (audio-driven deformation)

This is Workflow C of three (Workflow A = text-to-geometry, Workflow B = image-to-displacement, both Blender). TouchDesigner is used here because of one specific capability: deforming a 3D mesh **in real time** based on a streaming signal — in our case, the RMS power of the TTS voice of one of the GPT-generated inhabitants.

The thesis at this step: *the building breathes when the AI speaks.* The geometry trembles in proportion to how loudly the synthetic voice is articulating each word.

## What you build (network topology)

The complete `.toe` file has roughly the structure below. Build it in TouchDesigner 2025 (or any 2023+ build).

```
┌──────────────────────────┐
│ moviefilein1 (Movie File │   load Chapter_3/TouchDesigner/inhabitant_voice.wav
│  In TOP — audio only)    │
└────────────┬─────────────┘
             │  audio
             ▼
┌──────────────────────────┐
│ audiofilein1 (Audio File │   alternative if you prefer Audio File In CHOP directly
│  In CHOP)                │   — outputs raw waveform
└────────────┬─────────────┘
             │  channels
             ▼
┌──────────────────────────┐
│ analyze1 (Analyze CHOP)  │   method = RMS Power
│                          │   smooth = 4 samples
└────────────┬─────────────┘
             │  one-sample RMS
             ▼
┌──────────────────────────┐
│ math1 (Math CHOP)        │   scale = 5.0   pre-add = 0
│                          │   to lift RMS into a useful 0..1 driver range
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ script1 (Script CHOP)    │   ← paste audio_driven_deformation.py
│  language = Python       │     into its Script DAT input
└────────────┬─────────────┘
             │  rms_value
             ▼
┌──────────────────────────┐                    ┌─────────────────────────────────┐
│ geometry1 (Geometry COMP)│ ◄────── reads ───► │ noise1 (Noise SOP) inside it     │
│  imports frag_01.obj     │                    │  amplitude  ← rms × 0.6          │
│  from Blender Workflow A │                    │  period     ← 0.5 + rms × 2      │
│                          │                    │  translate Z ← absTime × 0.2     │
│                          │                    └─────────────────────────────────┘
│                          │                    ┌─────────────────────────────────┐
│                          │ ────────────────► │ twist1 (Twist SOP)               │
│                          │                    │  strength ← rms × 12             │
└────────────┬─────────────┘                    └─────────────────────────────────┘
             │
             ▼
┌──────────────────────────┐
│ render1 (Render TOP)     │   simple lighting via lightcomp1 + cameracomp1
│  → moviefileout1         │   record a 70 s pass to disk for the final animation
└──────────────────────────┘
```

## Step-by-step setup

1. **Generate the audio.** From a terminal in the project root:
   ```bash
   python Chapter_3/TouchDesigner/tts_inhabitant_monologue.py --inhabitant inhabitant_07
   ```
   This produces `Chapter_3/TouchDesigner/inhabitant_voice.wav` (~60–90 seconds, depending on the monologue length).

2. **Export the breathing fragment from Blender.** Open `synthetic_room.blend`, pick any high-rank fragment (e.g. `frag_01_c<…>`), then `File → Export → Wavefront (.obj)` to `Chapter_3/TouchDesigner/breathing_fragment.obj`. Apply all modifiers before export so the OBJ is a frozen mesh.

3. **Create the TouchDesigner network.**
   - New project, save as `Chapter_3/TouchDesigner/AudioVariations.toe`.
   - Drop an *Audio File In CHOP* → point it at `inhabitant_voice.wav`. Enable *Play*.
   - Drop an *Analyze CHOP* → method = `RMS Power`, scope = whole window.
   - Drop a *Math CHOP* after Analyze → multiply = `5` so RMS lands in roughly the 0–1 range.
   - Drop a *Script CHOP*, set language = Python, and paste the contents of `audio_driven_deformation.py` (next file) into its Callbacks DAT.
   - Drop a *Geometry COMP*. Inside it: *File In SOP* pointing at `breathing_fragment.obj` → *Noise SOP* → *Twist SOP* → *Out SOP*.
   - Wire the Script CHOP's output channel `rms_value` into the Noise/Twist parameters via the script (see file below) or via expressions: e.g. on the Noise SOP, set *Amplitude* to `op('script1')[0] * 0.6`.
   - Drop a *Camera COMP*, a *Light COMP*, a *Render TOP*. Connect Geometry + Camera + Light into the Render TOP.

4. **Capture.** Right-click the Render TOP → *Save Movie* → set duration ≥ 70 s, resolution 1280×720 at 30 fps. This becomes the per-fragment animation footage that Workflow A's scene assembly will composite as the central "breathing fragment" in the final 60-second camera fly-through.

## What to write in the report about why TouchDesigner

> TouchDesigner is used in this workflow because its CHOP/SOP signal-flow architecture is purpose-built for translating a time-varying signal into time-varying geometry. A Blender equivalent of this would require either driver expressions or a Python frame-handler — both possible but neither nearly as legible. The decision to do real-time audio deformation in TouchDesigner is therefore a tool-fit decision: TouchDesigner is the right software for the part of the pipeline where signal *is* form.
>
> The audio source is itself important. The voice is not a human recording. It is an off-the-shelf macOS TTS voice reading a GPT-generated text written in the voice of a person who never existed. Three layers of machine speech are stacked: the LLM that imagined the inhabitant, the TTS engine that gave her a voice, and the TouchDesigner network that lets the geometry feel the voice. This stack *is* the thesis — *AI rebuilds humans from debris and the architecture trembles in response.*
