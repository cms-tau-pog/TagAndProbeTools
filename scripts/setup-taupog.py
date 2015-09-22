#!/usr/bin/env python
from optparse import OptionParser, OptionGroup

## set up the option parser
parser = OptionParser(usage="usage: %prog [options] ARGS",
                      description="Script to setup the limit calculation for htt from a prepared reservoir of datacards. The output directory to copy the datacards to is expected to have a dedicated structure. Directories that do not exist are created on the fly. ARGS corresponds to a list of integer values resembling the mass points for which you want to create the datacards. Ranges can be indicated e.g. by: 110-145'. That only any x-th mass point should be taken into account can be indicated e.g. by: 110-145:5. The latter example will pick up the masses 110 115 120 130 135 140 145. Any combination of this syntax is possible.")
parser.add_option("-i", "--in", dest="input", default="auxiliaries/datacards", type="string", help="Name of the input directory from which to copy the prepared datacards. [Default: auxiliaries/datacards]")
parser.add_option("-o", "--out", dest="out", default="taupog-limits", type="string", help="Name of the output directory to which the datacards should be copied. [Default: htt-limits]")
parser.add_option("-p", "--periods", dest="periods", default="13TeV", type="string", help="Choose between run periods [Default: \"13TeV 14TeV\"]")
parser.add_option("-a", "--analysis", dest="analysis", default="tauid", type="choice", help="Type of analysis (sm or mssm). Lower case is required. [Default: sm]", choices=["tauid", "elefr", "mufr"])
parser.add_option("-c", "--channels", dest="channels", default="Comb3L Comb3M Comb3T", type="string", help="List of channels, for which datacards should be created. The list should be embraced by call-ons and separeted by whitespace or comma. Available channels are mm, em, mt, et, tt, vhtt, hmm, hbb. [Default: \"mm em mt et\"]")
parser.add_option("-l", "--label", dest="label", default="", type="string", help="Add a label to the subdirectories that belong to each corresponding sub-channel. [Default: \"\"]")
parser.add_option("-s", "--setup", dest="setup", default="all", type="choice", help="Setup in which to run. Choises are between cmb only (cmb), split by channels (chn), split by event category (cat), all (all). The combiend limit will always be calculated. [Default: all]", choices=["cmb", "chn", "cat", "all"])
parser.add_option("-v", "--verbose", dest="verbose", default=False, action="store_true", help="Run in verbose mode. [Default: False]")
parser.add_option("--model", dest="model", default="", type="string", help="For some BSM models the dir structure should not be in steps of mass but other parameters. Differences occure for lowmH and 2HDM. [Default: \"\"]")
parser.add_option("--SM4", dest="SM4", default=False, action="store_true", help="Copy datacards for SM4 (for SM only). [Default: False]")
cats1 = OptionGroup(parser, "SM EVENT CATEGORIES", "Event categories to be picked up for the SM analysis.")
cats1.add_option("--tauid-categories-Comb3L", dest="Comb3L_tauid_categories", default="pass fail", type="string", help="List of ee event categories. [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-Comb3M", dest="Comb3M_tauid_categories", default="pass fail", type="string", help="List of mm event categories. [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-Comb3T", dest="Comb3T_tauid_categories", default="pass fail", type="string", help="List of em event categories. [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-MVAVL", dest="MVAVL_tauid_categories", default="pass fail", type="string", help="List of MVAVL event categories. [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-MVAL", dest="MVAL_tauid_categories", default="pass fail", type="string", help="List of MVAL event categories. [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-MVAM", dest="MVAM_tauid_categories", default="pass fail", type="string", help="List of MVAM event categories. [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-MVAT", dest="MVAT_tauid_categories", default="pass fail", type="string", help="List of MVAT event categories. [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-MVAVT", dest="MVAVT_tauid_categories", default="pass fail", type="string", help="List of MVAVT event categories. [Default: \"pass fail\"]")
parser.add_option_group(cats1)
cats2 = OptionGroup(parser, "MSSM EVENT CATEGORIES", "Event categories to be used for the MSSM analysis.")
cats2.add_option("--mssm-categories-ee", dest="ee_mssm_categories", default="8 9", type="string", help="List of ee event categories. [Default: \"8 9\"]")
cats2.add_option("--mssm-categories-mm", dest="mm_mssm_categories", default="8 9", type="string", help="List of mm event categories. [Default: \"8 9\"]")
cats2.add_option("--mssm-categories-em", dest="em_mssm_categories", default="8 9", type="string", help="List of em event categories. [Default: \"8 9\"]")
parser.add_option_group(cats2)

