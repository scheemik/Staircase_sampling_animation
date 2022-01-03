"""
Script to extract one profile from an ITP data file and write it to a csv

made by: Mikhail Schee (January 2022)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import mat73 # For reading the ITP `cormat` files

################################################################################
# Select which profile to plot (must be a csv)
pf_file = 'ITP3cormat1073.csv'
# Set depth limits
p_lims = [240, 290]

################################################################################
# Set plot mode
dark_mode = True
# dark_mode = False

# Enable dark mode plotting
if dark_mode:
    plt.style.use('dark_background')
    std_clr = 'w'
else:
    std_clr = 'k'
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

def plot_profile(data, p_lims=None, filename=None):
    """
    Plots the Temperature vs Salinity data

    data    A pandas DataFrame with the following columns:
        temp        An array of temperature values
        salt        An array of salinity values
        p           An array of depth values (in m)
    p_lims  Limits for the pressure axis [p_min, p_max]
    """
    # Start plot title
    plt_title = 'Example ITP profile'
    # Set figure and axes for plot
    fig, axes = set_fig_axes([1], [1,1], fig_ratio=0.8, fig_size=1.25)
    #
    # Set limits
    p_lim_low  = 'p>'+str(p_lims[0])
    data       = data.query(p_lim_low)
    p_lim_high = 'p<'+str(p_lims[1])
    data       = data.query(p_lim_high)
    # Plot cormat
    #   Plot the same color lines for all of them
    clr = 'w'
    lbl = 'label'
    axes[0].plot(data['temp'], -data['p'], color='lightcoral', linewidth=1, alpha=0.5, zorder=1)
    axes[1].plot(data['salt'], -data['p'], color='silver', linewidth=1, alpha=0.5, zorder=1)
    #   Plot points with colors unique to this profile on top
    axes[0].scatter(data['temp'], -data['p'], color=clr, s=3.7, marker='.', label=lbl, zorder=2)
    axes[1].scatter(data['salt'], -data['p'], color=clr, s=3.7, marker='.', label=lbl, zorder=2)
    #
    # Set labels
    axes[0].set_ylabel('Pressure (dbar)')
    axes[0].set_xlabel(r'Temperature ($^\circ$C)')
    axes[1].set_xlabel(r'Salinity (g/kg)')
    # plt.tight_layout(pad=4)
    # Add overall plot title
    fig.suptitle(plt_title)
    #
    if filename != None:
        plt.savefig(filename, dpi=400)
    else:
        plt.show()

################################################################################

# Import data from csv
data = pd.read_csv(pf_file)

# Plot data
plot_profile(data, p_lims)
