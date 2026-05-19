import cmsstyle as cms
import ROOT as rt
import os
import sys
import math
import argparse

parser = argparse.ArgumentParser(description='Make plots from DQM files')
parser.add_argument('--logz', action='store_true', default=False)
parser.add_argument('--layer', action='store_true', default=False)
parser.add_argument('--avg', action='store_true', default=False)
dir_names = ['original_FH', 'dfh_1.0', 'dfh_1.5', 'dfh_2.0', 'dfh_2.5']
args = parser.parse_args()

latex_pts = {'photon_noPU_Si': '#gamma, no PU; default',
          'photon_PU_Si': '#gamma, 200 PU; default',
          'photon_noPU_Sci': '#gamma, no PU; default',
          'photon_PU_Sci': '#gamma, 200 PU; default',
          'original_Si': '#delta_{c} = 1.3, Silicon',
          'original_Sci': '#delta_{c} = 0.0315, Scintillator',
          'original_FH': '#delta_{c} = 1.3, Silicon, FH',
          'dsci_0.01': '#delta_{c} = 0.01, Scintillator',
          'dsci_0.05': '#delta_{c} = 0.05, Scintillator',
          'dsci_0.1': '#delta_{c} = 0.1, Scintillator',
          'dsci_0.2': '#delta_{c} = 0.2, Scintillator',
          'dsi_1.0': '#delta_{c} = 1.0, Silicon, BH',
          'dsi_1.5': '#delta_{c} = 1.5, Silicon, BH',
          'dsi_2.0': '#delta_{c} = 2.0, Silicon, BH',
          'dsi_2.5': '#delta_{c} = 2.5, Silicon, BH',
          'dfh_1.0': '#delta_{c} = 1.0, Silicon, FH',
          'dfh_1.5': '#delta_{c} = 1.5, Silicon, FH',
          'dfh_2.0': '#delta_{c} = 2.0, Silicon, FH',
          'dfh_2.5': '#delta_{c} = 2.5, Silicon, FH'}

rt.TH1.AddDirectory(False)
rt.TH1.SetDefaultSumw2(True)

canv = cms.cmsCanvas("c0", 0, 47, 0, 100, "", "", iPos=0, with_z_axis=True, yTitOffset=0.9, extraSpace=0.02, zExtra=0.035)
hframe = cms.GetcmsCanvasHist(canv)
hframe.GetXaxis().SetTitleSize(0.045)
hframe.GetYaxis().SetTitleSize(0.045)
hframe.GetXaxis().SetLabelSize(0.04)
hframe.GetYaxis().SetLabelSize(0.04)
hframe.GetXaxis().SetTitleOffset(1.20)
hframe.GetYaxis().SetTitleOffset(1.45)
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


def get_purity(dir_name, avg=False, layer=False):
    file = rt.TFile(os.path.join(dir_name, file_name))
    if layer:
        hist = rt.TH2D('h2', '', 47, 0, 47, 55, 0, 110)
        name = 'SharedEnergy_layercaloenergy_layercl2caloparticle' + ('_avg' if avg else '') + '_perlayer'
    else:
        hist = rt.TH2D('h2', '', 47, 0, 47, 100, 0, 1000)
        name = 'SharedEnergy_caloenergy_layercl2caloparticle' + ('_avg' if avg else '') + '_perlayer'
    hprofile = get_object_by_path(file, os.path.join(path, name))
    for i in range(1, hist.GetNbinsX() + 1):
        for j in range(1, hist.GetNbinsY() + 1):
            hist.SetBinContent(i, j, hprofile.GetBinContent(i + 47, j))
            hist.SetBinError(i, j, hprofile.GetBinError(i + 47, j))
    return hist
latex_pt = rt.TLatex()
latex_pt.SetTextFont(62)
latex_pt.SetTextAlign(21)
t = canv.GetTopMargin()
latex_pt.SetTextSize(cms.lumiTextSize * t * 0.9)

line1 = rt.TLine(26, 0, 26, 1)
line2 = rt.TLine(33, 0, 33, 1)
line1.SetLineStyle(2)
line1.SetLineWidth(3)
line2.SetLineStyle(2)
line2.SetLineWidth(3)
def draw_line(y_max=1, y_min=0):
    line1.SetY2(y_max)
    line2.SetY2(y_max)
    line1.SetY1(y_min)
    line2.SetY1(y_min)
    line1.Draw('same')
    line2.Draw('same')
def draw_text(y_text=0.6, y_max=1, y_min=0):
    regions = [
        (0, 26, "EE"),
        (26, 33, "FH"),
        (33, 47, "BH"),
    ]

    latex = rt.TLatex()
    latex.SetTextAlign(22)
    latex.SetTextSize(0.04)

    for (x_min, x_max, label) in regions:
        x_mid = 0.5 * (x_min + x_max)
        latex.DrawLatex(x_mid, y_text * (y_max - y_min) + y_min, label)

def draw_th2(h2, name, logz=False, latex=None):
    canv.cd()
    hframe.Draw()
    cms.CMS_lumi(canv, 0)
    hframe.SetLineWidth(0)
    if logz:
        canv.SetLogz(True)
        h2.GetZaxis().SetLabelOffset(0.001)
    if h2.GetYaxis().GetXmax() > 200:
        hframe.GetYaxis().SetRangeUser(0, 1000)
        hframe.GetYaxis().SetTitle('CaloParticle Energy [GeV]')
    else:
        hframe.GetYaxis().SetRangeUser(0, 110)
        hframe.GetYaxis().SetTitle('CaloParticle Energy per layer [GeV]')
    hframe.GetXaxis().SetTitle('Layer number in z+')
    h2.GetZaxis().SetTitleSize(0.05)
    h2.GetZaxis().SetRangeUser(0, 1.)
    h2.GetZaxis().SetLabelSize(0.04)
    h2.GetZaxis().SetTitleOffset(1.1)
    h2.GetZaxis().SetMaxDigits(3)
    h2.GetZaxis().SetTitle('Purity')
    latex_pt.DrawLatexNDC(0.47, 1 - t + cms.lumiTextOffset * t + 0.005, latex)
    cms.cmsDraw(h2, "colz")
    draw_line(0, h2.GetYaxis().GetXmax())
    draw_text(0.6, h2.GetYaxis().GetXmax(), 0)
    cms.UpdatePad(canv)
    canv.Print(name + ".pdf")

for dir_name in dir_names:
    hist = get_purity(dir_name, avg=args.avg, layer=args.layer)
    draw_th2(hist, f"plots/purity2D_{dir_name}{'_layer' if args.layer else ''}{'_avg' if args.avg else ''}", logz=args.logz, latex=latex_pts.get(dir_name, ""))
