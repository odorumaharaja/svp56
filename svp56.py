#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# 
#                           U    U   GGG    SSSS  TTTTT
#                           U    U  G       S       T
#                           U    U  G  GG   SSSS    T
#                           U    U  G   G       S   T
#                            UUU     GG     SSS     T
# 
#                    ========================================
#                     ITU-T - USER'S GROUP ON SOFTWARE TOOLS
#                    ========================================
# 
#        =============================================================
#        COPYRIGHT NOTE: This source code, and all of its derivations,
#        is subject to the "ITU-T General Public License". Please have
#        it  read  in    the  distribution  disk,   or  in  the  ITU-T
#        Recommendation G.191 on "SOFTWARE TOOLS FOR SPEECH AND  AUDIO 
#        CODING STANDARDS".
#        =============================================================
# 
# 
# MODULE:         SV-P56.C, FUNCTIONS RELATED TO ACTIVE LEVEL CALCULATIONS
# 
# ORIGINAL BY:    
#    Simao Ferraz de Campos Neto   CPqD/Telebras Brazil
# 
# DATE:           19/May/2005
# 
# RELEASE:        2.00
# 
# PROTOTYPES:     see sv-p56.h.
# 
# FUNCTIONS:
# 
# init_speech_voltmeter ......... initialization of the speech voltmeter state
#                                 variables in a structure of type SVP56_state.
# 
# speech_voltmeter .............. measurement of the active speech level of
#                                 data in a buffer according to P.56. Other 
# 				relevant statistics are also available.
# 
# HISTORY:
# 
#    07.Oct.91 v1.0 Release of 1st version to UGST.
#    28.Feb.92 v2.0 Correction of bug in speech_voltmeter; inclusion of test
#                   for extremes in bin_interp; use of structure to keep  
#                   state variables.   <simao@cpqd.br>
#    18.May.92 v2.1 Creation of init_speech_voltmeter and consequent changes;
#                   speech_voltmeter changed to operate with float data in the 
#                   normalized range. <simao@cpqd.br>
#    01.Sep.95 v2.2 Added very small constant to avoid problems first detected
#                   in a DEC Alpha VMS workstation with log(0) by
#                   <gerhard.schroeder@fz13.fz.dbp.de>; generalized to all
# 		  platforms <simao@ctd.comsat.com>
#    19.May.05 v2.3 Bug correction in bin_interp() routine, based on changes 
# 				  suggested by Mr Kabal. 
# 				  Upper and lower bounds are updated during the interpolation.
# 						<Cyril Guillaume & Stephane Ragot -- stephane.ragot@francetelecom.com>
# 
# =============================================================================

import math

