#!/bin/bash

MAYPATH=$1
RUNNUMBER=$2

mkdir $MAYPATH/FASTQC_results/

for f in $MAYPATH/$RUNNUMBER/*.fastq.gz;
do fastqc --outdir $MAYPATH/FASTQC_results/ $f;
done

/home/mecore/.local/bin/multiqc $MAYPATH/FASTQC_results -o $MAYPATH/MultiQC_results
