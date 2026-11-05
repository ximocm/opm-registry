#!/usr/bin/env python3
"""Smoke-test native pipelines with a local OPM checkout and installed QC tools."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from make_demo_data import generate

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--opm-root', type=Path, required=True)
    parser.add_argument('--tools-bin', type=Path, help='prepend an activated tool environment bin directory')
    parser.add_argument('--work', type=Path, help='retain the fresh work folders here; defaults to a temporary directory')
    parser.add_argument('--offline', action='store_true', help='use already cached Rust dependencies')
    args = parser.parse_args()
    opm = args.opm_root.resolve()
    for name in ('opm-store', 'opm-pipeline', 'opm-exec'):
        if not (opm / 'core' / name / 'Cargo.toml').is_file():
            parser.error(f'OPM crate not found: {name}')
    env = dict(os.environ)
    if args.tools_bin:
        env['PATH'] = str(args.tools_bin.resolve()) + os.pathsep + env.get('PATH', '')
    subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', str(ROOT / 'tests'), '-v'], env=env, check=True)
    with tempfile.TemporaryDirectory(prefix='opm-registry-check-') as directory:
        temporary = Path(directory)
        crate = temporary / 'native-check'
        (crate / 'src').mkdir(parents=True)
        (crate / 'src/main.rs').write_text((ROOT / 'scripts/check_opm.rs').read_text())
        manifest = '[package]\nname = "opm-registry-check"\nversion = "0.1.0"\nedition = "2021"\n\n[workspace]\nresolver = "2"\n\n[dependencies]\n'
        for name in ('opm-store', 'opm-pipeline', 'opm-exec'):
            manifest += name + ' = { path = ' + json.dumps(str(opm / 'core' / name)) + ' }\n'
        (crate / 'Cargo.toml').write_text(manifest)
        fixtures = temporary / 'fixtures'
        generate(fixtures)
        work = args.work.resolve() if args.work else temporary / 'work'
        command = ['cargo', 'run', '--manifest-path', str(crate / 'Cargo.toml')]
        if args.offline:
            command += ['--offline']
        command += ['--', str(ROOT), str(fixtures), str(work)]
        subprocess.run(command, check=True, env=env)


if __name__ == '__main__':
    main()
