import numpy as np
from scipy.ndimage import center_of_mass
from tqdm import tqdm
from scipy.spatial import distance
from scipy.optimize import linear_sum_assignment
from matplotlib import pyplot as plt
import scipy.linalg as sla


def ccl_3d(all_image_arr):
    """
    First we extract the labels of the components for all the cells
    across all the frames. Thus the number of components and their labels
    are discovered here:
    """
    from scipy.ndimage import label

    all_image_arr = np.asarray(all_image_arr)
    structure = np.ones((3, 3, 3), dtype=int)
    all_labeled = np.zeros(shape=all_image_arr.shape)
    all_ncomponents = np.zeros(all_image_arr.shape[0])

    for frames in tqdm(range(all_image_arr.shape[0]), desc="3D Connected Component Calculation"):
        all_labeled[frames], all_ncomponents[frames] = label(all_image_arr[frames], structure)

    return all_labeled, all_ncomponents


def noise_removal(all_img_arr, all_labeled, vol_threshold=1):
    """
    For Removing the noise,, i've considered only the components with
    the volume greater tha 1 pixel. Thus first I computed the volume of
    each component and then extracted the centers only for the components
    with the volume greater than 1 pixels:
    """
    all_img_arr = np.asarray(all_img_arr)

    unique = list()
    counts = list()
    for frames in range(all_img_arr.shape[0]):
        unq = np.unique(all_labeled[frames], return_counts=True)
        unique.append(unq[0])
        counts.append(unq[1])

    # Here I'm selecting only the center of the components with the volume
    # less than 1 pixel and put them in thr_idxs list  :

    thr_idxs = [[]]
    for i in tqdm(range(len(counts)), desc=f"Selecting volumes > {vol_threshold}"):
        for j in range(1, len(counts[i])):
            if counts[i][j] > vol_threshold:
                thr_idxs[i].append(unique[i][j])
        thr_idxs.append([])
    thr_idxs = [pick for pick in thr_idxs if len(pick) > 0]

    return thr_idxs


def center_detection(all_img_arr, all_labeled, thr_idxs):
    all_img_arr = np.asarray(all_img_arr)

    all_centers_noisefree = []
    for frames in tqdm(range(all_img_arr.shape[0]), desc="Detecting the center of components."):
        all_centers_noisefree.append(center_of_mass(all_img_arr[frames], labels=all_labeled[frames], index=thr_idxs[frames]))

    return all_centers_noisefree


def tracker(all_centers):
    all_cen = all_centers
    new_objects = [[(0, x)] for x in all_centers[0]]

    t_limit = 20

    for i in tqdm(range(1, len(all_cen) - 1), desc="Tracking..."):
        current_frame = all_cen[i]
        last_known_centers = [obj[-1][1] for obj in new_objects if len(obj) > 0]
        cost = distance.cdist(last_known_centers, current_frame, "euclidean")
        obj_ids, new_centers_ind = linear_sum_assignment(cost)

        all_center_inds = set(range(len(current_frame)))

        for obj_id, new_center_ind in zip(obj_ids, new_centers_ind):
            if (
                distance.euclidean(
                    np.array(current_frame[new_center_ind]),
                    np.array(new_objects[obj_id][-1][1]),
                )
                <= t_limit
            ):
                all_center_inds.remove(new_center_ind)
                new_objects[obj_id].append((i, current_frame[new_center_ind]))

        for new_center_ind in all_center_inds:
            new_objects.append([(i, current_frame[new_center_ind])])
    xx = [[]]
    yy = [[]]
    zz = [[]]
    for i in range(len(new_objects)):
        for j in range(len(new_objects[i])):
            zz[i].append(new_objects[i][j][1][0])
            xx[i].append(new_objects[i][j][1][1])
            yy[i].append(new_objects[i][j][1][2])
        xx.append([])
        zz.append([])
        yy.append([])

    zz = [pick for pick in zz if len(pick) > 0]
    xx = [pick for pick in xx if len(pick) > 0]
    yy = [pick for pick in yy if len(pick) > 0]

    return (xx, yy, zz)


