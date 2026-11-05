#!/usr/bin/env python3
"""Validate independent tools and native OPM pipeline graphs without running commands."""

import json
from pathlib import Path
import re
import shlex
import subprocess

from run_tool import ROOT, arguments, fields_for, load_tool, resolve

PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


def validate_pipeline(doc):
    if doc['format_version'] != 1 or not doc['name'].strip():
        raise ValueError('unsupported pipeline format or empty name')
    steps = doc['pipeline']['steps']
    by_id = {step['id']: step for step in steps}
    if len(by_id) != len(steps) or not steps:
        raise ValueError('duplicate step ids or empty graph')
    for step in steps:
        fields = step['inputs'] + step['outputs'] + step['parameters']
        keys = [field['key'] for field in fields if field['key']]
        if len(set(keys)) != len(keys):
            raise ValueError(f"duplicate fields in {step['id']}")
        missing = set(PLACEHOLDER.findall(step['command'])) - set(keys)
        if missing:
            raise ValueError(f"unknown placeholders: {missing}")
        if step['working_directory'] != '.':
            raise ValueError('examples must run relative to the work root')
        for dep in step['dependencies']:
            if dep not in by_id:
                raise ValueError(f'missing dependency {dep}')
        for field in step['inputs']:
            if 'source_step' in field:
                source = by_id[field['source_step']]
                if field['source_output'] not in {v['key'] for v in source['outputs']}:
                    raise ValueError('missing source output')
                if source['id'] not in step['dependencies']:
                    raise ValueError('source link must have an explicit dependency')
        for field in step['outputs']:
            path = Path(field['path'])
            if path.is_absolute() or '..' in path.parts:
                raise ValueError('output escapes work root')
        placeholder_values = {key: 'registry-value' for key in keys}
        rendered = PLACEHOLDER.sub(lambda m: shlex.quote(placeholder_values[m.group(1)]), step['command'])
        subprocess.run(['sh', '-n'], input=rendered, text=True, check=True)
    visiting, visited = set(), set()

    def visit(identifier):
        if identifier in visiting:
            raise ValueError('dependency cycle')
        if identifier in visited:
            return
        visiting.add(identifier)
        for dep in by_id[identifier]['dependencies']:
            visit(dep)
        visiting.remove(identifier)
        visited.add(identifier)
    for identifier in by_id:
        visit(identifier)


def main():
    tool_paths = sorted((ROOT / 'tools').glob('*.json'))
    pipeline_paths = sorted((ROOT / 'pipelines').glob('*.pipeline'))
    assert tool_paths and pipeline_paths, 'registry must contain tools and pipelines'
    for path in tool_paths:
        tool = load_tool(path.stem)
        assert tool['version'] and tool['homepage'].startswith('https://')
        fields = fields_for(tool)
        supplied = {}
        for key, field in fields.items():
            if field.get('required'):
                supplied[key] = 'fixtures/' + key
        values = resolve(tool, supplied, check_files=False)
        argv = arguments(tool, values)
        assert argv and argv[0] == tool['executable']
        print(f"tool: {tool['id']}@{tool['version']}")
    for path in pipeline_paths:
        validate_pipeline(json.loads(path.read_text()))
        print(f'pipeline: {path.name}')


if __name__ == '__main__':
    main()
