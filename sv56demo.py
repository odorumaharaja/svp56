#!/usr/bin/env python
# -*- coding: utf-8 -*-

#/*                                                              v3.5 02.Feb.10
#  ============================================================================
#
#  SV56DEMO.C
#  ~~~~~~~~~~
#
#  Description:
#  ~~~~~~~~~~~~
#
#  Example program that calculates the factor for equalizing, and
#  equalizes, a file's active speech level "NdB" dBs below a 0 dB
#  reference. Here, the default reference is 0 dB below system overload.
#  This program, as an option, may normalize the output file using the 
#  measure RMS (long term) level, instead of the active speech level.
#
#  The calculation of speech file's active power uses the algorithm
#  in ITU-T Recommendation P.56, and as a by-product of
#  this mudule, also  calculates the activity [%], RMS power,
#  positive and negative peaks for the file, and peak factors.
#
#  In general, input and output files are in integer represent-
#  ation, 16-bit words, 2's complement. In UGST convention, this
#  data must be left-adjusted, RATHER than right-adjusted. Since
#  the speech voltmeter uses `float' input data, it is necessary to
#  convert from short (in the mentioned format) to float; this is
#  carried out by the function `sh2fl()'. This function has the
#  option of `normalize' the input data to the range -1..+1, what
#  is done. After the equalization factor is found, the function
#  `scale()' is called to carry out the equalization using single
#  (rather than double) float precision. After equalized, data need
#  to be converted back to integer (short, right-justified). This
#  is done by function `fl2sh()', using: truncation, no
#  zero-padding of the least significant bits, left-justification
#  of data, hard-clipping of data outside the range -32768..+32767.
#  After that, data is saved to file.
#
#  The default values for the AD,DA systems resolution is 16
#  bits, for the sampling rate is 16000 Hz. To change this
#  on-line, just specify the parameters 6 and/or 7 conveniently
#  in the command line. For example, 14 bits and 8000 Hz:
#  $ sv56demo filein fileout 256 1 100 -15 8000 14 
#
#  Usage:
#  ~~~~~~
#  $ sv56demo [-options] FileIn FileOut 
#             [BlockSize [1stBlock [NoOfBlocks [DesiredLevel
#             [SampleRate [Resolution] ] ] ] ] ]
#  where:
#  FileIn           is the input file to be analysed and equalized;
#  FileOut          is the output equalized file
#  BlockSize        is the block size in number of samples;
#  1stBlock         the first block to be analysed/equalized
#  NoOfBlocks       number of blocks to be analysed/equalized
#  DesiredLevel     level desired to the output file, in dBov or dBm0
#  SampleRate       sampling rate used for acquiring/generating the
#                   file, in Hertz; default is 16000 Hz; THIS PARAMETER
#                   IS OPTIONAL!
#  Resolution       the digital system resolution (AD,DA systems), in
#                   number of bits; default to 16 bits; THIS PARAMETER
#                   IS OPTIONAL, but to specify it you need to specify
#                   the former one!
#  Options:
#  ~~~~~~~~
#  -bits n ........ change the default word length to n bits; equivalent
#                   to parameter Resolution above [default: 16 bits]
#  -lev ndB ....... equivalent to specifying DesiredLevel above, just that
#                   here do not need to specify the former 3 parameters.
#  -log file ...... print the statistics log into file rather than stdout
#  -q ............. quit operation - does not print the progress flag. 
#                   Saves time and avoids trash in batch processings.
#  -qq ............ print short statistics summary; no progress flag.
#  -rms ........... normalizes the output file using the RMS long-term level, 
#                   instead of the active speech level.
#  -sf f .......... set sampling frequency to `f' Hz; equivalent to parameter 
#                   SampleRate above.
#  -blk len  ...... is the block size in number of samples;
#                   this parameter is optional, and the default is block size
#	           of 256 samples; equivalent to parameter N above
#  -start sb ...... define `sb' as the first block to be measured; equivalent 
#                   to parameter N1 above [default: first block of the file] 
#  -end eb ........ define `eb' as the last block to be measured
#  -n nb .......... define `nb' as the number of blocks to be measured; 
#                   equivalent to parameter N2 above [default: whole file]
#
#  Modules used:
#  ~~~~~~~~~~~~~
#  > sv-P56.c: contains the functions related to active speech
#              level measurement according to P.56,
#              init_speech_voltmeter(), speech_voltmeter() and 
#              bin_interp(). Their prototypesare in `sv-p56.h'.
#  > ugst-utl.c: utility functions; here are used the gain/loss
#              (scaling) algorithm of scale() and the data type
#              conversion functions sh2fl() and fl2sh(). Prototypes 
#              are in `ugst-utl.h'.
#
#  Exit values:
#  ~~~~~~~~~~~~
#  0      success (all but VMS);
#  1      success (only in VMS);
#  2      error opening input file;
#  3      error creating output file;
#  4      error moving pointer to desired start of conversion;
#  5      error reading input file;
#  6      error writing to file;
#
#  Compilation:
#  ~~~~~~~~~~~~
#  VaxC:   cc sv56demo.c 
#          link sv56demo
#  TurboC: tcc sv56demo.c
#  Sun-OS: cc -o sv56demo sv56demo.c -lm 
#
#  Author: 
#  ~~~~~~~ 
#  Simao Ferraz de Campos Neto
#  DDS/Pr11                      Tel: +55-192-39-1396                
#  CPqD/Telebras                 Fax: +55-192-53-4754                
#  13085-061 Campinas SP Brazil  E-mail: <tdsimao@venus.cpqd.ansp.br>
#
#  Log of changes:
#  ~~~~~~~~~~~~~~~
#  09.Mar.90     0.0        Release of first version of a C speech
#                           voltmeter.
#  08.Oct.91     1.0        Release of demo program for the speech
#                           voltmeter module.
#  19.Feb.92     2.0        Call to module using state variable instead of
#                           individual variables. Compilation option 
#                           between dB(overload) and dBm0.
#  18.May.92     2.1        Removed references to dBm0; input data
#                           is converted to the normalized range; 
#                           speech voltmeter needs input data in
#                           normalized range. <tdsimao@cpqd.ansp.br>
#  10.Dec.94     3.0        Included additional input interface. NdB promoted
#                           from long to double. <simao@ctd.comsat.com>
#  21.Aug.95     3.1        Included additional option to normalize output
#                           file using RMS long-term level instead of active 
#                           level, and options for block size, first block, 
#                           last block, number of blocks. <simao@ctd.comsat.com>
#  29.May.97     3.2        moved summary statistics code to a function, and
#                           created a short summary function as well. Added
#                           command-line option to print short summary
#                           (-qq). Add -log option so save statistical
#                           summaries into a file <simao>
#  06.Apr.98     3.3        solved small bug that occurred when the file 
#                           size was not a multiple of the frame
#                           size. The program was truncating the output
#                           file size to a multiple of the current
#                           block size. The fix was to introduce a
#                           ceil() in the calculation of N2 when N2==0
#                           <simao>
#  08.Jul.99     3.4        fixed a bug in fwrite() call in main(); was 
#                           saving N samples, rather than "l". This was
#                           causing more samples to be written to the
#                           end of the file when the file size was not
#                           a multiple of the block size <simao>.
#  02.Feb.10     3.5        Modified maximum string length to avoid
#                           buffer overruns (y.hiwasaki)
#
#  ============================================================================
#*/

