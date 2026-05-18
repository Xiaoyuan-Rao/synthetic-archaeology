"""
sediment_from_images.py
=======================
Blender Python script. Workflow B of Chapter 3.

Converts a curated selection of Library of Congress "unidentified subject"
photographs into a layered terrain of displacement-driven tiles that sits
beneath the 20 cluster-fragments built by Workflow A. The grayscale of each
photograph drives the vertical relief of one tile, turning the photograph's
*structural geometry* (faces, buildings, landscapes) into literal architectural
relief.

Why this matters for the project
--------------------------------
Workflow A turned *text* into geometry. Workflow B turns *image* into geometry.
Together they satisfy the assignment's requirement that three different
3-D-conversion workflows be developed (Workflow C does audio in TouchDesigner).
Conceptually, the sediment layer is the project's archaeological stratum made
spatial: the surface beneath the synthetic room is paved with the unreadable
relief of forgotten faces.

How to run
----------
After running `fragments_from_clusters.py`, open this file in Blender's text
editor and click Run. It will add a sediment layer below the existing scene
(does *not* wipe the scene).
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import bpy
import bmesh


# -----------------------------------------------------------------------------
# Locate project + images
# -----------------------------------------------------------------------------
def find_project_root(marker: str = "sa_utils.py") -> Path:
    here = Path(bpy.data.filepath).resolve().parent if bpy.data.filepath else Path.cwd().resolve()
    for c in [here] + list(here.parents):
        if (c / marker).exists():
            return c
    cowork = Path.home() / "Library/Application Support/Claude/local-agent-mode-sessions"
    if cowork.exists():
        for hit in cowork.rglob(marker):
            return hit.parent
    raise FileNotFoundError("Could not find sa_utils.py; save the .blend inside the project.")

PROJECT_ROOT = find_project_root()
IMG_DIR      = PROJECT_ROOT / "data" / "raw" / "loc" / "images"
print(f"[sediment] project root: {PROJECT_ROOT}")
print(f"[sediment] image dir:    {IMG_DIR}")

if not IMG_DIR.exists():
    raise FileNotFoundError(f"Cannot find {IMG_DIR}. Run Chapter_1/Scraping/loc_unidentified_photos.ipynb first.")


# -----------------------------------------------------------------------------
# Curate a selection — deterministic but spread across the catalogue
# -----------------------------------------------------------------------------
def curate_images(img_dir: Path, n: int = 12, seed: int = 17) -> list[Path]:
    all_imgs = sorted(img_dir.glob("*.jpg")) + sorted(img_dir.glob("*.png"))
    if len(all_imgs) <= n:
        return all_imgs
    rng = random.Random(seed)
    # take an evenly-spaced sample, then jitter
    step = len(all_imgs) / n
    picks = []
    for i in range(n):
        idx = int(i * step + rng.uniform(0, step * 0.6))
        idx = min(idx, len(all_imgs) - 1)
        picks.append(all_imgs[idx])
    # de-duplicate while preserving order
    seen, unique = set(), []
    for p in picks:
        if p not in seen:
            seen.add(p); unique.append(p)
    return unique

N_TILES = 12
COLS    = 4
ROWS    = 3
TILE_W  = 4.5      # ground footprint of one tile
TILE_D  = 4.5
TILE_H  = 0.8      # max vertical relief
GROUND_Z = -3.0    # tiles sit this far below the fragments

tiles = curate_images(IMG_DIR, n=N_TILES)
print(f"[sediment] selected {len(tiles)} LoC images for the sediment layer")
for t in tiles:
    print(f"   {t.name}")


# -----------------------------------------------------------------------------
# Make one displacement tile per image
# -----------------------------------------------------------------------------
def make_tile_mesh(name: str, subdiv: int = 64, width: float = TILE_W, depth: float = TILE_D):
    me = bpy.data.meshes.new(name + "_mesh")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=subdiv, y_segments=subdiv, size=1.0)
    bmesh.ops.scale(bm, vec=(width * 0.5, depth * 0.5, 1.0), verts=bm.verts)
    bm.to_mesh(me); bm.free()
    return me

def load_image_texture(image_path: Path, tex_name: str):
    img = bpy.data.images.load(str(image_path), check_existing=True)
    tex = bpy.data.textures.new(tex_name, "IMAGE")
    tex.image = img
    # smoothing helps mid-grey land near zero instead of producing a jagged surface
    tex.use_interpolation = True
    tex.filter_type = "EWA"
    return tex, img

def make_tile_material(obj, image, brightness: float = 0.6):
    mat = bpy.data.materials.new(f"mat_{obj.name}")
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    output = nt.nodes.get("Material Output")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (-200, 0)
    tex_img = nt.nodes.new("ShaderNodeTexImage")
    tex_img.image = image
    tex_img.location = (-500, 0)
    bright = nt.nodes.new("ShaderNodeBrightContrast")
    bright.inputs["Bright"].default_value = -0.25
    bright.inputs["Contrast"].default_value = -0.2
    bright.location = (-300, 200)
    nt.links.new(tex_img.outputs["Color"], bright.inputs["Color"])
    nt.links.new(bright.outputs["Color"],  bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.85
    nt.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    obj.data.materials.append(mat)

def build_tile(image_path: Path, grid_pos: tuple[float, float], index: int):
    name = f"sediment_{index:02d}_{image_path.stem[:24]}"
    me = make_tile_mesh(name)
    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)
    obj.location = (grid_pos[0], grid_pos[1], GROUND_Z)
    obj.rotation_euler = (0, 0, random.uniform(-0.15, 0.15))   # slight skew, like loose paving

    tex, img = load_image_texture(image_path, f"disp_{name}")
    # displacement modifier reads the texture
    mod = obj.modifiers.new("ImageDisplace", "DISPLACE")
    mod.texture = tex
    mod.texture_coords = "UV"
    mod.mid_level = 0.5
    mod.strength = TILE_H
    # smooth shading + a tiny subdivision surface for cleaner relief
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()
    obj.select_set(False)

    make_tile_material(obj, img)

    # mark with custom properties so the scene-assembly script can iterate
    obj["loc_image"]    = image_path.name
    obj["sediment_idx"] = index
    return obj


random.seed(11)
SPACING_X = TILE_W * 1.05
SPACING_Y = TILE_D * 1.05
for i, img_path in enumerate(tiles[:COLS * ROWS]):
    col = i % COLS
    row = i // COLS
    gx = (col - (COLS - 1) / 2) * SPACING_X
    gy = (row - (ROWS - 1) / 2) * SPACING_Y
    obj = build_tile(img_path, (gx, gy), i + 1)
    print(f"   built {obj.name}  at ({gx:+.2f}, {gy:+.2f}, {GROUND_Z:.2f})")

print(f"\n[sediment] DONE. {min(len(tiles), COLS*ROWS)} tiles placed at z={GROUND_Z}.")
print("Re-render with the existing camera; tiles are now the floor under the fragments.")
