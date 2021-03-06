from matplotlib.collections import LineCollection
import matplotlib.colors as mpl_colors
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import sys
import warnings


def plot_matrix(mat, cmap='gray_r', labels=None, which_labels='both',
                labels_palette='Set1', ax=None, colorbar_labelsize=None):
    if ax is None:
        ax = plt.gca()

    values = np.unique(mat)

    vmin = values.min()
    vmax = values.max()

    plt_image = ax.imshow(mat, interpolation='none', cmap=cmap, vmin=vmin,
                          vmax=vmax)
    ax.grid(False)
    ax.tick_params(axis='both',
                   which='both',
                   bottom=False, top=False,
                   left=False, right=False,
                   labelbottom=False, labelleft=False)

    cbar = plt.colorbar(plt_image, orientation='horizontal', pad=.05,
                        fraction=.05, ax=ax)
    cbar.ax.tick_params(labelrotation=90)
    if colorbar_labelsize is not None:
        cbar.ax.tick_params(labelsize=colorbar_labelsize)

    if labels is not None:
        labels = np.sort(labels)
        unique_labels = np.unique(labels)

        segments = []
        for lab in unique_labels:
            subset = np.where(labels == lab)[0]
            segments.append((subset[0] - 0.5, subset[-1] + 0.5))

        offset = -0.05 * mat.shape[0]
        h_segments = [((s[0], offset), (s[1], offset)) for s in segments]
        v_segments = [((offset, s[0]), (offset, s[1])) for s in segments]

        colors = sns.color_palette(labels_palette, n_colors=len(unique_labels))

        if which_labels != 'both' and which_labels != 'horizontal'\
                and which_labels != 'vertical':
            raise ValueError('Wrong value for which_labels')

        if which_labels == 'both' or which_labels == 'horizontal':
            hlc = LineCollection(h_segments, colors=colors)
            hlc.set_linewidth(5)
            hlc.set_clip_on(False)
            ax.add_collection(hlc)
        if which_labels == 'both' or which_labels == 'vertical':
            vlc = LineCollection(v_segments, colors=colors)
            vlc.set_linewidth(5)
            vlc.set_clip_on(False)
            ax.add_collection(vlc)


def line_plot_clustered(X, gt, ax=None):
    if ax is None:
        ax = plt.gca()

    X = X.copy()
    X -= np.mean(X, axis=0)
    X /= np.std(X, axis=0, ddof=1)

    keys = np.unique(gt)
    order = np.argsort([sum(gt == k) for k in keys])[::-1]
    keys = keys[order]

    for k, c in zip(keys, sns.color_palette('Set1', n_colors=len(keys))):
        mask = gt == k
        ax.plot(X[mask, :].T, color=c)
    ax.set_xlim(0, X.shape[1] - 1)
    if X.shape[1] < 10:
        xticks = range(X.shape[1])
    else:
        xticks = range(0, X.shape[1], 5)
    ax.set_xticks(xticks)
    ax.tick_params(axis='y',
                   which='both',
                   left=False, right=False,
                   labelleft=False)


def plot_data_clustered(X, gt, marker='o', ax=None, palette='Set1'):
    if ax is None:
        ax = plt.gca()

    keys = np.unique(gt)
    for k, c in zip(keys, sns.color_palette(palette, n_colors=len(keys))):
        mask = gt == k
        ax.scatter(X[mask, 0], X[mask, 1], c=c, edgecolors=c,
                   marker=marker)

    ax.set_aspect('equal')
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    X_max = X.max(axis=0)
    X_min = X.min(axis=0)
    range = (1.1 / 2.) * (X_max - X_min).max()
    center = (X_max + X_min) / 2.
    ax.set_xlim(xmin=center[0] - range, xmax=center[0] + range)
    ax.set_ylim(ymin=center[1] - range, ymax=center[1] + range)


formatwarning_orig = warnings.formatwarning
warnings.formatwarning = lambda message, category, filename, lineno, line=None:\
    formatwarning_orig(message, category, filename, lineno, line='')


def plot_data_embedded(X, **kwargs):
    if X.shape[1] != 2 and X.shape[1] != 3:
        msg = 'Plotting first two dimensions out of {}.'.format(X.shape[1])
        warnings.warn(msg, category=RuntimeWarning)

        X = X[:, :2]

    _plot_data_embedded(X, **kwargs)


