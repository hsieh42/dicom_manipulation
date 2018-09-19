#!/usr/bin/env python
__author__ = 'HsiehM'
__EXEC__ = 'sortdicom.py'

import sys
import os
import shutil
import warnings as w
import dicom
from glob import glob
from collections import Counter
    
def get_laterality( ds ):
    if "ImageLaterality" in ds:
        return ds.ImageLaterality
    elif "FrameLaterality" in ds:
        return ds.FrameLaterality
    elif "Laterality" in ds:
        return ds.Laterality
    else:
        w.warn('Cannot determine laterality.', RuntimeWarning)
        return None

def get_view( ds ):
    if "ViewPosition" in ds:
        return ds.ViewPosition
    elif "ViewCodeseq_to_joinuence" in ds and "CodeMeaning" in ds.ViewCodeseq_to_joinuence[0]:
        return ds.ViewCodeseq_to_joinuence[0].CodeMeaning
    else:
        w.warn('Cannot determine view.', RuntimeWarning)
        return None
        
def get_type( ds ):
    if "PresentationIntentType" in ds:
        return ds.PresentationIntentType.replace(' ', '-')
    else:
        w.warn('Cannot determine presentation intent type.', RuntimeWarning)
        return None
        
def get_date( ds ):
    ''' Return an subject imaging date from the dicom header in an input meta file.
        Search order: AcquisitionDate [0x0008, 0x0022], StudyDate [0x0008, 0x0020].

        :param ds: dicom header information.
        :type ds: dicom.dataset.FileDataset or OrderedDict
        :returns:  a date in string.
    '''    
    if 'AcquisitionDate' in ds:
        dataset_date = ds.AcquisitionDate
    elif 'StudyDate' in ds:
        dataset_date = ds.StudyDate
    else:
        w.warn('Cannot find ID from all two possible fields: AcquisitionDate, and StudyDate.', RuntimeWarning)
        dataset_date = None
    
    return dataset_date

def get_sequence_info( ds ):
    ''' Return a sequnce information in CBICA convention from the dicom header in
        an input meta file.

        :param ds: dicom header information.
        :type ds: dicom.dataset.FileDataset or OrderedDict
        :returns:  A CBICA sequence information (<SeriesDescription>-<SeriesNumber>) in string.
    '''   
    sequence_info = None
    if 'SeriesDescription' in ds:
        sequence_info = ds.SeriesDescription
    elif 'ProtocolName' in ds:
        sequence_info = ds.ProtocolName
    else:
        w.warn('Cannot find fields containing sequence in the meta information. Both SeriesDescription and ProtocolName are missing.', RuntimeWarning)
        sequence_info = None

    if 'SeriesNumber' in ds:
        sequence_number = ds.SeriesNumber
    else:
        w.warn('Cannot find fields containing SeriesNumber in the meta information.', RuntimeWarning)
        sequence_number = None
        
    if sequence_info is None and sequence_number is None:
        return None
    elif sequence_info is None:
        return str(sequence_number)
    elif sequence_number is None:
        sequence_info = sequence_info.replace(' ', '_').replace('/','_').replace('(','').replace(')','').replace('*', '').replace('&', '').replace('$', '').replace(':', '.')
        return sequence_info
    else:
        sequence_info = sequence_info.replace(' ', '_').replace('/','_').replace('(','').replace(')','').replace('*', '').replace('&', '').replace('$', '').replace(':', '.')
        return sequence_info + '-' + str(sequence_number)
            
def get_modality(ds):
    if "Modality" in ds:
        return ds.Modality
    else:
        w.warn('Cannot determine modality.', RuntimeWarning)
        return None
        
def get_instance_number(ds):
    if 'InstanceNumber' in ds:
        return ds.InstanceNumber.original_string
    else:            
        w.warn('Cannot determine instance number.', RuntimeWarning)
        return None     
        
# TODO 20180517: to get acq date time in int so that we can sort the dicom list by time.
def get_acquisition_date_time(ds):
    pass
    
''' 
temp solution to sort the dicom list by last string of digit which has the same order as acq time.
DPm.1.2.840.113681.2863050707.1374648629.264.7180 predates DPm.1.2.840.113681.2863050707.1374648629.264.7197.
'''
def sort_func(s):
    return int(s.split('.')[-1])
    
    
