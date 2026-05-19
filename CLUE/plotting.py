import cmsstyle as cms
import ROOT as rt
import os
import sys
import math
import argparse

petroff_10 = ["#3f90da", "#ffa90e", "#bd1f01", "#94a4a2", "#832db6", "#a96b59", "#e76300", "#b9ac70", "#717581", "#92dadd"]
petroff_8 = ["#ff5e02", "#1845fb", "#c91f16", "#c849a9", "#656364"]
colors = [rt.TColor.GetColor(p) for p in petroff_10]
colors.reverse()

rt.TH1.AddDirectory(False)
rt.TH1.SetDefaultSumw2(True)

cms.setCMSStyle()
cms.cmsGrid(True)

file_name = 'DQM_V0001_R000000001__Global__CMSSW_X_Y_Z__RECO.root'
path = 'DQMData/Run 1/HGCAL/Run summary/HGCalValidator/LayerClusters/LCToCP_association'

def get_object_by_path(root_file, path):
    parts = path.strip("/").split("/")
    obj_name = parts[-1]
    dirs = parts[:-1]
    current_dir = root_file
    for d in dirs:
        current_dir = current_dir.GetDirectory(d)
        if not current_dir:
            print(f"Directory '{d}' not found!")
            return None
    obj = current_dir.Get(obj_name)
    if not obj:
        print(f"Object '{obj_name}' not found in path '{'/'.join(dirs)}'")
    return obj
legend = {'photon_noPU_Si': '#gamma, no PU; default',
          'photon_PU_Si': '#gamma, 200 PU; default',
          'photon_noPU_Sci': '#gamma, no PU; default',
          'photon_PU_Sci': '#gamma, 200 PU; default',
          'original_Si': '#delta_{c}: 1.3 (Si); default',
          'original_Sci': '#delta_{c}: 0.0315 (Sci); default',
          'dsci_0.01': '#delta_{c}: 0.01 (Sci)',
          'dsci_0.05': '#delta_{c}: 0.05 (Sci)',
          'dsci_0.1': '#delta_{c}: 0.1 (Sci)',
          'dsci_0.2': '#delta_{c}: 0.2 (Sci)',
          'dsi_1.0': '#delta_{c}: 1.0 (Si)',
          'dsi_1.5': '#delta_{c}: 1.5 (Si)',
          'dsi_2.0': '#delta_{c}: 2.0 (Si)',
          'dsi_2.5': '#delta_{c}: 2.5 (Si)'}
def to_p_string(x: float) -> str:
    if x == int(x):
        return str(int(x))
    s = str(x)
    if '.' in s:
        s = s.replace('.', 'p', 1)
    s = s.rstrip('0')
    if s.endswith('p'):
        s = s[:-1]
    return s
