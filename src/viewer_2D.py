# import pour la partie GUI
from colored import stylize, attr, fg, set_tty_aware
set_tty_aware(False)

#import pour la conversion des images 2D en tiff
import os
import numpy as np
import matplotlib.pyplot as plt
import fabio

def ui_viewer_2D(action):
    viewer_2D = action.add_parser('viewer_2D', prog='Convert 2D image to tiff')
    groupViewer_2D = viewer_2D.add_argument_group('2D to TIFF image conversion')
    groupViewer_2D.add_argument(
            "IMAGES",
            nargs='*',
            metavar='2D images',
            help="Select the 2D images to convert",
            widget="MultiFileChooser",
            gooey_options={
                        'full_width': True, 
            }    
        )
    groupViewer_2D.add_argument(
            "--DARK",
            metavar="Dark file",
            help="Select the dark file associated with the images to be converted",
            widget='FileChooser',
    )

def viewer_2D(args):
    IMAGES, DARK = args.IMAGES, args.DARK
    if DARK:
        im_dark = fabio.open(DARK)
    
    print(stylize(f">> Converting {len(IMAGES)} 2D images to .tiff", attr("bold")))

    for image in IMAGES:
        try:
            print(f'Processing: {image}')
            data = fabio.open(image)
            im = np.array(data.data, dtype=np.uint8)
            if DARK:
                dk = np.array(im_dark.data, dtype=np.uint8)
                img = im - dk
            else:
                img = im
            plt.imshow(img, cmap="gray", vmin=0, vmax=255)
            plt.axis('off')
            image_name = os.path.splitext(image)[0] + '.tiff'
            plt.savefig(image_name)
            print(stylize(f'Image saved:  {image_name}',  fg(
                    "green")))

        except:
            print(stylize(f'>> Problem after image : {img}', fg(
                    "red") + attr("bold")))