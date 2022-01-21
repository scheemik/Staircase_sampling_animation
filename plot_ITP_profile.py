"""
Script to extract one profile from an ITP data file and write it to a csv

made by: Mikhail Schee (January 2022)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import mpl_toolkits.axes_grid1.inset_locator as plt_inset
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

# Set parameters
sample_res  = 1.5
sample_rate = 40

# Select which profiles to plot (must be a csv)
ITP001_1259 = {'ITP_ID': '1',
               'ITP_pf': '1259',
               'inset': [210, 220],
               # 'p_lims': [203, 233], # Following Shibley et al. 2017 Figure 3b
               # 'p_lims': [210, 220], # For presentation purposes
               'p_lims': None,
               'interpolate': False,
               'og_markers': False,
               'subsample': False,
               'plot_S': False}

ITP008_1301 = {'ITP_ID': '8',
               'ITP_pf': '1301',
               'inset': [240, 250],
               # 'p_lims': [231, 263], # Following Shibley et al. 2017 Figure 3a
               # 'p_lims': [240, 250], # For presentation purposes
               'p_lims': None,
               'interpolate': False,
               'og_markers': False,
               'subsample': False,
               'plot_S': False}
#
pfs_to_plot = [ITP001_1259, ITP008_1301]
# pfs_to_plot = [ITP001_1259]

# Whether to write out the subsampled points to a csv
write_ss_to_csv = False

if write_ss_to_csv:
    # Check whether there already exists a csv for the
    if os.path.exists(frame_file_name+'.csv'):
        os.remove(frame_file_name+'.csv')

################################################################################
# Set plot mode
dark_mode = True
# dark_mode = False
mrk_size = 100

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

################################################################################

def add_inset_to_axis(ax, x_arr, y_arr, clr, inset_ylims, inset_pos, zoom_locs=[2,1]):
    """
    Adds an inset to a given axis

    ax              main axis on which to add inset
    x_arr           horizontal axis of data
    y_arr           vertical axis of data
    clr             color which to draw the line on the inset
    inset_ylims     array of y limits for the inset [y_min, y_max]
    inset_pos       array of positions for inset in units of the normalized
                    coordinate of the parent axis:
                        [left_edge, bottom_edge, width, height]
    zoom_locs       array of 2 corners to draw lines from:
                        [1=tr, 2=tl, 3=bl, 4=br]
    """
    # Create inset axes using provided position
    ax_in = ax.inset_axes(inset_pos)
    # Mark inset box on main axes and draw zoom lines
    #   loc1/loc2 are corners to draw lines from [1=tr, 2=tl, 3=bl, 4=br]
    plt_inset.mark_inset(ax, ax_in, loc1=zoom_locs[0], loc2=zoom_locs[1], facecolor="none", edgecolor='0.5')
    ax_in.plot(x_arr, -y_arr, color=clr)
    # Restrict limits of inset
    ax_in.set_ylim([-inset_ylims[1], -inset_ylims[0]])
    df = pd.DataFrame()
    df = df.assign(x=x_arr, y=y_arr)
    x_arr_in = df[(df['y'] > inset_ylims[0]) & (df['y'] < inset_ylims[1])].x
    ax_in.set_xlim([min(x_arr_in), max(x_arr_in)])
    # Fix the number of ticks on the inset axes
    ax_in.set_xticks(np.linspace(min(x_arr_in), max(x_arr_in), 2))
    ax_in.set_yticks(np.linspace(-inset_ylims[0], -inset_ylims[1], 3))

################################################################################

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
    axes[0].scatter(t_ss, -p_ss, color=t_clr, s=mrk_size, marker='.', zorder=3)
    axes[1].scatter(s_ss, -p_ss, color=s_clr, s=mrk_size, marker='.', zorder=3)
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
    out_dict = {'ITP_ID': [df['ITP_ID']]*len(t_ss),
                'ITP_pf': [df['ITP_pf']]*len(t_ss),
                'i_offset': [i_offset]*len(t_ss),
                'temp': t_ss,
                'salt': s_ss,
                'p': p_ss
                }
    # Build output data frame
    return pd.DataFrame(out_dict)

################################################################################

def plot_T_S_together(ax, df, s_res, s_rate, i_offset):
    """
    Function to make a profile plot on the given axis

    ax          the axis on which to plot
    df          a pandas dataframe containing data and parameters for the plot
    s_res       the sub-sampling resolution
    s_rate      the sub-sampling rate
    i_offset    an integer for the offset in the vertical of the sub-sampling
    """
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
    if df['interpolate']:
        # Interpolate the data to the given resolution
        p_new, t_new, s_new = interp_pts(s_res/s_rate, data['p'], data['temp'], data['salt'])
    else:
        # Just use the original data
        p_new, t_new, s_new = data['p'], data['temp'], data['salt']
    # Plot original profile
    og_T_ln = ax.plot(t_new, -p_new, color=t_clr, linewidth=2, alpha=0.7, zorder=1, label='Original T profile')
    # Plot markers for all points in original profile
    if df['og_markers']:
        ax.scatter(t_new, -p_new, color=t_clr, s=mrk_size, marker='.', zorder=1)
    # Add subsampled profile?
    if df['subsample'] and df['interpolate']:
        # Subsample the interpolated data
        p_ss, t_ss, s_ss = p_new[i_offset::s_rate], t_new[i_offset::s_rate], s_new[i_offset::s_rate]
        # Subsampled profiles
        ss_T_ln = ax.plot(t_ss, -p_ss, color=t_clr, linestyle='--', alpha=1, zorder=3, label='Subsampled T profile')
        #   Plot points of subsampled profile
        ax.scatter(t_ss, -p_ss, color=t_clr, s=mrk_size, marker='.', zorder=3)
        #
        # Add subsampled grid
        #   vertical lines
        ax.vlines(t_ss, -p_lims[1], -p_lims[0], linewidths=1, linestyles='-.', colors=t_clr, alpha=0.5, zorder=4)
        #   horizontal lines
        ax.hlines(-p_ss, min(t_new), max(t_new), linewidths=1, linestyles=':', colors=ss_clr, alpha=0.5, zorder=4)
        # ax.hlines(-p_ss, min(s_new), max(s_new), linewidths=1, linestyles=':', colors=ss_clr, alpha=0.5, zorder=4)
        # Get all the lines in one legend
        lines  = og_T_ln + ss_T_ln
    else:
        # Get all the lines in one legend
        lines  = og_T_ln
    #
    # Add inset?
    if not isinstance(df['inset'], type(None)):
        add_inset_to_axis(ax, t_new.values, p_new.values, t_clr, df['inset'], [0.25, 0.2, 0.4, 0.4], zoom_locs=[2,1])
    # Set titles and labels
    ax.set_title('ITP'+df['ITP_ID']+' profile '+df['ITP_pf'])
    y_label = 'Pressure (dbar)'
    ax.set_xlabel(r'Temperature ($^\circ$C)', color=t_clr)
    # Change colors of the vertical axes numbers
    ax.tick_params(axis='x', colors=t_clr)
    #
    # Plot the salinity profile on top?
    if df['plot_S']:
        # Create twin axes to plot T and S ontop of one another
        ax2 = ax.twiny()
        # Plot original profile
        og_S_ln = ax2.plot(s_new, -p_new, color=s_clr, linewidth=2, alpha=0.7, zorder=1, label='Original S profile')
        # Plot markers for all points in original profile
        if df['og_markers']:
            ax2.scatter(s_new, -p_new, color=s_clr, s=mrk_size, marker='.', zorder=1)
        # Add subsampled profile?
        if df['subsample'] and df['interpolate']:
            ss_S_ln = ax2.plot(s_ss, -p_ss, color=s_clr, linestyle='--', alpha=1, zorder=3, label='Subsampled S profile')
            ax2.scatter(s_ss, -p_ss, color=s_clr, s=mrk_size, marker='.', zorder=3)
            ax2.vlines(s_ss, -p_lims[1], -p_lims[0], linewidths=1, linestyles='-.', colors=s_clr, alpha=0.5, zorder=4)
            # Get all the lines in one legend
            lines  += og_S_ln + ss_S_ln
        else:
            # Get all the lines in one legend
            lines  += og_S_ln
        # Set salinity labels and colors
        ax2.set_xlabel(r'Salinity (g/kg)', color=s_clr)
        # Change colors of the vertical axes numbers
        ax2.tick_params(axis='x', colors=s_clr)
        #
    #
    # Get all the lines in one legend
    labels = [l.get_label() for l in lines]
    if len(labels) > 1:
        ax.legend(lines, labels)
    #

    if df['subsample']:
        if df['plot_S']:
            # Output the dataframe for the subsampled profiles
            out_dict = {'ITP_ID': [df['ITP_ID']]*len(t_ss),
                        'ITP_pf': [df['ITP_pf']]*len(t_ss),
                        'i_offset': [i_offset]*len(t_ss),
                        'temp': t_ss,
                        'salt': s_ss,
                        'p': p_ss
                        }
            # Build output data frame
            return y_label, pd.DataFrame(out_dict)
        #
    #
    return y_label, None

################################################################################

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
    plt_title = 'Profiles subsampled at '+str(s_res)+'m resolution, offset: '+str(i_offset).zfill(2)
    # Set figure and axes for plot
    fig, axes = set_fig_axes([1], [1,1], fig_ratio=0.7, fig_size=1.0, share_x_axis=False, share_y_axis=False)
    #
    if len(pfs_to_plot) == 2:
        y_label0, pf0 = plot_T_S_together(axes[0], pfs_to_plot[0], s_res, s_rate, i_offset)
        y_label1, pf1 = plot_T_S_together(axes[1], pfs_to_plot[1], s_res, s_rate, i_offset)
        axes[0].set_ylabel(y_label0)
        if not isinstance(ss_pfs, type(None)):
            ss_pfs.append(pf0)
            ss_pfs.append(pf1)
    else:
        y_label, pf = plot_T_S_separate(axes, pfs_to_plot[0], s_res, s_rate, i_offset)
        axes.set_ylabel(y_label)
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

# Check whether there already exists a directory for the output frames
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir)

# Create empty list for dataframes of the subsampled profiles
ss_pfs = []

# Create frames for the animation
for i in range(1):#sample_rate):
    ss_pfs = plot_profile(pfs_to_plot, sample_res, sample_rate, i, filename=(output_dir+'/'+frame_file_name+'-'+str(i).zfill(3)+'.png'), ss_pf_list=ss_pfs)
    # plot_profile(pfs_to_plot, sample_res, sample_rate, i, filename=(output_dir+'/'+pf_file+'-'+str(i).zfill(3)+'.png'))

# if not isinstance(ss_pfs, type(None)):
#     ss_pfs = pd.concat(ss_pfs)
#     ss_pfs.to_csv(frame_file_name+'.csv')
