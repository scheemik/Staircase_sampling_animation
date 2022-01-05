"""
Script to plot T-S pairs from a csv in a scatter plot

made by: Mikhail Schee (January 2022)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

################################################################################

# Define name of input csv
file_name = 'test_2_pfs'

################################################################################
# Set plot mode
dark_mode = True
# dark_mode = False

# Enable dark mode plotting
if dark_mode:
    plt.style.use('dark_background')
    std_clr = 'w'
    t_clr   = 'lightcoral'
    s_clr   = 'silver'
    ss_clr  = 'w'
else:
    std_clr = 'k'
    t_clr   = 'lightcoral'
    s_clr   = 'silver'
    ss_clr  = 'k'
################################################################################

def set_fig_axes(heights, widths, fig_ratio=0.5, fig_size=1, share_x_axis=None, share_y_axis=None, prjctn=None):
    """
    Creates fig and axes objects based on desired heights and widths of subplots
    Ex: if widths=[1,5], there will be 2 columns, the 1st 1/5 the width of the 2nd

    heights      array of integers for subplot height ratios, len=rows
    widths       array of integers for subplot width  ratios, len=cols
    fig_ratio    ratio of height to width of overall figure
    fig_size     size scale factor, 1 changes nothing, 2 makes it very big
    share_x_axis bool whether the subplots should share their x axes
    share_y_axis bool whether the subplots should share their y axes
    projection   projection type for the subplots
    """
    # Set aspect ratio of overall figure
    w, h = mpl.figure.figaspect(fig_ratio)
    # Find rows and columns of subplots
    rows = len(heights)
    cols = len(widths)
    # This dictionary makes each subplot have the desired ratios
    # The length of heights will be nrows and likewise len(widths)=ncols
    plot_ratios = {'height_ratios': heights,
                   'width_ratios': widths}
    # Determine whether to share x or y axes
    if share_x_axis == None and share_y_axis == None:
        if rows == 1 and cols != 1: # if only one row, share y axis
            share_x_axis = False
            share_y_axis = True
        elif rows != 1 and cols == 1: # if only one column, share x axis
            share_x_axis = True
            share_y_axis = False
        else:                       # otherwise, forget about it
            share_x_axis = False
            share_y_axis = False
    # Set ratios by passing dictionary as 'gridspec_kw', and share y axis
    fig, axes = plt.subplots(figsize=(w*fig_size,h*fig_size), nrows=rows, ncols=cols, gridspec_kw=plot_ratios, sharex=share_x_axis, sharey=share_y_axis, subplot_kw=dict(projection=prjctn))
    # Set ticklabel format for all axes
    if (rows+cols)>2:
        for ax in axes.flatten():
            ax.ticklabel_format(style='sci', scilimits=(-3,3), useMathText=True)
    else:
        axes.ticklabel_format(style='sci', scilimits=(-3,3), useMathText=True)
    return fig, axes

def plot_T_S(ax, df):
    """
    Function to plot all T-S pairs the same color
    """
    temps = df.temp
    salts = df.salt
    # Same color for every instrmt
    ax.scatter(salts, temps, color=std_clr, s=0.5, marker='.')
    # Set titles and labels
    ITP_ID = np.unique(np.array(df['ITP_ID']))[0]
    ITP_pf = np.unique(np.array(df['ITP_pf']))[0]
    ax.set_title('ITP'+str(ITP_ID)+' profile '+str(ITP_pf))
    return r'Salinity (g/kg)', r'Temperature ($^\circ$C)'

def plot_T_v_S(csv_file, filename=None):
    """
    Plots the Temperature vs Salinity data

    pfs_to_plot     A list of data frames, one for each profile
    data        A pandas DataFrame with the following columns:
        temp        An array of temperature values
        salt        An array of salinity values
        p           An array of depth values (in m)
    """
    # Start plot title
    plt_title = 'T-S pairs from '+csv_file
    # Get dataframe from csv file
    data = pd.read_csv(csv_file+'.csv')
    # Find the number of ITP ID's in the data
    unique_ITP_IDs = np.unique(np.array(data['ITP_ID']))
    if len(unique_ITP_IDs) > 2:
        print('Thats too many ITPs')
        return
    else:
        for id in unique_ITP_IDs:
            # Find the number of profiles in each
            unique_ITP_pfs = np.unique(np.array(data[(data['ITP_ID'] == id)]['ITP_pf']))
            if len(unique_ITP_pfs) > 1:
                print('Whoops')
                return
    #
    if len(unique_ITP_IDs) == 2:
        # Set figure and axes for plot
        fig, axes = set_fig_axes([1], [1,1], fig_ratio=0.5, fig_size=1.25, share_x_axis=False, share_y_axis=False)
        xlbl, ylbl = plot_T_S(axes[0], data[(data['ITP_ID'] == unique_ITP_IDs[1])])
        xlbl, ylbl = plot_T_S(axes[1], data[(data['ITP_ID'] == unique_ITP_IDs[0])])
        # Set axis labels only for the plots on the outside
        axes[0].set_ylabel(ylbl)
        axes[0].set_xlabel(xlbl)
        axes[1].set_xlabel(xlbl)
    else:
        # Set figure and axes for plot
        fig, axes = set_fig_axes([1], [1], fig_ratio=0.8, fig_size=1.25, share_x_axis=False, share_y_axis=False)
        xlbl, ylbl = plot_T_S(axes, data[(data['ITP_ID'] == unique_ITP_IDs[0])])
        # Set axis labels
        axes.set_ylabel(ylbl)
        axes.set_xlabel(xlbl)
    #
    plt.tight_layout(pad=4)
    # Add overall plot title
    fig.suptitle(plt_title)
    #
    if filename != None:
        plt.savefig(filename, dpi=400)
        # Close the figure after saving to avoid memory leaks when making many
        #   figures in a loop
        plt.close(fig)
    else:
        plt.show()

################################################################################

# Run script
plot_T_v_S('test_2_pfs')
