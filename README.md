# dicom_manipulation
A collection of python scripts to work with DICOM (Digital Imaging and Communications in Medicine) files.

## Intro
- `anonymization/`: Anonymize DICOM files. It strips fields that contains patient identifiable information and replaces accession ID, patient ID, study ID and dates with a reversible numerically shifted dummy values.
- `convert_dicom_to_figure.py`: Converts DICOM file(s) into a png for quick viewing.
- `read_dicom_header.py`: Read DICOM file(s) and save the DICOM fields into a csv file.
- `show_dicomdir.py`: Read a DICOMDIR file and print out patient, series and image information. This is particularly helpfule to quickly navigate through a study with just one single file.
- `sortdicom.py`: Traverse through all the DICOM files in a directory and rename the DICOM files with information within DICOM.

These codes are written as executable scripts, i.e. one can run it directly. This would be most of the use cases when working with large amount of studies and DICOM files on the cluster. Some functions inside each script can come in handy when imported in a python session for use.

## Dependencies
These codes are developed and tested in python 2.7.x with numpy, pandas, matplotlib and pydicom as dependencies. The codes should generally work well with any version of numpy, pandas and matplotlib. pydicom is the only package with version dependency (<=0.9.9). The python environment on the cluster has all the dependency satisfied already so you should not worry much about it. But to run it in other environment and to fulfill the dependency, run the following with the `requirements.txt`

    $ pip install -r requirements.txt
    
## Usage
To get usage or help file for each script, please run the command with --help or -h for more detail. For example:

```bash
$ ./read_dicom_header.py -h
usage: read_dicom_header.py [-h] -o OUTPUTCSV [-i INPUTDCM [INPUTDCM ...]]
                            [-l INPUTLIST] [-d INPUTDIR]

Read all dicom field and save them in a dataframe (then CSV).

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUTCSV          Output CSV
  -i INPUTDCM [INPUTDCM ...], --input_dcm INPUTDCM [INPUTDCM ...]
                        Input a single dicom
  -l INPUTLIST, --input_list INPUTLIST
                        Input a list of dicom
  -d INPUTDIR, --input_dir INPUTDIR
                        Input a directory of dicom
```
    

