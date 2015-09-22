#!/usr/bin/env python

from optparse import OptionParser, OptionGroup

## set up the option parser
parser = OptionParser(usage="usage: %prog [options]",
                      description="This is  a script to copy input files and datacards for limit and significance calculation from cvs to local or to the svn server that is used for the combination of all Higgs decay channels. If the output directory does not already exist a new directory structure will be created (for local copies). ARGs corresponds to a list of integer values resembling the mass points for which you want to copy the datacards. Ranges can be indicated e.g. by: 110-145'. That only any x-th mass point should be taken into account can be indicated e.g. by: 110-145:5. The latter example will pick up the masses 110 115 120 130 135 140 145. Any combination of this syntax is possible.")
parser.add_option("-i", "--in", dest="input", default="auxiliaries/datacards/", type="string",
                  help="Name of the input directory from where to pick up the datacards. [Default: auxiliaries/datacards/]")
parser.add_option("-o", "--out", dest="out", default="ichep2012", type="string",
                  help="Name of the output directory to which the datacards should be copied. [Default: ichep2012]")
parser.add_option("-p", "--periods", dest="periods", default="13TeV", type="string",
                  help="List of run periods for which the datacards are to be copied. [Default: \"7TeV 8TeV\"]")
parser.add_option("-a", "--analysis", dest="analysis", default="tauid", type="choice",
                  help="Type of analysis (tauid, elefr or mufr). Lower case is required. [Default: sm]", choices=["tauid", "elefr", "mufr"])
parser.add_option("-c", "--channels", dest="channels", default="mm em mt et tt", type="string",
                  help="List of channels, for which the datacards should be copied. The list should be embraced by call-ons and separeted by whitespace or comma. Available channels are ee, mm, em, mt, et, tt, vhtt, hmm, hbb. [Default: \"mm em mt et tt\"]")
parser.add_option("-u", "--no-update", dest="no_update", default=False, action="store_true",
                  help="If there are already root files in common, do not recopy them. This should be used by other tools only to speed up copy jobs. [Default: False]")
parser.add_option("--model", dest="model", default="", type="string", help="For some BSM models the dir structure should not be in steps of mass but other parameters. Differences occure for lowmH and 2HDM. [Default: \"\"]")
cats1 = OptionGroup(parser, "SM EVENT CATEGORIES", "Event categories to be picked up for the SM analysis.")
cats1.add_option("--tauid-categories-Comb3L", dest="Comb3L_tauid_categories", default="pass fail", type="string",
                 help="List ee of event categories. [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-Comb3M", dest="Comb3M_tauid_categories", default="pass fail", type="string",
                 help="List mm of event categories. [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-Comb3T", dest="Comb3T_tauid_categories", default="pass fail", type="string",
                 help="List em of event categories. [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-MVAVL", dest="MVAVL_tauid_categories", default="pass fail", type="string",
                 help="List em of event categories. [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-MVAL", dest="MVAL_tauid_categories", default="pass fail", type="string",
                 help="List em of event categories. [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-MVAM", dest="MVAM_tauid_categories", default="pass fail", type="string",
                 help="List em of event categories. [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-MVAT", dest="MVAT_tauid_categories", default="pass fail", type="string",
                 help="List em of event categories. [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-MVAVT", dest="MVAVT_tauid_categories", default="pass fail", type="string",
                 help="List em of event categories. [Default: \"pass fail\"]")
parser.add_option_group(cats1)
parser.add_option("-4", "--SM4", dest="sm4", default=False, action="store_true",
                  help="Copy SM4 datacards (will add a prefix SM4_ to each file). [Default: False]")
parser.add_option("-v", "--verbose", dest="verbose", default=False, action="store_true",
                  help="Run in verbose mode. [Default: False]")
(options, args) = parser.parse_args()
## check number of arguments; in case print usage
if len(args) < 0 :
    parser.print_usage()
    exit(1)

import os
from HiggsAnalysis.TagAndProbeTools.utils import parseArgs
from HiggsAnalysis.TagAndProbeTools.utils import is_integer

