# =============================================================================
# Created By  : VALLOT Sylvain
# Created Date: 2021
# =============================================================================

import re
import os
import numpy as np


def saveazi(fname: object, cts, tth, chi, npt_tth: int, npt_chi: int) -> object:
    """Function for writing integration parameters to a header

    Args:
        fname (object): File to integrate
        cts ([type]): [description]
        tth ([type]): [description]
        chi ([type]): [description]
        npt_tth (int): [description]
        npt_chi (int): [description]

    Returns:
        object: .dat file with header
    """
    f = open(fname, "w")
    ligne = "### tth/chi " + \
        str(npt_tth) + "  2theta values / " + str(npt_chi) + "  sectors  \n"
    f.write(ligne)
    f.write("### tth/chi  ")
    f.write("  ".join(["%.2f" % (c) for c in chi]))
    f.write("\n")
    for i in range(len(tth)):
        f.write("%f  " % (tth[i]))
        f.write("  ".join(["%.4f" % (c) for c in cts[:, i]]))
        f.write("\n")
    f.close()


def prepend_line(file: object, line: str, multi: bool) -> object:
    """Add a line in the file header

    Args:
        file (object): File to modify
        line (str): Line to add
        multi (bool): Add several lines, line is then a list 

    Returns:
        object: File modified with new line added
    """
    temp_file = file + '.bak'
    with open(file, 'r') as read_file, open(temp_file, 'w') as write_file:
        if multi == True:
            for l in line:
                write_file.write(l + '\n')
        else:
            write_file.write(line + '\n')
        for line in read_file:
            write_file.write(line)
    os.remove(file)
    os.rename(temp_file, file)


def delimiter_parser(filename: str) -> list:
    """Isolate file name and numbering pattern

    Args:
        filename (str): File name

    Returns:
        list: List containing the file digitization at index 0 and the file pattern at index 1
    """
    filename_array = re.split(r'_|-', filename)
    file_index = int(filename_array[-1])
    file_pattern = '_'.join(filename_array[:-1])

    return [file_index, file_pattern]


def file_parser(dir: object, imageArr: list, processedArr: list, accel: bool):
    """Upstream determination of useful files and results obtained to limit the number of integration operations
    
    Args:
        dir (object): Directory containing files to be integrated
        imageArr (list): List containing 2D images to be integrated
        processedArr (list): List containing 1D integrations according to imageArr
        accel (bool): Boolean to take into account files created during acceleration
    """
    for file in os.listdir(dir):
        img = os.path.splitext(file)
        if(img[1] == '.cbf'):
            if accel == True:
                if accel_parser(img[0]) == True:
                    imageArr.append(file)
                    processedArr.append(img[0] + '.dat')
            else:
                imageArr.append(file)
                processedArr.append(img[0] + '.dat')


def accel_parser(file: object) -> bool:
    """Separate the useful files from those produced by accelerating the beam scan.
    Valid only if the acceleration diffractograms are odd.    

    Args:
        file (object): File to analyze

    Returns:
        bool: Boolean, True if diffractogram is useful
    """
    index = delimiter_parser(file)[0]
    if index % 2 == 0:
        return True


def file_rename(file: object, pattern: str, accel: bool) -> str:
    """Rename a file, keeping the basic pattern and simplifying existing numbering

    Args:
        file (object): File to rename
        pattern (str): File name pattern to use
        accel (bool): Condition for taking beam acceleration files into account

    Returns:
        str:New file name with simplified numbering
    """
    divider = 1
    if accel == True:
        divider = 2
    file_index = int(file.replace(pattern, '').replace(
        '_', '').replace('-', '').replace('.dat', ''))
    new_filename = pattern + '_' + str(int(file_index / divider)) + '.dat'
    return new_filename


def intensity_correction(file: object, intensity_correction: int) -> object:
    """Uniform intensity correction for all points in a 2-column XY file

    Args:
        file (object): File with Ys to be modified
        intensity_correction (int): Integer value of intensity to be added to Y values

    Returns:
        object: 2-column file with modified Y
    """
    temp = []
    temp_header = []
    with open(file) as f:
        for lines in f:
            if lines.startswith("#"):
                temp_header.append(lines)
            else:
                data = lines.split()
                x = float(data[0])
                y = float(data[1]) + float(intensity_correction)
                temp.append([x, y])

    with open(file, "w+") as f:
        for _ in temp_header:
            f.write(_)
        for _ in temp:
            f.write(str(_).replace("[", '').replace("]", '')
                    .replace(",", "\t") + "\n")


def azim_angles(aperture: int) -> tuple:
    """Generation of integration limits as a function of the selected aperture around the 0° and 90° axes
    Multi-part method because pyFAI uses trigonometric notation -Pi/Pi

    Args:
        aperture (int): Aperture angle

    Returns:
        tuple: Tuple of the integration interval for axis 0 and axis 90
    """
    if aperture > 90:
        aperture = 90
    half_aperture = aperture / 2

    axis0 = ([- half_aperture, half_aperture],
            [180-half_aperture, 180], [-180+half_aperture, -180])
    axis90 = ([-90-half_aperture, -90+half_aperture],
            [90-half_aperture, 90+half_aperture])

    return axis0, axis90


def azim_integ(poni: object, dark: object, im: object, nb_pts: int, interval_angle: list):
    """Azimuthal integration for two given angular bounds

    Args:
        poni (object): Detector configuration poni file
        dark (object): Detector dark file
        im (object): File to integrate
        nb_pts (int): Number of point in the integrated diffractogram
        interval_angle (list): List containing start and end of integration angle

    Returns:
        [type]: [description]
    """
    if dark == None:
        return poni.integrate1d(im.data, nb_pts,
                            unit="2th_deg",
                            method="cython",
                            azimuth_range=(float(interval_angle[0]), float(interval_angle[1])))
    else:
        return poni.integrate1d(im.data, nb_pts,
                            unit="2th_deg",
                            dark=dark.data,
                            method="cython",
                            azimuth_range=(float(interval_angle[0]), float(interval_angle[1])))


def azim_sum(poni: object, dark: object, file: object, axis: tuple, nb_pts: int) -> np.ndarray:
    """Sum the different partial integrations of the defined intervals as a function of the opening angle

    Args:
        axis (tuple): Tuple containing the different integration intervals
        nbpts (int):Number of points for 1D diffractogram

    Returns:
        np.ndarray: Array 2D, a column for X and a column for Y
    """
    axis_arr = np.zeros((2, nb_pts))
    for i in axis:
        temp = np.array(azim_integ(poni, dark, file, nb_pts, i))
        axis_arr[0] = temp[0]
        axis_arr[1] = axis_arr[1] + temp[1]
    return axis_arr


def get_axis(i: int) -> int:
    """Obtain the ° position of the axis

    Args:
        i (int): Index in axis angle list

    Returns:
        int: Position in ° of axis
    """
    if i == 0:
        return 0
    else:
        return 90


def azim_filename(pattern, axis_index, aperture, index):
    return f"{pattern}_axis{axis_index}_apert{aperture}_{index}"


def save_to_file(file: str, data: object):
    """Save data to a file

    Args:
        file (str): Name for the file
        data (object): Data to be saved in two column format
    """
    f = open(file, "w")
    for i in range(len(data[0])):
        f.write("%f  " % (data[0][i]))
        f.write("%.4f" % (data[1][i]))
        f.write("\n")
    f.close()