#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : VALLOT Sylvain
# Created Date: 2021
# =============================================================================

# Import for the UI
import os
import sys
from gooey import Gooey, GooeyParser

# Softwares modules
from  src.buffer_creator import ui_buffer_creator, buffer_creator
from  src.integration import ui_integration, integrateXRD
from  src.reverse_fp import ui_reverse_fp, reverse_fp
from  src.viewer_2D import ui_viewer_2D, viewer_2D

__author__ = 'VALLOT Sylvain'
__version__ = '1.0.0'
__description__ = 'Partial and total integration of 2D diffractograms and tools'


@Gooey(
    #dump_build_config=True,
    language='english',
    default_size=(800, 550),
    program_name="IntegXR2D",
    menu=[
        {
            'name': 'Menu', 
            'items': [
                {
                    'type': 'MessageDialog',
                    'menuTitle': 'Generate a .poni file',
                    'caption': 'Generate a .poni file',
                    'message': 'To generate a .poni file, use pyFAI. Installation instructions are available on the internet.\nIn a command prompt:\npyFAI-calib -e <Beam Energy> -p <Nb lateral pixel Detector> -c <Calibrant type> -d <Dark Calibrant File> <Calibrant 2D Diffractogram>'
                },
                {
                    'type': 'Link',
                    'menuTitle': 'Visual Studio Code extension for .pcr file',
                    'url': 'https://marketplace.visualstudio.com/items?itemName=sylvainvallot.fullprof-vscode'               
                },
                {
                    'type': 'AboutDialog',
                    'menuTitle': 'About',
                    'name': "IntegXR2D",
                    'description': __description__,
                    'version': __version__,
                    'copyright': '2021',
                    'developer': f'{__author__} - GitHub : @sylvainvallot',
                }
            ]
        },
    ],
    image_dir="src/images",
    show_restart_button=False,
    richtext_controls=True,
    navigation='SIDEBAR',
)

def parse_args():
    desc = 'Partial and total integration of 2D diffractograms'
    
    parser = GooeyParser(description=desc)

    action = parser.add_subparsers(help='action', dest='action')

    # UI import for each action
    ui_integration(action)
    ui_reverse_fp(action)
    ui_buffer_creator(action)
    ui_viewer_2D(action)

    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()

    def switch(action, args):
        if action == 'integration':
            integrateXRD(args)
        elif action == 'create_buffer':
            buffer_creator(args)
        elif action == 'reverse_fp':
            reverse_fp(args)
        elif action == 'viewer_2D':
            viewer_2D(args)

    switch(args.action, args)