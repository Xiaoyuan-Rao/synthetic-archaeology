"""
fragments_from_clusters.py
==========================
Blender Python script. Workflow A of Chapter 3.

Reads `Chapter_2/Clustering/Outputs/fragment_drivers.csv` (produced by the K-means
notebook) and generates one rule-based architectural fragment per cluster.
Twenty fragments total — satisfying the assignment's "≥ 20 fragments, generated
by rules, responding to dataset logic" requirement.

The fragment generation is parametric:
  * base primitive       = chosen from {cube, cylinder, prism} by dominant source
  * dimensions           = first 3 scalars of cluster centroid (mapped to scale)
  * vertical subdivision = cluster size  → more docs in a cluster = more layers
  * twist amount         = mixing_entropy → more confusion = more twisted
  * displacement noise   = mixing_entropy × random vertex offsets
  * boolean cuts         = (n_sources - 1) cuts → cross-domain confusion is literal
  * material tint        = blend of source-share colours
  * fragment label       = soul words, attached as custom property
  * grid position        = arranged in a 5 × 4 lattice

How to run
----------
1. Open Blender (4.x).
2. Switch to the *Scripting* workspace tab.
3. In the text editor at the top, click `Open` and pick this file.
4. Click `Run Script` (▶).

What it produces
----------------
* 20 mesh fragments named `frag_01_<cluster>` through `frag_20_<cluster>`.
* A camera and three area lights, sufficient for a viewport-quality render.
* A simple Principled BSDF material per fragment with a tint derived from the cluster.
* Each fragment carries custom properties: `soul_words`, `mixing_entropy`,
  `cluster_id`, `rank`, `source_shares`.

The .blend file should be saved to `Chapter_3/Blender/synthetic_room.blend`
after the script finishes.
"""

from __future__ import annotations

import csv
import math
import os
import random
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector


# -----------------------------------------------------------------------------
# Locate the project root and the fragment-drivers CSV
# -----------------------------------------------------------------------------
def find_project_root(marker: str = "sa_utils.py") -> Path:
    """Walk up from this script's directory and from the user's home looking for the project."""
    here = Path(bpy.data.filepath).resolve().parent if bpy.data.filepath else Path.cwd().resolve()
    for c in [here] + list(here.parents):
        if (c / marker).exists():
            return c
    # fallback: search under the standard Cowork session directory
    cowork = Path.home() / "Library/Application Support/Claude/local-agent-mode-sessions"
    if cowork.exists():
        for hit in cowork.rglob(marker):
            return hit.parent
    raise FileNotFoundError(
        f"Could not find {marker}; either save this .blend file inside the project, "
        "or hard-code PROJECT_ROOT below."
    )


PROJECT_ROOT = find_project_root()
DRIVER_CSV   = PROJECT_ROOT / "Chapter_2" / "Clustering" / "Outputs" / "fragment_drivers.csv"
print(f"[fragments] project root: {PROJECT_ROOT}")
print(f"[fragments] driver CSV:   {DRIVER_CSV}")
if not DRIVER_CSV.exists():
    raise FileNotFoundError(
        f"Cannot find {DRIVER_CSV}. Run Chapter_2/Clustering/kmeans_misclusters.ipynb first."
    )


# -----------------------------------------------------------------------------
# Read the 20 fragment drivers
# -----------------------------------------------------------------------------
def parse_centroid(s: str) -> list[float]:
    """Parse a comma-separated list of signed floats like '+0.1234, -0.5678, ...'."""
    return [float(x.strip()) for x in str(s).split(",") if x.strip()]

fragments = []
with open(DRIVER_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        fragments.append({
            "fragment_id":    row["fragment_id"],
            "rank":           int(row["rank"]),
            "cluster":        int(row["cluster"]),
            "size":           int(row["size"]),
            "entropy":        float(row["mixing_entropy"]),
            "n_sources":      int(row["n_sources"]),
            "shares": {
                "reddit":     float(row["share_reddit"]),
                "wayback":    float(row["share_wayback"]),
                "loc":        float(row["share_loc"]),
                "synthetic":  float(row["share_synthetic"]),
            },
            "soul_words":     row.get("soul_words", ""),
            "centroid":       parse_centroid(row.get("centroid_top10", "")),
        })

print(f"[fragments] loaded {len(fragments)} clusters")
if len(fragments) < 20:
    print(f"[fragments] WARNING: only {len(fragments)} fragments (need ≥20). "
          "Check the K-means K value in the clustering notebook.")


# -----------------------------------------------------------------------------
# Clean scene
# -----------------------------------------------------------------------------
def wipe_scene() -> None:
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for coll in list(bpy.data.collections):
        bpy.data.collections.remove(coll)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)

