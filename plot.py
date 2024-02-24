import os
import sys
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

matplotlib.rcParams['figure.figsize'] = (6, 3.5)
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

def human_format(num, pos):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.1f%s' % (num, ['', 'k', 'M', 'B', 'T', 'P'][magnitude])

formatter = FuncFormatter(human_format)

def isnumber(x):
    try:
        float(x)
        return True
    except:
        return False

def plot_data(x_data_name, y_data_name, filename, zoom_factor, percentile):
    x = df[x_data_name].to_numpy().astype(float)
    y = df[y_data_name].to_numpy().astype(float)

    lineStart = 0 
    lineEnd = np.nanmax(x) * 1.01

    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(1,1,1)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim(lineStart, lineEnd)
    ax.set_ylim(lineStart, lineEnd)
    ax.set_xlabel("VC (s)", fontsize=xfontsize)
    ax.set_ylabel("TC (s)", fontsize=yfontsize)

    ax.scatter(x, y, s=markersize)
    ax.plot([lineStart, lineEnd], [lineStart, lineEnd], 'k-', color='r')

    #lineStart = 0 
    #lineEnd = np.nanpercentile(x, percentile)
    #axins = zoomed_inset_axes(ax, zoom_factor, loc=2) # zoom = 6
    #axins.scatter(x, y, s=markersize)
    #axins.plot([0, lineEnd], [lineStart, lineEnd], 'k-', color='r')
    #axins.set_xlim(0, lineEnd) # Limit the region for zoom
    #axins.set_ylim(0, lineEnd)

    #axins.set_xlabel("VC (s)", fontsize=xfontsize)
    #axins.set_ylabel("TC (s)", fontsize=yfontsize)

    #plt.xticks(visible=False)  # Not present ticks
    #plt.yticks(visible=False)
    #mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5", linewidth=0.5, fill=True)

    plot_file_path = os.path.join(exp_home, "plots", f"{filename}.pdf")
    fig.savefig(plot_file_path)

def compute_ratios(folder_path):
    analyses_meta = {
        "HB": ("HB_result.csv", "HBVectorClockNoRace", "HBTreeClockNoRace"),
        "HBRaceAnalysis": ("HBRaceAnalysis_result.csv", "HBVectorClockRaceAnalysis", "HBTreeClockRaceAnalysis"),
        "SHB": ("SHB_result.csv", "SHBVectorClockNoRace", "SHBTreeClockNoRace"),
        "SHBRaceAnalysis": ("SHBRaceAnalysis_result.csv", "SHBVectorClockRaceAnalysis", "SHBTreeClockRaceAnalysis"),
        "MAZ": ("MAZ_result.csv", "MAZVectorClockNoRace", "MAZTreeClockNoRace"),
        "MAZRaceAnalysis": ("MAZRaceAnalysis_result.csv", "MAZVectorClockRaceAnalysis", "MAZTreeClockRaceAnalysis") 
    }
    
    ratios = {}

    for a in analyses_meta:
        filename, vc_alg, tc_alg = analyses_meta[a]
        file_path = os.path.join(folder_path, filename)

        df = pd.read_csv(file_path)

        vc_avgs = df[df["algorithm"] == vc_alg].groupby(["benchmark"]).mean()["average_total_time"]
        tc_avgs = df[df["algorithm"] == tc_alg].groupby(["benchmark"]).mean()["average_total_time"]

        ratios[vc_alg] = vc_avgs
        ratios[tc_alg] = tc_avgs

    return pd.DataFrame(data=ratios)

if __name__ == "__main__":
    exp_home = sys.argv[1]

    plots_folder_path = os.path.join(exp_home, "plots")
    if not os.path.isdir(plots_folder_path):
        os.mkdir(plots_folder_path)

    df = compute_ratios(exp_home)
    df = df.replace(r'^\#DIV\/0\!$', np.NaN, regex=True)
    df = df.replace(r'^\#VALUE\!$', np.NaN, regex=True)
    df = df.replace(r'^-$', np.NaN, regex=True)
    df = df.astype(float)
    df = df / 1000.0
    print(df)

    xfontsize = 15
    yfontsize = 15
    dpi = 600
    figsize = (6, 6)
    markersize = 7
    plt.subplots_adjust(left=.15, right=.95)

    plot_data(x_data_name='HBVectorClockNoRace', y_data_name='HBTreeClockNoRace', filename='hb', zoom_factor=0.5, percentile=85)
    plot_data(x_data_name='HBVectorClockRaceAnalysis', y_data_name='HBTreeClockRaceAnalysis', filename='hb_race_analysis', zoom_factor=0.5, percentile=70)
    plot_data(x_data_name='SHBVectorClockNoRace', y_data_name='SHBTreeClockNoRace', filename='shb', zoom_factor=0.5, percentile=75)
    plot_data(x_data_name='SHBVectorClockRaceAnalysis', y_data_name='SHBTreeClockRaceAnalysis', filename='shb_race_analysis', zoom_factor=0.5, percentile=75)
    plot_data(x_data_name='MAZVectorClockNoRace', y_data_name='MAZTreeClockNoRace', filename='maz', zoom_factor=0.5, percentile=70)
    plot_data(x_data_name='MAZVectorClockRaceAnalysis', y_data_name='MAZTreeClockRaceAnalysis', filename='maz_race_analysis', zoom_factor=0.5, percentile=70)

    plt.show()

