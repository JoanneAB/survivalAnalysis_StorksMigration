#!/bin/bash

filename='report'

pdflatex $filename.tex
bibtex $filename
bibtex $filename

pdflatex $filename.tex
pdflatex $filename.tex

rm $filename.toc $filename.aux $filename.log $filename.out $filename.blg $filename.bbl
