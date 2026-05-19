cmsDriver.py DoubleElectronPt35Extended_pythia8_cfi  -s GEN,SIM -n 100 \
--conditions auto:phase2_realistic_T33 --geometry ExtendedRun4D110  --era Phase2C17I13M9 \
--eventcontent FEVTDEBUG --datatier GEN-SIM --fileout file:step1.root --nThreads 8 --no_exec \
--beamspot DBrealisticHLLHC --python_filename step1.py

cmsDriver.py step2 -s DIGI:pdigi_valid,L1TrackTrigger,L1,L1P2GT,DIGI2RAW,HLT:@relvalRun4 \
--conditions auto:phase2_realistic_T33 --datatier GEN-SIM-DIGI-RAW --eventcontent FEVTDEBUGHLT \
--geometry ExtendedRun4D110 --era Phase2C17I13M9 --filein file:step1.root \
--fileout file:step2.root -n -1 --nThreads 8 --no_exec --python_filename step2.py

cmsDriver.py step2 -s DIGI:pdigi_valid,L1TrackTrigger,L1,L1P2GT,DIGI2RAW,HLT:@relvalRun4 \
--conditions auto:phase2_realistic_T33 --datatier GEN-SIM-DIGI-RAW --eventcontent FEVTDEBUGHLT \
--geometry ExtendedRun4D110 --era Phase2C17I13M9 --pileup AVE_200_BX_25ns \
--pileup_input das:/RelValMinBias_14TeV/CMSSW_14_1_0_pre5-140X_mcRun4_realistic_v4_RegeneratedGS_2026D110_noPU-v1/GEN-SIM \
--filein  file:step1.root --fileout file:step2.root -n -1 --nThreads 8 --no_exec --python_filename step2_pu.py

cmsDriver.py step3  -s RAW2DIGI,RECO,RECOSIM,PAT,VALIDATION:@phase2Validation+@miniAODValidation,DQM:@phase2+@miniAODDQM \
--conditions auto:phase2_realistic_T33 --datatier GEN-SIM-RECO,MINIAODSIM,DQMIO --eventcontent FEVTDEBUGHLT,MINIAODSIM,DQM \
--geometry ExtendedRun4D110 --era Phase2C17I13M9 --filein file:step2.root --fileout file:step3.root \
-n -1 --procModifiers ticl_v5 --customise RecoHGCal/TICL/customiseTICLFromReco.customiseTICLForDumper \
--nThreads 8 --no_exec --python_filename step3.py

cmsDriver.py step4  -s HARVESTING:@phase2Validation+@phase2+@miniAODValidation+@miniAODDQM \
--conditions auto:phase2_realistic_T33 --mc --geometry ExtendedRun4D110 --scenario pp --filetype DQM \
--era Phase2C17I13M9 -n -1 --filein file:step3_inDQM.root --fileout file:step4.root --no_exec \
--python_filename step4.py