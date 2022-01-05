"""
Script to extract one profile from an ITP data file and write it to a csv

made by: Mikhail Schee (January 2022)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import mat73 # For reading the ITP `cormat` files
from scipy import interpolate # For interpolating data
import os # For checking whether the output directory exists
import shutil # For removing old versions of the output directory

################################################################################
# Define output directory
output_dir = 'frames'

# Define name of output frames
frame_file_name = 'test_2_pfs'

# Select which profiles to plot (must be a csv)


ITP001_1259 = {'ITP_ID': '1',
               'ITP_pf': '1259',
               # 'p_lims': [203, 233]} # Following Shibley et al. 2017 Figure 3b
               'p_lims': [210, 220]} # For presentation purposes
ITP008_1301 = {'ITP_ID': '8',
               'ITP_pf': '1301',
               # 'p_lims': [231, 263]} # Following Shibley et al. 2017 Figure 3a
               'p_lims': [240, 250]} # For presentation purposes
#
pfs_to_plot = [ITP008_1301, ITP001_1259]
pfs_to_plot = [ITP001_1259]

# Whether to write out the subsampled points to a csv
write_ss_to_csv = True

if write_ss_to_csv:
    # Check whether there already exists a csv for the
    if os.path.exists(frame_file_name+'.csv'):
        os.remove(frame_file_name+'.csv')

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

def interp_pts(res, p, t, s):
    """
    Interpolates the given temperature and salinity points to the given resolution

    res     The resolution for the new, interpolated arrays
    p       The original data's pressure array
    t       The original data's temperature array
    s       The original data's salinity array
        Note: p, t, and s must all be the same length
              Requires the following import statement:
               from scipy import interpolate
    """
    # Interpolate the data to the given resolution
    #   Define interpolated functions
    temp1 = interpolate.interp1d(p, t)
    salt1 = interpolate.interp1d(p, s)
    #   Define new pressure axis
    p_new = np.arange(min(p), max(p), res)
    #   Interpolate temp and salt on new p axis
    t_new = temp1(p_new)
    s_new = salt1(p_new)
    return p_new, t_new, s_new

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

def plot_T_S_separate(axes, df, s_res, s_rate, i_offset):
    # Import data from csv
    csv  = 'ITP'+df['ITP_ID']+'cormat'+df['ITP_pf']+'.csv'
    data = pd.read_csv(csv)
    p_lims = df['p_lims']
    # Set limits
    if not isinstance(p_lims, type(None)):
        p_lim_low  = 'p>'+str(p_lims[0])
        data       = data.query(p_lim_low)
        p_lim_high = 'p<'+str(p_lims[1])
        data       = data.query(p_lim_high)
    # Interpolate the data to the given resolution
    p_new, t_new, s_new = interp_pts(s_res/s_rate, data['p'], data['temp'], data['salt'])
    # Subsample the interpolated data
    p_ss, t_ss, s_ss = p_new[i_offset::s_rate], t_new[i_offset::s_rate], s_new[i_offset::s_rate]
    #
    # Plot interpolated profile
    axes[0].plot(t_new, -p_new, color=t_clr, linewidth=2, alpha=0.7, zorder=1, label='Original T profile')
    axes[1].plot(s_new, -p_new, color=s_clr, linewidth=2, alpha=0.7, zorder=1, label='Original S profile')
    # Subsampled profiles
    axes[0].plot(t_ss, -p_ss, color=t_clr, linestyle='--', alpha=1, zorder=3, label='Subsampled T profile')
    axes[1].plot(s_ss, -p_ss, color=s_clr, linestyle='--', alpha=1, zorder=3, label='Subsampled S profile')
    #   Plot points of subsampled profile
    axes[0].scatter(t_ss, -p_ss, color=t_clr, s=65, marker='.', zorder=3)
    axes[1].scatter(s_ss, -p_ss, color=s_clr, s=65, marker='.', zorder=3)
    # Add subsampled grid
    #   vertical lines
    axes[0].vlines(t_ss, -p_lims[1], -p_lims[0], linewidths=1, linestyles='--', colors=t_clr, alpha=0.5, zorder=4)
    axes[1].vlines(s_ss, -p_lims[1], -p_lims[0], linewidths=1, linestyles='--', colors=s_clr, alpha=0.5, zorder=4)
    #   horizontal lines
    axes[0].hlines(-p_ss, min(t_new), max(t_new), linewidths=1, linestyles=':', colors=ss_clr, alpha=0.5, zorder=4)
    axes[1].hlines(-p_ss, min(s_new), max(s_new), linewidths=1, linestyles=':', colors=ss_clr, alpha=0.5, zorder=4)
    #
    # Set titles and labels
    axes[0].set_title('ITP'+df['ITP_ID']+' profile '+df['ITP_pf']+' Temperature')
    axes[0].set_ylabel('Pressure (dbar)')
    axes[0].set_xlabel(r'Temperature ($^\circ$C)')
    axes[0].legend()
    #
    axes[1].set_title('ITP'+df['ITP_ID']+' profile '+df['ITP_pf']+' Salinity')
    axes[1].set_xlabel(r'Salinity (g/kg)')
    axes[1].legend()
    # Output the dataframe for the subsampled profiles
    out_dict = {'ITP_ID': df['ITP_ID']*len(t_ss),
                'ITP_pf': df['ITP_pf']*len(t_ss),
                'i_offset': [i_offset]*len(t_ss),
                'temp': t_ss,
                'salt': s_ss,
                'p': p_ss
                }
    # Build output data frame
    return pd.DataFrame(out_dict)

def plot_T_S_together(ax, df, s_res, s_rate, i_offset, ax_n):
    # Import data from csv
    csv  = 'ITP'+df['ITP_ID']+'cormat'+df['ITP_pf']+'.csv'
    data = pd.read_csv(csv)
    p_lims = df['p_lims']
    # Set limits
    if not isinstance(p_lims, type(None)):
        p_lim_low  = 'p>'+str(p_lims[0])
        data       = data.query(p_lim_low)
        p_lim_high = 'p<'+str(p_lims[1])
        data       = data.query(p_lim_high)
    # Interpolate the data to the given resolution
    p_new, t_new, s_new = interp_pts(s_res/s_rate, data['p'], data['temp'], data['salt'])
    # Subsample the interpolated data
    p_ss, t_ss, s_ss = p_new[i_offset::s_rate], t_new[i_offset::s_rate], s_new[i_offset::s_rate]
    #
    # Plot interpolated profile
    og_T_ln = ax.plot(t_new, -p_new, color=t_clr, linewidth=2, alpha=0.7, zorder=1, label='Original T profile')
    # Subsampled profiles
    ss_T_ln = ax.plot(t_ss, -p_ss, color=t_clr, linestyle='--', alpha=1, zorder=3, label='Subsampled T profile')
    #   Plot points of subsampled profile
    ax.scatter(t_ss, -p_ss, color=t_clr, s=65, marker='.', zorder=3)
    # Add subsampled grid
    #   vertical lines
    ax.vlines(t_ss, -p_lims[1], -p_lims[0], linewidths=1, linestyles='-.', colors=t_clr, alpha=0.5, zorder=4)
    #   horizontal lines
    ax.hlines(-p_ss, min(t_new), max(t_new), linewidths=1, linestyles=':', colors=ss_clr, alpha=0.5, zorder=4)
    # ax.hlines(-p_ss, min(s_new), max(s_new), linewidths=1, linestyles=':', colors=ss_clr, alpha=0.5, zorder=4)
    # Set titles and labels
    ax.set_title('ITP'+df['ITP_ID']+' profile '+df['ITP_pf'])
    if ax_n == 0:
        ax.set_ylabel('Pressure (dbar)')
    ax.set_xlabel(r'Temperature ($^\circ$C)', color=t_clr)
    # Change colors of the vertical axes numbers
    ax.tick_params(axis='x', colors=t_clr)
    #
    # Create twin axes to plot T and S ontop of one another
    ax2 = ax.twiny()
    og_S_ln = ax2.plot(s_new, -p_new, color=s_clr, linewidth=2, alpha=0.7, zorder=1, label='Original S profile')
    ss_S_ln = ax2.plot(s_ss, -p_ss, color=s_clr, linestyle='--', alpha=1, zorder=3, label='Subsampled S profile')
    ax2.scatter(s_ss, -p_ss, color=s_clr, s=65, marker='.', zorder=3)
    ax2.vlines(s_ss, -p_lims[1], -p_lims[0], linewidths=1, linestyles='-.', colors=s_clr, alpha=0.5, zorder=4)
    #
    # Get all the lines in one legend
    lines  = og_T_ln + og_S_ln + ss_T_ln + ss_S_ln
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels)
    #
    ax2.set_xlabel(r'Salinity (g/kg)', color=s_clr)
    # Change colors of the vertical axes numbers
    ax2.tick_params(axis='x', colors=s_clr)

def plot_profile(pfs_to_plot, s_res, s_rate, i_offset, filename=None, ss_pf_list=None):
    """
    Plots the Temperature vs Salinity data

    pfs_to_plot     A list of data frames, one for each profile
    data        A pandas DataFrame with the following columns:
        temp        An array of temperature values
        salt        An array of salinity values
        p           An array of depth values (in m)
    s_res       The resolution for sampling
    s_rate      The sampling rate
                    Interpolation happens at s_res / s_rate
    i_offset    The index offset for subsampling
    p_lims      Limits for the pressure axis [p_min, p_max]
    ss_pf_list  A blank list in which to store the dataframes of ss profiles
    """
    # Start plot title
    plt_title = 'Profiles subsampled at '+str(s_res)+'m resolution'
    # Set figure and axes for plot
    fig, axes = set_fig_axes([1], [1,1], fig_ratio=0.5, fig_size=1.25, share_x_axis=False, share_y_axis=False)
    #
    if len(pfs_to_plot) == 2:
        plot_T_S_together(axes[0], pfs_to_plot[0], s_res, s_rate, i_offset, 0)
        plot_T_S_together(axes[1], pfs_to_plot[1], s_res, s_rate, i_offset, 1)
    else:
        pf = plot_T_S_separate(axes, pfs_to_plot[0], s_res, s_rate, i_offset)
        if not isinstance(ss_pfs, type(None)):
            ss_pfs.append(pf)
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
    return ss_pfs

################################################################################

# Import data from csv
# data = pd.read_csv(pf_file+'.csv')

# Set parameters
sample_res  = 1.5
sample_rate = 40

# Check whether there already exists a directory for the output frames
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir)

# Create empty list for dataframes of the subsampled profiles
ss_pfs = []

# Create frames for the animation
for i in range(sample_rate):
    ss_pfs = plot_profile(pfs_to_plot, sample_res, sample_rate, i, filename=(output_dir+'/'+frame_file_name+'-'+str(i).zfill(3)+'.png'), ss_pf_list=ss_pfs)
    # plot_profile(pfs_to_plot, sample_res, sample_rate, i, filename=(output_dir+'/'+pf_file+'-'+str(i).zfill(3)+'.png'))

if not isinstance(ss_pfs, type(None)):
    ss_pfs = pd.concat(ss_pfs)
    ss_pfs.to_csv(frame_file_name+'.csv')