def preprocessing_for_clustering(x, y, z, frame_number, object_numbers):
    newxx = []
    newyy = []
    newzz = []
    for i in range(object_numbers):
        if len(x[i]) == frame_number:
            newxx.append(x[i])
            newyy.append(y[i])
            newzz.append(z[i])
    # print ('len obj(' +str(i) +')='+str(len(xx[i])) )
    # allx = np.asarray(newxx)
    # ally = np.asarray(newyy)
    # allz = np.asarray(newzz)

    return (newxx, newyy, newzz)


def laplacian(A):
    """Computes the symetric normalized laplacian.
    L = D^{-1/2} A D{-1/2}
    """
    D = np.zeros(A.shape)
    w = np.sum(A, axis=0)
    D.flat[:: len(w) + 1] = w ** (-0.5)  # set the diag of D to w
    return D.dot(A).dot(D)


# def apply_martin()
def state_space(raw_data, q):
    import numpy as np
    import numpy.linalg as linalg

    """
    Performs the state-space projection of the original data using principal
    component analysis (eigen-decomposition).
    Parameters
    ----------
    raw_data : array, shape (N, M)
        Row-vector data points with M features.
    q : integer
        Number of principal components to keep.
    Returns
    -------
    X : array, shape (q, M)
        State-space projection of the original data.
    C : array, shape (N, q) the PCA matrix (useful for returning to the data space)
        Projection matrix.
    """
    if q <= 0:
        raise Exception('Parameter "q" restricted to positive integer values.')

    # Perform the SVD on the data.
    # For full documentation on this aspect, see page 15 of Midori Hyndman's
    # master's thesis on Autoregressive modeling.
    #
    # Y = U * S * Vt,
    #
    # Y = C * X,
    #
    # So:
    # C = first q columns of U
    # S_hat = first q singular values of S
    # Vt_hat = first q rows of Vt
    #
    # X = S_hat * Vt_hat
    #
    # For the full documentation of SVD, see:
    # http://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.svd.html#numpy.linalg.svd
    U, S, Vt = linalg.svd(raw_data, full_matrices=False)
    C = U[:, :q]
    Sh = np.diag(S)[:q, :q]
    Vth = Vt[:q, :]
    X = np.dot(Sh, Vth)
    return [X, C]


def train(X, order=2):
    import numpy as np
    import numpy.linalg as linalg

    """
    Estimates the transition matrices A (and eventually the error parameters as
    well) for this AR model, given the order of the markov process.
    (in this notation, the parameter to this method "order" has the same value as "q")
    Parameters
    ----------
    X : array, shape (q, M) or (M,)
        Matrix of column vectors of the data (either original or state-space).
    order : integer
        Positive, non-zero integer order value for the order of the Markov process.
    Returns
    -------
    A : array, shape (q, q)
        Transition coefficients for the system
    """
    if order <= 0:
        raise Exception('Parameter "order" restricted to positive integer values')
    W = None

    # A particular special case first.
    if len(X.shape) == 1:
        Xtemp = np.zeros(shape=(1, np.size(X)))
        Xtemp[0, :] = X
        X = Xtemp

    # What happens in this loop is so obscenely complicated that I'm pretty
    # sure I couldn't replicate if I had to, much less explain it. Nevertheless,
    # this loop allows for the calculation of n-th order transition matrices
    # of a high-dimensional system.
    #
    # I know this could be done much more simply with some np.reshape() voodoo
    # magic, but for the time being I'm entirely too lazy to do so. Plus, this
    # works. Which is good.
    for i in range(1, order + 1):
        Xt = X[:, order - i : -i]
        if W is None:
            W = np.zeros((np.size(Xt, axis=0) * order, np.size(Xt, axis=1)))
        W[
            (i - 1) * np.size(Xt, axis=0) : ((i - 1) * np.size(Xt, axis=0)) + np.size(Xt, axis=0),
            ...,
        ] = Xt
    Xt = X[:, order:]
    A = np.dot(Xt, linalg.pinv(W))

    # The data structure "A" is actually all the transition matrices appended
    # horizontally into a single NumPy array. We need to extract them.
    matrices = []
    for i in range(0, order):
        matrices.append(
            A[
                ...,
                i * np.size(A, axis=0) : (i * np.size(A, axis=0)) + np.size(A, axis=0),
            ]
        )
    return matrices


