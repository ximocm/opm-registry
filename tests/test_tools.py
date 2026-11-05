import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import make_demo_data
import run_tool
from validate_registry import validate_pipeline


class Tools(unittest.TestCase):
    def test_adapter_notation_and_shell_characters_remain_single_arguments(self):
        tool = run_tool.load_tool('cutadapt-single')
        values = run_tool.resolve(tool, dict(reads='input with spaces.fastq', trimmed='out.fastq', report='report.txt', adapter3='A{10}; touch unexpected'), check_files=False)
        argv = run_tool.arguments(tool, values)
        self.assertEqual(argv[argv.index('-a') + 1], 'A{10}; touch unexpected')
        self.assertEqual(argv[-1], 'input with spaces.fastq')
        self.assertNotIn('-g', argv)
        self.assertNotIn('-M', argv)

    def test_paired_tail_trimming_uses_both_mates_and_r2_flag(self):
        tool = run_tool.load_tool('cutadapt-paired')
        values = run_tool.resolve(tool, dict(read1='r1.fastq', read2='r2.fastq', trimmed1='o1.fastq', trimmed2='o2.fastq', report='report.txt', cut2=-10), check_files=False)
        argv = run_tool.arguments(tool, values)
        self.assertEqual(argv[argv.index('-U') + 1], '-10')
        self.assertEqual(argv[-2:], ['r1.fastq', 'r2.fastq'])
        self.assertIn('-p', argv)

    def test_reject_invalid_values_and_overwriting_input(self):
        tool = run_tool.load_tool('cutadapt-single')
        defaults = dict(reads='in.fastq', trimmed='out.fastq', report='report.txt')
        for overrides in ({'quality': 100}, {'threads': 0}, {'threads': True}, {'max_length': 5, 'min_length': 10}, {'trimmed': 'in.fastq'}, {'extra': 'x'}, {'report': 'out.fastq'}):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                run_tool.resolve(tool, defaults | overrides, check_files=False)

    def test_dry_run_has_no_output_side_effects(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'input.fastq'
            source.write_text('@r\nACGT\n+\nIIII\n')
            command = [sys.executable, str(ROOT / 'scripts/run_tool.py'), 'cutadapt-single', '--dry-run', '--set', f'reads={source}', '--set', f'trimmed={root}/new/out.fastq', '--set', f'report={root}/new/report.txt']
            result = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((root / 'new').exists())

    def test_generated_fixtures_are_valid_and_pairs_match(self):
        with tempfile.TemporaryDirectory() as directory:
            names = make_demo_data.generate(directory, 5)
            records = {}
            for name in names:
                lines = (Path(directory) / name).read_text().splitlines()
                self.assertEqual(len(lines), 20)
                for start in range(0, len(lines), 4):
                    self.assertEqual(len(lines[start+1]), len(lines[start+3]))
                records[name] = lines[::4]
            self.assertEqual([v[:-2] for v in records['metagen_R1.fastq']], [v[:-2] for v in records['metagen_R2.fastq']])
            with self.assertRaises(ValueError):
                make_demo_data.generate(directory, 5)

    def test_pipelines_have_resolvable_acyclic_graphs(self):
        for path in (ROOT / 'pipelines').glob('*.pipeline'):
            with self.subTest(path=path.name):
                validate_pipeline(json.loads(path.read_text()))


if __name__ == '__main__':
    unittest.main()
