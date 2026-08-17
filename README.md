# Archicad Agent Skills

Two [Agent Skills](https://agentskills.io) for driving **Graphisoft Archicad** with Claude (or any
skill-capable agent) through the open-source [Tapir add-on](https://github.com/ENZYME-APD/tapir-archicad-automation)'s
JSON API — from reading a scanned floor plan all the way to a modelled, dimensioned, published BIM file.

| Skill | What it covers |
|---|---|
| [`abstracting-building-models`](abstracting-building-models/) | Turn architectural drawings (floor plans, sections, elevations, PDFs, scans) into a structured, evidence-backed parametric building model — calibration, dimension-chain extraction, uncertainty tracking, validation. |
| [`archicad-automation`](archicad-automation/) | Operate Archicad itself over Tapir's HTTP interface — create/modify elements, read details, place associative dimensions, manage layers/attributes, build layouts, publish, and verify everything by read-back. |

The two skills chain: `abstracting-building-models` produces the intermediate model,
`archicad-automation` executes it against a live Archicad instance.

## What makes these different

They are **live-verified field guides**, not API summaries. The command references carry
hand-tested payload shapes, exact error codes, known crash traps, and **per-release version
gates** (behavior differs meaningfully between Tapir releases — the skills tell you which
fields exist since which release and how to probe the connected instance instead of assuming).

## Requirements

- Archicad 25–29 (Windows or macOS) with the [Tapir add-on](https://github.com/ENZYME-APD/tapir-archicad-automation/releases) installed — recent releases (≥ 1.5.4) strongly recommended
- An open Archicad project (the JSON port only listens while a project is open)
- An agent runtime that can reach `localhost` of the Archicad host (ports 19723–19743)

## Installation

**Claude Code / compatible CLI runtimes:** copy the two skill folders into your skills directory
(e.g. `~/.claude/skills/` or your project's `.claude/skills/`).

**Claude.ai / Desktop:** zip each folder (the folder itself as the zip root) and import it as a
skill, or use a skill packager of your choice.

## Safety model

The `archicad-automation` skill enforces a verification discipline: no mutation counts as done
until an independent read-back confirms it, destructive operations require explicit confirmation,
and known crash inputs (zero-length walls, unsupported batch shapes on older releases) are
sanitized before they reach Archicad. Test against a scratch project first.

## Credits

Built on the [Tapir Archicad Automation](https://github.com/ENZYME-APD/tapir-archicad-automation)
project by ENZYME-APD and its contributors. The skills document the public Tapir API and reference
upstream issues/PRs by number; they contain no Tapir code.

## License

[MIT](LICENSE)
