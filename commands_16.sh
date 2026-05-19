# in: /grid_mnt/data_cms_upgrade/song/HGCAL/CMSSW_16_0_0_pre4/src dryRun for 'cd 34413.0_SingleElPt35Extended+Run4D121
 cmsDriver.py DoubleElectronPt35Extended_pythia8_cfi  -s GEN,SIM -n 100 --conditions auto:phase2_realistic_T33 --beamspot DBrealisticHLLHC --datatier GEN-SIM --eventcontent FEVTDEBUG --geometry ExtendedRun4D121 --era Phase2C22I13M9 --fileout file:step1.root --nThreads 8 --no_exec --python_filename step1.py


# in: /grid_mnt/data_cms_upgrade/song/HGCAL/CMSSW_16_0_0_pre4/src dryRun for 'cd 34413.0_SingleElPt35Extended+Run4D121
 cmsDriver.py step2  -s DIGI:pdigi_valid,L1TrackTrigger,L1,L1P2GT,DIGI2RAW,HLT:@relvalRun4 --conditions auto:phase2_realistic_T33 --datatier GEN-SIM-DIGI-RAW -n -1 --eventcontent FEVTDEBUGHLT --geometry ExtendedRun4D121 --era Phase2C22I13M9 --filein  file:step1.root  --fileout file:step2.root --nThreads 8 --no_exec --python_filename step2.py
 
 cmsDriver.py step2  -s DIGI:pdigi_valid,L1TrackTrigger,L1,L1P2GT,DIGI2RAW,HLT:@relvalRun4 --conditions auto:phase2_realistic_T33 --datatier GEN-SIM-DIGI-RAW -n -1 --eventcontent FEVTDEBUGHLT --geometry ExtendedRun4D121 --era Phase2C22I13M9 --pileup AVE_200_BX_25ns --pileup_input das:/RelValMinBias_14TeV/CMSSW_16_0_0_pre2-150X_mcRun4_realistic_v1_STD_RegeneratedGS_Run4D121_noPU-v1/GEN-SIM --filein  file:step1.root  --fileout file:step2.root --nThreads 8 --no_exec --python_filename step2_pu.py


# in: /grid_mnt/data_cms_upgrade/song/HGCAL/CMSSW_16_0_0_pre4/src dryRun for 'cd 34413.0_SingleElPt35Extended+Run4D121
 cmsDriver.py step3  -s RAW2DIGI,RECO,RECOSIM,PAT,VALIDATION:@phase2Validation+@miniAODValidation,DQM:@phase2+@miniAODDQM --conditions auto:phase2_realistic_T33 --datatier GEN-SIM-RECO,MINIAODSIM,DQMIO -n -1 --eventcontent FEVTDEBUGHLT,MINIAODSIM,DQM --geometry ExtendedRun4D121 --era Phase2C22I13M9 --filein  file:step2.root  --fileout file:step3.root  --procModifiers ticl_v5 --customise RecoHGCal/TICL/customiseTICLFromReco.customiseTICLForDumper --nThreads 8 --no_exec --python_filename step3.py
 

# in: /grid_mnt/data_cms_upgrade/song/HGCAL/CMSSW_16_0_0_pre4/src dryRun for 'cd 34413.0_SingleElPt35Extended+Run4D121
 cmsDriver.py step4  -s HARVESTING:@phase2Validation+@phase2+@miniAODValidation+@miniAODDQM --conditions auto:phase2_realistic_T33 --mc  --geometry ExtendedRun4D121 --scenario pp --filetype DQM --era Phase2C22I13M9 -n -1  --filein file:step3_inDQM.root --fileout file:step4.root --no_exec --python_filename step4.py
 

# in: /grid_mnt/data_cms_upgrade/song/HGCAL/CMSSW_16_0_0_pre4/src dryRun for 'cd 34413.0_SingleElPt35Extended+Run4D121
#  cmsDriver.py step5  -s ALCA:SiPixelCalSingleMuonLoose+SiPixelCalSingleMuonTight+TkAlMuonIsolated+TkAlMinBias+MuAlOverlaps+EcalESAlign+TkAlZMuMu+TkAlDiMuonAndVertex+HcalCalHBHEMuonProducerFilter+TkAlUpsilonMuMu+TkAlJpsiMuMu --conditions auto:phase2_realistic_T33 --datatier ALCARECO -n 10 --eventcontent ALCARECO --geometry ExtendedRun4D121 --era Phase2C22I13M9 --filein file:step3.root --fileout file:step5.root  > step5_SingleElPt35Extended+Run4D121.log  2>&1