# Opening side triad (`oSide`, `reflected`, `refSide`) and live-retry pattern

## Durable lesson

For Tapir/Archicad door/window side control, use the full side-and-handing triad:

- `oSide` — host-wall side / inside-vs-outside symbol side. `false` = exterior/outside; `true` = interior/inside. This is the primary control for inward/outward placement relative to the wall.
- `reflected` — symbol mirroring along the Y axis; affects the opening/swing direction but does not by itself move the symbol to the other side of the host wall.
- `refSide` — symbol mirroring along the X axis; hinge side (`false` left, `true` right).

For inward-opening exterior doors, set `oSide: true` first, then set `reflected` and `refSide` for the intended swing/hinge.

## Why this matters

Do **not** conflate two different things:

1. **Swing direction** — whether the leaf swings inward or outward relative to the room / host wall side.
2. **Hinge side** (DIN left / DIN right in some regional conventions) — which jamb carries the hinge when read from the relevant side.

In Tapir terms these concerns are related but not identical:
- `oSide` primarily controls on which wall side the symbol is drawn (inside vs outside).
- `reflected` changes the swing/mirroring behaviour of the symbol.
- `refSide` changes the hinge/jamb side.

Operational rule: when checking source vs publish, verify **both** independently. A door can already swing to the correct side (inside/outside) while still having the wrong hinge side. Describe corrections explicitly in those two layers instead of saying only "the door direction is wrong".

A live measured-plan run showed that writing only `reflected` and `refSide` can produce correct readback booleans while the published drawing still shows the old/wrong outside-swing symbol. The missing control was `oSide`. Therefore, never claim door/window handing is fixed from boolean readback alone: publish and visually inspect the fresh PDF/PNG.

## Verification sequence

1. Rediscover the live schema after Add-On/MCP deployment or server restart.
2. Confirm `oSide`, `reflected`, and `refSide` appear in `CreateDoors`/`ModifyDoors` and/or window equivalents.
3. Confirm an active Archicad/Tapir connection via `discovery_list_active_archicads`; do not reuse a stale port if discovery is empty.
4. Modify or recreate the target openings with all relevant side fields set together.
5. Read back with `GetDoorsDetails` / `GetWindowsDetails`.
6. If openings were recreated, rebuild dependent associative dimensions and verify with `GetDimensionData`.
7. Publish to the known project output path, verify the PDF timestamp advanced, render a fresh PNG, and visually inspect the symbols.

## Runtime pitfall

After an MCP server restart, the schema may already show new fields while `discovery_list_active_archicads` returns no active project, or a previously valid port reports `not an active Archicad connection`. Treat this as a transient connection state: poll discovery for a bounded period instead of hardcoding the stale port or concluding that the schema update failed.
