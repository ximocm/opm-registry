# Independent tool descriptors, schema version 1

One JSON document defines one reusable invocation. This is the registry's own
format, independent of OPM's pipeline document schema; no OPM package is needed
to load it or run `scripts/run_tool.py`.

- `id`, `version`, `name`, `description`: registry identity and metadata.
- `executable`, `version_arguments`, `homepage`: the external program to run and
  where to find it. Executables are installed separately.
- `tested_software_version`: the external program version checked locally,
  distinct from the descriptor version.
- `inputs`, `parameters`, `outputs`: keyed fields with `type` (`file`, `folder`,
  `text`, `integer`), `description`, `required`, optional `default`, numeric
  `min`/`max`, and optional `multiple` for lists of file/folder values.
- `arguments`: an argument vector. A complete `{field}` token expands to one
  value, or several argv entries for a list. Values are never interpolated into
  shell source. A group `{"when": "field", "args": [...]}` is included when the
  optional field has a value. No embedded expressions are evaluated.
- `stdout`: optional output field receiving the program's standard output.

Input files/directories are checked before running. Output directories are
created after validation; file outputs cannot alias input paths or another
declared output. Programs may overwrite existing output files: choose a separate
work folder for each run. `--dry-run` creates no outputs and does not launch the
external executable.

Native `.pipeline` examples embed their commands and declarations, with the
tool ID/version recorded in step descriptions. OPM does not currently import
these independent tool descriptors automatically. When changing an invocation,
update its descriptor version and the affected pipelines together, and run the
real-binary checks as well as graph validation.
