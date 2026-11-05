#!/usr/bin/env python3
"""Run an independent registry tool descriptor using argv, without a shell."""

import argparse
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def load_tool(tool_id):
    if not tool_id or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in tool_id):
        raise ValueError("tool id must contain lowercase letters, digits, hyphens or underscores")
    tool = json.loads((ROOT / "tools" / f"{tool_id}.json").read_text())
    if tool.get("schema_version") != 1 or tool.get("id") != tool_id:
        raise ValueError(f"unsupported or mismatched tool descriptor: {tool_id}")
    return tool


def fields_for(tool):
    fields = {}
    for group in ("inputs", "parameters", "outputs"):
        for key, spec in tool[group].items():
            if key in fields:
                raise ValueError(f"duplicate field {key}")
            fields[key] = spec
    return fields


def resolve(tool, supplied, check_files=True):
    fields = fields_for(tool)
    if unknown := supplied.keys() - fields.keys():
        raise ValueError(f"unknown fields: {', '.join(sorted(unknown))}")
    values = {}
    for key, spec in fields.items():
        value = supplied.get(key, spec.get("default"))
        if value is None or value == "":
            if spec.get("required"):
                raise ValueError(f"{key} is required")
            values[key] = None
            continue
        if spec.get("multiple"):
            items = value if isinstance(value, list) else [value]
            if not items:
                raise ValueError(f"{key} cannot be empty")
        else:
            items = [value]
        for item in items:
            kind = spec["type"]
            if kind == "integer":
                if not isinstance(item, int) or isinstance(item, bool):
                    raise ValueError(f"{key} must be an integer")
                if "min" in spec and item < spec["min"]:
                    raise ValueError(f"{key} must be >= {spec['min']}")
                if "max" in spec and item > spec["max"]:
                    raise ValueError(f"{key} must be <= {spec['max']}")
            elif not isinstance(item, str) or not item or "\x00" in item:
                raise ValueError(f"{key} must be a nonempty string")
            if key in tool["inputs"] and check_files:
                path = Path(item)
                if kind == "file" and not path.is_file():
                    raise ValueError(f"input file does not exist: {item}")
                if kind == "folder" and not path.is_dir():
                    raise ValueError(f"input folder does not exist: {item}")
        values[key] = items if spec.get("multiple") else value
    input_paths = {
        Path(item).resolve()
        for key in tool["inputs"]
        if fields[key]["type"] in ("file", "folder") and values[key] is not None
        for item in (values[key] if fields[key].get("multiple") else [values[key]])
    }
    output_paths = []
    for key, spec in tool["outputs"].items():
        if values[key] is None:
            continue
        path = Path(values[key]).resolve()
        if path in input_paths:
            raise ValueError(f"{key} would overwrite an input")
        if path in output_paths:
            raise ValueError(f"{key} duplicates another output")
        output_paths.append(path)
    if values.get("max_length") is not None and values["max_length"] < values.get("min_length", 0):
        raise ValueError("max_length must be >= min_length")
    return values


def arguments(tool, values):
    def expand(tokens):
        result = []
        for token in tokens:
            if isinstance(token, dict):
                if values[token["when"]] is not None:
                    result.extend(expand(token["args"]))
            elif token.startswith("{") and token.endswith("}"):
                value = values[token[1:-1]]
                if value is None:
                    raise ValueError(f"missing argument {token}")
                result.extend(str(v) for v in (value if isinstance(value, list) else [value]))
            else:
                result.append(token)
        return result
    return [tool["executable"], *expand(tool["arguments"])]


def parse_assignments(assignments, tool):
    fields = fields_for(tool)
    supplied = {}
    for assignment in assignments:
        key, separator, text = assignment.partition("=")
        if not separator or key not in fields or key in supplied:
            raise ValueError(f"unknown, duplicate or malformed assignment: {assignment}")
        spec = fields[key]
        if spec["type"] == "integer":
            try:
                value = int(text)
            except ValueError as error:
                raise ValueError(f"{key} must be an integer") from error
        elif spec.get("multiple") and text.startswith("["):
            value = json.loads(text)
            if not isinstance(value, list):
                raise ValueError(f"{key} must be a JSON array")
        else:
            value = text
        supplied[key] = value
    return supplied


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool", nargs="?")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    parser.add_argument("--dry-run", action="store_true", help="validate and print without creating outputs")
    args = parser.parse_args()
    if args.list:
        for path in sorted((ROOT / "tools").glob("*.json")):
            print(path.stem)
        return 0
    if not args.tool:
        parser.error("choose a tool or use --list")
    try:
        tool = load_tool(args.tool)
        values = resolve(tool, parse_assignments(args.set, tool))
        argv = arguments(tool, values)
        report = values.get(tool.get("stdout"))
        print(shlex.join(argv) + (f" > {shlex.quote(report)}" if report else ""), flush=True)
        if args.dry_run:
            return 0
        if not shutil.which(argv[0]):
            raise ValueError(f"{argv[0]} is not on PATH; install/activate its environment first")
        for key, spec in tool["outputs"].items():
            if values[key] is not None:
                path = Path(values[key])
                (path if spec["type"] == "folder" else path.parent).mkdir(parents=True, exist_ok=True)
        if report:
            with open(report, "w") as output:
                return subprocess.run(argv, stdout=output, check=False).returncode
        return subprocess.run(argv, check=False).returncode
    except (ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
