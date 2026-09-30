import pandas as pd
import numpy as np
import cv2
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import find_peaks_cwt, find_peaks
from scipy.stats import gamma
import tkinter as tk
from tkinter import filedialog, simpledialog

def gauss(x,mu,sigma,A):
    return A*np.exp(-(x-mu)**2/2/sigma**2)

def multi_gauss(x, plist):
    """
    Sum of N Gaussians.

    plist = [mu1, sigma1, A1, mu2, sigma2, A2, mu3, sigma3, A3, ...]
    len(plist) must be a multiple of 3.
    """
    y = np.zeros_like(x, dtype=float)
    for i in range(0, len(plist), 3):
        y += gauss(x, plist[i], plist[i + 1], plist[i + 2])
    return y

def multi_gamma(x, plist):
    """
    Sum of N Gamma.

    plist = [mu1, alpha1, theta1, A1, mu2, alpha2, theta2, A2, mu3, alpha3, theta3, A3, ...]
    len(plist) must be a multiple of 4.
    """
    y = np.zeros_like(x, dtype=float)
    for i in range(0, len(plist), 4):
        y += plist[i + 3]*gamma.pdf(x, a=plist[i + 1], loc=plist[i], scale=plist[i + 2])
    return y

def make_model(use_gamma='no'):
    """
    Returns a function f(x, *flat_params) that curve_fit can use,
    which internally calls multi_gauss(x, list(flat_params)).
    """
    def model(x, *flat_params):
        if use_gamma == 'no':
            return multi_gauss(x, list(flat_params))
        else:
            return multi_gamma(x, list(flat_params))
    return model

def find_overlap_boundaries(model, params, x_mins, x_maxs, x, centers, sigmas, As, use_gamma, num_points=1000):
    """
    Adjust overlapping distribution bounds to the local minimum between
    adjacent fitted Gaussian/Gamma distributions.
    """
    order = np.argsort(x_mins)
    x_mins = x_mins[order]
    x_maxs = x_maxs[order]
    centers = centers[order]
    sigmas = sigmas[order]
    As = As[order]

    for i in range(len(x_mins) - 1):
        if x_maxs[i] >= x_mins[i + 1]:

            left = x_mins[i + 1]
            right = x_maxs[i]

            if left >= right:
                continue

            x_local = np.linspace(left, right, num_points)
            y_local = model(x_local, *params)

            # Local minima of the fitted mixture.
            minima, _ = find_peaks(-y_local)

            if minima.size:
                # If several minima exist, choose the one closest to
                # the midpoint between the two distributions.
                midpoint = (left + right) / 2
                idx = minima[np.argmin(np.abs(x_local[minima] - midpoint))]
                boundary = float(x_local[idx])
            else:
                # Fallback for strongly overlapping distributions.
                if use_gamma == 'no':
                    diff = gauss(x,centers[i],sigmas[i],As[i]) - gauss(x,centers[i+1],sigmas[i+1],As[i+1])
                    idx = np.where(np.sign(diff[:-1]) != np.sign(diff[1:]))[0][0]
                    boundary = x[idx]
                else:
                    idx = np.argmin(y_local)
                    boundary = float(x_local[idx])

            # Make the two distributions meet at the local minimum.
            x_maxs[i] = boundary
            x_mins[i + 1] = boundary

    # Restore original distribution order.
    inverse = np.argsort(order)
    return x_mins[inverse], x_maxs[inverse]

