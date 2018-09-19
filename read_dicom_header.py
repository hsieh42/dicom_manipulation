#!/usr/bin/env python
__author__ = 'HsiehM'
__EXEC__ = 'read_dicom_header.py'

import sys, os
import time
from glob import glob
from collections import OrderedDict
import dicom 
import numpy as np
import pandas as pd

def create_parser():
    import argparse
    ''' Create an argparse.ArgumentParser object 
    
        :returns: An argparse.ArgumentParser parser.
    '''
    parser = argparse.ArgumentParser(prog = __EXEC__,
                                     description = 'Read all dicom field and save them in a dataframe (then CSV).')
    # Required
    parser.add_argument('-o',
                        required = True,
                        dest = 'outputcsv',
                        action = 'store',
                        type = str,
                        help = 'Output CSV')
    
    # Optional
    parser.add_argument('-i', '--input_dcm',
                        dest = 'inputdcm',
                        action = 'store',
                        default = None,
                        nargs = '+',
                        type = str,
                        help = 'Input a single dicom')
    parser.add_argument('-l', '--input_list',
                        dest = 'inputlist',
                        action = 'store',
                        default = None,
                        type = str,
                        help = 'Input a list of dicom')
    parser.add_argument('-d', '--input_dir',
                        dest = 'inputdir',
                        action = 'store',
                        default = None,
                        type = str,
                        help = 'Input a directory of dicom')
    return parser


def collect_dicom_header(dcm):

    d = OrderedDict()

    try:
        ds = dicom.read_file(dcm, stop_before_pixels = True)
    except dicom.errors.InvalidDicomError:
        print '%s is not a valid dicom.' % (dcm)
        return d
    except:
        print 'Unknown error occurred'
        return d
        
    for k in ds.file_meta.keys():
        if "unknown" not in ds.file_meta[k].name.lower():
            d[ds.file_meta[k].name] = ds.file_meta[k].value

    for k in ds.keys():
        if "unknown" not in ds[k].name.lower():
            d[ds[k].name] = ds[k].value
    
    return d


def main(argv = None):
    if argv is None:
        argv = sys.argv[1:]
    # parse input from command line
    args = create_parser().parse_args(argv)

    import socket

    exe_folder = os.getcwd()
    exe_time = time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime())
    host = socket.gethostname()
    print "Command", __EXEC__
    print "Arguments", args
    print "Executing on", host
    print "Executing at", exe_time
    print "Executing in", exe_folder

    print "Parsing dicom files..."
    if args.inputdcm is not None:
        dcms_all = args.inputdcm
    elif args.inputlist is not None:
        dcms_all = [line.strip('\n') for line in open(args.inputlist, 'r')]
    elif args.inputdir is not None:
        dcms_all = glob(os.path.join(args.inputdir, '*.dcm'))
    print "%d dicom found" % (len(dcms_all))
    
    print "Collecting dicom header fields..."
    start = time.time()
    out_d = map(collect_dicom_header, dcms_all)
    end = time.time()
    print "Elaspsed time: %.1f s" % (end-start)

    out_d_all = OrderedDict()
    for i, f in enumerate(dcms_all):
        out_d_all[f] = out_d[i]

    print "Writing out csv..."
    df = pd.DataFrame.from_dict(out_d_all, orient='index')
    df.index.name = 'Files'
    df.to_csv(args.outputcsv)
          
if __name__ == '__main__':
    sys.exit(main())
