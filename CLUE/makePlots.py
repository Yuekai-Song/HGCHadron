import cmsstyle as cms
import ROOT as rt
import os
import sys
import math
import argparse

parser = argparse.ArgumentParser(description='Make plots from DQM files')
parser.add_argument('--dsi', action='store_true', default=False, help='parameters for Si')
parser.add_argument('--r2s', type=float, default=0.1, help='R2S cut')
parser.add_argument('--s2r', type=float, default=0.1, help='S2R cut')
parser.add_argument('--purity', action='store_true', default=False)
parser.add_argument('--layer', action='store_true', default=False)
parser.add_argument('--tp', action='store_true', default=False)
parser.add_argument('--no2x2', action='store_true', default=False)
parser.add_argument('--logy', action='store_true', default=False)
args = parser.parse_args()

petroff_10 = ["#3f90da", "#ffa90e", "#bd1f01", "#94a4a2", "#832db6", "#a96b59", "#e76300", "#b9ac70", "#717581", "#92dadd"]
petroff_8 = ["#ff5e02", "#1845fb", "#c91f16", "#c849a9", "#656364"]
colors = [rt.TColor.GetColor(p) for p in petroff_10]
colors.reverse()
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

dsi = args.dsi
name = 'dsi' if args.dsi else 'dsci'
r2s = to_p_string(args.r2s)
s2r = to_p_string(args.s2r)

rt.TH1.AddDirectory(False)
rt.TH1.SetDefaultSumw2(True)

cms.setCMSStyle()
cms.cmsGrid(True)
if args.layer:
    canv = cms.cmsCanvas('c1', 0, 47, 0, 1.0, 'Layer Number in z+', 'Efficiency', square=False, iPos=0, extraSpace=0.06, yTitOffset=1.1)
else:
    canv = cms.cmsCanvas('c1', 0, 5, 0, 1000, 'E_{LCs} / E_{CP}', '#CP', square=True, iPos=0, extraSpace=0.06, yTitOffset=1.2)
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
def clear(ytitle='Efficiency', y_max=1, y_min=0):
    hframe.Draw()
    hframe.SetYTitle(ytitle)
    cms.CMS_lumi(canv, 0)
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

def get_nb(dir_name):
    # cp, lc = [], []
    file = rt.TFile(os.path.join(dir_name, file_name))
    hist_cp = rt.TH1D('num_cp', '', 47, 0, 47)
    hist_lc = rt.TH1D('num_lc', '', 47, 0, 47)
    n_cp = get_object_by_path(file, os.path.join(path, f'Responce_reco2sim_cut1')).Integral()
    for i in range(hist_cp.GetNbinsX()):
        num_lc = get_object_by_path(file, os.path.join(path, f'Denom_LayerCluster_Eta_perlayer{i + 47}')).Integral()
        num_cp = get_object_by_path(file, os.path.join(path, f'Denom_CaloParticle_Eta_perlayer{i + 47}')).Integral()
        hist_cp.SetBinContent(i + 1, num_cp)
        hist_lc.SetBinContent(i + 1, num_lc / n_cp)
        # lc.append(get_object_by_path(file, os.path.join(path, f'Denom_LayerCluster_Eta_perlayer{i + 47}')).Integral())
        # cp.append(get_object_by_path(file, os.path.join(path, f'Denom_CaloParticle_Eta_perlayer{i + 47}')).Integral())
    return hist_lc, hist_cp

def get_purity(dir_name):
    # cp, lc = [], []
    file = rt.TFile(os.path.join(dir_name, file_name))
    hist_pr = rt.TH1D('num_pr', '', 47, 0, 47)
    h_temp = get_object_by_path(file, os.path.join(path, f'SharedEnergy_caloparticle2layercl_perlayer_avg')).Integral()
    for i in range(hist_pr.GetNbinsX()):
        hist_pr.SetBinError(i + 1, h_temp.GetBinError(i + 48))
        hist_pr.SetBinContent(i + 1, h_temp.GetBinContent(i + 48))
        # lc.append(get_object_by_path(file, os.path.join(path, f'Denom_LayerCluster_Eta_perlayer{i + 47}')).Integral())
        # cp.append(get_object_by_path(file, os.path.join(path, f'Denom_CaloParticle_Eta_perlayer{i + 47}')).Integral())
    return hist_pr
