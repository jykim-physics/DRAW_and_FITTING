import ROOT
import pandas as pd

# Open the ROOT file
root_file = ROOT.TFile("output_file_gg.root", "READ")

# Access the RooDataSet (replace "sweight" with the correct name)
data_combined = root_file.Get("sweight")  # Replace with the name of your RooDataSet

# Check if the object is a RooDataSet
if isinstance(data_combined, ROOT.RooDataSet):
    # Initialize a dictionary to hold the data for each variable
    data = {}

    # Loop over all variables in the RooDataSet
    for var in data_combined.get():
        var_name = var.GetName()
        data[var_name] = []

        # Loop through all entries in the RooDataSet
        for entry in data_combined:
            data[var_name].append(entry.getRealValue(var_name))

    # Convert the dictionary to a pandas DataFrame
    df = pd.DataFrame(data)

    # Show the first few rows of the DataFrame
    print(df.head())

else:
    print("The object is not a RooDataSet!")

# Close the ROOT file
root_file.Close()

