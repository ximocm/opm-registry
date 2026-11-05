# OPM Registry

Biblioteca compartida de **herramientas independientes** y **pipelines de ejemplo**.
Las herramientas se pueden invocar desde línea de comandos sin instalar
[Open Pipeline Manager](https://github.com/ximocm/OpenPipelineManager). Consulta
su [manual](https://github.com/ximocm/OpenPipelineManager/blob/main/MANUAL.md)
para diseñar y ejecutar pipelines en la aplicación. Las pipelines se distribuyen como un único archivo `.pipeline`
compatible con OPM 0.3.0, formato nativo 1.

## Contenido

| Herramienta | Definición | Función |
| --- | --- | --- |
| FastQC | [fastqc.json](tools/fastqc.json) | Informes de calidad de uno o varios FASTQ. |
| Cutadapt single-end | [cutadapt-single.json](tools/cutadapt-single.json) | Adaptadores, calidad y longitud. |
| Cutadapt paired-end | [cutadapt-paired.json](tools/cutadapt-paired.json) | Recortes de R1/R2 conservando las parejas. |
| MultiQC | [multiqc.json](tools/multiqc.json) | Comparación de los informes FastQC. |

| Pipeline | Procesamiento |
| --- | --- |
| [sars-cov2-small-rna-qc](pipelines/sars-cov2-small-rna-qc.pipeline) | Adaptador Illumina, Q30, recorte de 3 bases, cola poli-A y longitud 10–35 nt. |
| [metagenomics-paired-qc](pipelines/metagenomics-paired-qc.pipeline) | Recorte de 10 bases en 5′ en ambas lecturas y 10 bases en 3′ en R2. |
| [mirna-precursor-qc](pipelines/mirna-precursor-qc.pipeline) | Adaptadores 5′/3′, Q10 y longitud 17–30 nt. |

Todas incluyen FastQC antes/después y un informe comparativo MultiQC. Consulta
las [notas de procesamiento y documentación de las herramientas](SOURCES.md).

## Preparar las herramientas

El registro contiene las definiciones y utilidades propias. FastQC, Cutadapt y
MultiQC se instalan desde sus distribuidores. Versiones comprobadas localmente:
FastQC 0.13.0, Cutadapt 5.2 y MultiQC 1.35; FastQC requiere Java. El ejecutor
independiente utiliza Python 3.10 o posterior y su biblioteca estándar.

Por ejemplo, con Conda:

```bash
conda create -n opm-qc -c conda-forge -c bioconda fastqc=0.13.0 cutadapt=5.2 multiqc=1.35
conda activate opm-qc
```

Para ejecutar las pipelines, abre OPM desde ese entorno para que encuentre las
herramientas. También hace falta un shell POSIX con `cp` y `mkdir`.

## Usar una herramienta sin OPM

```bash
python3 scripts/run_tool.py --list
python3 scripts/make_demo_data.py --output work/Input
python3 scripts/run_tool.py fastqc \
  --set reads=work/Input/metagen_R1.fastq \
  --set outdir=work/outputs/fastqc
python3 scripts/run_tool.py cutadapt-paired \
  --set read1=work/Input/metagen_R1.fastq \
  --set read2=work/Input/metagen_R2.fastq \
  --set cut1=10 --set cut2=10 \
  --set trimmed1=work/outputs/R1.fastq \
  --set trimmed2=work/outputs/R2.fastq \
  --set report=work/outputs/cutadapt.txt
```

Añade `--dry-run` para validar entradas y mostrar el comando sin crear salidas.
Para varios archivos, utiliza un array JSON, por ejemplo
`--set 'reads=["work/Input/metagen_R1.fastq","work/Input/metagen_R2.fastq"]'`.
Las rutas se resuelven desde el directorio donde ejecutas el comando. La
ejecución utiliza argumentos separados, sin evaluar un shell.

## Usar una pipeline en OPM

1. Clona este repositorio. Configura `OPM_PIPELINES_DIR` para que apunte a su
   carpeta `pipelines/` antes de abrir OPM, o copia el `.pipeline` elegido a la
   biblioteca cuya ubicación muestra la aplicación. Para editar tus propias
   variantes, usa una biblioteca local separada y **Guardar como**.
2. Elige **Open pipeline** y revisa la definición. Usa **New work** para crear
   una carpeta de trabajo nueva fuera del registro.
3. Coloca tus FASTQ en `Input/`. Los nombres predeterminados son:
   `SARS_cov_2_1.fastq`, `metagen_R1.fastq`/`metagen_R2.fastq` y
   `f010_raw_mirna.fastq`, respectivamente. También puedes asignar otros archivos
   en las entradas del paso **Stage inputs**.
4. Revisa adaptadores y parámetros, valida y ejecuta. El primer paso crea una
   copia de las entradas bajo nombres estables dentro de `steps/`; los originales
   se conservan. La pipeline de RNA pequeño procesa una muestra por carpeta de trabajo.
5. Abre `outputs/comparison/multiqc_report.html`. Los recortes y sus informes
   quedan en `steps/` y `outputs/`. El estado y los logs permanecen en la carpeta
   de trabajo, dentro de `.pipeline-manager/`.

Para probar el flujo con datos sintéticos, genera FASTQ con
`python3 scripts/make_demo_data.py --output /ruta/al/trabajo/Input`. Sirven para
comprobar el flujo técnico de extremo a extremo.

## Validación y contribuciones

```bash
python3 scripts/validate_registry.py
python3 -m unittest discover -s tests -v
python3 scripts/check_opm.py --opm-root /ruta/a/OpenPipelineManager
```

El último comando necesita Rust y las herramientas instaladas: carga los archivos
con el lector nativo de OPM y ejecuta las tres pipelines con su motor real,
siempre en carpetas nuevas con datos sintéticos. Opcionalmente acepta
`--tools-bin /ruta/al/entorno/bin`, `--offline` y `--work /ruta/nueva` para
conservar los resultados. CI repite la validación y la ejecución.

La rama inicial de integración es `dev`. Propón cambios mediante pull requests;
fija un commit al reutilizar definiciones para evitar actualizaciones implícitas.
Las versiones de las fichas pertenecen al registro, y
`tested_software_version` identifica la versión del programa comprobada. El
formato de las herramientas se documenta en [tools/README.md](tools/README.md).

Las pipelines contienen una copia de los pasos que utilizan y funcionan sin
consultar GitHub durante la ejecución. La descarga y actualización automática
del catálogo dentro de OPM queda fuera de esta primera entrega.

Licencia: [atribución y uso no comercial](LICENSE), siguiendo la política de
Open Pipeline Manager. Los programas externos conservan sus propias licencias.