def sortdicom( idir, odir = None, mode='test',
               identifier = None, id_tag = None, use_date = False,
               use_modality = False, use_laterality = False,
               use_view = False, use_series = True, use_type = False):
    print "Input directory is " + idir    
    if odir:
        print "Output directory is " + odir
#    print 'Use date?' + str(use_date)
#    print 'Use modality?' + str(use_modality)
    
    delimiter = '_'
    names = []
    
    files = glob(os.path.join(idir, "*"))
    #files = sorted(glob(os.path.join(idir, "*")), key = sort_func)
    #files = sorted(glob(os.path.join(idir, "*")), key = os.path.getmtime) # this would sort the files by their modified time.
    print str(len(files)) + " files found for sorting"
    # idir contains dicoms to be sorted
    for dcm in files:
        index = 1
        laterality = None
        view = None
        date = None
        modality = None
        series = None
        ID = None
        instance_number = None
        presentation_type = None
        
        # read dcm
        try:
            ds = dicom.read_file(dcm, stop_before_pixels = True)
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            names.append('')
            continue
            
        if use_laterality:
            laterality = get_laterality(ds)
        if use_view:
            view = get_view(ds)
        if use_date:
            date = get_date(ds)
        if use_modality:
            modality = get_modality(ds)
        if use_series:
            series = get_sequence_info(ds)
            instance_number = get_instance_number(ds)
        if use_type:
            presentation_type = get_type(ds)
            
        if identifier:
            ID = identifier
        elif id_tag:
            if id_tag in ds:
                ID = ds.data_element(id_tag).value
        elif "AccessionNumber" in ds:
            ID = ds.AccessionNumber
        else:
            # take the dir name as ID
            ID = idir.strip(os.sep).split(os.sep)[-1]  
        

        seq_to_join = [ID, modality, presentation_type, series, laterality, view, date]            
        # Remove the None in seq_to_join
        for i in xrange(len(seq_to_join)):
            try:
                seq_to_join.remove(None)
            except ValueError as e:
                break

        if instance_number is not None:
            index2 = instance_number
        else:
            index2 = str(index)
        new_name = delimiter.join(seq_to_join + [index2])

        if series is not None:
            new_name = os.path.join(series, new_name)
        
        while (new_name in names):
            index += 1
            new_name = delimiter.join(seq_to_join + [str(index)])
            
        names.append(new_name)
        
    ''' copy/move/create symbolic the files to odir
        'test' to be default
        'symbolic', 'move' and 'copy' to be other options '''
        
    # also check if the system allows symlinks.
    if sys.platform == 'win32' and mode == 'symbolic':
        print 'Symbolic links are not allowed on windows system. Use copy mode instead'
        mode = 'copy'        
    if mode != 'test' and not os.path.exists(odir):
        print 'Creating output dir'
        os.makedirs(odir)
    
    for i, basename in enumerate(names):
        print os.path.basename(files[i]) + ' -> ' + basename + '.dcm'
        if basename is '':
            continue
        if mode != 'test':
            if use_series:
                subodir, tail = os.path.split(os.path.join(odir, basename))
                outpath = os.path.join(odir, basename + '.dcm')
                if not os.path.exists(subodir):
                    os.makedirs(subodir)
            else:
                outpath = os.path.join(odir, basename + '.dcm')
            
        if mode == 'move':
            shutil.move(files[i], outpath)
        elif mode == 'symbolic':
            if os.path.islink(outpath):
                os.unlink(outpath)
            os.symlink(files[i], outpath)
        elif mode == 'copy':
            shutil.copyfile(files[i], outpath)
        