def _plot_data_embedded(X, palette='hls', marker='o', s=None, ax=None,
                        elev_azim=None, alpha=1, edgecolors=None):
    if ax is None:
        ax = plt.gca()

    if palette == 'w':
        colors = [(1, 1, 1)] * len(X)
    elif palette == 'k':
        colors = [(0, 0, 0)] * len(X)
    elif palette == 'none':
        c = mpl_colors.to_rgb('#377eb8')
        colors = [c] * len(X)
    elif isinstance(palette, str) and palette[0] == '#':
        c = mpl_colors.to_rgb(palette)
        colors = [c] * len(X)
    else:
        colors = sns.color_palette(palette, n_colors=len(X))

    try:
        colors = [c + (a,) for c, a in zip(colors, alpha)]
        alpha = None
        if edgecolors is None:
            edgecolors = 'k'
    except TypeError:
        if edgecolors is None:
            edgecolors = colors

    X_max = X.max(axis=0)
    X_min = X.min(axis=0)
    range = (1.1 / 2.) * (X_max - X_min).max()
    center = (X_max + X_min) / 2.

    if X.shape[1] == 2:
        ax.scatter(X[:, 0], X[:, 1], c=colors, edgecolors=edgecolors, s=s,
                   marker=marker, alpha=alpha)

        ax.set_aspect('equal')
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.set_xlim(xmin=center[0] - range, xmax=center[0] + range)
        ax.set_ylim(ymin=center[1] - range, ymax=center[1] + range)

    elif X.shape[1] == 3:
        if elev_azim is not None:
            ax.view_init(elev=elev_azim[0], azim=elev_azim[1])

        ax.scatter(X[:, 0], X[:, 1], X[:, 2], c=colors, edgecolors=edgecolors,
                   s=s, marker=marker, alpha=alpha)

        ax.set_xlim(center[0] - range, center[0] + range)
        ax.set_ylim(center[1] - range, center[1] + range)
        ax.set_zlim(center[2] - range, center[2] + range)
        ax.set_aspect('equal')
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)


def plot_images_embedded(embedding, img_getter, labels=None, palette='hls',
                         marker='o', ax=None, subsampling=10, zoom=.5):
    if ax is None:
        ax = plt.gca()

    plot_data_embedded(embedding, palette=palette, marker=marker, ax=ax)

    if labels is not None:
        frame_palette = sns.color_palette('Set1',
                                          n_colors=len(np.unique(labels)))

    for k in range(0, len(embedding), subsampling):
        pos = embedding[k, :]
        img = img_getter(k)
        if len(img.shape) == 2:
            oim = OffsetImage(img_getter(k), cmap='gray', zoom=zoom)
        else:
            oim = OffsetImage(img_getter(k), zoom=zoom)
        oim.image.axes = ax

        if labels is not None:
            frameon = True
            bboxprops = dict(edgecolor=frame_palette[labels[k]], linewidth=3)
        else:
            frameon = False
            bboxprops = None

        ab = AnnotationBbox(oim, pos,
                            xybox=(0., 0.),
                            xycoords='data',
                            boxcoords='offset points',
                            frameon=frameon, pad=0,
                            bboxprops=bboxprops)
        ax.add_artist(ab)


def plot_bumps_1d(Y, subsampling=20, labels=None, labels_palette='hls',
                  ax=None):
    if ax is None:
        ax = plt.gca()

    idx = np.argmax(Y, axis=1)
    idx = np.sort(idx[::subsampling])
    Y_subsampled = Y[:, idx]

    ax.plot(Y_subsampled)
    ax.set_xticks([])
    ax.set_yticks([])

    if labels is not None:
        labels = np.sort(labels)
        unique_labels = np.unique(labels)

        segments = []
        for lab in unique_labels:
            subset = np.where(labels == lab)[0]
            segments.append((subset[0] - 0.5, subset[-1] + 0.5))

        offset = -0.1 * Y_subsampled.max()
        h_segments = [((s[0], offset), (s[1], offset)) for s in segments]

        colors = sns.color_palette(labels_palette, n_colors=len(unique_labels))

        hlc = LineCollection(h_segments, colors=colors)
        hlc.set_linewidth(5)
        hlc.set_clip_on(False)
        ax.add_collection(hlc)


class Logger(object):
    def __init__(self, filename="Console.log"):
        self.stdout = sys.stdout
        self.log = open(filename, "w")

    def __del__(self):
        self.log.close()

    def close(self):
        self.log.close()

    def write(self, message):
        self.stdout.write(message)
        self.log.write(message)
        self.log.flush()

    def __getattr__(self, attr):
        return getattr(self.terminal, attr)
