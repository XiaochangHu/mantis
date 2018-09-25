import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pickle
from scipy.stats import vonmises
from skimage.filters import median
from skimage.io import imread, imsave
import skimage.morphology as morpho
from skimage.measure import find_contours
from mantis import sdp_km_burer_monteiro
from experiments.utils import plot_matrix, plot_data_embedded


def extract_boundary(img):
    contour = find_contours(img.T, 0)[0]
    contour[:, 1] *= -1
    return contour


def generate_bunny_curves(save_scatter=False):
    img = imread('./bunny.png', as_grey=True)
    img = 255 * (img < 0.5).astype(np.uint8)

    img_filtered = img.copy()
    bunny_dict = {}
    for i in range(700):
        img_filtered = median(img_filtered, selem=morpho.disk(10))

        bunny = extract_boundary(img_filtered)
        bunny_dict[i] = bunny

    with open('bunny.pickle', mode='w+b') as f:
        pickle.dump(bunny_dict, f)


def bunny2circle2clusters():
    with open('bunny.pickle', mode='r+b') as f:
        bunny_dict = pickle.load(f)

    for i in bunny_dict:
        k = len(bunny_dict[i]) // 150
        print(i, k, len(bunny_dict[i][::k]))
        if len(bunny_dict[i]) > 150:
            bunny_dict[i] = bunny_dict[i][::4]
        else:
            bunny_dict[i] = bunny_dict[i]

    idx_last = max([i for i in bunny_dict])
    last_bunny = bunny_dict[idx_last]
    centroid = np.mean(last_bunny, axis=0, keepdims=True)
    norms = np.linalg.norm(last_bunny - centroid, axis=1)
    r = norms.mean()

    samples = np.linspace(0, 1, endpoint=False, num=len(last_bunny) // 4 + 1)[1:]

    circle_clustered_dict = {}
    for kappa in range(1, 200):
        angles = []
        for theta in [0, 0.5 * np.pi, np.pi, 1.5 * np.pi]:
            angles.extend(vonmises.ppf(samples, kappa, loc=theta))

        # plt.figure()
        # plt.plot(angles)
        # plt.show()

        angles = np.sort(np.mod(angles, 2 * np.pi))

        # plt.figure()
        # plt.plot(angles)
        # plt.show()

        x = r * np.cos(angles) + centroid[0, 0]
        y = r * np.sin(angles) + centroid[0, 1]
        curve = np.vstack((x, y)).T
        circle_clustered_dict[kappa] = curve

    with open('bunny_processed.pickle', mode='w+b') as f:
        pickle.dump(bunny_dict, f)
        pickle.dump(circle_clustered_dict, f)


def save_curve_plots():
    with open('bunny_processed.pickle', mode='r+b') as f:
        bunny_dict = pickle.load(f)
        circle_clustered_dict = pickle.load(f)

    bunny_filename = 'bunny{}.png'
    plt.savefig(bunny_filename.format(0))
    plt.close()

    for i in bunny_dict:
        curve = bunny_dict[i]

        plt.figure()
        plt.scatter(curve[:, 0], curve[:, 1], s=2, marker='.')
        plt.axis('equal')
        if i == 0:
            plt.gca().set_aspect('equal', adjustable='box')
            xlim = plt.xlim()
            ylim = plt.ylim()
        else:
            plt.xlim(xlim)
            plt.ylim(ylim)
            plt.gca().set_aspect('equal', adjustable='box')

        plt.savefig(bunny_filename.format(i))
        plt.close()

    for i, k in enumerate(circle_clustered_dict):
        curve = circle_clustered_dict[k]

        plt.figure()
        plt.scatter(curve[:, 0], curve[:, 1], s=2, marker='.')
        plt.axis('equal')

        plt.xlim(xlim)
        plt.ylim(ylim)
        plt.gca().set_aspect('equal', adjustable='box')

        plt.savefig(bunny_filename.format(i + len(bunny_dict)))
        plt.close()


def process_curves():
    with open('bunny_processed.pickle', mode='r+b') as f:
        bunny_dict = pickle.load(f)
        circle_clustered_dict = pickle.load(f)

    plt.figure(figsize=(20, 5), tight_layout=True)
    gs = gridspec.GridSpec(2, 12)

    bunny_idx = [0, 40, 80, 174, 524, 699]
    circle_idx = [1, 3, 5, 7, 10, 199]
    # bunny_idx = np.linspace(0, len(bunny_dict) - 1, num=5, endpoint=True,
    #                         dtype=np.int)
    # circle_idx = np.linspace(1, len(circle_clustered_dict), num=5,
    #                          endpoint=True, dtype=np.int)

    for i, idx in enumerate(bunny_idx):
        print(idx)
        curve = bunny_dict[idx]
        Y = sdp_km_burer_monteiro(curve, 32, rank=len(curve),
                                  tol=1e-6, maxiter=5000, verbose=True)
        Q = Y.dot(Y.T)
        labels = np.arange(len(curve))

        ax = plt.subplot(gs[0, i])
        plot_data_embedded(curve, ax=ax)
        ax = plt.subplot(gs[1, i])
        plot_matrix(Q, labels=labels, labels_palette='hls', ax=ax)

    for i, idx in enumerate(circle_idx):
        print(idx)
        curve = circle_clustered_dict[idx]
        Y = sdp_km_burer_monteiro(curve, 4, rank=len(curve),
                                  tol=1e-6, maxiter=5000, verbose=True)
        Q = Y.dot(Y.T)
        labels = np.arange(len(curve))

        ax = plt.subplot(gs[0, i + 6])
        plot_data_embedded(curve, ax=ax)
        ax = plt.subplot(gs[1, i + 6])
        plot_matrix(Q, labels=labels, labels_palette='hls', ax=ax)

    plt.savefig('bunny_deformation.pdf', dpi=300)

    plt.show()

def main():
    # generate_bunny_curves()
    # bunny2circle2clusters()
    # save_curve_plots()
    process_curves()


if __name__ == '__main__':
    main()