## check number of arguments; in case print usage
(options, args) = parser.parse_args()

import os
from HiggsAnalysis.TagAndProbeTools.utils import parseArgs

## label
label = "" if options.label == "" else "-"+options.label
## periods
periods = options.periods.split()
for idx in range(len(periods)) : periods[idx] = periods[idx].rstrip(',')
## channels
channels = options.channels.split()
for idx in range(len(channels)) : channels[idx] = channels[idx].rstrip(',')

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

## switch to mssm event categories
if options.analysis == "elefr" :
    categories = {
        "Comb3L"   : options.Comb3L_elefr_categories.split(),
        "Comb3M"   : options.Comb3M_elefr_categories.split(),
        "Comb3T"   : options.Comb3T_elefr_categories.split(),
        }

## configuration for summer13
directories_tauid = {
    'Comb3L' : {
    'pass' : ['pass'],
    'fail' : ['fail'],
    },
    'Comb3M' : {
    'pass' : ['pass'],
    'fail' : ['fail'],
    },
    'Comb3T' : {
    'pass' : ['pass'],
    'fail' : ['fail'],
    },
    'MVAVL' : {
    'pass' : ['pass'],
    'fail' : ['fail'],
    },
    'MVAL' : {
    'pass' : ['pass'],
    'fail' : ['fail'],
    },
    'MVAM' : {
    'pass' : ['pass'],
    'fail' : ['fail'],
    },
    'MVAT' : {
    'pass' : ['pass'],
    'fail' : ['fail'],
    },
    'MVAVT' : {
    'pass' : ['pass'],
    'fail' : ['fail'],
    },
}

## determine directories
def directories(channel) :
    if options.analysis == "tauid" :
        category_names = directories_tauid
    return category_names

## setup directory structure in case it does not exist, yet.
if not os.path.exists(options.out) :
    os.system("mkdir {OUTPUT}/".format(OUTPUT=options.out))
if not os.path.exists("{OUTPUT}/0{LABEL}".format(OUTPUT=options.out, ANA=options.analysis, LABEL=label)) :
    os.system("mkdir {OUTPUT}/0{LABEL}".format(OUTPUT=options.out, ANA=options.analysis, LABEL=label))
for channel in channels :
    if not os.path.exists("{OUTPUT}/{CHN}{LABEL}".format(OUTPUT=options.out, CHN=channel, LABEL=label)) :
        os.system("mkdir {OUTPUT}/{CHN}{LABEL}".format(OUTPUT=options.out, CHN=channel, LABEL=label))
for channel in channels :
    category_names = directories(channel)
    for cat in categories[channel] :
        for dir in category_names[channel][cat]:
            if not os.path.exists("{OUTPUT}/{CHN}/{DIR}{LABEL}".format(OUTPUT=options.out, CHN=channel, DIR=dir, LABEL=label)) :
                os.system("mkdir {OUTPUT}/{CHN}/{DIR}{LABEL}".format(OUTPUT=options.out, CHN=channel, DIR=dir, LABEL=label))

verb = "-v" if options.verbose else ""

for channel in channels :
    category_names = directories(channel)
    for period in periods :
        for cat in categories[channel] :
             print "setup directory structure for", options.analysis, period, channel, cat
             ## setup combined
             os.system("cvs2local.py -i {INPUT} -o {OUTPUT} -p {PER} -a {ANA} -c {CHN} --no-update --{ANA}-categories-{CHN} {CAT}".format(
             INPUT=options.input, OUTPUT=options.out+"/"+channel+"/0"+label, PER=period, ANA=options.analysis, CHN=channel, CAT=cat))
	     print "cvs2local.py -i {INPUT} -o {OUTPUT} -p {PER} -a {ANA} -c {CHN} --no-update --{ANA}-categories-{CHN} {CAT}".format(
             INPUT=options.input, OUTPUT=options.out+"/"+channel+"/0"+label, PER=period, ANA=options.analysis, CHN=channel, CAT=cat)

