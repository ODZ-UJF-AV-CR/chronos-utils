#!/usr/bin/python

# standard python imports
import sys
import struct
import os
import time
import array
import getopt
import platform
import errno
import numpy
import numpy as np
from PIL import Image
#from tqdm import tqdm
import pandas as pd
import datetime


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime

## Read the frame data out and convert it to 16-bpp
def readFrame(file, width, length, bpp):
    try:
        if (bpp == 12):
#             ## Read and convert to 16-bpp.
#             frame = [None] * (width*length)
#             for off in range(0, len(frame), 2):
#                 pix = bytearray(file.read(3))
#                 a = int((pix[0] << 4) + ((pix[1] & 0xf0) << 8))
#                 b = int((pix[2] << 8) + ((pix[1] & 0x0f) << 4))
#                 frame[off + 0] = a
#                 frame[off + 1] = b

            frame = [None] * (width*length)
            off = 0
            #for off in range(0, len(frame), 2):
            while off < len(frame):
                #print(off, len(frame))
                #if off > len(frame):
                #    print("end of loop")
                #    return frame
                pix = bytearray(file.read(3))
                #print(pix)
                #a = int((pix[0] << 4) + ((pix[1] & 0xf0) << 8))
                #b = int((pix[2] << 8) + ((pix[1] & 0x0f) << 4))
                frame[off + 0] = int((pix[0] << 4) + ((pix[1] & 0xf0) << 8))
                frame[off + 1] = int((pix[2] << 8) + ((pix[1] & 0x0f) << 4))
                #print(off)
                off += 2
            
            #print("Return")
            return frame
                
            
    
    except:
        return None

def convertVideo(inputFilename, outputFilename, width, length, colour, bpp):
    #dngTemplate = DNG()
    print("Output file", outputFilename)

    creationTime = creation_date(inputFilename)
    creationTimeString = time.strftime("%x %X", time.localtime(creationTime))
                
    dl = []

    # set up the image binary data
    rawFile = open(inputFilename, "rb")
    rawFrame = readFrame(rawFile, width, length, bpp)
    #dngTemplate.ImageDataStrips.append(rawFrame)

    
    frameNum = 0
    while(rawFrame):
        Frame = np.reshape(np.array(rawFrame, 'uint16'), (width,length))
        #print(frameNum, Frame.sum())

        #pillow_image = Image.fromarray(Frame, mode = "I;16")
        #file = outputFilenameFormat.format(frameNum)
        #pillow_image.save(file)
        
        print(".", end = '', flush=1)
        dl.append([Frame.sum(), 0, 0])
        
        if frameNum % 20 == 0:
            pdf = pd.DataFrame(dl, columns=['AllSum', 'MaskSum', 'Median'])
            pdf.index.name = "FrameNum"
            print(frameNum, end = '', flush=1)
            #print(" ")
            #print(pdf)
            pdf.to_csv(outputFilename)
        
        # go onto next frame
        rawFrame = readFrame(rawFile, width, length, bpp)
        frameNum += 1
        
        #if frameNum > 10:
        #    break
    
    pdf = pd.DataFrame(dl, columns=['AllSum', 'MaskSum', 'Median'])
    pdf.index.name = "FrameNum"
    print(" ")
    print(pdf)
    pdf.to_csv(outputFilename)



#=========================================================================================================
helptext = '''pyraw2dng.py - Command line converter from Chronos1.4 raw format to DNG image sequence
Version 0.1
Copyright 2018 Kron Technologies Inc.

pyraw2dng.py <options> <inputFilename> [<OutputFilenameFormat>]

Options:
 --help      Display this help message
 -M/--mono   Raw data is mono
 -C/--color  Raw data is colour
 -p/--packed Raw 12-bit packed data (default: 16-bit)
 --legacy    Legacy 12-bit packed data (v0.3.0 and earlier)
 -w/--width  Frame width
 -l/--length Frame length
 -h/--height Frame length (please use only one)
   
Output filename format must include '{:06d}' which will be replaced by the image sequence number.

Examples:
  pyraw2dng.py -M -w 1280 -l 1024 test.raw
  pyraw2dng.py -w 336 -l 96 test.raw test_output/test_{:06d}.DNG
'''


def main():
    width = None
    length = None
    colour = True
    inputFilename = None
    outputFilenameFormat = None
    bpp = 16
    
    try:
        options, args = getopt.getopt(sys.argv[1:], 'CMpw:l:h:',
            ['help', 'color', 'packed', 'mono', 'width', 'length', 'height', 'oldpack'])
    except getopt.error:
        print('Error: You tried to use an unknown option.\n\n')
        print(helptext)
        sys.exit(0)
        
    if len(sys.argv[1:]) == 0:
        print(helptext)
        sys.exit(0)
    
    for o, a in options:
        if o in ('--help'):
            print(helptext)
            sys.exit(0)

        elif o in ('-C', '--color'):
            colour = True

        elif o in ('-M', '--mono'):
            colour = False
        
        elif o in ('-p', '--packed'):
            bpp = 12
        
        elif o in ('--oldpack'):
            bpp = -12
        
        elif o in ('-l', '-h', '--length', '--height'):
            length = int(a)

        elif o in ('-w', '--width'):
            width = int(a)

    if len(args) < 1:
        print(helptext)
        sys.exit(0)

    elif len(args) == 1:
        inputFilename = args[0]
        dirname = os.path.splitext(inputFilename)[0]
        basename = os.path.basename(inputFilename)
        print(inputFilename)
        print(basename)
        print(dirname)
        outputFilenameFormat = dirname + '/' + basename + '_{:06d}.'
    else:
        inputFilename = args[0]
        outputFilenameFormat = args[1]

    outputFilename = inputFilename[:-4]+'.csv'
    start = datetime.datetime.now()
    convertVideo(inputFilename, outputFilename, width, length, colour, bpp)
    print("Duration of the script run", datetime.datetime.now()-start)

if __name__ == "__main__":
    main()

        
        