def get_purity_avg(dir_name):
    # cp, lc = [], []
    file = rt.TFile(os.path.join(dir_name, file_name))
    hist_pr = rt.TH1D('num_pr', '', 47, 0, 47)
    
    for i in range(hist_pr.GetNbinsX()):
        purity = get_object_by_path(file, os.path.join(path, f'SharedEnergy_layercluster2caloparticle_perlayer{i + 47}')).GetMean()
        error = get_object_by_path(file, os.path.join(path, f'SharedEnergy_layercluster2caloparticle_perlayer{i + 47}')).GetStdDev()
        hist_pr.SetBinError(i + 1, error)
        hist_pr.SetBinContent(i + 1, purity)
        # lc.append(get_object_by_path(file, os.path.join(path, f'Denom_LayerCluster_Eta_perlayer{i + 47}')).Integral())
        # cp.append(get_object_by_path(file, os.path.join(path, f'Denom_CaloParticle_Eta_perlayer{i + 47}')).Integral())
    return hist_pr

def get_purity(dir_name):
    # cp, lc = [], []
    file = rt.TFile(os.path.join(dir_name, file_name))
    hist_pr = rt.TH1D('num_pr', '', 47, 0, 47)
    h_temp = get_object_by_path(file, os.path.join(path, f'SharedEnergy_caloparticle2layercl_perlayer_avg')).Integral()
    for i in range(hist_pr.GetNbinsX()):
        hist_pr.SetBinError(i + 1, h_temp.GetBinError(i + 48))
        hist_pr.SetBinContent(i + 1, h_temp.GetBinContent(i + 48))
        # lc.append(get_object_by_path(file, os.path.join(path, f'Denom_LayerCluster_Eta_perlayer{i + 47}')).Integral())
        # cp.append(get_object_by_path(file, os.path.join(path, f'Denom_CaloParticle_Eta_perlayer{i + 47}')).Integral())
    return hist_pr

def get_responce(dir_name):
    # cp, lc = [], []
    file = rt.TFile(os.path.join(dir_name, file_name))

    res_all = get_object_by_path(file, os.path.join(path, f'Responce_reco2sim_cut{r2s}'))
    res_h = get_object_by_path(file, os.path.join(path, f'Responce_H_reco2sim_cut{r2s}'))
    res_e = get_object_by_path(file, os.path.join(path, f'Responce_E_reco2sim_cut{r2s}'))
    for hist in [res_all, res_e, res_h]:
        hist.GetXaxis().SetRangeUser(0.9, 1.2)
    return res_all, res_h, res_e

# tps = {'fake': {'frac': ('Denom_LayerCluster_Eta', 'Num_LayerCluster_Eta'), 'bin_range': None},
#        'eff_cp': {'frac': ('Denom_CaloParticle_Eta', 'Num_CaloParticle_Eta'), 'bin_range': None},
#        'eff_lc': {'frac': ('Denom_LayerCluster_Eta', 'Nums_LayerCluster_Eta'), 'bin_range': None},
#        'rp_r2s': {'frac': ('Denom_CaloParticle_Eta', 'Responce_reco2sim'), 'bin_range': (0.8, 1.2)},
#        'rp_s2r': {'frac': ('Denom_CaloParticle_Eta', 'Responce_sim2reco'), 'bin_range': (0.8, 1.2)}}

