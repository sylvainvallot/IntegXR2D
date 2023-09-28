# =============================================================================
# Created By  : VALLOT Sylvain
# Created Date: 2021
# =============================================================================

# GUI import
from colored import stylize, attr, fg, set_tty_aware
set_tty_aware(False)
# Import for handling diffractograms
import os
import shutil
import pyFAI
import fabio
import time
import src.utils as IXR2D



def ui_integration(action):
    # Integration UI
    integration = action.add_parser(
        'integration', prog='2D image integration')

    groupInteg = integration.add_argument_group("Integration settings")
    groupOptionInteg = integration.add_argument_group("Integration options")
    
    # Folder containing 2D images
    groupInteg.add_argument(
        "IMAGES_2D",
        metavar='Images 2D',
        help="Folder containing ONLY 2D images to integrate",
        widget="DirChooser",
        gooey_options={
            'full_width': True,
        }
    )
    # PONI file
    groupInteg.add_argument(
        "PONI",
        help="Detector calibration .poni file to use",
        widget="FileChooser",
        gooey_options={
            'validator': {
                'test': '".poni" in user_input',
                'message': 'Invalid .poni file, check extension'
            },
        },
    )
    # Check if acceleration images are present
    groupInteg.add_argument(
        "ACCEL",
        metavar="Acceleration files available?",
        help="Are the 2D beam acceleration images in the file?",
        choices=['Yes', 'No'],
        default='Yes',
    )
    # Creat a group for a mutually exclusive choice for the file names
    delimiter = groupInteg.add_mutually_exclusive_group(
        required=True,
        gooey_options={
            'initial_selection': 0,
            'full_width': True,
        }
    )
    # Delimiter in file names
    delimiter.add_argument(
        '--DELIMITER_ON',
        metavar='Delimiter - or _ ',
        action='store_true',
        help='File names have a - or _ delimiter to separate the file name pattern and the numbering. For example: Sample-X-000 or Sample_X_000'
    )
    # File name pattern
    delimiter.add_argument(
        '--FILE_PATTERN',
        metavar='File name pattern',
        help='Enter the file name pattern without numbering',
        gooey_options={
            'validator': {
                'test': '" " != user_input',
                'message': 'Invalid file name pattern'
            }
        },
    )
    # DARK file
    groupOptionInteg.add_argument(
        "--DARK", help="Dark file to suppress detector noise", widget="FileChooser", gooey_options={
            'full_width': True,
        }
    )
    # Number of points per 1D diffractogram
    groupOptionInteg.add_argument(
        "NPT",
        metavar="Number of points",
        default=6000,
        type=int,
        help='Number of points per 1D diffractogram'
    )
    # Intensity correction
    groupOptionInteg.add_argument(
        'ICOR',
        metavar='Intensity correction', default=0, type=int,
        help='Intensity to shift the diffractogram'
    )
    # Creation of a group for a mutually exclusive choice for the circular integration
    azymInteg = groupOptionInteg.add_mutually_exclusive_group(
        required=True,
        gooey_options={
            'initial_selection': 0
        }
    )
    # Total integration
    azymInteg.add_argument(
        '--TOTAL_INTEG',
        metavar='Total integration',
        action='store_true',
        help='360° integration'
    )
    # Partial integration
    azymInteg.add_argument(
        '--PARTIAL_INTEG',
        metavar='Partial integration',
        help='Enter opening angle in ° around the two orthogonal axes',
        type=int,
        gooey_options={
            'validator': {
                'test': 'int(user_input) < 90',
                'message': 'Please enter an angle value less than 90°'
            }
        },
    )


