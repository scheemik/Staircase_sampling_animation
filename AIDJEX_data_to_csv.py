"""
Script to extract one profile from an AIDJEX data file and write it to a csv

made by: Mikhail Schee (January 2022)
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

################################################################################
# Select which profile to use

# Where the ITP data files are stored
d_source_file_path = "/Users/Grey/Documents/Research/Science_Data/AIDJEX/AIDJEX"
# Which AIDJEX station to use (must be a string)
AIDJEX_station = 'BlueFox'
# The profile number to read data from (must be a 3 digit string)
pf_no = '001'

# Assemble the data file's path
pf_file_path = d_source_file_path + '/' + AIDJEX_station + '/' + AIDJEX_station + '_' + pf_no
print('Accessing',pf_file_path)

# Define output directory
output_dir = '' # same directory as executed from
# Define output file name
filename = 'AIDJEX-' + AIDJEX_station + '_' + pf_no + '.csv'

################################################################################

def load_AIDJEX(file_path):
    """
    Loads the data from an ITP profile file in the `cormat` format
    Returns a pandas dataframe

    file_path           string of a file path to the specific file
    """
    # Read in data from the file
    dat = pd.read_table(file_path,header=3,skipfooter=0,engine='python',delim_whitespace=True)
    # If it finds the correct column headers, put data into arrays
    if 'Depth(m)' and 'Temp(C)' and 'Sal(PPT)' in dat.columns:
        temp0 = dat['Temp(C)'][:].values
        salt0 = dat['Sal(PPT)'][:].values
        p0    = dat['Depth(m)'][:].values
        #
        out_dict = {'temp': temp0,
                    'salt': salt0,
                    'p': p0
                    }
        # Build output data frame
        df = pd.DataFrame(out_dict)
        # Return all the relevant values
        return df

################################################################################

# Read in profile data
pf_df = load_AIDJEX(pf_file_path)

# Remove rows of the data frame with missing data
pf_df.dropna(inplace = True)

# Write dataframe to csv
pf_df.to_csv(output_dir+filename)
