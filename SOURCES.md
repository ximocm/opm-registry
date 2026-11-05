# Tool documentation and processing notes

## Tools

- [FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)
- [Cutadapt user guide](https://cutadapt.readthedocs.io/en/stable/guide.html)
- [Running MultiQC](https://docs.seqera.io/multiqc/getting_started/running_multiqc/)
- [Open Pipeline Manager manual](https://github.com/ximocm/OpenPipelineManager/blob/main/MANUAL.md)

The registry stores reusable invocation definitions and pipelines. External
programs are installed separately and retain their own licenses.

## Processing choices

- **Small RNA:** one selected single-end sample per work folder. Adapter
  removal, Q30 plus 3-base 5-prime trimming, and poly-A/length filtering are
  separate Cutadapt passes so their order is explicit.
- **Paired-end metagenomics:** both mates enter both Cutadapt calls. The second
  pass uses `-u 0 -U -10` to trim only the R2 tail in paired mode. Final quality
  control uses the final R1/R2 outputs rather than intermediate files.
- **miRNA precursors:** a 5-prime adapter is supplied with `-g` and a 3-prime
  adapter with `-a`. Both sequences and filtering thresholds are editable.
- **All pipelines:** explicit dependencies, declared outputs, relative work
  paths, separate Cutadapt text reports, and one MultiQC comparison of raw and
  processed FastQC reports. Staging uses stable basenames so output report
  paths remain verifiable when a different input filename is selected.

Review adapters, read layout, and filtering thresholds for your preparation
protocol before using these templates with your own data. Synthetic fixtures
check execution and output wiring; they are not reference biological datasets.