def martin(A1, C1, A2, C2):
    """
    Computes the pairwise Martin distance between two d-order AR systems.
    Parameters
    ----------
    A1, A2 : lists
        Lists of AR parameters for two systems. They MUST be identical
        in dimensionality (q) and order (d).
    C1, C2 : array, shape (N, q)
        Subspaces for the two systems.
    Returns
    -------
    m : float
        Martin distance between the two systems.
    """
    N, q = C1.shape
    d = len(A1)
    # print(N, q, d)
    A = np.zeros(shape=(2 * q * d, 2 * q * d))
    # print(A.shape, C1t.shape, C2t.shape)

    C1t, C2t = np.zeros(shape=(N * d, q * d)), np.zeros(shape=(N * d, q * d))

    # First, append all the parameters into our gargantuan matrix.
    for i, (a1, a2) in enumerate(zip(A1, A2)):
        A[:q, (i * q) : (i * q) + q] = a1
        A[(d * q) : (d * q) + q, (d * q) + (i * q) : (d * q) + (i * q) + q] = a2

        # Do we have a higher order system?
        if d > 1:
            C1t[(i * N) : (i * N) + N, (i * q) : (i * q) + q] = C1
            C2t[(i * N) : (i * N) + N, (i * q) : (i * q) + q] = C2

    # Some clean-up.
    if d == 1:
        C1t = C1
        C2t = C2
    else:
        A[q : (d * q), : (d - 1) * q] = A[((d + 1) * q) :, (d * q) : -q] = np.identity(q * (d - 1))

    # Create the Q matrix and solve the Lyapunov system.
    Q = np.hstack([C1t, C2t]).T.dot(np.hstack([C1t, C2t]))
    X = sla.solve_discrete_lyapunov(A, Q)

    # Because roundoff errors.
    X = (X + X.T) * 0.5

    # Now continue as usual.
    P11, P12, P22 = (
        X[: (q * d), : (q * d)],
        X[: (q * d), (q * d) :],
        X[(q * d) :, (q * d) :],
    )
    PPP = sla.inv(P11).dot(P12).dot(sla.inv(P22)).dot(P12.T)

    w = sla.eigvalsh(PPP)
    maxpp = w.flatten().max()
    w = np.true_divide(w, maxpp)
    if w.prod() <= 0.0:
        # Swigert: Hey we've got a problem here.
        w = np.delete(w, np.where(w <= 0.0))
    # print(w)
    return -np.log(w.prod())