wipe_scene()
print("[fragments] scene cleaned")


# -----------------------------------------------------------------------------
# Colour helpers — each source has a base colour; per-cluster colour is the
# share-weighted blend, slightly desaturated so the whole scene stays muted.
# -----------------------------------------------------------------------------
SRC_COLOR = {
    "reddit":    (0.80, 0.30, 0.30),
    "wayback":   (0.25, 0.40, 0.65),
    "loc":       (0.55, 0.55, 0.50),
    "synthetic": (0.60, 0.40, 0.65),
}

def blend_color(shares: dict[str, float]) -> tuple[float, float, float]:
    r = g = b = 0.0
    for src, share in shares.items():
        cr, cg, cb = SRC_COLOR[src]
        r += cr * share
        g += cg * share
        b += cb * share
    # desaturate toward grey (matte, almost-remembered)
    mean = (r + g + b) / 3.0
    DESAT = 0.45
    r = r * (1 - DESAT) + mean * DESAT
    g = g * (1 - DESAT) + mean * DESAT
    b = b * (1 - DESAT) + mean * DESAT
    return (r, g, b)


# -----------------------------------------------------------------------------
# Fragment generator
# -----------------------------------------------------------------------------
def make_base_mesh(name: str, source_kind: str, height: float, width: float, depth: float):
    """Create a base mesh primitive depending on the dominant source."""
    me = bpy.data.meshes.new(name + "_mesh")
    bm = bmesh.new()
    if source_kind == "reddit":
        # emotional residue → vertical column (a body, abstracted)
        bmesh.ops.create_cone(
            bm, segments=12, radius1=width*0.4, radius2=width*0.3, depth=height, cap_ends=True,
        )
    elif source_kind == "wayback":
        # dead web → flat slab, like a screen lying down
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(width, depth, height*0.3), verts=bm.verts)
    elif source_kind == "loc":
        # photographic remain → portrait-rectangle prism
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(width*0.7, depth*0.4, height), verts=bm.verts)
    elif source_kind == "synthetic":
        # GPT inhabitant → tall hollow cylinder, the shape of a small room
        bmesh.ops.create_cone(
            bm, segments=8, radius1=width*0.7, radius2=width*0.5, depth=height*1.3, cap_ends=False,
        )
    else:
        bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(me); bm.free()
    return me

def add_subdivision(obj, levels: int):
    mod = obj.modifiers.new("Subdivide", "SUBSURF")
    mod.levels = levels
    mod.render_levels = levels

def add_displace(obj, strength: float, seed: int):
    tex = bpy.data.textures.new(f"disp_{seed}", "NOISE")
    tex.noise_scale = 0.6 + (seed % 5) * 0.1
    mod = obj.modifiers.new("Displace", "DISPLACE")
    mod.texture = tex
    mod.strength = strength
    mod.mid_level = 0.5

def add_twist(obj, angle_deg: float, axis: str = "Z"):
    if abs(angle_deg) < 1.0:
        return
    mod = obj.modifiers.new("Twist", "SIMPLE_DEFORM")
    mod.deform_method = "TWIST"
    mod.deform_axis = axis
    mod.angle = math.radians(angle_deg)

