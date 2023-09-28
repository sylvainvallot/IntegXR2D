# =============================================================================
# Created By  : VALLOT Sylvain
# Created Date: 2021
# =============================================================================

# GUI import
from colored import stylize, attr, fg, set_tty_aware
set_tty_aware(False)

# Imports for buffer creation
from math import *
import os


def ui_buffer_creator(action):
    # Buffer creation UI
    create_buffer = action.add_parser(
        'create_buffer', prog='Create a WinPLOTR buffer')
    groupBuffer = create_buffer.add_argument_group(
        "Create a WinPLOTR buffer")
    groupBuffer.add_argument(
        "buffer",
        nargs='*',
        metavar='Select diffractograms',
        help='Choose the list of 1D diffractograms for which you wish to create a buffer file for WinPlotr',
        widget="MultiFileChooser",
        gooey_options={
            'full_width': True,
        }
    )

    # Group creation for a mutually exclusive choice for circular integration
    bufferType = groupBuffer.add_mutually_exclusive_group(
        required=True,
        gooey_options={
            'initial_selection': 0
        }
    )
    # Total integration
    bufferType.add_argument(
        '--partial_buffer',
        metavar='Number of diffractograms in the buffer',
        type=int,
        help='Enter the desired number of diffractograms in the buffer'
    )
    # Degree partial integration
    bufferType.add_argument(
        '--complete_buffer',
        metavar='Buffer containing all diffractograms',
        help='All diffractograms will be added to the buffer file',
        action='store_true',
    )


def create_buffer_file(file: str, dat_files: list) -> object:
    """Writes a list of diffractograms to a .buf file

    Args:
        file (str): Filename
        dat_files (list): List of diffractograms in buffer

    Returns:
        object: File .buf
    """
    buf_filename = file + '.buf'
    f = open(buf_filename, "w")
    for i in range(len(dat_files)):
        f.write(dat_files[i])
        f.write("\n")
    f.close()
    print(stylize(f"Buffer file for WinPLOTR created: {buf_filename}", fg(
        "green")))


def buffer_creator(args: object):
    """Create a buffer file from arguments received from the Gooey interface

    Args:
        args (object): Gooey args input
    """
    print(stylize(">> Buffer file creation for WinPLOTR", attr("bold")))

    file = "buffer"
    path = args.buffer[0].replace(os.path.basename(args.buffer[0]), '')
    file_selection = []

    for f in args.buffer:
        file_selection.append(os.path.basename(f))

    if args.complete_buffer == False:
        size_buffer = int(args.partial_buffer)
        nb_files = int(len(args.buffer))
        spacer = ceil(nb_files / size_buffer)
        print(f"Buffer file with 1 diffractogram on {spacer}")

        i = 0
        buffer = []

        while i <= len(file_selection):
            buffer.append(file_selection[i])
            i += spacer

        create_buffer_file(os.path.join(path, file),  buffer)

    else:
        create_buffer_file(os.path.join(path, file), file_selection)
