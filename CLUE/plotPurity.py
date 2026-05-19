import cmsstyle as cms
import ROOT as rt
import os
import sys
import math
import argparse

parser = argparse.ArgumentParser(description='Make plots from DQM files')
parser.add_argument('--dc', choices=['si', 'sci', 'fh'], type=str, default='sci', help='parameters for different detector options')
parser.add_argument('--avg', action='store_true', default=False)
parser.add_argument('--focus', action='store_true', default=False)
parser.add_argument('--logy', action='store_true', default=False)
args = parser.parse_args()

petroff_10 = ["#3f90da", "#ffa90e", "#bd1f01", "#94a4a2", "#832db6", "#a96b59", "#e76300", "#b9ac70", "#717581", "#92dadd"]
petroff_8 = ["#ff5e02", "#1845fb", "#c91f16", "#c849a9", "#656364"]
colors = [rt.TColor.GetColor(p) for p in petroff_10]
colors.reverse()

dc = args.dc
name = dc
name += '_avg' if args.avg else ''
name += '_focus' if args.focus else ''
rt.TH1.AddDirectory(False)
rt.TH1.SetDefaultSumw2(True)

cms.setCMSStyle()
cms.cmsGrid(True)

canv = cms.cmsCanvas('c1', 0, 50, 0, 1.0, 'Layer Number in z+', 'Efficiency', square=False, iPos=0, extraSpace=0.06, yTitOffset=1.1)
hframe = cms.GetcmsCanvasHist(canv)
hframe.GetYaxis().SetMaxDigits(3)
hframe.Draw()
canv.SetRightMargin(0.05)
canv.SetBottomMargin(0.15)
canv.SetLeftMargin(0.15)
cms.UpdatePad(canv)
hframe.GetXaxis().SetTitleOffset(1.1)
cms.SetLumi('HGCAL', unit=None)
cms.SetExtraText('')
cms.SetEnergy('')
cms.CMS_lumi(canv, 0)
rt.TGaxis.SetExponentOffset(-0.5 * canv.GetLeftMargin(), 0.015, 'y')

line1 = rt.TLine(26, 0, 26, 1)
line2 = rt.TLine(33, 0, 33, 1)
line1.SetLineStyle(2)
line1.SetLineWidth(3)
line2.SetLineStyle(2)
line2.SetLineWidth(3)
def clear(ytitle='Efficiency', y_max=1, y_min=0, line=True):
    hframe.Draw()
    hframe.SetYTitle(ytitle)
    cms.CMS_lumi(canv, 0)
    if line:
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
def get_purity_avg(dir_name):
    # cp, lc = [], []
    file = rt.TFile(os.path.join(dir_name, file_name))
    start = 0 if args.focus else 33
    hist_pr = rt.TH1D('num_pr', '', 47 - start, start, 47)
    
    for i in range(hist_pr.GetNbinsX()):
        purity = get_object_by_path(file, os.path.join(path, f'SharedEnergy_layercluster2caloparticle_perlayer{i + start + 47}')).GetMean()
        error = get_object_by_path(file, os.path.join(path, f'SharedEnergy_layercluster2caloparticle_perlayer{i + start + 47}')).GetStdDev()
        hist_pr.SetBinError(i + 1, error)
        hist_pr.SetBinContent(i + 1, purity)
        # lc.append(get_object_by_path(file, os.path.join(path, f'Denom_LayerCluster_Eta_perlayer{i + 47}')).Integral())
        # cp.append(get_object_by_path(file, os.path.join(path, f'Denom_CaloParticle_Eta_perlayer{i + 47}')).Integral())
    return hist_pr

def get_purity(dir_name, avg=False):
    # cp, lc = [], []
    file = rt.TFile(os.path.join(dir_name, file_name))
    start = 0 if not args.focus else 33 if dc != 'fh' else 26
    end = 47 if not args.focus else 47 if dc != 'fh' else 33
    hist_pr = rt.TH1D('num_pr', '', end - start, start, end)
    h_temp = get_object_by_path(file, os.path.join(path, 'SharedEnergy_layercl2caloparticle_perlayer' + ('_avg' if avg else '')))
    for i in range(hist_pr.GetNbinsX()):
        hist_pr.SetBinError(i + 1, h_temp.GetBinError(i + start + 48))
        hist_pr.SetBinContent(i + 1, h_temp.GetBinContent(i + start + 48))
        # lc.append(get_object_by_path(file, os.path.join(path, f'Denom_LayerCluster_Eta_perlayer{i + 47}')).Integral())
        # cp.append(get_object_by_path(file, os.path.join(path, f'Denom_CaloParticle_Eta_perlayer{i + 47}')).Integral())
    return hist_pr

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
          'dsi_2.5': '#delta_{c}: 2.5 (Si)',
          'original_FH': '#delta_{c}: 1.3 (Si, FH)',
          'dfh_1.0': '#delta_{c}: 1.0 (Si, FH)',
          'dfh_1.5': '#delta_{c}: 1.5 (Si, FH)',
          'dfh_2.0': '#delta_{c}: 2.0 (Si, FH)',
          'dfh_2.5': '#delta_{c}: 2.5 (Si, FH)'
        }
# legend['original'] = legend['original_Si'] if dsi else legend['original_Sci']
dir_names = ['dsci_0.01', 'original_Sci', 'dsci_0.05', 'dsci_0.1', 'dsci_0.2'] if dc == 'sci' else [
    'dsi_1.0', 'original_Si', 'dsi_1.5', 'dsi_2.0', 'dsi_2.5'] if dc == 'si' else ['dfh_1.0', 'original_FH', 'dfh_1.5', 'dfh_2.0', 'dfh_2.5']


colors = [2, 4, 1, 8, colors[4]]
hists = []
y_max = 1.1
for dir_name in dir_names:
    hist = get_purity(dir_name, args.avg)
    hists.append(hist)

if not args.focus:
    clear(ytitle='Purity', y_max=y_max)
    draw_text(y_text=0.95, y_max=y_max)
    hframe.GetYaxis().SetRangeUser(0, y_max)
    leg_pos = (0.2, 0.65, 0.5, 0.85) if dc != 'sci' and args.avg else (0.25, 0.20, 0.55, 0.4)
else:
    clear(ytitle='Purity', y_max=y_max, line=False)
    if dc != 'fh':
        hframe.GetXaxis().SetRangeUser(33, 47)
        hframe.GetYaxis().SetRangeUser(0.8, 1.05)
    else:
        hframe.GetXaxis().SetRangeUser(26, 33)
        hframe.GetYaxis().SetRangeUser(0.4, 1.0)
    leg_pos = (0.2, 0.75, 0.45, 0.9) if dc != 'sci' and args.avg else (0.2, 0.2, 0.45, 0.4)
leg = cms.cmsLeg(*leg_pos, textSize=0.02, columns=1)
leg.SetFillStyle(1001)
leg.SetBorderSize(1)
for i, dir_name in enumerate(dir_names):
    cms.cmsDraw(hists[i], 'hist', lcolor=colors[i], lwidth=2, msize=0, fstyle=0)
    leg.AddEntry(hists[i], legend[dir_name], 'l')

leg.Draw("same")
cms.UpdatePad(canv)
canv.Print(f'plots/purity_{name}.pdf')
