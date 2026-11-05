#!/usr/bin/env python3
"""Create original synthetic FASTQ fixtures; no course or study data are bundled."""

import argparse
from pathlib import Path
import random

ADAPTER5 = "CTGGGAAATCACCATAAACGTGAAATGTCTTTGGATTTGGGAATCTTATAAGTTCTGTATGAGACCACTCTAAAAA"
ADAPTER3 = "CTTTTTTTCGTCCTTTCCACAAGATATATAAAGCCAAGAAATCGAAATACTTTCAAGTTACGGTAAGC"


def generate(output, count=100):
    output = Path(output)
    if count < 1:
        raise ValueError("read count must be positive")
    names = ("SARS_cov_2_1.fastq", "metagen_R1.fastq", "metagen_R2.fastq", "f010_raw_mirna.fastq")
    if any((output / name).exists() for name in names):
        raise ValueError("choose an empty output directory; fixture files already exist")
    output.mkdir(parents=True, exist_ok=True)
    random_ = random.Random(20260929)
    sequences = {name: [] for name in names}
    for index in range(count):
        rna = ''.join(random_.choices('ACGT', k=22))
        sequences[names[0]].append((f"synthetic_sars_{index}", "TGA" + rna + "AAAAAAAAAAAAAGATCGGAAGAG"))
        sequences[names[1]].append((f"synthetic_pair_{index}/1", ''.join(random_.choices('ACGT', k=250))))
        sequences[names[2]].append((f"synthetic_pair_{index}/2", ''.join(random_.choices('ACGT', k=250))))
        sequences[names[3]].append((f"synthetic_mirna_{index}", ADAPTER5 + rna + ADAPTER3))
    for name, reads in sequences.items():
        with (output / name).open('x') as handle:
            for identifier, sequence in reads:
                handle.write(f"@{identifier}\n{sequence}\n+\n{'I' * len(sequence)}\n")
    return list(names)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='input directory of a fresh work folder')
    parser.add_argument('--reads', type=int, default=100)
    args = parser.parse_args()
    try:
        for name in generate(args.output, args.reads):
            print(args.output / name)
    except (ValueError, OSError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == '__main__':
    main()
