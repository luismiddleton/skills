# Obsidian .canvas Specification & Aesthetics

Obsidian Canvas (`.canvas`) is an open JSON file format representing an infinite 2D spatial canvas with typed nodes, groups, and directional edges.

## 1. Schema Overview

```json
{
  "nodes": [ ... ],
  "edges": [ ... ]
}
```

### Node Types
1. **`text`**: Markdown content card.
   - `id` (string, required): Unique identifier within the canvas.
   - `type` (string): `"text"`.
   - `x`, `y` (int): Top-left position coordinates on canvas plane.
   - `width`, `height` (int): Dimensions in pixels.
   - `text` (string): Full Markdown formatted string (`# Header`, lists, bold, code blocks).
   - `color` (string, optional): Preset color code `"1"` to `"6"`.

2. **`group`**: Visual container grouping related nodes.
   - `id` (string): Unique identifier.
   - `type` (string): `"group"`.
   - `x`, `y`, `width`, `height` (int): Bounds enclosing child elements.
   - `label` (string, optional): Heading title shown on container tab.
   - `color` (string, optional): Border/background color tint.

3. **`file`**: Embeds a note or media file.
   - `file` (string): Relative vault path to target note or asset.

---

## 2. Color Palette Reference

Obsidian assigns thematic meaning to 6 standard color presets:
- `"1"`: **Red** (Risks, alerts, explicit denials, vulnerabilities, root tier)
- `"2"`: **Orange** (High importance, security tools, AWS KMS, medium risk)
- `"3"`: **Yellow / Amber** (Decision points, review steps, warm standby)
- `"4"`: **Green** (Approved state, production workloads, successful paths)
- `"5"`: **Cyan / Blue** (Client ingress, users, endpoints, shared services)
- `"6"`: **Purple** (Orchestration, global governance, AWS STS, core headers)

---

## 3. Geometric Formulas & Layout Rules

### A. Node Height Calculation
Obsidian's card renderer renders text with line-height and inner container padding. When card height is too small, text is silently truncated with scrollbars. Always use this formula:

$$\text{Height} = \text{Base Padding} (50\text{px}) + (\text{Headings} \times 18\text{px}) + (\text{Text Lines} \times 30\text{px}) + (\text{Code Lines} \times 32\text{px})$$

*Minimum node height:* **$100\text{px}$** for simple 1-liner cards; **$180\text{px}$** for 3-line structured concept cards.

### B. Labeled Edge Clearance
When an edge has a text label (e.g. `label: "After ~45 items"`):
- **Horizontal Connections (`fromSide: "right"`, `toSide: "left"`)**:
  - Distance: $\text{toNode.x} - (\text{fromNode.x} + \text{fromNode.width}) \ge 180\text{px}$ (Recommended: $200\text{px}$).
  - Gaps under $180\text{px}$ cause the label box to collide with adjacent nodes.
- **Vertical Connections (`fromSide: "bottom"`, `toSide: "top"`)**:
  - Distance: $\text{toNode.y} - (\text{fromNode.y} + \text{fromNode.height}) \ge 70\text{px}$ (Recommended: $80\text{px}$).

### C. Group Enclosure Clearance
- A group container must pad its innermost child nodes by at least **$40\text{px}$ on all four edges**:
  - $\text{group.x} \le \min(child.x) - 40$
  - $\text{group.y} \le \min(child.y) - 40$
  - $\text{group.width} \ge (\max(child.x + child.width) - \text{group.x}) + 40$
  - $\text{group.height} \ge (\max(child.y + child.height) - \text{group.y}) + 40$
