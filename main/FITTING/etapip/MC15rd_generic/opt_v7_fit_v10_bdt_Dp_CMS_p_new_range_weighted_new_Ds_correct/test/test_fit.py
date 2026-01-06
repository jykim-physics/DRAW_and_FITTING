import ROOT

def run_comparison():
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

    # --- FIX START ---
    # Step A: Add the weight column to the existing dataset
    # This calculates 'w_var' (0.25) for every event and stores it in 'data'
    data.addColumn(w_var)

    # Step B: Create the new weighted dataset
    # Now 'data.get()' includes 'w', so this constructor will work
    data_weighted = ROOT.RooDataSet("data_w", "Weighted Data",
                                    data,
                                    data.get(),
                                    "",
                                    "w") # <--- Specifies 'w' is the weight
    # --- FIX END ---

    print("\n" + "="*60)
    print(f" Dataset Created: {data_weighted.numEntries()} entries")
    print(f" Weight per event: {w_val}")
    print(f" Sum of Weights: {data_weighted.sumEntries()}")
    # Check: Should be 1000 * 0.25 = 250
    print("="*60 + "\n")

    # ---------------------------------------------------------
    # 3. Fit 1: SumW2Error OFF (Default)
    # ---------------------------------------------------------
    # Expectation: Errors will be ~2x LARGER because fit sees N=250 events

    fit_result_OFF = gauss.fitTo(data_weighted,
                                 ROOT.RooFit.Save(),
                                 ROOT.RooFit.SumW2Error(False),
                                 ROOT.RooFit.PrintLevel(-1))

    mean_err_OFF = mean.getError()
    print(f"[SumW2Error OFF] Mean Error: {mean_err_OFF:.4f}")

    # ---------------------------------------------------------
    # 4. Fit 2: SumW2Error ON (Corrected)
    # ---------------------------------------------------------
    # Expectation: Errors will be normal (small) because it corrects for weights

    mean.setVal(0) # Reset
    fit_result_ON = gauss.fitTo(data_weighted,
                                ROOT.RooFit.Save(),
                                ROOT.RooFit.SumW2Error(True),
                                ROOT.RooFit.PrintLevel(-1))

    mean_err_ON = mean.getError()
    print(f"[SumW2Error ON ] Mean Error: {mean_err_ON:.4f}")

    # ---------------------------------------------------------
    # 5. Comparison
    # ---------------------------------------------------------
    ratio = mean_err_OFF / mean_err_ON
    expected_ratio = 1.0 / (w_val**0.5) # 1 / 0.5 = 2.0

    print("\n" + "="*60)
    print(" SUMMARY")
    print("="*60)
    print(f"Error (OFF): {mean_err_OFF:.5f}")
    print(f"Error (ON) : {mean_err_ON:.5f}")
    print(f"Ratio (OFF/ON): {ratio:.2f}")
    print(f"Expected Scaling: {expected_ratio:.2f}")
    print("="*60)

if __name__ == "__main__":
    run_comparison()
