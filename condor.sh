#!/bin/bash
set -e

export X509_USER_PROXY=/home/llr/cms/song/.globus/user_proxy.pem

source /cvmfs/cms.cern.ch/cmsset_default.sh
cd $CMSSW_BASE_PATH/src
cmsenv
cd -

# [[ "$ParticleId" == "11" ]] && {
#   step1="step1_flat.py"
# } ||
#   {
step1="step1.py"
  # }
if [[ "$ParticleId" == "11" || "$ParticleId" == "-11" ]]; then
  outdir="electron"
elif [[ "$ParticleId" == "22" ]]; then
  outdir="photon"
else
  outdir="pion"
fi
# PU
[[ "$PU" == "1" ]] && {
  step2="step2_pu.py"
  outdir="${outdir}_PU"
} ||
  {
    step2="step2.py"
    outdir="${outdir}_noPU"
  }

# Scintillator
[[ "$Scintillator" == "1" ]] && {
  maxEta="2.0"
  minEta="1.8"
  outdir="${outdir}_Sci"
} ||
  {
    maxEta="2.8"
    minEta="2.4"
    outdir="${outdir}_Si"
  }

cat <<EOF >>"${step1}"
from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper 
randSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService) 
randSvc.populate() 

process.source.firstLuminosityBlock = cms.untracked.uint32($INDEX)

####### WARNING the name is different than Pythia guns : PartID vs ParticleID
process.generator.PGunParameters.PartID = cms.vint32($ParticleId)
process.generator.PGunParameters.MaxEta = cms.double($maxEta)
process.generator.PGunParameters.MinEta = cms.double($minEta)
EOF

cmsRun "${step1}"


cat <<EOF >>"${step2}"
from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper 
randSvc = RandomNumberServiceHelper(process.RandomNumberGeneratorService) 
randSvc.populate() 
EOF
cmsRun "${step2}"

outdir=/grid_mnt/data_cms_upgrade/song/HGCAL/HGCHadron/${outdir}/jobs
mkdir -p $outdir
if [[ "$ParticleId" == "11" ]]; then
  cmsRun step3.py
  mv step3_inDQM.root ${outdir}/step3_inDQM_$INDEX.root
else
  mv step2.root ${outdir}/step2_$INDEX.root
fi


# mv step2.root ${outdir}/step2_$INDEX.root

# mv step3.root ${outdir}/step3_$INDEX.root
# mv step3_inDQM.root ${outdir}/step3_inDQM_$INDEX.root
# mv histo.root ${outdir}/histo_$INDEX.root