def integrateXRD(args):
    IMAGES_2D, PONI, DARK, ACCEL, NPT, ICOR = [
        args.IMAGES_2D, args.PONI, args.DARK, args.ACCEL, args.NPT, args.ICOR]
    TOTAL_INTEG, PARTIAL_INTEG = [args.TOTAL_INTEG, args.PARTIAL_INTEG]
    DELIMITER_ON, FILE_PATTERN = [args.DELIMITER_ON, args.FILE_PATTERN]

    poni = pyFAI.load(PONI)

    if DARK:
        dark = fabio.open(DARK)
    else:
        dark = None

    npt_tth = int(NPT)
    npt_chi = 1

    imagesArray = []
    processedArray = []

    os.chdir(IMAGES_2D)

    # Isolate useful diffracograms by removing those produced during beam acceleration
    if ACCEL == 'Oui':
        print(stylize(">> Scanning acceleration files", attr("bold")))
        IXR2D.file_parser(IMAGES_2D, imagesArray, processedArray, accel=True)
    else:
        IXR2D.file_parser(IMAGES_2D, imagesArray, processedArray, accel=False)

    print(f"Integration of {len(imagesArray)} diffraction images")

    # Total integration of 2D diffractograms to 1D
    if TOTAL_INTEG == True:
        print(stylize(">> Total integration of 2D diffractograms", attr("bold")))

        for img in imagesArray:
            try:
                im = fabio.open(img)
                print(f'Processing: {im.filename}')
                
                if DARK:
                    cts, tth, chi = poni.integrate2d(im.data, npt_tth, npt_chi,
                                                    unit="2th_deg", dark=dark.data, method="cython")
                else:
                    cts, tth, chi = poni.integrate2d(im.data, npt_tth, npt_chi,
                                                    unit="2th_deg", method="cython")
                
                filename = os.path.splitext(img)[0] + '.dat'
                
                IXR2D.saveazi(filename, (cts),
                            tth, chi, npt_tth, npt_chi)
            except:
                print(stylize(f'>> Problem after image : {img}', fg(
                    "red") + attr("bold")))

        if DELIMITER_ON == True:
            FILE_PATTERN = IXR2D.delimiter_parser(
                os.path.splitext(imagesArray[0])[0])[1]

        INTEG_FOLDER = FILE_PATTERN + '_INTEG_FULL'

        print(stylize(">> Cleaning working directory", attr("bold")))

        if not os.path.exists(INTEG_FOLDER):
            os.mkdir(INTEG_FOLDER)

        # Move integrated .dat files with overwrite if existing
        for file in processedArray:
            shutil.move(os.path.join(IMAGES_2D, file),
                        os.path.join(INTEG_FOLDER, file))

        # Apply intensity correction on diffractograms
        if ICOR != 0:
            print(
                stylize(f">> Intensity correction of {ICOR}", attr("bold")))
            for file in os.listdir(INTEG_FOLDER):
                print(f'Processing: {file}')
                IXR2D.intensity_correction(
                    os.path.join(INTEG_FOLDER, file), ICOR)

        time.sleep(1)

        # Simplified numbering of diffractograms for easier management in FullpProf with overwrite
        for file in os.listdir(INTEG_FOLDER):
            if file in processedArray:
                original = os.path.join(INTEG_FOLDER, file)
                comment = str(f"### Original file: {file}")
                IXR2D.prepend_line(original, comment, multi=False)

                if(ACCEL == 'Yes'):
                    output = os.path.join(INTEG_FOLDER, IXR2D.file_rename(
                        file, FILE_PATTERN, accel=True))
                else:
                    output = os.path.join(INTEG_FOLDER, IXR2D.file_rename(
                        file, FILE_PATTERN, accel=False))

                try:
                    os.rename(original, output)
                except (FileNotFoundError, OSError):
                    os.remove(output)
                    os.rename(original, output)

    # Intégration partielle des diffractogrammes 2D
    if TOTAL_INTEG == False:
        print(stylize(">> Partial integration", attr("bold")))

        axis0, axis90 = IXR2D.azim_angles(PARTIAL_INTEG)

        if DELIMITER_ON == True:
            FILE_PATTERN = IXR2D.delimiter_parser(
                os.path.splitext(imagesArray[0])[0])[1]

        AZIM_INTEG_FOLDER = f"{FILE_PATTERN}_INTEG_AZIM_{PARTIAL_INTEG}"
        azim_array = []

        for img in imagesArray:
            try:
                im = fabio.open(img)
                print(f'> Processing: {im.filename}')
                azim_axis = [
                    IXR2D.azim_sum(poni, dark, im, axis0, npt_tth),
                    IXR2D.azim_sum(poni, dark, im, axis90, npt_tth)
                ]

                for i in range(len(azim_axis)):
                    if DELIMITER_ON == True:
                        index = IXR2D.delimiter_parser(
                            os.path.splitext(img)[0])[0]
                    else:
                        index = os.path.splitext(
                            img)[0].replace(FILE_PATTERN, '')
                    file = IXR2D.azim_filename(FILE_PATTERN, int(
                        IXR2D.get_axis(i)), PARTIAL_INTEG, index) + '.dat'
                    IXR2D.save_to_file(file, azim_axis[int(i)])
                    azim_array.append(file)
                    print(f"File saved: {file}")
            except:
                print(stylize(f'>> Problem after image : {img}', fg(
                    "red") + attr("bold")))

        print(stylize(">> Cleaning working directory", attr("bold")))

        if not os.path.exists(AZIM_INTEG_FOLDER):
            os.mkdir(AZIM_INTEG_FOLDER)

        # Move integrated .dat files with overwrite if existing
        for file in azim_array:
            shutil.move(os.path.join(IMAGES_2D, file),
                        os.path.join(AZIM_INTEG_FOLDER, file))

        # Apply intensity correction on diffractograms
        if ICOR != 0:
            print(
                stylize(f">> Intensity correction of {ICOR}", attr("bold")))
            for file in os.listdir(AZIM_INTEG_FOLDER):
                print(f'Processing: {file}')
                IXR2D.intensity_correction(
                    os.path.join(AZIM_INTEG_FOLDER, file), ICOR)

        time.sleep(1)

        # Add integration parameters to the header of the file
        for file in os.listdir(AZIM_INTEG_FOLDER):
            if file in azim_array:
                original = os.path.join(AZIM_INTEG_FOLDER, file)
                comment = str(f"### Original file: {file}")
                azim_comment = str(
                    f"### Azimutal integration parameters: \n### Angle: {PARTIAL_INTEG} deg - Npt: {npt_tth}")
                IXR2D.prepend_line(
                    original, [comment, azim_comment], multi=True)
