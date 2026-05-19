import cmsstyle as cms
import ROOT as rt
import os
import sys
import math
import argparse

parser = argparse.ArgumentParser(description='Make plots from DQM files')
parser.add_argument('--energy', action='store_true', default=False, help='parameters for Si')
parser.add_argument('--logz', action='store_true', default=False)
parser.add_argument('--layers', type=int, nargs='+', default=[35], help='Layer numbers to plot')
dir_names = ['original_Sci', 'original_Si', 'dsci_0.01', 'dsci_0.05', 'dsci_0.1', 'dsci_0.2', 'dsi_1.0', 'dsi_1.5', 'dsi_2.0', 'dsi_2.5']
args = parser.parse_args()

latex_pts = {'photon_noPU_Si': '#gamma, no PU; default',
          'photon_PU_Si': '#gamma, 200 PU; default',
          'photon_noPU_Sci': '#gamma, no PU; default',
          'photon_PU_Sci': '#gamma, 200 PU; default',
          'original_Si': '#delta_{c} = 1.3, Silicon',
          'original_Sci': '#delta_{c} = 0.0315, Scintillator',
          'dsci_0.01': '#delta_{c} = 0.01, Scintillator',
          'dsci_0.05': '#delta_{c} = 0.05, Scintillator',
          'dsci_0.1': '#delta_{c} = 0.1, Scintillator',
          'dsci_0.2': '#delta_{c} = 0.2, Scintillator',
          'dsi_1.0': '#delta_{c} = 1.0, Silicon',
          'dsi_1.5': '#delta_{c} = 1.5, Silicon',
          'dsi_2.0': '#delta_{c} = 2.0, Silicon',
          'dsi_2.5': '#delta_{c} = 2.5, Silicon'}

rt.TH1.AddDirectory(False)
rt.TH1.SetDefaultSumw2(True)

canv = cms.cmsCanvas("c0", 0, 1, 0, 100, "", "", iPos=0, with_z_axis=True, yTitOffset=0.9, extraSpace=0.01, zExtra=0.05)
hframe = cms.GetcmsCanvasHist(canv)
hframe.GetXaxis().SetTitleSize(0.045)
hframe.GetYaxis().SetTitleSize(0.045)
hframe.GetXaxis().SetLabelSize(0.04)
hframe.GetYaxis().SetLabelSize(0.04)
hframe.GetXaxis().SetTitleOffset(1.20)
hframe.GetYaxis().SetTitleOffset(1.15)
cms.getCMSStyle().SetPalette(rt.kRainBow)
cms.SetLumi('HGCAL', unit=None)
cms.SetExtraText('')
cms.SetEnergy('')
cms.CMS_lumi(canv, 0)

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

def get_energy(dir_name, layerID):
    # cp, lc = [], []
    file = rt.TFile(os.path.join(dir_name, file_name))
    return get_object_by_path(file, os.path.join(path, f'TotalEnergy_vs_Score_layer2caloparticle_perlayer{layerID + 47}'))

def get_fraction(dir_name, layerID):
    # cp, lc = [], []
    file = rt.TFile(os.path.join(dir_name, file_name))
    return get_object_by_path(file, os.path.join(path, f'Energy_vs_Score_layer2caloparticle_perlayer{layerID + 47}'))
latex_pt = rt.TLatex()
latex_pt.SetTextFont(62)
latex_pt.SetTextAlign(21)
t = canv.GetTopMargin()
latex_pt.SetTextSize(cms.lumiTextSize * t * 0.9)

def draw_th2(h2, name, logz=False, latex=None):
    canv.cd()
    hframe.Draw()
    hframe.SetLineWidth(0)
    if logz:
        canv.SetLogz(True)
        h2.GetZaxis().SetLabelOffset(0.001)
    elif args.energy and 'sci' not in name:
        h2.GetZaxis().SetRangeUser(0, math.ceil(h2.GetMaximum() / 5000) * 5000 + 1000)
    cms.CMS_lumi(canv, 0)
    if h2.GetYaxis().GetXmax() > 10:
        hframe.GetYaxis().SetRangeUser(0, 50)
        hframe.GetYaxis().SetTitle('E_{LC}')
    else:
        hframe.GetYaxis().SetRangeUser(0, 1.02)
        hframe.GetYaxis().SetTitle('Purity_{LC}')
    hframe.GetXaxis().SetTitle('R2S score')
    h2.GetZaxis().SetTitleSize(0.05)
    h2.GetZaxis().SetLabelSize(0.04)
    h2.GetZaxis().SetMaxDigits(3)
    h2.GetZaxis().SetTitle('# LC')
    latex_pt.DrawLatexNDC(0.47, 1 - t + cms.lumiTextOffset * t + 0.005, latex)
    cms.cmsDraw(h2, "colz")
    cms.UpdatePad(canv)
    canv.Print(name + ".pdf")

prefix = "energy" if args.energy else "fraction"
for layerID in args.layers:
    print(f"Layer {layerID}:")
    for dir_name in dir_names:
        hist = get_energy(dir_name, layerID) if args.energy else get_fraction(dir_name, layerID)
        draw_th2(hist, f"plots/{prefix}_{dir_name}_layer{layerID}", logz=args.logz, latex=latex_pts.get(dir_name, "") + f", layer {layerID}")

        