# Docs Guide

This folder is now grouped by role in the project lifecycle instead of keeping every file flat at the top level.
Use this file as the entry point.

## Folder Structure

### `architecture/`

Current system shape and technical flow.

- [AGENTS.md](architecture/AGENTS.md) — quick technical map of the pipeline, outputs, and core files
- [pipeline-architecture-diagram.md](architecture/pipeline-architecture-diagram.md) — visual data flow across scan, triage, quant, analysis, queue, and portfolio workflows

### `plans/`

Forward-looking change proposals and implementation roadmaps.

- [next-steps.md](plans/next-steps.md) — short near-term build list
- [masterplan-fix-mos.md](plans/masterplan-fix-mos.md) — focused proposal around MOS and allocator behavior
- [transition-into-ready-system.md](plans/transition-into-ready-system.md) — broader portfolio-system roadmap

### `reviews/`

Review packets, audit-style writeups, and AI-facing analysis artifacts.

- [REPO-SNAPSHOT.md](reviews/REPO-SNAPSHOT.md) — large repo snapshot prepared for AI review
- [chatgpt-report.md](reviews/chatgpt-report.md) — technical review memo
- [gemini-report.md](reviews/gemini-report.md) — prior review artifact

### `archive/`

Older state snapshots kept for reference.

- [before-changes-queue.md](archive/before-changes-queue.md) — queue snapshot before a prior change set
- [before-changes-queue.json](archive/before-changes-queue.json) — machine-readable version of the same snapshot

### `reference/`

Loose supporting references that are not active plans.

- [possible_repos.md](reference/possible_repos.md) — external repos worth revisiting

## Suggested Reading Paths

### Understand The Current System

1. [AGENTS.md](architecture/AGENTS.md)
2. [pipeline-architecture-diagram.md](architecture/pipeline-architecture-diagram.md)
3. [README.md](../README.md)
4. [CLAUDE.md](../CLAUDE.md)

### Review Roadmap And Gaps

1. [transition-into-ready-system.md](plans/transition-into-ready-system.md)
2. [next-steps.md](plans/next-steps.md)
3. [masterplan-fix-mos.md](plans/masterplan-fix-mos.md)

### Prepare An AI Review Packet

1. [REPO-SNAPSHOT.md](reviews/REPO-SNAPSHOT.md)
2. [AGENTS.md](architecture/AGENTS.md)
3. [pipeline-architecture-diagram.md](architecture/pipeline-architecture-diagram.md)