def main(argv = None):
    ''' parse a given directory and see if it contains 
        dicoms or subdirectories. If dicoms, call sortdicoms
        once, if subdirectories, execute sortdicom for all.'''
    
    if argv is None:
        argv = sys.argv[1:]
    # parse input from command line
    args = create_parser().parse_args(argv)
    
    import socket, time

    exe_folder = os.getcwd()
    exe_time = time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime())
    host = socket.gethostname()
    print "Command", __EXEC__
    print "Arguments", args
    print "Executing on", host
    print "Executing at", exe_time
    print "Executing in", exe_folder
    
    #print args
    if not os.path.isdir(args.idir):
        raise RuntimeError(args.idir + ' is not a valid directory.')
        
    for dirpath, dirnames, filenames in os.walk(args.idir):
        if dirnames == []:
            root, subdirname = os.path.split(dirpath)
            ##TMP#subodir = os.path.join(args.odir,subdirname)
            
            sortdicom( dirpath, odir = args.odir, mode = args.mode, 
                       identifier = args.subj, id_tag = args.tag_subj,
                       use_date = args.suffix_date,
                       use_modality = args.suffix_modality,
                       use_series = args.suffix_series,
                       use_laterality = args.suffix_laterality,
                       use_view = args.suffix_view,
                       use_type = args.suffix_type)
            print
            print
            
def create_parser():
    import argparse
    ''' Create an argparse.ArgumentParser object 
    
        :returns: An argparse.ArgumentParser parser.
    '''
    parser = argparse.ArgumentParser(prog = __EXEC__,
                                     description = 'Sort dicom images by laterality, view position and other identifiers. This program is designed for breast mammograms. CBIG output convention (Default): ID_LATERALITY_VIEW_#.dcm. MSKCC output convention: ID_LATERALITY_MODALITY_VIEW_DATE_#.dcm.')
    # Required
    parser.add_argument('-i', '--inputdir',
                        required = True,
                        dest = 'idir',
                        action = 'store',
                        type = str,
                        help = 'Input directory.')                          

    ## optional
    parser.add_argument('-o', '--outputdir',
                        dest = 'odir',
                        action = 'store',
                        default = None,
                        type = str,
                        help = 'Output directory. Subdirectory, if any found in input directory, will be created under output directory.')      
    parser.add_argument('-m', '--mode',
                        dest = 'mode',
                        action = 'store',
                        default = 'test',
                        choices = ['test', 'symbolic', 'move', 'copy'],
                        type = str,
                        help = 'There are four ways to create sorted filenames: test (default): dry-run on the data and display the result on standard output; symbolic: create soft/symbolic links at output_dir. (overwrite existing links); copy: create a new copy of files in output_dir; move: rename the original dicoms and move to output_dir. Creating symbolic link is highly recommended to reduce filesystem IO during runtime and also to preserve the linkage between unsorted files to sorted files.')                      
    parser.add_argument('-s', '--subject_id',
                        dest = 'subj',
                        action = 'store',
                        default = None,
                        type = str,
                        help = 'Force to use provided identifier. Default: use AccessionID in the dicom header.')
    parser.add_argument('--subject_id_tag',
                        dest = 'tag_subj',
                        action = 'store',
                        default = None,
                        type = str,
                        help = 'Force to use the provided dicom tag for subject ID. Default is AccessionID. Options are (not limited to) PatientID, StudyID, PatientName. If subject_id is not provided, accession ID is not available, subject_id_tag provided from input is not available, the program would use the data directory name.')
    parser.add_argument('--series',
                        dest = 'suffix_series',
                        action = 'store_true',
                        default = False,
                        help = 'A flag to add series description in the output suffix. If True, subdirectories for each series will be created. Default: off.')
    parser.add_argument('--modality',
                        dest = 'suffix_modality',
                        action = 'store_true',
                        default = False,
                        help = 'A flag to add modality in the output suffix. Default: off.')
    parser.add_argument('--type',
                        dest = 'suffix_type',
                        action = 'store_true',
                        default = False,
                        help = 'A flag to add presentation intent type in the output suffix. Default: off.')
    parser.add_argument('--date',
                        dest = 'suffix_date',
                        action = 'store_true',
                        default = False,
                        help = 'A flag to add acquisition date in the output suffix. Default: off.')
    parser.add_argument('--laterality',
                        dest = 'suffix_laterality',
                        action = 'store_true',
                        default = False,
                        help = 'A flag to add image laterality in the output suffix. Default: off.')  
    parser.add_argument('--view',
                        dest = 'suffix_view',
                        action = 'store_true',
                        default = False,
                        help = 'A flag to add view position in the output suffix. Default: off.')
    return parser


if __name__ == '__main__': 
    import sys
    sys.exit(main())
    