tps = {
    # 'fr_LC': {'frac': ('Denom_LayerCluster_Eta', f'Num_LayerCluster_perlayer_cut_{r2s}'), 'leg': (0.20, 0.65, 0.50, 0.90), 'y_text': 0.6, 'ytitle': 'Fake Rate', 'output': f'fr_LC_{name}_{r2s}', 'fake': True},
    # 'eff_CP': {'frac': ('Denom_CaloParticle_Eta', f'Num_CaloParticle_perlayer_cut_{s2r}'), 'leg': (0.20, 0.20, 0.50, 0.45), 'y_text': 0.9, 'ytitle': 'Efficiency (CP)', 'output': f'eff_CP_{name}_{s2r}'},
    # 'eff_LC': {'frac': ('Denom_LayerCluster_Eta', f'Nums_LayerCluster_perlayer_cut_{s2r}'), 'leg': (0.25, 0.45, 0.55, 0.70), 'y_text': 0.9, 'ytitle': 'Efficiency (LC)', 'output': f'eff_LC_{name}_{s2r}'},
    'rp_r2s': {'frac': ('', f'Responce_reco2sim_perlayer_cut{r2s}'), 'leg': (0.26, 0.77, 0.95, 0.9), 'y_text': 0.75, 'ytitle': 'E_{LCs} / E_{CP}', 'output': f'rp_r2s_{name}_{r2s}', 'mean': True, 'yrange': (0, 3), 'lcolumn': 3},
    'rp_s2r': {'frac': ('', f'Responce_sim2reco_perlayer_cut{s2r}'), 'leg': (0.26, 0.77, 0.95, 0.9), 'y_text': 0.75, 'ytitle': 'E_{LCs} / E_{CP}', 'output': f'rp_s2r_{name}_{s2r}', 'mean': True, 'yrange': (0., 3.), 'lcolumn': 3}
}

def get_hists(dir_names, tp, fake=False, mean=False):
    hists = []
    for dir_name in dir_names:
        file = rt.TFile(os.path.join(dir_name, file_name))
        eff = rt.TH1D('efficiency', '', 47, 0, 47)
        h_denom = rt.TH1D('denom', '', 47, 0, 47)
        if not mean:
            for i in range(eff.GetNbinsX()):
                denom = get_object_by_path(file, os.path.join(path, f"{tps[tp]['frac'][0]}_perlayer{i + 47}")).Integral()
                num = get_object_by_path(file, os.path.join(path, f"{tps[tp]['frac'][1]}")).GetBinContent(i + 48)
                # h_num = get_object_by_path(file, os.path.join(path, f"{tps[tp]['frac'][1]}_perlayer{i + 47}"))
                # if tps[tp]['bin_range'] is None:
                #     num = h_num.Integral()
                # else:
                #     bin_x1 = h_num.FindBin(tps[tp]['bin_range'][0])
                #     bin_x2 = h_num.FindBin(tps[tp]['bin_range'][1])
                #     num = h_num.Integral(bin_x1, bin_x2)
                h_denom.SetBinContent(i + 1, denom)
                eff.SetBinContent(i + 1, num)
                h_denom.SetBinError(i + 1, math.sqrt(denom))
                eff.SetBinError(i + 1, math.sqrt(num))
            eff.Divide(h_denom)
            if fake:
                eff_in = rt.TH1D('fake_rate', '', 47, 0, 47)
                for i in range(eff_in.GetNbinsX()):
                    eff_in.SetBinContent(i + 1, 1)
                eff_in.Add(eff, -1)
                eff = eff_in
        else:
            for i in range(eff.GetNbinsX()):
                val = get_object_by_path(file, os.path.join(path, tps[tp]['frac'][1].replace('perlayer', f'perlayer{i + 47}'))).GetMean()
                err = get_object_by_path(file, os.path.join(path, tps[tp]['frac'][1].replace('perlayer', f'perlayer{i + 47}'))).GetStdDev()
                eff.SetBinContent(i + 1, val)
                eff.SetBinError(i + 1, err)
        hists.append(eff)
        file.Close()
    return hists


# dir_names = ['dc_1.1_0.02', 'dc_1.2_0.025', 'original', 'dc_1.5_0.04', 'dc_1.7_0.05', 'dc_1.9_0.06']
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
# legend['original'] = legend['original_Si'] if dsi else legend['original_Sci']
dir_names = ['photon_noPU_Sci', 'photon_PU_Sci', 'dsci_0.01', 'original_Sci', 'dsci_0.05', 'dsci_0.1', 'dsci_0.2'] if not dsi else [
    'photon_noPU_Si', 'photon_PU_Si', 'dsi_1.0', 'original_Si', 'dsi_1.5', 'dsi_2.0', 'dsi_2.5']