def add_boolean_cut(obj, n_cuts: int, base_size: float):
    """Add `n_cuts` cube boolean differences to introduce subtractive openings."""
    if n_cuts <= 0:
        return
    for i in range(n_cuts):
        bpy.ops.mesh.primitive_cube_add(size=base_size * 0.4)
        cutter = bpy.context.active_object
        cutter.name = f"{obj.name}_cutter_{i}"
        cutter.location = (
            (random.random() - 0.5) * base_size,
            (random.random() - 0.5) * base_size,
            (random.random() - 0.5) * base_size * 1.5,
        )
        cutter.rotation_euler = (
            random.uniform(0, math.pi),
            random.uniform(0, math.pi),
            random.uniform(0, math.pi),
        )
        cutter.hide_render = True
        cutter.hide_viewport = True
        # boolean modifier
        mod = obj.modifiers.new(f"BoolCut_{i}", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.object = cutter
        mod.solver = "FAST"

def make_material(obj, color, entropy: float):
    mat = bpy.data.materials.new(f"mat_{obj.name}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
        # high-entropy fragments are slightly emissive — they 'glow' faintly with their wrongness
        if "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = (color[0]*0.3, color[1]*0.3, color[2]*0.3, 1.0)
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = entropy * 0.4
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.75
    obj.data.materials.append(mat)


def build_fragment(frag: dict, grid_pos: tuple[float, float]):
    name = f"{frag['fragment_id']}_c{frag['cluster']:02d}"
    dom = max(frag["shares"], key=frag["shares"].get)

    # ---- scale comes from first 3 centroid scalars, normalised to a useful range
    cent = frag["centroid"] + [0.0] * 10
    s = [abs(cent[i]) for i in range(3)]
    s = [0.4 + min(s_i * 8.0, 1.6) for s_i in s]      # width, depth, height multipliers ~ [0.4, 2.0]
    width, depth, height = s[0], s[1], s[2] * 1.8

    me = make_base_mesh(name, dom, height, width, depth)
    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)

    # ---- subdivision driven by cluster size (more docs = denser mesh)
    sub_levels = min(3, 1 + int(frag["size"] // 50))
    add_subdivision(obj, sub_levels)

    # ---- twist driven by mixing entropy (more confusion = more twist)
    twist_deg = frag["entropy"] * 80.0
    add_twist(obj, twist_deg, axis="Z")

    # ---- displacement noise also driven by entropy
    disp_strength = 0.05 + frag["entropy"] * 0.18
    add_displace(obj, disp_strength, seed=frag["cluster"])

    # ---- boolean cuts driven by n_sources (cross-domain wounds)
    add_boolean_cut(obj, n_cuts=max(0, frag["n_sources"] - 1), base_size=max(width, depth, height))

    # ---- material
    color = blend_color(frag["shares"])
    make_material(obj, color, frag["entropy"])

    # ---- placement in a 5x4 grid (rank-ordered)
    gx, gy = grid_pos
    obj.location = (gx, gy, 0.0)
    # high-rank (most confused) fragments hover slightly above the ground plane
    obj.location.z = (21 - frag["rank"]) * 0.06

    # ---- custom properties (queryable in the report screenshots / TouchDesigner)
    obj["cluster_id"]     = frag["cluster"]
    obj["rank"]           = frag["rank"]
    obj["mixing_entropy"] = frag["entropy"]
    obj["size"]           = frag["size"]
    obj["n_sources"]      = frag["n_sources"]
    obj["soul_words"]     = frag["soul_words"]
    obj["dominant_source"]= dom
    return obj


# -----------------------------------------------------------------------------
# Build all fragments in a 5 × 4 grid spaced by the largest expected dimension
# -----------------------------------------------------------------------------
COLS, ROWS = 5, 4
SPACING = 5.5
random.seed(7)

for i, frag in enumerate(fragments[:COLS * ROWS]):
    col = i % COLS
    row = i // COLS
    gx = (col - (COLS - 1) / 2) * SPACING
    gy = (row - (ROWS - 1) / 2) * SPACING
    obj = build_fragment(frag, (gx, gy))
    print(f"  built {obj.name}   pos=({gx:+.2f},{gy:+.2f},{obj.location.z:+.2f})   "
          f"entropy={frag['entropy']:.3f}   src={obj['dominant_source']}")


# -----------------------------------------------------------------------------
# Camera + lights
# -----------------------------------------------------------------------------
def setup_camera():
    bpy.ops.object.camera_add(location=(0, -22, 9), rotation=(math.radians(72), 0, 0))
    cam = bpy.context.active_object
    cam.name = "Camera"
    bpy.context.scene.camera = cam
    return cam

def setup_lights():
    # key
    bpy.ops.object.light_add(type="AREA", location=(8, -10, 12))
    key = bpy.context.active_object
    key.data.energy = 800
    key.data.size = 6
    # fill
    bpy.ops.object.light_add(type="AREA", location=(-10, -6, 8))
    fill = bpy.context.active_object
    fill.data.energy = 250
    fill.data.size = 8
    # rim
    bpy.ops.object.light_add(type="AREA", location=(0, 10, 6))
    rim = bpy.context.active_object
    rim.data.energy = 400
    rim.data.size = 5

def setup_world():
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.04, 0.04, 0.05, 1.0)
        bg.inputs["Strength"].default_value = 0.6

setup_camera()
setup_lights()
setup_world()
bpy.context.scene.render.engine = "CYCLES"
bpy.context.scene.cycles.samples = 64
bpy.context.scene.render.resolution_x = 1600
bpy.context.scene.render.resolution_y = 900
bpy.context.scene.render.film_transparent = False

print(f"\n[fragments] DONE. {min(len(fragments), COLS*ROWS)} fragments built. "
      f"Save the .blend to Chapter_3/Blender/synthetic_room.blend.")
