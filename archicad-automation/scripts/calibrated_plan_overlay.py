#!/usr/bin/env python3
"""Create a calibrated source-vs-publish floor-plan overlay.

Reusable full-plan comparison pattern for measured-plan verification runs. It assumes
you already know the source full-page crop box and a last-known published fallback box
for the same physical outer contour.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def parse_box(values: list[int]) -> tuple[int, int, int, int]:
    if len(values) != 4:
        raise argparse.ArgumentTypeError("box needs 4 integers: x0 y0 x1 y1")
    x0, y0, x1, y1 = map(int, values)
    if x1 <= x0 or y1 <= y0:
        raise argparse.ArgumentTypeError("box must satisfy x1>x0 and y1>y0")
    return x0, y0, x1, y1


def binary_mask(rgb: np.ndarray, thresh: int = 225) -> np.ndarray:
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    _, inv = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY_INV)
    inv = cv2.morphologyEx(inv, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    return inv


def structural_mask(rgb: np.ndarray, thresh: int = 225, kernel_len: int = 24) -> np.ndarray:
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    _, inv = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY_INV)
    inv = cv2.morphologyEx(inv, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    h = cv2.morphologyEx(inv, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len, 2)))
    v = cv2.morphologyEx(inv, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (2, kernel_len)))
    mask = cv2.bitwise_or(h, v)
    mask = cv2.dilate(mask, np.ones((2, 2), np.uint8), iterations=1)
    return mask


def detect_published_outer_box(rgb: np.ndarray, fallback: tuple[int, int, int, int], min_fraction: float) -> tuple[int, int, int, int]:
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    _, inv = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY_INV)
    h, w = inv.shape

    hk = cv2.getStructuringElement(cv2.MORPH_RECT, (max(80, w // 12), 3))
    vk = cv2.getStructuringElement(cv2.MORPH_RECT, (3, max(80, h // 6)))
    horiz = cv2.morphologyEx(inv, cv2.MORPH_OPEN, hk)
    vert = cv2.morphologyEx(inv, cv2.MORPH_OPEN, vk)

    def collect(mask: np.ndarray, orientation: str) -> list[tuple[int, int, int, int, int, int]]:
        n, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
        items = []
        for i in range(1, n):
            x, y, ww, hh, _ = map(int, stats[i])
            length = ww if orientation == 'h' else hh
            thickness = hh if orientation == 'h' else ww
            items.append((x, y, x + ww, y + hh, length, thickness))
        return items

    h_items = [it for it in collect(horiz, 'h') if it[4] >= w * 0.12 and it[5] >= 3]
    v_items = [it for it in collect(vert, 'v') if it[4] >= h * 0.12 and it[5] >= 3]
    if not h_items or not v_items:
        return fallback

    detected = (
        min(it[0] for it in v_items),
        min(it[1] for it in h_items),
        max(it[2] for it in v_items),
        max(it[3] for it in h_items),
    )

    fallback_w = fallback[2] - fallback[0]
    fallback_h = fallback[3] - fallback[1]
    if (detected[2] - detected[0]) < fallback_w * min_fraction or (detected[3] - detected[1]) < fallback_h * min_fraction:
        return fallback
    return detected


def draw_diff_canvas(base: np.ndarray, common: np.ndarray, source_only: np.ndarray, publish_only: np.ndarray, alpha: float | None) -> np.ndarray:
    canvas = np.full_like(base, 255)
    canvas[common] = (70, 70, 70)
    canvas[source_only] = (220, 30, 30)
    canvas[publish_only] = (0, 190, 220)
    if alpha is None:
        result = canvas
    else:
        a = np.zeros((common.shape[0], common.shape[1], 1), dtype=np.float32)
        a[common | source_only | publish_only] = alpha
        result = (base * (1 - a) + canvas * a).astype(np.uint8)
    origin = (0, common.shape[0] - 1)
    cv2.circle(result, origin, 12, (255, 140, 0), 3)
    cv2.line(result, (origin[0], max(0, origin[1] - 26)), (origin[0], origin[1]), (255, 140, 0), 2)
    cv2.line(result, (origin[0], origin[1]), (min(result.shape[1] - 1, origin[0] + 26), origin[1]), (255, 140, 0), 2)
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', required=True, help='Full source page image')
    ap.add_argument('--published', required=True, help='Published/exported plan image or content crop')
    ap.add_argument('--source-box', nargs=4, type=int, required=True, metavar=('X0', 'Y0', 'X1', 'Y1'))
    ap.add_argument('--published-box-fallback', nargs=4, type=int, required=True, metavar=('X0', 'Y0', 'X1', 'Y1'))
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--min-fallback-fraction', type=float, default=0.90, help='Minimum detected width/height fraction vs fallback before accepting auto-detection')
    args = ap.parse_args()

    source_box = parse_box(args.source_box)
    fallback_box = parse_box(args.published_box_fallback)

    source_path = Path(args.source)
    published_path = Path(args.published)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    src_img = Image.open(source_path).convert('RGB')
    pub_img = Image.open(published_path).convert('RGB')
    pub_np_full = np.array(pub_img)
    published_box = detect_published_outer_box(pub_np_full, fallback_box, args.min_fallback_fraction)

    src_crop = src_img.crop(source_box)
    pub_crop = pub_img.crop(published_box)
    common_size = pub_crop.size
    src_reg = src_crop.resize(common_size, Image.Resampling.LANCZOS)
    pub_reg = pub_crop.copy()

    src_np = np.array(src_reg)
    pub_np = np.array(pub_reg)
    src_raw = binary_mask(src_np)
    pub_raw = binary_mask(pub_np)
    src_struct = structural_mask(src_np)
    pub_struct = structural_mask(pub_np)

    raw_common = (src_raw > 0) & (pub_raw > 0)
    raw_source_only = (src_raw > 0) & ~(pub_raw > 0)
    raw_publish_only = (pub_raw > 0) & ~(src_raw > 0)
    struct_common = (src_struct > 0) & (pub_struct > 0)
    struct_source_only = (src_struct > 0) & ~(pub_struct > 0)
    struct_publish_only = (pub_struct > 0) & ~(src_struct > 0)

    src_crop.save(out_dir / 'source-plan-crop-raw.png')
    pub_crop.save(out_dir / 'published-plan-crop-raw.png')
    src_reg.save(out_dir / 'source-plan-registered.png')
    pub_reg.save(out_dir / 'published-plan-registered.png')
    Image.fromarray(src_raw).save(out_dir / 'source-raw-mask.png')
    Image.fromarray(pub_raw).save(out_dir / 'published-raw-mask.png')
    Image.fromarray(src_struct).save(out_dir / 'source-structural-mask.png')
    Image.fromarray(pub_struct).save(out_dir / 'published-structural-mask.png')

    raw_overlay = draw_diff_canvas(src_np, raw_common, raw_source_only, raw_publish_only, alpha=None)
    diff_map = draw_diff_canvas(src_np, struct_common, struct_source_only, struct_publish_only, alpha=None)
    diff_overlay = draw_diff_canvas(src_np, struct_common, struct_source_only, struct_publish_only, alpha=0.88)
    Image.fromarray(raw_overlay).save(out_dir / 'raw-registered-overlay.png')
    Image.fromarray(diff_map).save(out_dir / 'structural-difference-map.png')
    Image.fromarray(diff_overlay).save(out_dir / 'structural-difference-overlay.png')

    summary = {
        'source_full_page': str(source_path),
        'published_crop': str(published_path),
        'source_box_px': list(source_box),
        'published_box_px': list(published_box),
        'published_box_fallback_px': list(fallback_box),
        'common_registered_size_px': list(common_size),
        'basis': 'Both drawings were cropped to the same physical outer contour, then registered to the same bottom-left origin and same scale.',
        'legend': {
            'dark_gray': 'overlap (in both)',
            'red': 'source only',
            'cyan': 'publish/Archicad only',
            'orange': 'shared bottom-left origin'
        },
        'raw_pixel_counts': {
            'common': int(raw_common.sum()),
            'source_only': int(raw_source_only.sum()),
            'published_only': int(raw_publish_only.sum())
        },
        'structural_pixel_counts': {
            'common': int(struct_common.sum()),
            'source_only': int(struct_source_only.sum()),
            'published_only': int(struct_publish_only.sum())
        },
        'outputs': {
            'source_registered': str(out_dir / 'source-plan-registered.png'),
            'published_registered': str(out_dir / 'published-plan-registered.png'),
            'raw_registered_overlay': str(out_dir / 'raw-registered-overlay.png'),
            'structural_difference_map': str(out_dir / 'structural-difference-map.png'),
            'structural_difference_overlay': str(out_dir / 'structural-difference-overlay.png')
        }
    }
    (out_dir / 'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