real_dir_names = [os.path.join('NoUse2x2', d) for d in dir_names] if args.no2x2 else dir_names
style = ['PC' if i % 2 == 0 or i < 2 else 'Hist' for i in range(len(dir_names))]
# style = ['PE' for i in range(len(dir_names))]
lstyle = ['Pl' if i % 2 == 0 or i < 2 else 'l' for i in range(len(dir_names))]
# lstyle = ['PEl' for i in range(len(dir_names))]
# colors = [2, 41, 1, 8, 4]

latex_pt = rt.TLatex()
latex_pt.SetTextFont(62)
latex_pt.SetTextAlign(21)
t = canv.GetTopMargin()
latex_pt.SetTextSize(cms.lumiTextSize * t)


if args.purity:
    colors = [colors[3], colors[5], 2, 4, 1, 8, colors[4]]
    style = ['PE' for i in range(len(dir_names))]
    lstyle = ['PEl' for i in range(len(dir_names))]
    hists = []
    y_max = 0
    for dir_name in dir_names:
        hist = get_purity_avg(dir_name)
        hists.append(hist)
        y_max = max(y_max, hist.GetMaximum() * 1.4)
    clear(ytitle='Purity', y_max=y_max)
    leg = cms.cmsLeg(0.2, 0.70, 0.5, 0.87, textSize=0.02, columns=1)
    leg.SetFillStyle(1001)
    leg.SetBorderSize(1)
    for i, dir_name in enumerate(dir_names):
        cms.cmsDraw(hists[i], style[i], lcolor=colors[i], lwidth=2, msize=0.65, mcolor=colors[i], fstyle=0)
        leg.AddEntry(hists[i], legend[dir_name], 'l')
    leg.Draw("same")
    draw_text(y_text=0.95, y_max=y_max)
    hframe.GetYaxis().SetRangeUser(0, y_max)
    cms.UpdatePad(canv)
    canv.Print(f'plots/purity_{name}.pdf')
    exit(0)
if args.layer and args.tp:
    colors = [colors[3], colors[5], 2, 4, 1, 8, colors[4]]
    style = ['PE' for i in range(len(dir_names))]
    lstyle = ['PEl' for i in range(len(dir_names))]
    for tp, cfg in tps.items():
        mean = False if 'mean' not in cfg else cfg['mean']
        fake = False if 'fake' not in cfg else cfg['fake']
        yrange = (0, 1) if 'yrange' not in cfg else cfg['yrange']
        lcolumn = 1 if 'lcolumn' not in cfg else cfg['lcolumn']
        # print(mean, fake)
        hists = get_hists(dir_names, tp, fake=fake, mean=mean)
        clear(ytitle=cfg['ytitle'], y_max=yrange[1], y_min=yrange[0])
        # hframe.GetYaxis().SetRangeUser(1e-5, 1)'leg': (0.26, 0.77, 0.95, 0.9)
        leg = cms.cmsLeg(0.3, 0.8, 0.8, 0.9, textSize=0.02, columns=lcolumn)
        # leg = cms.cmsLeg(*cfg['leg'], textSize=0.02, columns=lcolumn)
        leg.SetFillStyle(1001)
        leg.SetBorderSize(1)
        for i, dir_name in enumerate(dir_names):
            cms.cmsDraw(hists[i], style[i], lcolor=colors[i], msize=0.65, mcolor=colors[i], fstyle=0, lwidth=1, lalpha=0.9)
            leg.AddEntry(hists[i], legend[dir_name], lstyle[i])

        leg.Draw("same")
        draw_text(y_text=cfg['y_text'], y_max=yrange[1], y_min=yrange[0])
        lpt = f'Score_{{R2S}} < {args.r2s}' if 'r2s' in tp else f'Score_{{S2R}} < {args.s2r}'
        latex_pt.DrawLatexNDC(0.55, 1 - t + cms.lumiTextOffset * t + 0.005, lpt)
        hframe.GetYaxis().SetRangeUser(*yrange)
        cms.UpdatePad(canv)
        canv.Print(f"plots/{cfg['output']}.pdf")

