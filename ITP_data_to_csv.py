"""
Script to extract one profile from an ITP data file and write it to a csv

made by: Mikhail Schee (January 2022)
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import mat73 # For reading the ITP `cormat` files

################################################################################
# Select which profile to use

# Where the ITP data files are stored
d_source_file_path = "/Users/Grey/Documents/Research/Science_Data/ITPs"
# Which ITP to use (must be a string)
ITP_ID = '8'
# The type of ITP data file to use (only cormat is supported right now)
ITP_type = 'cormat'
# The profile number to read data from (must be a 4 digit string)
pf_no = '1301'

# Assemble the data file's path
pf_file_path = d_source_file_path + '/itp' + ITP_ID + '/itp' + ITP_ID + ITP_type + '/cor' + pf_no + '.mat'
print('Accessing',pf_file_path)

# Define output directory
output_dir = '' # same directory as executed from
# Define output file name
filename = 'ITP' + ITP_ID + ITP_type + pf_no + '.csv'

################################################################################

def load_cormat_itp(file_path):
    """
    Loads the data from an ITP profile file in the `cormat` format
    Returns a pandas dataframe

    file_path           string of a file path to the specific file
    """
    # Load cormat file into dictionary with mat73
    #   (specific to version of MATLAB used to make cormat files)
    dat = mat73.loadmat(file_path)
    # If it finds the correct column headers, put data into arrays
    if 'te_adj' in dat and 'sa_adj' in dat and 'pr_filt' in dat:
        temp0 = dat['te_adj']
        salt0 = dat['sa_adj']
        p0    = dat['pr_filt']
        # Down-casts have an issue with the profiler wake, so only take profiles
        #   that were measured as the profiler was moving upwards
        if p0[0] < p0[-1]:
            print('Skipping down-cast')
            return None
        # else:
        #     print('prof:',prof_no,'goes from',p0[0],'to',p0[-1])
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
pf_df = load_cormat_itp(pf_file_path)

# Remove rows of the data frame with missing data
pf_df.dropna(inplace = True)

# Write dataframe to csv
pf_df.to_csv(output_dir+filename)
