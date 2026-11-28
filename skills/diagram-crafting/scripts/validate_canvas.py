#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
validate_canvas.py
Geometric and schema validator for Obsidian .canvas files.
Enforces standards from the diagram-crafting skill:
1. Valid JSON schema, unique node IDs, and edge reference integrity.
2. Generous node heights to eliminate text and code clipping.
3. Adequate clearance (minimum 180px horizontal, 70px vertical) on labeled edges.
4. Group container enclosure padding (minimum 40px on all four sides).
"""
import argparse
import glob
import json
import os
import sys

MIN_HORIZONTAL_LABELED_GAP = 180
MIN_VERTICAL_LABELED_GAP = 70
MIN_GROUP_PADDING = 40
BASE_HEIGHT_PADDING = 50
LINE_HEIGHT_TEXT = 30
LINE_HEIGHT_CODE = 32
REQUIRED_GEOMETRY_KEYS = ("x", "y", "width", "height")


def _has_valid_geometry(node: dict) -> bool:
    return all(isinstance(node.get(k), (int, float)) for k in REQUIRED_GEOMETRY_KEYS)


def validate_canvas(file_path: str) -> list[str]:
    issues: list[str] = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return [f"Invalid JSON: {e}"]

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    node_map: dict[str, dict] = {}

    # 1. Check node IDs and geometry fields
    for node in nodes:
        nid = node.get("id")
        if not nid:
            issues.append("Node is missing required 'id' field")
            continue
        if nid in node_map:
            issues.append(f"Duplicate node ID '{nid}'")
            continue
        if not _has_valid_geometry(node):
            issues.append(
                f"Node '{nid}' is missing numeric geometry fields ({', '.join(REQUIRED_GEOMETRY_KEYS)})"
            )
            continue
        node_map[nid] = node

    # 2. Check edge reference integrity
    for edge in edges:
        eid = edge.get("id", "unknown-edge")
        fn = edge.get("fromNode")
        tn = edge.get("toNode")
        if fn not in node_map:
            issues.append(f"Edge '{eid}' references non-existent fromNode '{fn}'")
        if tn not in node_map:
            issues.append(f"Edge '{eid}' references non-existent toNode '{tn}'")

    # 3. Check text node height sufficiency
    for nid, node in node_map.items():
        if node.get("type") != "text":
            continue
        text = node.get("text", "")
        h = node["height"]

        lines = text.split("\n")
        text_lines = 0
        code_lines = 0
        heading_count = 0
        in_code = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code = not in_code
                code_lines += 1
            elif in_code:
                code_lines += 1
            else:
                text_lines += 1
                if stripped.startswith("#"):
                    heading_count += 1

        min_expected_h = max(
            100,
            BASE_HEIGHT_PADDING
            + (heading_count * 18)
            + (text_lines * LINE_HEIGHT_TEXT)
            + (code_lines * LINE_HEIGHT_CODE),
        )

        if h < min_expected_h:
            sample = lines[0][:40] if lines else ""
            issues.append(
                f"Node '{nid}' ({sample}...) height {h}px < required {min_expected_h}px (Risk of text clipping)"
            )

    # 4. Check labeled edge clearance
    for edge in edges:
        lbl = edge.get("label")
        if not lbl:
            continue
        fn_id = edge.get("fromNode")
        tn_id = edge.get("toNode")
        if fn_id not in node_map or tn_id not in node_map:
            continue

        fn = node_map[fn_id]
        tn = node_map[tn_id]
        from_side = edge.get("fromSide")
        to_side = edge.get("toSide")

        if from_side == "right" and to_side == "left":
            h_gap = tn["x"] - (fn["x"] + fn["width"])
            if h_gap < MIN_HORIZONTAL_LABELED_GAP:
                issues.append(
                    f"Edge '{lbl}' ({fn_id} -> {tn_id}) horizontal gap is {h_gap}px < required {MIN_HORIZONTAL_LABELED_GAP}px (Label will collide with nodes)"
                )
        elif from_side == "left" and to_side == "right":
            h_gap = fn["x"] - (tn["x"] + tn["width"])
            if h_gap < MIN_HORIZONTAL_LABELED_GAP:
                issues.append(
                    f"Edge '{lbl}' ({fn_id} -> {tn_id}) horizontal gap is {h_gap}px < required {MIN_HORIZONTAL_LABELED_GAP}px (Label will collide with nodes)"
                )
        elif from_side == "bottom" and to_side == "top":
            v_gap = tn["y"] - (fn["y"] + fn["height"])
            if v_gap < MIN_VERTICAL_LABELED_GAP:
                issues.append(
                    f"Edge '{lbl}' ({fn_id} -> {tn_id}) vertical gap is {v_gap}px < required {MIN_VERTICAL_LABELED_GAP}px (Label will collide with nodes)"
                )
        elif from_side == "top" and to_side == "bottom":
            v_gap = fn["y"] - (tn["y"] + tn["height"])
            if v_gap < MIN_VERTICAL_LABELED_GAP:
                issues.append(
                    f"Edge '{lbl}' ({fn_id} -> {tn_id}) vertical gap is {v_gap}px < required {MIN_VERTICAL_LABELED_GAP}px (Label will collide with nodes)"
                )

    # 5. Check group enclosure padding (>= 40px on all 4 sides)
    groups = [(nid, n) for nid, n in node_map.items() if n.get("type") == "group"]
    children = [(nid, n) for nid, n in node_map.items() if n.get("type") != "group"]
    for gid, grp in groups:
        gx1, gy1 = grp["x"], grp["y"]
        gx2, gy2 = gx1 + grp["width"], gy1 + grp["height"]
        for cid, child in children:
            cx_mid = child["x"] + child["width"] / 2
            cy_mid = child["y"] + child["height"] / 2
            if gx1 <= cx_mid <= gx2 and gy1 <= cy_mid <= gy2:
                left_pad = child["x"] - gx1
                top_pad = child["y"] - gy1
                right_pad = gx2 - (child["x"] + child["width"])
                bottom_pad = gy2 - (child["y"] + child["height"])
                min_pad = min(left_pad, top_pad, right_pad, bottom_pad)
                if min_pad < MIN_GROUP_PADDING:
                    issues.append(
                        f"Group '{gid}' encloses '{cid}' with {min_pad}px padding < required {MIN_GROUP_PADDING}px"
                    )

    return issues


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Obsidian .canvas files for schema integrity, node height, edge clearance, and group padding."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        metavar="PATH",
        help="One or more .canvas file paths or glob patterns.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    files: list[str] = []
    for arg in args.paths:
        expanded = glob.glob(arg, recursive=True)
        files.extend(expanded if expanded else [arg])

    files = sorted(set(files))
    total_files = len(files)
    failed_files = 0
    total_issues = 0

    print(f"Validating {total_files} Obsidian .canvas files...")
    for f in files:
        if not os.path.exists(f):
            print(f"[MISSING] {f}")
            failed_files += 1
            total_issues += 1
            continue

        issues = validate_canvas(f)
        if issues:
            failed_files += 1
            total_issues += len(issues)
            print(f"\n[FAIL] {os.path.basename(f)} ({len(issues)} issues):")
            for iss in issues:
                print(f"  - {iss}")
        else:
            print(f"[PASS] {os.path.basename(f)}")

    print("\n" + "=" * 50)
    if total_issues == 0:
        print(f"ALL {total_files} CANVASES PASSED! Zero clippings or edge label collisions.")
        return 0
    print(f"FAILED: {failed_files}/{total_files} files had {total_issues} total issues.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