import os
import math
import argparse
from ctypes import sizeof, c_short

import numpy as np

from svp56 import SVP56_state, bin_interp, init_speech_voltmeter, speech_voltmeter

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='sv56demo', add_help=True)
    parser.add_argument('FileIn', help='the input file to be analysed and equalized')
    parser.add_argument('FileOut', help='the output equalized file')
    
    args = parser.parse_args()

    # Parameters for operation 
    N=256
    N1=0
    N2=0
    NdB=-26 # dBov

    #  Intermediate storage variables for speech voltmeter
    state = SVP56_state()

    # Other variables
    quiet=0
    use_active_level = 1
    long_summary = 1
    NrSat = 0
    start_byte = 0
    bitno = 16
    sf = 16000
    factor = 0.0
    ActiveLeveldB = None
    DesiredSpeechLeveldB = None

    # ......... SOME INITIALIZATIONS .........
    start_byte = N1
    start_byte *= N * sizeof(c_short)

    # Check if is to process the whole file
    if N2 == 0:
        st = os.stat(args.FileIn)
        N2 = math.ceil((st.st_size - start_byte) / (N * sizeof(c_short)))
    
    # Overflow (saturation) point
    Overflow = math.pow(2.0, (bitno-1))

    init_speech_voltmeter(state, sf)
    print(state)
    # Opening input file
    Fi = None
    with open(args.FileIn, 'rb') as fid:
        Fi = np.fromfile(fid, dtype=np.int16)
        Fi = Fi.astype(np.float32) / np.iinfo(np.int16).max

    index = 0
    for i in range(0, N2):
        index = i * N

        ActiveLeveldB = speech_voltmeter(Fi[index:min(index+N, len(Fi))], state)

    # ... COMPUTE EQUALIZATION FACTOR ... 
    DesiredSpeechLeveldB = float( NdB )
    if use_active_level:
        factor = math.pow(10.0, (DesiredSpeechLeveldB-ActiveLeveldB) / 20.0)
    else:
        factor = math.pow(10.0, (DesiredSpeechLeveldB-SVP56_get_rms_dB(state)) / 20.0)

    #
    # EQUALIZATION: hard clipping (with truncation)
    #

    #  Get data of interest, equalize and de-normalize
    Fo = Fi * factor
    Fo = (Fo * np.iinfo(np.int16).max).astype(np.int16)
    with open(args.FileOut, 'wb') as fid:
        Fo.tofile(fid)

