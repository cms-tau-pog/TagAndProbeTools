#!/usr/bin/env python
import os

from optparse import OptionParser, OptionGroup

## set up the option parser
parser = OptionParser(usage="usage: %prog [options] ARGS",
                      description="Script to create datacards to be used locally or to be uploaded to the cvs. The output directory to copy the datacards to is expected to have a dedicated structure. Directories that do not exist are created on the fly.")
parser.add_option("-i", "--in", dest="input", default="%s/src/HiggsAnalysis/HiggsToTauTau/setup" % os.environ["CMSSW_BASE"], type="string",
                  help="Full path to the input directory from which you would like to create the datacards. The path should be given relative to $CMSSW_BASE. Note that you need to obey the directory structures provide the corresponding configurationfiels for the translatino of the uncertainties into the datacards if you plan to use your own input path. [Default: src/HiggsAnalysis/HiggsToTauTau/setup]")
parser.add_option("-o", "--out", dest="out", default="auxiliaries/datacards", type="string",
                  help="Name of the output directory to which the datacards should be copied. [Default: auxiliaries/datacards]")
parser.add_option("-p", "--periods", dest="periods", default="13TeV 14TeV", type="string",
                  help="Choose between run periods [Default: \"13TeV 14TeV\"]")
parser.add_option("-a", "--analysis", dest="analysis", default="tauid", type="choice", help="Type of analysis. [Default: tauid]", choices=["tauid", "elefr" ,"mufr"])
parser.add_option("-c", "--channels", dest="channels", default="Comb3L Comb3M Comb3T", type="string",
                  help="List of discriminators, for which datacards should be created. The list should be embraced by call-ons and separeted by whitespace or comma.")
parser.add_option("--ignore-mass-argument", dest="ignore_mass_argument", default=True, action="store_true",
                  help="Ignore the mass argument when creating datacards. In this case the process name will not be extended by a specific mass value. This option should be used e.g. when replacing Higgs signal by ZTT")
cats1 = OptionGroup(parser, "tauid EVENT CATEGORIES", "Event categories to be picked up for the SM analysis.")
cats1.add_option("--tauid-categories-Comb3L", dest="Comb3L_tauid_categories", default="pass fail", type="string",
                 help="List of event categories (Comb3L). [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-Comb3M", dest="Comb3M_tauid_categories", default="pass fail", type="string",
                 help="List of event categories (Comb3M). [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-Comb3T", dest="Comb3T_tauid_categories", default="pass fail", type="string",
                 help="List of event categories (Comb3T). [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-MVAVL", dest="MVAVL_tauid_categories", default="pass fail", type="string",
                 help="List of event categories (MVAVL). [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-MVAL", dest="MVAL_tauid_categories", default="pass fail", type="string",
                 help="List of event categories (MVAL). [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-MVAM", dest="MVAM_tauid_categories", default="pass fail", type="string",
                 help="List of event categories (MVAM). [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-MVAT", dest="MVAT_tauid_categories", default="pass fail", type="string",
                 help="List of event categories (MVAT). [Default: \"pass fail\"]")
cats1.add_option("--tauid-categories-MVAVT", dest="MVAVT_tauid_categories", default="pass fail", type="string",
                 help="List of event categories (MVAVT). [Default: \"pass fail\"]")
parser.add_option_group(cats1)
cats2 = OptionGroup(parser, "Ele FR EVENT CATEGORIES", "Event categories to be used for the MSSM analysis.")
cats2.add_option("--elefr-categories-Comb3L", dest="Comb3L_elefr_categories", default="pass fail", type="string",
                 help="List ee of event categories. [Default: \"pass fail\"]")
cats2.add_option("--elefr-categories-Comb3M", dest="Comb3M_elefr_categories", default="pass fail", type="string",
                 help="List mm of event categories. [Default: \"pass fail\"]")
cats2.add_option("--elefr-categories-Comb3T", dest="Comb3T_elefr_categories", default="pass fail", type="string",
                 help="List em of event categories. [Default: \"pass fail\"]")
parser.add_option_group(cats2)
cats3 = OptionGroup(parser, "Hhh EVENT CATEGORIES", "Event categories to be used for the Hhh analysis.")
cats3.add_option("--mufr-categories-Comb3L", dest="Comb3L_mufr_categories", default="pass fail", type="string",
                 help="List ee of event categories. [Default: \"pass fail\"]")
cats3.add_option("--mufr-categories-Comb3M", dest="Comb3M_mufr_categories", default="pass fail", type="string",
                 help="List mm of event categories. [Default: \"pass fail\"]")
cats3.add_option("--mufr-categories-Comb3T", dest="Comb3T_mufr_categories", default="pass fail", type="string",
                 help="List em of event categories. [Default: \"pass fail\"]")
parser.add_option_group(cats3)

## check number of arguments; in case print usage
(options, args) = parser.parse_args()

if len(args) < 1 :
    parser.print_usage()
    exit(1)

from HiggsAnalysis.TagAndProbeTools.utils import parseArgs
from HiggsAnalysis.TagAndProbeTools.utils import mass_category

## periods
periods = options.periods.split()
for idx in range(len(periods)) : periods[idx] = periods[idx].rstrip(',')
## channels
channels = options.channels.split()
for idx in range(len(channels)) : channels[idx] = channels[idx].rstrip(',')

