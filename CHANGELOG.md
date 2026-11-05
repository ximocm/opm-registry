# Changelog

## Unreleased

- Presented the registry as a general tool and pipeline catalog, with links to
  the OPM application documentation and neutral processing notes.

## 0.1.0 — 2026-11-05

- Four independent tool definitions: FastQC, Cutadapt single-end, Cutadapt
  paired-end, and MultiQC, usable from a standalone Python CLI.
- Three native OPM pipelines for sequencing quality control and preprocessing.
- Original synthetic FASTQ generator, graph and tool validation, standalone
  real-binary tests, and native OPM execution smoke checks.
- CI for registry validation and actual execution using a pinned OPM revision.