def computing_affinity(traj_pool, frame_numbers, flatten_AR_mat, number_of_points):
    # first We create a trajectory pool with the dimensions of 3x(Num_of_trajectoris)x(Num_of_frames)
    all_traj_mat = traj_pool.copy()
    all_traj_mat = all_traj_mat.reshape(all_traj_mat.shape[0], all_traj_mat.shape[1] * all_traj_mat.shape[2])
    print(all_traj_mat.shape)

    # Parameterization:
    # Then we set the AR dimensions to be 2 ( A dimensionality reduction ), so that the matrix C will be a 3x2 Matrix
    # and the matrix X will be a 2x(Num_of_trajectoris)x(Num_of_frames)
    X, C = state_space(all_traj_mat, 2)
    print("AR_Matrix, Projection_Matrix dims=", str(X.shape), str(C.shape))
    for index in range(number_of_points):
        traj2 = X[:, frame_numbers * index : (index + 1) * frame_numbers]
        A1, A2, A3, A4, A5 = train(traj2, 5)
        flatten_AR_mat[index] = np.concatenate((A1.flatten(), A2.flatten(), A3.flatten(), A4.flatten(), A5.flatten()))
    print(flatten_AR_mat.shape)

    # Now let us create a pairwise Martin Distance:

    # ===========================================================================================================

    Mrt_dist_mat = np.zeros(shape=(flatten_AR_mat.shape[0], flatten_AR_mat.shape[0]))
    for i in range(flatten_AR_mat.shape[0]):
        for j in range(flatten_AR_mat.shape[0]):
            Mrt_dist_mat[i, j] = martin(flatten_AR_mat[i], C, flatten_AR_mat[j], C)
            if i == 1 and j == 1:
                print(Mrt_dist_mat[i, j])
        print(i, j)
    # ===========================================================================================================

    Mrt_dist_mat = (Mrt_dist_mat.T + Mrt_dist_mat) * 0.5
    for i in range(Mrt_dist_mat.shape[0]):
        for j in range(Mrt_dist_mat.shape[1]):
            if i == j:
                Mrt_dist_mat[i, j] = 0.0
    print(
        'Check if any value in distance matrix in "Nan": ',
        str(np.isnan(Mrt_dist_mat).any()),
    )
    print(
        'Check if any value in distance matrix in "inf": ',
        str(np.isinf(Mrt_dist_mat).any()),
    )

    # Converting the distance to similarity:
    similarity1 = np.exp(-0.5 * Mrt_dist_mat / Mrt_dist_mat.std())

    # Now, Let us visualize the distance matrix:
    fig = plt.figure(figsize=(15, 10))
    plt.imshow(similarity1, cmap="Blues")
    plt.colorbar()
    plt.show()

    # Now, let us also compute the the Normal distance matrix too.
    lap = laplacian(Mrt_dist_mat)
    for i in range(Mrt_dist_mat.shape[0]):
        for j in range(Mrt_dist_mat.shape[1]):
            if i == j:
                lap[i, j] = 0.0
    lap = (lap + lap.T) * 0.5
    var1 = lap
    # Converting the distance to similarity:
    similarity2 = np.exp(-0.5 * lap / lap.std())

    print(np.isnan(lap).any())
    print(np.isinf(lap).any())
    plt.imshow(similarity2, cmap="hot")
    plt.colorbar()
    return similarity1, similarity2, [A1, A2, A3, A4, A5], (X, C)


def clustering(affinity, num_of_clusters, labels_file_name, affinity_file_name):
    from sklearn.cluster import spectral_clustering
    import sklearn.cluster as cluster

    nclusters = num_of_clusters
    scB = cluster.SpectralClustering(n_clusters=nclusters, affinity="precomputed", assign_labels="discretize")
    # Mrt_dist_mat2 = (Mrt_dist_mat2 - np.mean(Mrt_dist_mat2, axis=0)) / np.std(Mrt_dist_mat2, axis=0)
    scB.fit(affinity)

    yB = scB.labels_

    np.save(labels_file_name, yB)
    np.save(affinity_file_name, affinity)
    return yB


def visualize_clusters(color_list, label, xx, yy, zz, output_png_file):
    # Plotting the trajectories and showing the clustering using a specific color for each label
    col = color_list
    # for i in range(Number_of_points):
    #     plt.plot(matrix_nexb[i],matrix_neyb[i] , color= col[yB[i]])

    # plt.gca().invert_yaxis()
    # plt.show()

    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111, projection="3d")
    for i in range(len(xx)):
        ax.plot(yy[i], xx[i], zz[i], zdir="zz[i]", linewidth=3, color=col[label[i]])

    ax.xaxis.set_pane_color((0.0, 0.0, 0.0, 1.0))
    ax.yaxis.set_pane_color((0.0, 0.0, 0.0, 1.0))
    ax.zaxis.set_pane_color((0.0, 0.0, 0.0, 1.0))
    ax.view_init(35, 45)
    plt.grid(False)
    plt.savefig(output_png_file)
    plt.show()

    # import time
