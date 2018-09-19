#!/usr/bin/env python
__author__ = 'HsiehM'
__EXEC__ = __file__

# Import modules here
import os, sys
import traceback as tb
import matplotlib.pyplot as plt
import numpy as np
    
def create_collage(dcms, outname, mammogram = False, dpi=100):       
    num_col = np.ceil(len(dcms)/2.).astype(np.int)
    f, axes = plt.subplots(2, num_col, figsize = (num_col*5,10))
    
    for i, dcm in enumerate(dcms):
        _, tail = os.path.split(dcm)
        try:
            axes[i%2][i/2].tick_params(axis='both', which='both', bottom='off', top='off',
                                       labelbottom='off', right='off', left='off', labelleft='off')
            axes[i%2][i/2].set_title(tail, fontsize = 20)
            if mammogram:
                plot_mammogram(dcm, axes[i%2][i/2])
            else:
                plot_dicom(dcm, axes[i%2][i/2])
        except:
            tb.print_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            pass
        #f.suptitle('%s %s' % (m.dicom.AccessionNumber, m.IntentType[0]), fontsize = 32, y=0.97)

    f.savefig(outname, dpi=dpi, bbox_inches='tight')
    plt.close(f)

    return 0

def plot_dicom(dcm, ax = None):
    import dicom
    
    if ax is None:
        f, ax = plt.subplots(1,1)
        
    image = dicom.read_file(dcm).pixel_array
    ax.imshow(image, cmap='gray')
    ax.set_xlim((0, image.shape[1]))
    ax.set_ylim((image.shape[0], 0))
    
    return ax
    
def plot_mammogram(dcm, ax = None):
    import libra
    from skimage.transform import resize
    from skimage.measure import find_contours

    if ax is None:
        f, ax = plt.subplots(1,1)

    m = libra.io.read_image(dcm)
    m_out = libra.preprocessing.standardize_intensity(libra.preprocessing.standardize_orientation(m))
    image = resize(m_out.image, np.array(m_out.image.shape)/4, preserve_range=True)
    ax.imshow(image, cmap='gray') # , vmin = low_window, vmax = high_window)
        
    mask, breast = libra.segmentation.segment_breast(image, pecseg=m_out.IsMLO)
    contour = find_contours(mask, 0.8) 
    for j in xrange(len(contour)):
        ax.plot(contour[j][:,1], contour[j][:,0], 'r', linewidth = 2)
    
    ax.set_xlim((0, image.shape[1]))
    ax.set_ylim((image.shape[0], 0))
    
    return ax
    
def convert_dicom_to_figure(dcm, outname, mammogram = False, dpi=100):
    _, tail = os.path.split(dcm)
    
    if mammogram:
        ax = plot_mammogram(dcm)
    else:
        ax = plot_dicom(dcm)
    
    ax.tick_params(axis='both', which='both', bottom='off', top='off',
                   labelbottom='off', right='off', left='off', labelleft='off')
    ax.set_title(tail, fontsize = 20)
        
    plt.savefig(outname, dpi=dpi, bbox_inches='tight')
    plt.close('all')



def create_parser():
    import argparse
    ''' Create an argparse.ArgumentParser object

        :returns: An argparse.ArgumentParser parser.
    '''
    parser = argparse.ArgumentParser(prog = __EXEC__,
                                     description = 'EDIT DESCRIPTION HERE')
    # Required
    parser.add_argument('-i', '--input',
                        dest = 'inputfile',
                        action = 'store',
                        type = str,
                        nargs='+',
                        help = 'Input DICOM')
    parser.add_argument('-d', '--dir',
                        dest = 'inputdir',
                        action = 'store',
                        type = str,
                        help = 'Input directory of DICOM')   
    parser.add_argument('-o', '--outputdir',
                        dest = 'odir',
                        default = None,
                        action = 'store',
                        type = str,
                        help = 'Output')
    parser.add_argument('-f', '--format',
                        dest = 'format',
                        default = 'png',
                        choices = ['png', 'jpg', 'tif', 'svg', 'eps', 'pdf'],
                        action = 'store',
                        type = str,
                        help = 'Output format')
    parser.add_argument('-c', '--collage',
                        dest = 'collage',
                        default = False,
                        action = 'store_true',
                        help = 'Create collage for multiple images.')
    parser.add_argument('-m', '--mammogram',
                        dest = 'mammo',
                        default = False,
                        action = 'store_true',
                        help = 'Indicate the image is a mammogram. Pectoral segmentation will be applied.')
    parser.add_argument('--dpi',
                        dest = 'dpi',
                        default = 100,
                        action = 'store',
                        type = int,
                        help = 'Resolution for the output figure. Default: 100.')
    return parser
    
    
def main(argv = None):
    if argv is None:
        argv = sys.argv[1:]
    # parse input from command line
    parser = create_parser()
    args = parser.parse_args(argv)
    
    import socket, time

    exe_folder = os.getcwd()
    exe_time = time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime())
    host = socket.gethostname()
    print "Command", __EXEC__
    print "Arguments", args
    print "Executing on", host
    print "Executing at", exe_time
    print "Executing in", exe_folder

    # Start of the program
    from glob import glob
    
    dcms = []
    if isinstance(args.inputdir, str) and os.path.isdir(args.inputdir):
        dcms = glob(os.path.join(args.inputdir, '*'))
    if isinstance(args.inputfile, str):
        dcms = dcms.append(args.inputfile)
    elif isinstance(args.inputfile, list):
        dcms = dcms + args.inputfile
    
    num_img = len(dcms)
    if num_img < 1:
        print 'No images to plot'
        return 1

    head, _ = os.path.split(dcms[0])
    if args.odir is None:
        odir = head
    else:
        odir = args.odir
    
    if args.collage:
        _, tail = os.path.split(head)
        outname = os.path.join(odir, '%s_collage.%s' % (tail, args.format))
        print "Creating collage for %d images in %s" % (num_img, head)
        status = create_collage(dcms, outname, mammogram = args.mammo, dpi=args.dpi)
    else:
        for i, dcm in enumerate(dcms):
            _, tail = os.path.split(dcm)
            outname = os.path.join(odir, "%s.%s" % (tail, args.format))
            print "%d/%d: %s -> %s\n" % (i+1, num_img, dcm, outname)
            try:
                convert_dicom_to_figure(dcm, outname, mammogram = args.mammo, dpi=args.dpi)
            except:
                tb.print_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                pass

    return 0

if __name__ == '__main__':
    sys.exit(main())