## prepare input
input = options.input + "/" + options.analysis
## run periods
periods = options.periods.split()
for idx in range(len(periods)) : periods[idx] = periods[idx].rstrip(',')
## channels
channels = options.channels.split()
for idx in range(len(channels)) : channels[idx] = channels[idx].rstrip(',')
## define prefix for SM4
prefix = "SM4_" if options.sm4 else ""

## switch to sm event categories
if options.analysis == "tauid" :
    categories = {
        "Comb3L"   : options.Comb3L_tauid_categories.split(),
        "Comb3M"   : options.Comb3M_tauid_categories.split(),
        "Comb3T"   : options.Comb3T_tauid_categories.split(),
        "MVAVL"   : options.MVAVL_tauid_categories.split(),
        "MVAL"   : options.MVAL_tauid_categories.split(),
        "MVAM"   : options.MVAM_tauid_categories.split(),
        "MVAT"   : options.MVAT_tauid_categories.split(),
        "MVAVT"   : options.MVAVT_tauid_categories.split(),
        }

## valid run periods
if options.analysis == "tauid" :
    valid_periods = {
        "Comb3L"   : "7TeV 8TeV 13TeV 14TeV",
        "Comb3M"   : "7TeV 8TeV 13TeV 14TeV",
        "Comb3T"   : "7TeV 8TeV 13TeV 14TeV",
        "MAVL"   : "7TeV 8TeV 13TeV 14TeV",
        "MVAL"   : "7TeV 8TeV 13TeV 14TeV",
        "MVAM"   : "7TeV 8TeV 13TeV 14TeV",
        "MVAT"   : "7TeV 8TeV 13TeV 14TeV",
        "MVAVT"   : "7TeV 8TeV 13TeV 14TeV",
        }

if options.verbose :
    print "------------------------------------------------------"
    print " Valid mass run periods per channel:"
    print "------------------------------------------------------"
    for chn in channels :
        print "chn: ", chn, "valid run periods:", valid_periods[chn]
    print
    print "copy datacards for:", options.analysis, options.channels, options.periods

## setup directory structure in case it does not exist, yet
if not os.path.exists(options.out) :
    os.system("mkdir {OUTPUT}".format(OUTPUT=options.out))
if not os.path.exists("{OUTPUT}/../common".format(OUTPUT=options.out)) :
    os.system("mkdir {OUTPUT}/../common".format(OUTPUT=options.out))

for period in periods :
    for channel in channels :
            ## check validity of run period
            if not period in valid_periods[channel] :
                #print "drop due to failing period: ", channel, valid_periods[channel], period
                continue
            else :
                for category in categories[channel] :
                    if options.verbose :
                        print "copying datacards for:", period, channel, category
                    ## check validity of run period
                    if not period in valid_periods[channel] :
                        #print "drop due to failing period: ", channel, valid_periods[channel], period
                        continue
                    os.system("cp {INPUT}/taupog_{CHN}/taupog_{CHN}.inputs-{ANA}-{PERIOD}.root {OUTPUT}/../common/taupog_{CHN}.input_{PERIOD}.root".format(INPUT=input, CHN=channel, ANA=options.analysis, OUTPUT=options.out, PRE=prefix, PERIOD=period))
                    os.system("cp {INPUT}/taupog_{CHN}/taupog_{CHN}_{CAT}_{PERIOD}-.txt {OUTPUT}/taupog_{CHN}_{CAT}_{PERIOD}.txt".format(INPUT=input, CHN=channel, CAT=category, PERIOD=period, OUTPUT=options.out))
                    os.system("perl -pi -e 's/taupog_{CHN}.inputs-{ANA}-{PERIOD}.root/..\/common\/taupog_{CHN}.input_{PERIOD}.root/g' {OUTPUT}/taupog_{CHN}_{CAT}_{PERIOD}.txt".format(CHN=channel, ANA=options.analysis, PERIOD=period, OUTPUT=options.out, CAT=category))

