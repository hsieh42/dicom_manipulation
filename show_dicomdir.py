#!/usr/bin/env python
"""Example file to show use of read_dicomdir()
"""
# Copyright (c) 2013 Darcy Mason
# This file is part of pydicom, relased under an MIT-style license.
#    See the file license.txt included with this distribution, also
#    available at http://pydicom.googlecode.com
#
__EXEC__ = 'show_dicomdir.py'
__DOC__ ='''Example program showing DICOMDIR contents, assuming standard
            Patient -> Study -> Series -> Images hierarchy'''
               
import sys, os
import dicom
from pprint import pprint
# dicom.debug()

def main(argv = None):
    if argv is None:
        argv = sys.argv[1:]
    # parse input from command line
    args = create_parser().parse_args(argv)
    
    if os.path.isdir(args.filepath):  # only gave directory, add standard name
        filepath = os.path.join(args.filepath, "DICOMDIR")
    dcmdir = dicom.read_dicomdir(args.filepath)
    base_dir = os.path.dirname(args.filepath)

    for patrec in dcmdir.patient_records:
        print "Patient: {0.PatientID}: {0.PatientsName}".format(patrec)
        studies = patrec.children
        for study in studies:
            print("  Study {0.StudyID}: {0.StudyDate}: "
                  "{0.StudyDescription} ({0.StudyInstanceUID})".format(study))
            all_series = study.children
            for series in all_series:
                image_count = len(series.children)
                plural = ('', 's')[image_count > 1]

                # Write basic series info and image count

                # Put N/A in if no Series Description
                if 'SeriesDescription' not in series:
                    series.SeriesDescription = "N/A"
                print(" " * 4 + "Series {0.SeriesNumber}:  {0.Modality}: {0.SeriesDescription}"
                      " ({0.SeriesInstanceUID}, {1} image{2})".format(series, image_count, plural))

                if args.verbosity>0:
                    # Open and read something from each image, for demonstration purposes
                    # For simple quick overview of DICOMDIR, leave the following out
                    print " " * 8 + "Reading images..."
                    image_records = series.children
                    image_filenames = [os.path.join(base_dir, *image_rec.ReferencedFileID)
                                       for image_rec in image_records]

                    # slice_locations = [dicom.read_file(image_filename).SliceLocation
                    #                   for image_filename in image_filenames]

                    datasets = [dicom.read_file(image_filename)
                                for image_filename in image_filenames]

                    patient_names = set(ds.PatientName for ds in datasets)
                    patient_IDs = set(ds.PatientID for ds in datasets)

                    # List the image filenames
                    print "\n" + " " * 8 + "Image filenames:"
                    print " " * 8,
                    pprint(image_filenames, indent=8)

                    # Expect all images to have same patient name, id
                    # Show the set of all names, IDs found (should each have one)
                    print(" " * 8 + "Patient Names in images..: "
                          "{0:s}".format(patient_names))
                    print(" " * 8 + "Patient IDs in images..:"
                          "{0:s}".format(patient_IDs))
                

                # print (" " * 12 + "Slice Locations from "
                #       "{0} to {1}".format(min(slice_locations), max(slice_locations)))
def create_parser():
    import argparse
    ''' Create an argparse.ArgumentParser object 
    
        :returns: An argparse.ArgumentParser parser.
    '''
    parser = argparse.ArgumentParser(prog = __EXEC__,
                                     description = __DOC__)
    # Required
    parser.add_argument('-i', '--input',
                        required = True,
                        dest = 'filepath',
                        action = 'store',
                        type = str,
                        help = 'Input DICOMDIR')                          

    ## optional
    parser.add_argument('-v', '--verbose',
                        dest = 'verbosity',
                        action = 'count',
                        help = 'Increase verbosity of the program. By calling the flag multiple time, the verbosity can be further increased.')
    
    return parser

if __name__ == "__main__":
    sys.exit(main())
    
