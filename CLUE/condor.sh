#!/bin/bash
set -e

export X509_USER_PROXY=/home/llr/cms/song/.globus/user_proxy.pem

source /cvmfs/cms.cern.ch/cmsset_default.sh
cd $CMSSW_BASE_PATH/src
cmsenv
cd -

# file=$(basename "$FILE")
file=$FILE
sed -i "s|#{EDITS}|process.source.fileNames = cms.untracked.vstring('file:${file}')|" step3.py
echo "Input file is ${file}, the output dir is ${OUTDIR}"
cmsRun step3.py

tmp="${file%.root}"
INDEX="${tmp##*_}"

outdir=${OUTDIR}/jobs
# mkdir -p $outdir

mv step3_inDQM.root ${outdir}/step3_inDQM_${INDEX}.root
# mv histo.root ${outdir}/histo_${INDEX}.root
# mv step3.root ${outdir}/step3_$INDEX.root