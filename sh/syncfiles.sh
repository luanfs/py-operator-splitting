#!/bin/bash
# P. Peixoto - Jul 2012
# modified by Luan Santos - 2022

date=` date +%F `
version=` date +%y.%m.%d `

source sh/tarfiles.sh

output="py-dimsplit$version.tar.bz2"
bkpdir="dimsplit" 

#Edit place to sync relative to system used
dropdir="/home/luan/Dropbox/doc/code/"$bkpdir
echo "Sync with Dropbox:"
rsync -v -t -u $output  "$dropdir/."
echo "Synchronized with Dropbox"
echo

#remote server ime.usp.br backup sync
echo "Sending to ime.usp.br:"
rsync -t -v -z -a --progress $output luansantos@ime.usp.br:/home/posmap/luansantos/doc/$bkpdir
echo "Sent to luansantos@ime.usp.br"
echo

#remote server ybytu backup sync
echo "Sending to ybytu:"
ssh -t luansantos@ime.usp.br  "rsync -t -v -z -a --progress doc/$bkpdir/$output luansantos@ybytu:/home/luansantos/doc/"$bkpdir
echo "Sent to luansantos@ybytu"
echo

# remove tar file
rm -rf $output
