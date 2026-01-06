import ROOT

def run_comparison_with_plots():
    # ---------------------------------------------------------
    # 1. Setup: Create a Model (Gaussian) and Toy Data
    # ---------------------------------------------------------
    x = ROOT.RooRealVar("x", "x", -10, 10)
    mean = ROOT.RooRealVar("mean", "mean", 0, -5, 5)
    sigma = ROOT.RooRealVar("sigma", "sigma", 2, 0.1, 5)

    gauss = ROOT.RooGaussian("gauss", "Gaussian PDF", x, mean, sigma)

    # Generate "Unweighted" Data (1000 events)
    data = gauss.generate(ROOT.RooArgSet(x), 1000)

    # ---------------------------------------------------------
    # 2. Add Weights (Scaling by 0.25)
    # ---------------------------------------------------------
    w_val = 0.25
    w_var = ROOT.RooRealVar("w", "weight", w_val)

    # Step A: Add the weight column
    data.addColumn(w_var)

    # Step B: Create the new weighted dataset
    data_weighted = ROOT.RooDataSet("data_w", "Weighted Data",
                                    data,
                                    data.get(),
                                    "",
                                    "w")

    print("\n" + "="*60)
    print(f" Dataset Created: {data_weighted.numEntries()} entries")
    print(f" Sum of Weights: {data_weighted.sumEntries()}")
    print("="*60 + "\n")

    # ---------------------------------------------------------
    # 3. Fit 1: SumW2Error OFF (Default/Asymptotic)
    # ---------------------------------------------------------
    # Reset params to ensure fair start
    mean.setVal(0)
    sigma.setVal(2)

    fit_result_OFF = gauss.fitTo(data_weighted,
                                 ROOT.RooFit.Save(),
                                 ROOT.RooFit.SumW2Error(False),
                                 ROOT.RooFit.PrintLevel(-1))

    mean_err_OFF = mean.getError()

    # --- PLOTTING 1 ---
    c1 = ROOT.TCanvas("c1", "Fit 1: SumW2Error OFF", 800, 600)
    frame1 = x.frame(ROOT.RooFit.Title("Fit 1: SumW2Error(False)"))

    # Plot Data
    #data_weighted.plotOn(frame1, ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
    data_weighted.plotOn(frame1, ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson))

    # Plot PDF (Red line)
    gauss.plotOn(frame1, ROOT.RooFit.LineColor(ROOT.kRed))

    # Show Parameters on Plot (Look at the 'mean' error here!)
    gauss.paramOn(frame1,
                  ROOT.RooFit.Layout(0.60, 0.90, 0.90),
                  ROOT.RooFit.Label("Fit Result (OFF)"))

    frame1.Draw()
    c1.Update()
    c1.SaveAs("c1.png")


    # ---------------------------------------------------------
    # 4. Fit 2: SumW2Error ON (Corrected)
    # ---------------------------------------------------------
    # Reset params again
    mean.setVal(0)
    sigma.setVal(2)

    fit_result_ON = gauss.fitTo(data_weighted,
                                ROOT.RooFit.Save(),
                                ROOT.RooFit.SumW2Error(True),
                                ROOT.RooFit.PrintLevel(-1))

    mean_err_ON = mean.getError()

    # --- PLOTTING 2 ---
    c2 = ROOT.TCanvas("c2", "Fit 2: SumW2Error ON", 800, 600)
    frame2 = x.frame(ROOT.RooFit.Title("Fit 2: SumW2Error(True)"))

    # Plot Data
    data_weighted.plotOn(frame2, ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))

    # Plot PDF (Blue line)
    gauss.plotOn(frame2, ROOT.RooFit.LineColor(ROOT.kBlue))

    # Show Parameters on Plot (Compare this error with the first plot)
    gauss.paramOn(frame2,
                  ROOT.RooFit.Layout(0.60, 0.90, 0.90),
                  ROOT.RooFit.Label("Fit Result (ON)"))

    frame2.Draw()
    c2.Update()
    c2.SaveAs("c2.png")

    # ---------------------------------------------------------
    # 5. Comparison Summary
    # ---------------------------------------------------------
    ratio = mean_err_OFF / mean_err_ON
    expected_ratio = 1.0 / (w_val**0.5)

    print("\n" + "="*60)
    print(" SUMMARY")
    print("="*60)
    print(f"Error (OFF): {mean_err_OFF:.5f} (Visible in Red Plot Box)")
    print(f"Error (ON) : {mean_err_ON:.5f}  (Visible in Blue Plot Box)")
    print(f"Ratio (OFF/ON): {ratio:.2f}")
    print(f"Expected Scaling: {expected_ratio:.2f}")
    print("="*60)

    # Keep window open
    input("Press Enter to exit...")

if __name__ == "__main__":
    run_comparison_with_plots()
