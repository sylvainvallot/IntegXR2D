# IntegXR2D

## Description
IntegXR2D is a Python-based software package for full and partial integration of multiple 2D diffractograms with simplified numbering for Rietveld refinement with [FullProf](https://www.ill.eu/sites/fullprof/index.html).

Features currently available: 
    
- Total integration of multiple 2D diffractograms.
- Partial integration around the 0° and 90° axes.
- Buffer file creation for WinPLOTR with :
    - All selected diffractograms.
    - A defined number of diffractograms over the range of selected files.
- Invert diffractogram numbering (e.g. for use in cyclic for cyclic refinement of a core-to-surface profile).
- Conversion of multiple 2D images to TIFF.

## Installation

Follow these steps to set up the project on your local machine.

### Prerequisites

- [Anaconda](https://www.anaconda.com/distribution) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed on your system.

### Clone the Repository

```bash
git clone https://github.com/username/project.git
cd project
```

### Create the Conda Environment

```bash
conda env create -f environment.yml -n integxr2d
```

### Activate the Conda Environment

```bash
conda activate integxr2d
```

## Usage
```bash
python integxr2d.py
```
A graphical interface then opens, displaying the various actions in the sidebar.

## Contributing

If you'd like to contribute, please fork the repository and make changes as you'd like. Pull requests are welcome.