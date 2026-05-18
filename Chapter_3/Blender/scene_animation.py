"""
scene_animation.py
==================
Blender Python script. Final step of Chapter 3.

Assumes the scene already contains:
  * 20 cluster fragments (from fragments_from_clusters.py)
  * ~12 sediment displacement tiles (from sediment_from_images.py)

This script then:
  1. Picks the rank-1 fragment (highest mixing entropy) as the *breathing
     centerpiece* and tags it (so a TD-rendered video can later be projected
     on a plane beside it during compositing).
  2. Builds a Bezier camera path that flies through the scene over 70 seconds
     at 30 fps (= 2100 frames). The path has four narrative beats:
         a) approach from the dark (0–15 s)
         b) orbit the fragment field (15–35 s)
         c) close on the rank-1 fragment, pause (35–50 s)
         d) pull back, rise, fade to wide shot (50–70 s)
  3. Animates a subtle scale 'breath' on every fragment so the whole field
     pulses gently in the absence of the TouchDesigner audio (the audio
     deformation runs on the centerpiece in TD; the script's pulse is the
     stand-in for the rest of the room).
  4. Configures render output: 70 s × 30 fps × 1600×900 at 64 Cycles samples,
     saved to Chapter_3/Renders/frames/####.png and a final
     synthetic_room_70s.mp4.

The output animation satisfies the assignment's *>1 minute camera animation*
requirement.

Run after the other two Blender scripts.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

import bpy
from mathutils import Vector


# -----------------------------------------------------------------------------
# Project paths
# -----------------------------------------------------------------------------
def find_project_root(marker="sa_utils.py") -> Path:
    here = Path(bpy.data.filepath).resolve().parent if bpy.data.filepath else Path.cwd().resolve()
    for c in [here] + list(here.parents):
        if (c / marker).exists():
            return c
    cowork = Path.home() / "Library/Application Support/Claude/local-agent-mode-sessions"
    if cowork.exists():
        for hit in cowork.rglob(marker):
            return hit.parent
    raise FileNotFoundError("Could not find sa_utils.py")

PROJECT_ROOT = find_project_root()
RENDER_DIR   = PROJECT_ROOT / "Chapter_3" / "Renders"
FRAMES_DIR   = RENDER_DIR / "frames"
FRAMES_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------------
# Find the fragment objects
# -----------------------------------------------------------------------------
fragments = [o for o in bpy.data.objects if o.name.startswith("frag_") and "_cutter_" not in o.name]
sediments = [o for o in bpy.data.objects if o.name.startswith("sediment_")]
print(f"[anim] fragments found: {len(fragments)}")
print(f"[anim] sediment tiles : {len(sediments)}")
if not fragments:
    raise RuntimeError("No fragments in the scene. Run fragments_from_clusters.py first.")

# Sort by rank custom property; rank 1 = the centerpiece
fragments_sorted = sorted(fragments, key=lambda o: o.get("rank", 999))
center = fragments_sorted[0]
center["IS_BREATHING_CENTER"] = True
print(f"[anim] breathing centerpiece: {center.name}   (entropy={center.get('mixing_entropy', '?')})")


# -----------------------------------------------------------------------------
# Frame / fps configuration
# -----------------------------------------------------------------------------
FPS               = 30
DUR_SECONDS       = 70
SCENE             = bpy.context.scene
SCENE.render.fps  = FPS
SCENE.frame_start = 1
SCENE.frame_end   = FPS * DUR_SECONDS    # 2100 frames

# narrative beats in seconds
BEAT_APPROACH = 15
BEAT_ORBIT    = 35
BEAT_PAUSE    = 50
BEAT_RETREAT  = 70


# -----------------------------------------------------------------------------
# Camera path — keyframed location + target empty
# -----------------------------------------------------------------------------
# remove any existing camera animation
cam = SCENE.camera
if cam is None:
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    SCENE.camera = cam
cam.animation_data_clear()

# create / find a 'CamTarget' empty that the camera always looks at
target = bpy.data.objects.get("CamTarget")
if target is None:
    bpy.ops.object.empty_add(type="PLAIN_AXES")
    target = bpy.context.active_object
    target.name = "CamTarget"
target.animation_data_clear()

# add (or refresh) the Track To constraint
for c in list(cam.constraints):
    cam.constraints.remove(c)
trk = cam.constraints.new("TRACK_TO")
trk.target = target
trk.track_axis = "TRACK_NEGATIVE_Z"
trk.up_axis = "UP_Y"


def kf_loc(obj, frame: int, location: tuple[float, float, float], interpolation: str = "BEZIER"):
    obj.location = location
    obj.keyframe_insert(data_path="location", frame=frame)
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                if kp.co.x == frame:
                    kp.interpolation = interpolation


# Camera keyframes — four beats
# (units: blender units; the fragment grid spans ~25u × 20u centred at origin)
center_pos = center.location
kf_loc(cam,    1,                   ( 0.0, -40.0,  6.0), "BEZIER")   # far, low, dark
kf_loc(target, 1,                   ( 0.0,   0.0,  2.0))
kf_loc(cam,    FPS * BEAT_APPROACH, (-8.0, -20.0,  8.0))
kf_loc(target, FPS * BEAT_APPROACH, ( 0.0,   0.0,  3.0))
kf_loc(cam,    FPS * BEAT_ORBIT,    (15.0,  -8.0,  6.0))             # orbit pass 1
kf_loc(target, FPS * BEAT_ORBIT,    ( center_pos.x, center_pos.y, center_pos.z))
kf_loc(cam,    FPS * BEAT_PAUSE,    (center_pos.x + 5.0,
                                     center_pos.y - 4.0,
                                     center_pos.z + 2.5))            # close on centerpiece
kf_loc(target, FPS * BEAT_PAUSE,    (center_pos.x, center_pos.y, center_pos.z))
kf_loc(cam,    FPS * BEAT_RETREAT,  ( 0.0, -28.0, 14.0))              # retreat + rise
kf_loc(target, FPS * BEAT_RETREAT,  ( 0.0,   0.0,  2.0))

# Camera lens — short on approach, normal on orbit, medium-tele on close-up, then wide pull
cam.data.animation_data_clear()
def kf_lens(frame, mm):
    cam.data.lens = mm
    cam.data.keyframe_insert(data_path="lens", frame=frame)
kf_lens(1,                   35)
kf_lens(FPS * BEAT_APPROACH, 35)
kf_lens(FPS * BEAT_ORBIT,    50)
kf_lens(FPS * BEAT_PAUSE,    85)
kf_lens(FPS * BEAT_RETREAT,  24)


# -----------------------------------------------------------------------------
# Per-fragment 'breath' — subtle scale pulse for all fragments
# -----------------------------------------------------------------------------
PULSE_HZ      = 0.4
PULSE_DEPTH   = 0.04
rng = random.Random(11)

for f in fragments:
    # only animate non-centerpiece fragments here; centerpiece is animated by TD pass
    if f.get("IS_BREATHING_CENTER"):
        continue
    base = Vector(f.scale)
    phase = rng.uniform(0, math.tau)
    f.animation_data_clear()
    for sec in range(0, DUR_SECONDS + 1):
        frame = max(1, sec * FPS)
        pulse = 1.0 + PULSE_DEPTH * math.sin(2 * math.pi * PULSE_HZ * sec + phase)
        f.scale = (base.x * pulse, base.y * pulse, base.z * pulse)
        f.keyframe_insert(data_path="scale", frame=frame)


# -----------------------------------------------------------------------------
# Render configuration
# -----------------------------------------------------------------------------
SCENE.render.engine = "CYCLES"
SCENE.cycles.samples = 64
SCENE.cycles.use_denoising = True
SCENE.render.resolution_x = 1600
SCENE.render.resolution_y = 900
SCENE.render.resolution_percentage = 100
SCENE.render.film_transparent = False
SCENE.render.image_settings.file_format = "PNG"
SCENE.render.filepath = str(FRAMES_DIR) + "/"

print(f"\n[anim] frame range:   {SCENE.frame_start} → {SCENE.frame_end}  ({DUR_SECONDS}s at {FPS} fps)")
print(f"[anim] frames out:    {FRAMES_DIR}")
print(f"[anim] resolution:    {SCENE.render.resolution_x}×{SCENE.render.resolution_y}")
print(f"[anim] samples:       {SCENE.cycles.samples}")
print()
print("[anim] DONE. To render:")
print("   * Test quickly with Eevee: change Render Properties → Render Engine to 'Eevee'.")
print("   * For final, keep Cycles and run Render → Render Animation (or run from CLI:)")
print(f"     blender -b synthetic_room.blend -s 1 -e {SCENE.frame_end} -a")
print()
print("Then encode the PNGs into an MP4 with ffmpeg:")
print(f"   ffmpeg -framerate {FPS} -i Chapter_3/Renders/frames/%04d.png -c:v libx264 -pix_fmt yuv420p Chapter_3/Renders/synthetic_room_70s.mp4")
