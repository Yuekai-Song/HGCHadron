from plotting import *
parser = argparse.ArgumentParser(description='Make plots from DQM files')
parser.add_argument('--dsi', action='store_true', default=False, help='parameters for Si')
parser.add_argument('--r2s', type=float, default=0.1, help='R2S cut')
parser.add_argument('--wide', action='store_true', default=False)
parser.add_argument('--logy', action='store_true', default=False)
args = parser.parse_args()

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
r2s = to_p_string(args.r2s)

def get_responce(dir_name):
    # cp, lc = [], []
    file = rt.TFile(os.path.join(dir_name, file_name))

    res_all = get_object_by_path(file, os.path.join(path, f'Responce_reco2sim_cut{r2s}'))
    res_h = get_object_by_path(file, os.path.join(path, f'Responce_H_reco2sim_cut{r2s}'))
    res_e = get_object_by_path(file, os.path.join(path, f'Responce_E_reco2sim_cut{r2s}'))
    for hist in [res_all, res_e, res_h]:
        if not args.wide:
            hist.GetXaxis().SetRangeUser(0.9, 1.2)
        else:
            hist.GetXaxis().SetRangeUser(0.8, 1.6)
            hist.Rebin(5)
    return res_all, res_h, res_e

dir_names = ['photon_noPU_Sci', 'photon_PU_Sci', 'dsci_0.01', 'original_Sci', 'dsci_0.05', 'dsci_0.1', 'dsci_0.2'] if not args.dsi else [
    'photon_noPU_Si', 'photon_PU_Si', 'dsi_1.0', 'original_Si', 'dsi_1.5', 'dsi_2.0', 'dsi_2.5']

colors = [2, 4, 1, 8, colors[4], colors[3], colors[5],]
ex_offset = -0.65
ey_offset = 0.015

t = canv.GetTopMargin()
latex_fil = rt.TLatex()
latex_fil.SetTextFont(62)
latex_fil.SetTextAlign(21)
latex_fil.SetTextSize(cms.lumiTextSize * t)

rt.TGaxis.SetExponentOffset(ex_offset * canv.GetLeftMargin(), ey_offset, 'y')
filters = ['', '_H', '_E']
texts = ['', '#frac{E_{HAD}}{E_{tot}} > 0.9', '#frac{E_{EM}}{E_{tot}} > 0.9']
cut_text = f'Score_{{R2S}} < {args.r2s}'
if args.wide:
    hframe.GetXaxis().SetRangeUser(0.8, 1.6)
else:
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
    for dir_name in dir_names:
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
    canv.Print(f"plots/responce{out}_cut{r2s}.pdf")