# legs = ['default with CP from PU', 'default']
if args.layer and not args.tp and s2r == '0p1' and r2s == '0p1':
    hists = []
    y_max = 0
    colors = [colors[3], colors[5], 2, 4, 1, 8, colors[4]]
    for dir_name in dir_names:
        hist = get_nb(dir_name)[0]
        hists.append(hist)
        y_max = max(y_max, hist.GetMaximum() * 1.4)
    clear(ytitle='#LC / #CP', y_max=y_max)
    # style = ['CP' for i in range(len(dir_names))]
    leg = cms.cmsLeg(0.2, 0.70, 0.5, 0.87, textSize=0.02, columns=1)
    leg.SetFillStyle(1001)
    leg.SetBorderSize(1)
    # lstyle = ['Pl' for i in range(len(dir_names))]
    for i, dir_name in enumerate(dir_names):
        cms.cmsDraw(hists[i], style[i], lcolor=colors[i], lwidth=2, msize=0.65, mcolor=colors[i], fstyle=0)
        leg.AddEntry(hists[i], legend[dir_name], lstyle[i])
    leg.Draw("same")
    draw_text(y_text=0.95, y_max=y_max)
    hframe.GetYaxis().SetRangeUser(0, y_max)
    cms.UpdatePad(canv)
    canv.Print(f'plots/num_LC_{name}.pdf')

if not args.layer:
    colors = [2, 4, 1, 8, colors[4], colors[3], colors[5],]
    ex_offset = -0.65
    ey_offset = 0.015
    latex_fil = rt.TLatex()
    latex_fil.SetTextFont(62)
    latex_fil.SetTextAlign(21)
    latex_fil.SetTextSize(cms.lumiTextSize * t)

    rt.TGaxis.SetExponentOffset(ex_offset * canv.GetLeftMargin(), ey_offset, 'y')
    filters = ['', '_H', '_E']
    texts = ['', '#frac{E_{HAD}}{E_{tot}} > 0.9', '#frac{E_{EM}}{E_{tot}} > 0.9']
    cut_text = f'Score_{{R2S}} < {args.r2s}'
    hframe.GetXaxis().SetRangeUser(0.9, 1.2)
    ymin = 0
    yscale = 1.4
    if args.logy:
        canv.SetLogy(True)
        ymin = 1e-4
        yscale = 1000
    for ii in range(3):
        y_max = 0
        hframe.Draw()
        cms.CMS_lumi(canv, 0)
        out = filters[ii] + ('_Si' if args.dsi else '_Sci')
        hists = []
        for dir_name in real_dir_names:
            if 'photon' in dir_name:
                continue
            hist = get_responce(dir_name)[ii]
            print(hist.Integral())
            hists.append(hist)
            y_max = max(y_max, hist.GetMaximum() * yscale)
        hframe.GetYaxis().SetRangeUser(ymin, y_max)
        leg = cms.cmsLeg(0.6, 0.7, 0.92, 0.90, textSize=0.025, columns=1)
        leg.SetFillStyle(1001)
        leg.SetBorderSize(1)
        i = 0
        for dir_name in dir_names:
            if 'photon' in dir_name:
                continue
            cms.cmsDraw(hists[i], 'hist', lcolor=colors[i], lwidth=2, msize=0.65, mcolor=colors[i], fstyle=0)
            leg.AddEntry(hists[i], legend[dir_name], 'l')
            i += 1
        if texts[ii]:
            latex_fil.DrawLatexNDC(0.35, 0.85, texts[ii])
            latex_fil.DrawLatexNDC(0.35, 0.75, cut_text)
        else:
            latex_fil.DrawLatexNDC(0.35, 0.8, cut_text)
        leg.Draw("same")
        cms.UpdatePad(canv)
        canv.Print(f"plots/{'NoUse2x2/' if args.no2x2 else ''}responce{out}_cut{r2s}.pdf")