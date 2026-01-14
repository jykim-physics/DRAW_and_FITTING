import ROOT
import sys

# --- 1. Get Arguments ---
if len(sys.argv) < 13:
    print("Usage: python script.py data_A data_B MC_A MC_B output var min max display_var norm loc log")
    sys.exit(1)

data_A_fname = sys.argv[1]
data_B_fname = sys.argv[2]
MC_A_fname = sys.argv[3]
MC_B_fname = sys.argv[4]
output_img_fname = sys.argv[5]
var_name = sys.argv[6]
min_bin = sys.argv[7]
max_bin = sys.argv[8]
display_var_name = sys.argv[9]
if_normalized = sys.argv[10]
legend_loc = sys.argv[11]
use_log_y = sys.argv[12]

ROOT.gROOT.LoadMacro('/home/jykim/workspace/DRAW_and_FITTING/main/FITTING/Belle2Style.C')
ROOT.SetBelle2Style()

# Create Canvas
cdata_mc = ROOT.TCanvas("cdata_mc", "Data and MC Comparison", 800, 600)

# --- 2. Setup Configuration ---
inputs = [
    {"file": data_A_fname, "label": "Data, D^{+} #rightarrow K_{S}^{0} K^{+}",   "color": ROOT.kBlue,     "is_data": True},
    {"file": data_B_fname, "label": "Data, D^{+} #rightarrow K_{S}^{0} #pi^{+}", "color": ROOT.kCyan+1,   "is_data": True},
    {"file": MC_A_fname,   "label": "MC, D^{+} #rightarrow K_{S}^{0} K^{+}",     "color": ROOT.kRed,      "is_data": False},
    {"file": MC_B_fname,   "label": "MC, D^{+} #rightarrow K_{S}^{0} #pi^{+}",   "color": ROOT.kOrange+1, "is_data": False},
]

histograms = []
files = []

n_bins = 50
if var_name == "Dp_CMS_p":
    n_bins = 100

# --- 3. Fill Histograms ---
for i, inp in enumerate(inputs):
    f = ROOT.TFile(inp["file"], "READ")
    files.append(f)

    dataset = f.Get("sweight")
    if not dataset:
        print(f"Error: 'sweight' dataset not found in {inp['file']}")
        continue

    h_name = f"h_{i}"
    h = ROOT.TH1F(h_name, inp["label"], n_bins, float(min_bin), float(max_bin))
    h.Sumw2()
    h.SetXTitle(f"{display_var_name}")

    # Fill
    num_entries = dataset.numEntries()
    for j in range(num_entries):
        entry = dataset.get(j)
        target_value = entry.getRealValue(f"{var_name}")
        N_total_sw = entry.getRealValue("N_total_sw")
        h.Fill(target_value, N_total_sw)

    # Normalize
    if if_normalized == 'True':
        if h.Integral() != 0:
            h.Scale(1.0 / h.Integral())

    # --- STYLE SETTINGS ---
    h.SetLineColor(inp["color"])
    h.SetLineWidth(3)

    if inp["is_data"]:
        # Data Style: Points with Error bars
        h.SetMarkerStyle(20)
        h.SetMarkerSize(1.0)
        h.SetMarkerColor(inp["color"])
        h.SetFillStyle(0)
    else:
        # MC Style: Line + Error bars (No Fill)
        h.SetMarkerStyle(0)
        h.SetLineStyle(1)
        # Ensure hollow fill style so no color band appears
        h.SetFillStyle(0)

    histograms.append(h)

# --- 4. Scale Logic ---
global_max = 0
for h in histograms:
    # Check max of histogram + error to avoid cutting off error bars
    # Use GetBinErrorUp to be precise if errors are asymmetric (though Sumw2 is symmetric)
    local_max = h.GetMaximum() + h.GetBinError(h.GetMaximumBin())
    if local_max > global_max:
        global_max = local_max

for h in histograms:
    if use_log_y == 'True':
        ROOT.gPad.SetLogy()
        min_val = 1e-4 if if_normalized == 'True' else 0.1
        h.SetMinimum(min_val)
        h.SetMaximum(global_max * 500)
    else:
        ROOT.gPad.SetLogy(0)
        h.SetMinimum(0)
        # Slightly increased headroom for linear scale to accommodate error bars comfortably
        h.SetMaximum(global_max * 1.3)

# --- 5. Draw ---
# Draw axis frame first
histograms[0].Draw("AXIS")

# Loop to draw MC first (so they are behind data)
for i, h in enumerate(histograms):
    if not inputs[i]["is_data"]:
        # Draw Histogram line (HIST) and Error bars (E)
        h.Draw("HIST E SAME")

# Loop to draw Data second (so they are on top)
for i, h in enumerate(histograms):
    if inputs[i]["is_data"]:
        # Draw Markers (P) and Error bars (E)
        h.Draw("PE SAME")

# --- 6. Legend ---
if legend_loc == 'left':
    legend = ROOT.TLegend(0.18, 0.65, 0.45, 0.88)
else:
    legend = ROOT.TLegend(0.60, 0.65, 0.87, 0.88)

legend.SetFillColorAlpha(ROOT.kWhite, 0.0)
legend.SetBorderSize(0)
legend.SetTextFont(42)
legend.SetTextSize(0.045)

for i, h in enumerate(histograms):
    if inputs[i]["is_data"]:
        legend.AddEntry(h, inputs[i]["label"], "ep") # Line, Error, Point
    else:
        # Changed from "lf" to "le" (Line, Error)
        legend.AddEntry(h, inputs[i]["label"], "le")

legend.Draw()

cdata_mc.SaveAs(f"{output_img_fname}")

for f in files:
    f.Close()