## setup output directory structure in case it does not exist, yet
if not os.path.exists(options.out) :
    os.system("mkdir {OUTPUT}/".format(OUTPUT=options.out))
if not os.path.exists("{OUTPUT}/{ANA}".format(OUTPUT=options.out, ANA=options.analysis)) :
    os.system("mkdir {OUTPUT}/{ANA}".format(OUTPUT=options.out, ANA=options.analysis))
for channel in channels :
    prefix="taupog_"
    if not os.path.exists("{OUTPUT}/{ANA}/{PRE}{CHN}".format(OUTPUT=options.out, ANA=options.analysis, PRE=prefix, CHN=channel)) :
        os.system("mkdir {OUTPUT}/{ANA}/{PRE}{CHN}".format(OUTPUT=options.out, ANA=options.analysis, PRE=prefix, CHN=channel))
os.chdir(options.out)

## valid mass range per category
if options.analysis == "tauid" :
    valid_masses = {
        "Comb3L"   : (-1,0),
        "Comb3M"   : (-1,0),
        "Comb3T"   : (-1,0),
        "MVAVL"   : (-1,0),
        "MVAL"   : (-1,0),
        "MVAM"   : (-1,0),
        "MVAT"   : (-1,0),
        "MVAVT"   : (-1,0),
    }
if options.analysis == "elefr" :
    valid_masses = {
        "Comb3L"   : (-1,0),
        "Comb3M"   : (-1,0),
        "Comb3T"   : (-1,0),
    }
if options.analysis == "mufr" :
    valid_masses={
        "Comb3L" : (-1,0),
        "Comb3M" : (-1,0),
        "Comb3T" : (-1,0),
    }

print "------------------------------------------------------"
print " Valid mass ranges per channel:"
print "------------------------------------------------------"
for chn in channels :
    print "chn: ", chn, "valid mass range:", valid_masses[chn]
print

## valid run periods
if options.analysis == "tauid" :
    valid_periods = {
        "Comb3L"   : "13TeV 14TeV",
        "Comb3M"   : "13TeV 14TeV",
        "Comb3T"   : "13TeV 14TeV",
        "MVAVL"   : "13TeV 14TeV",
        "MVAL"   : "13TeV 14TeV",
        "MVAM"   : "13TeV 14TeV",
        "MVAT"   : "13TeV 14TeV",
        "MVAVT"   : "13TeV 14TeV",
        }
if options.analysis == "elefr" :
    valid_periods = {
        "Comb3L"   : "13TeV 14TeV",
        "Comb3M"   : "13TeV 14TeV",
        "Comb3T"   : "13TeV 14TeV",
        }
if options.analysis == "mufr" :
    valid_periods = {
        "Comb3L"   : "13TeV 14TeV",
        "Comb3M"   : "13TeV 14TeV",
        "Comb3T"   : "13TeV 14TeV",
        }

print "------------------------------------------------------"
print " Valid mass run periods per channel:"
print "------------------------------------------------------"
for chn in channels :
    print "chn: ", chn, "valid run periods:", valid_periods[chn]
print

## switch to sm event categories
if options.analysis == "tauid" :
    os.chdir("tauid")
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
    os.chdir("elefr")
    categories = {
        "Comb3L"   : options.Comb3L_elefr_categories.split(),
        "Comb3M"   : options.Comb3M_elefr_categories.split(),
        "Comb3T"   : options.Comb3T_elefr_categories.split(),
        }

if options.analysis == "mufr" :
    os.chdir("mufr")
    categories = {
        "Comb3L"   : options.Comb3L_mufr_categories.split(),
        "Comb3M"   : options.Comb3M_mufr_categories.split(),
        "Comb3T"   : options.Comb3T_mufr_categories.split(),
        }

## return closest simulated masspoint to value
def closest_simulated_masspoint(value) :
    closest = 150
    return closest

## start the process here
base = os.getcwd()
for channel in channels :
    for period in periods :
        for cat in categories[channel] :
            ## here the normal workflow continues
            prefix="taupog_"
            os.chdir("{PWD}/{CHN}".format(CHN=prefix+channel, PWD=base))
            ## check validity of run period
            if not period in valid_periods[channel] :
                #print "drop due to failing period: ", channel, valid_periods[channel], period
                continue
            os.system("datacard-project.py -i {PATH} -c {CHN} -e {ANA}-{PER}-{CAT} {PER}-{CAT}".format(PATH=options.input, CHN=channel, ANA=options.analysis, PER=period, CAT=cat.zfill(2)))
            os.chdir("{PWD}/{CHN}/{PER}-{CAT}".format(CHN=prefix+channel, PER=period, PWD=base, CAT=cat.zfill(2)))
            for mass in parseArgs(args) :
                os.system("create-datacard.py -i {CHN}.inputs-{ANA}-{PER}.root -o {CHN}_{CAT}_{PER}-{LABEL}.txt {MASS}".format(
                CHN=prefix+channel,
                ANA=options.analysis,
                PER=period,
                CAT=cat,
                MASS='' if options.ignore_mass_argument else mass,
                LABEL='' if options.ignore_mass_argument else mass
                 ))

            os.system("mv *.* ../")
            os.chdir("{PWD}/{CHN}".format(CHN=prefix+channel, PWD=base))
            os.system("rm -r {PER}-{CAT}".format(PER=period, CAT=cat.zfill(2)))
            os.system("rm -r cgs.* unc.*")