class SVP56_state(object):

    def __init__(self):
        self.f = 0.0        # (float) sampling frequency, in Hz
        self.a = []         # (unsigned long) activity count
        self.c = []         # (double) threshold level; 15 is the no.of thres.
        self.hang = []      # (unsigned long) hangover count
        self.n = 0          # (unsigned long) number of samples read since last reset
        self.s = 0.0        # (double) sum of all samples since last reset
        self.sq = 0.0       # (double) squared sum of samples since last reset
        self.p = 0.0        # (double) intermediate quantities
        self.q = 0.0        # (double) envelope
        self.max = 0.0      # (double) max absolute value found since last reset
        self.refdB = 0.0    # (double) 0 dB reference point, in [dB]
        self.rmsdB = 0.0    # (double) rms value found since last reset
        self.maxP = 0.0     # (double) maximum positive values since last reset
        self.maxN = 0.0     # (double) maximum negative values since last reset
        self.DClevel = 0.0  # (double) average level since last reset
        self.ActivityFactor = 0.0 # (double) Activity factor since last reset
        # const values
        self.T = 0.03       # in [s]
        self.H = 0.20       # in [s]
        self.M = 15.9       # in [dB]
        self.THRES_NO = 15  # number of thresholds in the speech voltmeter
        self.MIN_LOG_OFFSET=1e-20 # Hooked to eliminate sigularity with log(0.0) (happens w/all-0 data blocks
        
    def bin_interp(self, upcount, lwcount, upcount, lwthr, Margin, tol):

        # Consistency check
        if tol < 0.:
            tol = -1.0 * tol
        
        # Check if extreme counts are not already the true active value
        interno = 1
        diff = math.abs((upcount - upthr) - Marnig)
        if diff < tol:
            return upcount
        diff = math.abs((lwcount - lwthr) - Marnig)
        if diff < tol:
            return lwcount
        
        # Initialize first middle for given (initial) bounds
        midcount = (upcount + lwcount) / 2.0
        midthr = (upthr + lwthr) / 2.0
        
        # Repeats loop until `diff' falls inside the tolerance (-tol<=diff<=tol)
        while (diff = (midcount - midthr) - Margin, math.fabs(diff)) > tol:
            
            # if tolerance is not met up to 20 iteractions, then relax the 
            # tolerance by 10
            iterno += 1
            if iterno > 20:
                tol *= 1.0
            
            if diff > tol:
                # then new bounds are ... 
                midcount = (upcount + midcount) / 2.0   # upper and middle activities
                midthr = (upthr + midthr) / 2.0	        # ... and thresholds
                lwcount = midcount
                lwthr = midthr
            elif diff < -1.0 * tol:
                # then new bounds are ... 
                midcount = (midcount + lwcount) / 2.0   # middle and lower activities
                midthr = (midthr + lwthr) / 2.0         # ... and thresholds
                upcount = midcount
                upthr = midthr
   
        # Since the tolerance has been satisfied, midcount is selected 
        # as the interpolated value with a tol [dB] tolerance. */
        return midcount
        
    def init_speech_voltmeter(self, sampl_freq):
        
        # First initializations
        self.f = sampl_freq
        I = math.floor(self.H * self.f + 0.5)
        
        # Inicialization of threshold vector
        x = 0.5
        for j in range(1, self.THRES_NO + 1):
            self.c.insert(0, x)
            x /= 2.0
            
        # Inicialization of activity and hangover count vectors
        for j in range(0, self.THRES_NO):
            self.a.append(0)
            self.hang.append(I)
            
        # Inicialization for the quantities used in the two P.56's processes
        self.s = self.sq = self.n = self.p = self.q = 0
        
        # Inicialization of other quantities referring to state variables
        self.max = 0
        self.maxP = -32768.0
        self.maxN = 32767.0
        
        # Defining the 0 dB reference level in terms of normalized values
        self.refdB = 0 # dBov
        
    def speech_voltmeter(self, buffer):
        
        # Some initializations
        I = math.floor(self.H * self.f + 0.5)
        g = math.exp(-1.0 / (self.f * T))
        
        # Calculates statistics for all given data points
        for k in range(len(buffer)):
            x = buffer[k]
            
            # Compares the sample with the max. already found for the file
            if math.fabs(x) > f.max:
                f.max = math.fabs(x)
            # Check for the max. pos. value
            if x > self.maxP:
                f.maxP = x
            # Check for the max. neg. value
            if x < self.maxN:
                f.maxN = x
                
            # Implements Process 1 of P.56
            self.sq += x * x
            self.s  += x
            self.n  += 1
            
            # Implements Process 2 of P.56
            self.p = g * self.p + (1 - g) * math.fabs(x)
            self.q = g * self.q + (1 - g) * self.p      

            # Applies threshold to the envelope q
            for j in range(self.THRES_NO):
                if self.q >= self.c[j]:
                    self.a[j] += 1
                    self.hang[j] = 0
                if (self.q < self.c[j]) and (self.hang[j] < I):
                    self.a[j] += 1
                    self.hang[j] += 1
       
        # Computes the statistics
        self.DCleven = self.s / self.n
        LongTermLevel = 10 * math.log10(self.sq / sqlf.n + self.MIN_LOG_OFFSET)
        self.rmsdB = LongTermLevel - self.refdB
        self.ActivityFactor = 0
        ActiveSpeechLevel = -100.0
        
        # Test the lower active counter; if 0, is silence
        if self.a[0] == 0:
            return ActiveSpeechLevel
        else:
           AdB = 10 * math.log10(((self.sq) / self.a[0]) + MIN_LOG_OFFSET)
        
        # Test if the lower act.counter is below the margin: if yes, is silence
        CdB = 20 * math.log10(float(self.c[0]))
        if AdB - CdB < self.M:
            ActiveSpeechLevel
            
        # Proceed serially for steps 2 and up -- this is the most common case
        Delta = [0.0 for i in range(self.THRES_NO)]
        for j in range(1, self.THRES_NO):
            if self.a[j] != 0:
                AdB = 10 * math.log10(((self.sq) / self.a[j]) + MIN_LOG_OFFSET)
                CdB = 20 * math.log10((float(self.c[j])) + MIN_LOG_OFFSET)
                Delta[j] = AdB - CdB
                # then interpolates to find the active
                # level and the activity factor and exits
                if Delta[j] <= self.M
                    # AmdB is AdB for j-1, CmdB is CdB for j-1
                    AmdB = 10 * math.log10(((self.sq) / self.a[j - 1]) + MIN_LOG_OFFSET)
                    CmdB = 20 * math.log10(float(self.c[j - 1]) + MIN_LOG_OFFSET)

                    ActiveSpeechLevel = self.bin_interp(AdB, AmdB, CdB, CmdB, M, 0.5 )
                    
                    self.ActivityFactor = math.pow(10.0, ((LongTermLevel - ActiveSpeechLevel) / 10))
                    break
                    
                    
       return ActiveSpeechLevel