def calculate_area(filename, use_gamma='no', input_limit='no', plot='no'):
    """
    Calculate intensity-distribution areas for one TIFF image.

    Parameters
    ----------
    filename : str
        Path to the TIFF image.
    use_gamma : str, optional
        If 'yes', use Gamma distributions for fitting, otherwise Gaussian distributions.
    plot : str, optional
        If 'yes', display the histogram and fitted distribution mixture.
    """
    # img = cv2.imread('image/FM2025_0355_PP_La1.03Fe12B6_1100C, 1d, Zirc wrap (2026)-4.1.tif', 0)
    img = cv2.imread(filename, 0)
    img_clean = img[:-200, :]

    var = 3
    num_bins = 1000
    img_max = img_clean.max()
    img_min = img_clean.min()

    counts, bins = np.histogram(img_clean, bins=num_bins, range=(img_min, img_max))
    total_area = counts.sum()
    x = (bins[1:] + bins[:-1]) / 2

    peaks = find_peaks_cwt(counts, widths=50)
    x_peaks = x[peaks]
    if input_limit == 'yes':
        x_peaks_low  = simpledialog.askfloat('Lower Cut-Off', 'Enter lower cut-off', initialvalue=50)
        x_peaks_high = simpledialog.askfloat('Upper Cut-Off', 'Enter upper cut-off', initialvalue=235)
    else:
        x_peaks_low  = 50
        x_peaks_high = 235
    x_peaks = x_peaks[(x_peaks >= x_peaks_low) & (x_peaks <= x_peaks_high)]
    num_peaks = x_peaks.size

    print('filename = ', filename)
    print('Gamma fitting = ', use_gamma)
    print('lower cut-off = ', x_peaks_low)
    print('upper cut-off = ', x_peaks_high)
    print('x_peaks = ', x_peaks)

    # curve fitting
    expected = []
    if use_gamma == 'no':
        for idx in range(num_peaks):
            expected.append(x_peaks[idx])
            expected.append(10.0)
            expected.append(1000.0)
    else:
        for idx in range(num_peaks):
            expected.append(x_peaks[idx])
            expected.append(9.0)
            expected.append(0.5)
            expected.append(1000.0)

    model = make_model(use_gamma)
    params, cov = curve_fit(model, x, counts, expected)

    sigma=np.sqrt(np.diag(cov))

    x_mins = []
    x_maxs = []
    centers = []
    sigmas = []
    As = []

    if use_gamma == 'no':
        for mu, sigma, Amp in zip(params[::3], np.abs(params[1::3]), params[2::3]):
            centers.append(mu)
            x_mins.append(mu - var * sigma)
            x_maxs.append(mu + var * sigma)
            sigmas.append(sigma)
            As.append(Amp)
    else:
        for mu, alpha, theta in zip(params[::4], params[1::4], params[2::4]):
            centers.append(mu)
            x_mins.append(gamma.ppf(0.0027, a=alpha, loc=mu, scale=theta))
            x_maxs.append(gamma.ppf(0.9973, a=alpha, loc=mu, scale=theta))

    x_mins = np.asarray(x_mins, dtype=float)
    x_maxs = np.asarray(x_maxs, dtype=float)
    centers = np.asarray(centers, dtype=float)
    sigmas = np.asarray(sigmas, dtype=float)
    As = np.asarray(As, dtype=float)

    x_mins, x_maxs = find_overlap_boundaries(model=model, params=params, x_mins=x_mins, x_maxs=x_maxs, x=x, centers=centers, sigmas=sigmas, As=As, use_gamma=use_gamma)

    x_max_low = np.min(x_mins)
    x_min_high = np.max(x_maxs)

    areas = []
    for x_min, x_max in zip(x_mins, x_maxs):
        area = np.array(counts, copy=True)
        area[x < x_min] = 0
        area[x > x_max] = 0
        print('x_min, x_max, area (%) = ', x_min, x_max, area.sum() * 100 / total_area)
        areas.append(area.sum() * 100 / total_area)

    area = np.array(counts, copy=True)
    x_max = x_max_low
    area[x > x_max] = 0
    print('crack/pore area(%) =', np.round(area.sum()*100/total_area, 2))
    areas.append(area.sum()*100/total_area)

    area = np.array(counts, copy=True)
    x_min = x_min_high
    area[x < x_min] = 0
    print('oxide area(%) =', np.round(area.sum()*100/total_area, 2))
    areas.append(area.sum()*100/total_area)

    if plot == 'yes':
        plt.stairs(counts, bins)
        plt.plot(x, model(x, *params), color='red', lw=3, label='model')
        plt.show()

    return areas, num_peaks

def get_options(parent=None):
    root_option = tk.Toplevel(parent)
    root_option.title("Options")
    root_option.geometry("400x200")
    root_option.resizable(False, False)

    # Variables
    use_gamma_var = tk.BooleanVar(master=root_option, value=False)
    plot_var = tk.BooleanVar(master=root_option, value=False)
    input_limit_var = tk.BooleanVar(master=root_option, value=False)

    # Checkbuttons
    tk.Checkbutton(root_option, text="Use gamma distribution fitting", variable=use_gamma_var).pack(anchor="w", padx=20, pady=5)
    tk.Checkbutton(root_option, text="Plot histogram", variable=plot_var).pack(anchor="w", padx=20, pady=5)
    tk.Checkbutton(root_option, text="Input lower/upper cut-off limit", variable=input_limit_var).pack(anchor="w", padx=20, pady=5)

    # Store returned values
    result = []

    def submit():
        result.extend([
            'yes' if use_gamma_var.get() else 'no',
            'yes' if plot_var.get() else 'no',
            'yes' if input_limit_var.get() else 'no'
        ])
        root_option.destroy()

    tk.Button(root_option, text="OK", command=submit).pack(pady=10)

    root_option.transient(parent)
    root_option.grab_set()
    root_option.protocol("WM_DELETE_WINDOW", root_option.destroy)
    root_option.wait_window()

    return result[0], result[1], result[2]

def calculate_areas():
    """Select multiple TIFF files and calculate their areas."""
    filenames = filedialog.askopenfilenames(initialdir="/",
                                            title="File Names",
                                            filetype=(("tif files", "*.tif"),("All Files", "*.*")))

    use_gamma, plot, input_limit = get_options()

    areas = []
    num_peaks = []
    for filename in filenames:
        areas_tmp, num_peaks_tmp = calculate_area(filename, use_gamma=use_gamma, input_limit=input_limit, plot=plot)
        areas.append(areas_tmp)
        num_peaks.append(num_peaks_tmp)

    num_peaks_max = max(num_peaks)
    peak_cols = [f'peak area-{i+1} (%)' for i in range(num_peaks_max)]
    columns = ['filename'] + peak_cols + ['crack/pore area (%)', 'oxide area (%)']

    rows = []
    for filename, area, n in zip(filenames, areas, num_peaks):
        row = {'filename': filename}

        # peak areas (pad with 0 if this file has fewer peaks)
        for i, col in enumerate(peak_cols):
            row[col] = area[i] if n > i else 0

        # trailing fixed fields
        row['crack/pore area (%)'] = area[-2]
        row['oxide area (%)'] = area[-1]

        rows.append(row)

    df = pd.DataFrame(rows, columns=columns)

    filename_output = filenames[0].replace('.tif', '.csv')
    filename_output = simpledialog.askstring("Enter Output File", 
                                            "Enter output path/file name (and .ext):", 
                                            initialvalue=filename_output)
    df.to_csv(filename_output, index=False)