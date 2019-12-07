import numpy as np
import scipy.ndimage as ndimage
from scipy.spatial import ConvexHull
from sklearn.cluster import KMeans


def segment_image(img):

    min_size = 5  # min number of pixels in x-axis
    padding = 10  # padding around the mole pixel

    # transform RGB into vector for kmeans
    img_2d = img.reshape(-1, img.shape[2])

    # cluster the image
    clusters = KMeans(n_clusters=3, random_state=0).fit(img_2d)

    # get the cluster labels
    cluster_labels = clusters.labels_
    cluster_labels = cluster_labels.reshape((img.shape[0], img.shape[1]))

    # find cluster than is associated with minimum label (RED band only)
    min_cluster_label = np.argmin(ndimage.minimum(img[:, :, 0], labels=cluster_labels, index=np.unique(cluster_labels)))

    # get the mask associated with label containing minima
    min_cluster_mask = cluster_labels == min_cluster_label

    # relabel min cluster mask to extract each unique mole
    labeled_image, num_features = ndimage.label(min_cluster_mask)

    # get the convex hull of the plume
    mole_images = []
    for l in np.unique(labeled_image):

        if not l:
            continue

        y, x = np.where(labeled_image == l)
        if x.size < min_size:  # not enough points to make hull
            continue
        points = np.array(list(zip(y, x)))
        hull = ConvexHull(points)
        hull_indicies_y, hull_indicies_x = points[hull.vertices, 0], points[hull.vertices, 1]

        # mole
        min_r = hull_indicies_y.min() - padding
        max_r = hull_indicies_y.max() + padding
        min_c = hull_indicies_x.min() - padding
        max_c = hull_indicies_x.max() + padding
        mole_image = (img[int(min_r):int(max_r), int(min_c):int(max_c)])
        if np.all(np.array(mole_image.shape) != 0):
            mole_images.append(mole_image)
    return mole_images


def main():
    import glob
    from skimage import io
    import matplotlib.pyplot as plt
    img_path_list = glob.glob('../../skin-disease-detector/data/segmentation_test_data/*.jpg')
    for img_path in img_path_list:
        print(img_path)
        img = io.imread(img_path)
        image_segments = segment_image(img)
        for image in image_segments:
            plt.imshow(image)
            plt.show()


if __name__ == "__main__":
    main()