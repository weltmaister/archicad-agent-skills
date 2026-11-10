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

Before writing, `archicad-automation` looks things up with `scripts/ac_lookup.py`: the command
schema of the exact Tapir release, whether the Archicad API can do it at all, and — for new or
domain-heavy workflows — the official Graphisoft Archicad Help of the version and language in use.
The Help index is built locally on first use (`ac_lookup.py build-help --ac 28 --lang GER`) and is
not part of this repository.

## Requirements

- Archicad 25–30 (Windows or macOS) with the [Tapir add-on](https://github.com/ENZYME-APD/tapir-archicad-automation/releases) installed — the skill is synced to Tapir 2.0.0; older releases work with the version gates it documents
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
