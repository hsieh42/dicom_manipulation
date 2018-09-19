# anonymization
Anonymize DICOM files. It strips fields that contains patient identifiable information and replaces accession ID, patient ID, study ID and dates with a reversible numerically shifted dummy values.

## Intro
- `remove_dicom_fields.py`: The main code to perform anonymization for DICOM files in a given directory.
- `id_linking.py`: Helper function to get the dummy ID from a real ID or vice versa.
- `dicom_anon_tags.csv`: Defines what fields to completely remove, and what to replace with dummy ID/date. **Basic Application Level Confidentiality Profile Attributes** is loosely followed. See <url>ftp://medical.nema.org/medical/dicom/2008/08_15pu.pdf</url> for more information.
- `sample_anonpattern.cfg`: A sample digit shifting (or anonymization key if you wish).

`remove_dicom_fields.py` is written as an executable script, i.e. one can run it directly. This would be most of the use cases when working with large amount of studies and DICOM files on the cluster. Some functions inside each python scripts can come in handy when imported in a python session for use.

## Dependencies
These codes are developed and tested in python 2.7.x with pandas and pydicom as dependencies. The codes should generally work well with any version of pandas. pydicom is required to be <= 0.9.9. The python environment on the cluster has all the dependency satisfied already so you should not worry much about it. But to run it in other environment and to fulfill the dependency, run the following with the `requirements.txt` provided in the repo.

    $ pip install -r requirements.txt
    

