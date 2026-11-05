"""Optional real-binary checks; run when FastQC, Cutadapt and MultiQC are on PATH."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from make_demo_data import generate


@unittest.skipUnless(all(shutil.which(v) for v in ('fastqc', 'cutadapt', 'multiqc')), 'activate a QC environment to run real-binary tests')
class InstalledTools(unittest.TestCase):
    def test_independent_tools_run_without_opm(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generate(root / 'Input')

            def run(tool, **values):
                command = [sys.executable, str(ROOT / 'scripts/run_tool.py'), tool]
                for key, value in values.items():
                    command += ['--set', f'{key}={value}']
                result = subprocess.run(command, cwd=root, text=True, capture_output=True, timeout=90)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            run('cutadapt-single', reads='Input/SARS_cov_2_1.fastq', trimmed='outputs/trimmed.fastq', report='outputs/trim.txt', adapter3='AGATCGGAAGAG')
            self.assertGreater((root / 'outputs/trimmed.fastq').stat().st_size, 0)
            self.assertIn('Total reads processed', (root / 'outputs/trim.txt').read_text())
            run('cutadapt-paired', read1='Input/metagen_R1.fastq', read2='Input/metagen_R2.fastq', trimmed1='outputs/r1.fastq', trimmed2='outputs/r2.fastq', report='outputs/pairs.txt', cut1=10, cut2=-10)
            r1 = (root / 'outputs/r1.fastq').read_text().splitlines()
            r2 = (root / 'outputs/r2.fastq').read_text().splitlines()
            self.assertEqual(len(r1), len(r2))
            self.assertEqual(len(r1[1]), 240)
            self.assertEqual(len(r2[1]), 240)
            run('fastqc', reads='outputs/trimmed.fastq', outdir='outputs/fastqc')
            self.assertTrue((root / 'outputs/fastqc/trimmed_fastqc.zip').is_file())
            run('multiqc', reports='outputs/fastqc', outdir='outputs/multiqc')
            self.assertGreater((root / 'outputs/multiqc/multiqc_report.html').stat().st_size, 100)


if __name__ == '__main__':
    unittest.main()
