# Source and adaptation notes

The initial examples were independently written from the exercises in
*Quality control and data preprocessing*, dated 29 September 2026, credited in
the supplied tutorial to **Sergio Romera Giner**, Máster Universitario en
Bioinformática. The supplied folder was named
`2026-09-29-quality-control-and-data-preprocessing` and contained the tutorial
and presentation HTML plus the exercise FASTQ datasets.

The tutorial, slides, figures, study FASTQ data, and third-party program source
or binaries are not redistributed here. Original synthetic fixture generation
is included instead. Providing the original exercise files is optional: point
the stage-input fields at your own suitable FASTQ files.

## Intentional differences

- **Exercise 1:** one selected single-end sample per work folder instead of
  repeating the same commands manually for three samples. Adapter removal,
  Q30 plus 3-base 5-prime trimming, and poly-A/length filtering remain separate
  Cutadapt passes, preserving the teaching order of operations.
- **Exercise 2:** both mates are passed to both Cutadapt calls. The second pass
  uses `-u 0 -U -10` to trim only the R2 tail in paired mode. Final QC sees the
  final R1/R2 outputs only, rather than every intermediate file matching a glob.
- **Exercise 3:** the sequence described as a 5-prime adapter is supplied using
  `-g`; the 3-prime sequence uses `-a`. The tutorial's example applied `-a` to
  both despite describing different positions. Both sequences remain editable;
  review their orientation against the actual preparation protocol.
- **All exercises:** explicit dependencies, declared outputs, relative work
  paths, separate cutadapt text reports, and one MultiQC comparison of raw/final
  FastQC reports. Staging uses stable basenames so output report paths remain
  verifiable even when a different input filename is selected.

## Tool references

- [FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)
- [Cutadapt user guide](https://cutadapt.readthedocs.io/en/stable/guide.html)
- [Running MultiQC](https://docs.seqera.io/multiqc/getting_started/running_multiqc/)

These programs retain their own licenses. The repository license covers the
original registry definitions, scripts, and documentation.
