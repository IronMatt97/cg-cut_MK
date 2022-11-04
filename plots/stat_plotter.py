from matplotlib import colors
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

params = {
    'axes.titlesize': 16,
    'axes.labelsize': 12,
    'figure.titleweight':'bold',
    'figure.titlesize':20
}
# Updating the rcParams in Matplotlib
plt.rcParams.update(params)

def get_raw_data():
    df = pd.read_excel('../stats.xlsx')
    return df

def gap_variations(df):
    df  = df[["name","relative_gap","ncuts","cluster_type"]]
    cluster_types = df["cluster_type"].unique()
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 8))
    fig.suptitle("Relative gap variations")
    for cluster_name, ax in zip(cluster_types,axes.flatten()):
        cluster = df[df['cluster_type'] == cluster_name]
        for name in cluster["name"].unique():
            instance = cluster[cluster['name'] == name]
            ax.plot(instance["ncuts"].values,instance["relative_gap"].values, label = name)
            ax.set_title(cluster_name)
    plt.legend(title="Instances",loc=3,bbox_to_anchor=(1,0))
    plt.savefig("gap_variations.png")

def gap_histograms(df):
    df  = df[["name","relative_gap","ncuts","cluster_type"]]
    cluster_types = df["cluster_type"].unique()
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 8))
    fig.suptitle("Relative gap distributions")
    for cluster_name, ax in zip(cluster_types,axes.flatten()):
        cluster = df[df['cluster_type'] == cluster_name]
        N,bins,patches = ax.hist(cluster["relative_gap"].values, label = cluster_name, bins=50, edgecolor = 'black')
        fracs = N / N.max()
        norm = colors.Normalize(fracs.min(), fracs.max())
        for thisfrac, thispatch in zip(fracs, patches):
            color = plt.cm.viridis(norm(thisfrac))
            thispatch.set_facecolor(color)
        ax.set_title(cluster_name)
    plt.savefig("gap_histogram.png")

def gap_variations_over_time(df):
    df  = df[["name","relative_gap","ncuts","cluster_type","elapsed_time"]]
    cluster_types = df["cluster_type"].unique()
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 8))
    fig.suptitle("Relative gap variations over time")
    for cluster_name, ax in zip(cluster_types,axes.flatten()):
        cluster = df[df['cluster_type'] == cluster_name]
        for name in cluster["name"].unique():
            instance = cluster[cluster['name'] == name]
            ax.plot(instance["elapsed_time"].values,instance["relative_gap"].values, label = name)
            ax.set_title(cluster_name)
    plt.legend(title="Instances",loc=3,bbox_to_anchor=(1,0))
    plt.savefig("gap_variations_over_time.png")

if __name__ == '__main__':
    df = get_raw_data()
    df = df.dropna()
    gap_variations(df)
    gap_histograms(df)
    gap_variations_over_time(df)
    
    