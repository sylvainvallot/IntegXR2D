# UI imports
from colored import stylize, attr, fg, set_tty_aware
set_tty_aware(False)
# Imports for reversing diffractograms
import os
import shutil
import src.utils as IXR2D



def ui_reverse_fp(action):
    # UI for reversing the diffractograms order, for cyclic integration
    reverse_fp = action.add_parser(
        'reverse_fp', prog='Reverse diffractograms')
    groupReverse_fp = reverse_fp.add_argument_group(
        "Reverse the diffractogram order")
    groupReverse_fp.add_argument(
        'FOLDER',
        metavar='Diffractograms (.dat file) to reverse',
        help='Directory containing diffractograms to be reversed',
        widget='DirChooser',
        gooey_options={
            'full_width': True,
        }
    )
    # Create a group for a mutually exclusive choice for file names
    delimiter = groupReverse_fp.add_mutually_exclusive_group(
        required=True,
        gooey_options={
            'initial_selection': 0
        }
    )
    # Delimiter - or _
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


def reverse_fp(args):
    FOLDER, DELIMITER_ON, FILE_PATTERN = [
        args.FOLDER, args.DELIMITER_ON, args.FILE_PATTERN]
    fileArray = []
    reversedArray = []
    FILE_EXTENSION = '.dat'

    os.chdir(FOLDER)

    print(stylize(">> Scan of diffractograms to be inverted", attr("bold")))

    for file in os.listdir(FOLDER):
        if os.path.splitext(file)[1] == FILE_EXTENSION:
            fileArray.append(file)

    print(f"Reversing {len(fileArray)} diffractograms")

    if DELIMITER_ON == True:
        FILE_PATTERN = IXR2D.delimiter_parser(
            os.path.splitext(fileArray[0])[0])[1]

    REVERSE_FOLDER = FILE_PATTERN + '_REVERSE'

    if not os.path.exists(REVERSE_FOLDER):
        os.mkdir(REVERSE_FOLDER)

    # Creation of the list of reversed diffractograms index
    reversed_index = [i for i in range(1, len(fileArray) + 1)]

    # Numerical sorting of the 1D diffractograms
    sortedFiles = sorted(fileArray, key=lambda x: int(os.path.splitext(
        x)[0].replace(FILE_PATTERN, '').replace(FILE_EXTENSION, '').replace('_', '')))

    for file, index in zip(reversed(sortedFiles), reversed_index):
        try:
            print(f'Processing: {file}')
            reversed_filename = REVERSE_FOLDER + \
                '_' + str(index) + FILE_EXTENSION
            reversedArray.append(reversed_filename)
            shutil.copy(file, reversed_filename)
            comment = f'### Reversed file from: {file}'
            IXR2D.prepend_line(reversed_filename, comment, multi=False)
        except:
            print(stylize(f'>> Problem after file : {file}', fg(
                "red") + attr("bold")))

    print(stylize(">> Cleaning working directory", attr("bold")))

    pathDestFolder = os.path.join(FOLDER, REVERSE_FOLDER)

    for revfile in reversedArray:
        shutil.move(os.path.join(FOLDER, revfile),
                    os.path.join(pathDestFolder, revfile))
