from optparse import OptionParser, OptionGroup

## set up the option parser
parser = OptionParser(usage="usage: %prog [options]",
                      description="Script to produce postfit plos from a set of inputs cards (datacards), input histograms (root) and maximum likelihood fits for niussance parameter pulls (fitresults)")
## direct options
parser.add_option("-f", "--fitresults", dest="fitresults", default="fitresults/mlfit.txt", type="string", help="Path to the pulls of the maximum likelihood fit. [Default: \"fitresults/mlfit_{ANALYSIS}.txt\"]")
parser.add_option("-p", "--periods", dest="periods", default="13TeV 14TeV", type="string", help="List of run periods, for which postfit plots shuld be made. [Default: \"7TeV 8TeV\"]")
parser.add_option("-a", "--analysis", dest="analysis", default="tauid", type="string", help="Type of analysis (sm or mssm). Lower case is required. [Default: tauid]")
parser.add_option("-c", "--channels", dest="channels", default="em, et, mt, mm", type="string", help="Channels for which postfit plots should be made. Individual channels should be separated by comma or whitespace. [Default: 'em, et, mt, mm']")
parser.add_option("-y", "--yields", dest="yields", default="1", type="int", help="Shift yield uncertainties. [Default: '1']")
parser.add_option("-s", "--shapes", dest="shapes", default="1", type="int", help="Shift shape uncertainties. [Default: '1']")
parser.add_option("-u", "--uncertainties", dest="uncertainties", default="1", type="int", help="Set uncertainties of backgrounds. [Default: '1']")
parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="Run in verbose more. [Default: 'False']")
cats1 = OptionGroup(parser, "TAU ID EVENT CATEGORIES", "Event categories to be picked up for the SM analysis.")
cats1.add_option("--tauid-categories-Comb3L", dest="Comb3L_tauid_categories", default="pass fail", type="string", help="List mm of event categories. [Default: \"0 1 2 3 5\"]")
cats1.add_option("--tauid-categories-Comb3M", dest="Comb3M_tauid_categories", default="pass fail", type="string", help="List em of event categories. [Default: \"0 1 2 3 5\"]")
cats1.add_option("--tauid-categories-Comb3T", dest="Comb3T_tauid_categories", default="pass fail", type="string", help="List mt of event categories. [Default: \"0 1 2 3 5\"]")
parser.add_option_group(cats1)

(options, args) = parser.parse_args()
if len(args) > 0 :
    parser.print_usage()
    exit(1)

## use parse_dcard to get a dictionary mapping
## sample name strings to fit weights
from DatacardUtils import parse_dcard
from ROOT import *
import math
import os

class Analysis:
    """
    A class designed to insert the proper scale factors into a pre-defined template set of plotting macros
    """
    def __init__(self, analysis, histfile, category, process_weight, process_shape_weight, process_uncertainties, process_shape_uncertainties, template_fname, output_fname):
         """
         Takes a dictionary (mapping strings representing samples) of fit weights and inserts these into the template macro
         at template_fname. Output is written to output_fname
         """
         self.process_weight = process_weight
         self.process_shape_weight = process_shape_weight
         self.process_uncertainties = process_uncertainties
         self.process_shape_uncertainties = process_shape_uncertainties
         self.template_fname = template_fname
         self.output_fname   = output_fname
         self.histfile       = histfile 
         self.category       = category
         self.analysis       = analysis

    def run(self):
         """
         Inserts the weights into the macros
         """
         input_file = open(self.template_fname,'r')
         output_file = open(self.output_fname,'w')
         
         curr_name = ""
         for line in input_file:
             move_on = False
             template_name = self.template_fname[self.template_fname.find("/")+1:self.template_fname.rfind("_template.C")]
             output_name   = self.output_fname[:self.output_fname.rfind(".C")]
             ## prepare first lines of macro
             line = line.replace("$CMSSW_BASE", os.environ['CMSSW_BASE'])
             line = line.replace(template_name, output_name)
             line = line.replace("$HISTFILE", self.histfile)
             line = line.replace("$CATEGORY", self.category)
	     if options.uncertainties and (options.yields or options.shapes):
                line = line.replace("$DRAW_ERROR", 'if(scaled) errorBand->Draw("e2same");')
                line = line.replace("$ERROR_LEGEND", 'if(scaled) leg->AddEntry(errorBand, "Bkg. uncertainty" , "F" );')
	     else:
                line = line.replace("$DRAW_ERROR", '')
                line = line.replace("$ERROR_LEGEND", '')
             word_arr=line.split("\n")
             uncertainties_set=[]
             for process_name in self.process_weight.keys():
                 cand_str = "$%s" % process_name
                 output_cand = ""
		 #print "cand_str "+cand_str
                 if line.strip().startswith(cand_str):
                     if options.verbose :
                         print word_arr[0]
                     curr_name = process_name
                     move_on   = True
		     if line.strip().startswith("$DYS120"):
			   move_on   = False
                     if options.yields:
                         print_me  = ''#'''std::cout << "scaling by %(value)f %(name)s" << std::endl;''' % {"value":self.process_weight[curr_name],"name":curr_name}
                         out_line  = print_me+"hin->Scale(%f); \n" % self.process_weight[curr_name]
                         output_file.write(out_line)
                         if options.verbose :
                             print out_line
                         if options.uncertainties:
		             input = TFile("root/"+self.histfile)
		             for key in input.GetListOfKeys():
                                   remnant = cand_str.rstrip(process_name)
			           histname=key.GetName()+"/"+word_arr[0][len(remnant)+2:].strip().rstrip()
			     hist = input.Get(histname)
                             if not hist :
                                 continue
                             for bin in range(1,hist.GetNbinsX()+1):
		               if not process_name+str(bin) in uncertainties_set:
			         uncertainties_set+=[process_name+str(bin)]
		                 uncertainty = math.sqrt(self.process_uncertainties[curr_name])
				 if uncertainty>0:
		                   out_line  = "hin->SetBinError(%(bin)i,hin->GetBinContent(%(bin)i)*%(uncertainty)f); \n" % {"bin":bin, "uncertainty":uncertainty}
                                   output_file.write(out_line)
                                   if options.verbose :
                                       print out_line
				 elif options.verbose:
			            print "WARNING: There is a zero yield uncertainty. Maybe you are missing uncertainties in the datacards which are in the fitresult in",self.analysis,self.category,". Please check."
	     if options.shapes:
               for process_name in self.process_shape_weight.keys():
                 cand_str = "$%s" % process_name
                 output_cand = ""
                 if line.strip().startswith(cand_str):
		     if options.verbose:
		         print cand_str
                     curr_name = process_name
                     for shape_name in self.process_shape_weight[curr_name]:
		       if options.verbose:
		         print shape_name
		       input = TFile("root/"+self.histfile)
		       for key in input.GetListOfKeys():
                           if self.category==key.GetName():
                              remnant = cand_str.rstrip(process_name)
			      histname=key.GetName()+"/"+word_arr[0][len(remnant)+2:].strip().rstrip()
                       hist = input.Get(histname)
                       hist_down = input.Get(histname+"_"+shape_name+"Down")
                       hist_up = input.Get(histname+"_"+shape_name+"Up")
                       if not hist or not hist_down or not hist_up :
                         continue
                       for bin in range(1,hist.GetNbinsX()+1):
		         shift = self.process_shape_weight[curr_name][shape_name]
                         out_line = ''
			 value = 0
		         if shift>0:
                             value = (hist_up.GetBinContent(bin)-hist.GetBinContent(bin))/hist.GetBinWidth(bin)
		         elif shift<0:
                             value = (hist.GetBinContent(bin)-hist_down.GetBinContent(bin))/hist.GetBinWidth(bin)
			 if value!=0:
		             print_me  = ''#'''std::cout << "scaling bin %(bin)i by %(shift)f %(name)s" << std::endl;''' % {"bin":bin, "shift":shift, "name":shape_name}
		             out_line  = print_me+"hin->SetBinContent(%(bin)i,hin->GetBinContent(%(bin)i)+%(value)f); \n" % {"bin":bin, "value":value*shift}
			 if options.uncertainties:
			   if self.process_shape_uncertainties[curr_name][shape_name]>0.99 and self.process_shape_weight[curr_name][shape_name]==0:
			       if options.verbose:
			          print "WARNING: Nuisance parameter not constrained (>99%)",shape_name
			   uncertainty = self.process_shape_uncertainties[curr_name][shape_name]*abs(value)
			   if options.verbose and uncertainty>max(hist_down.GetBinContent(bin)/hist.GetBinWidth(bin),hist.GetBinContent(bin)/hist.GetBinWidth(bin),hist_up.GetBinContent(bin)/hist.GetBinWidth(bin)):
			       print "WARNING: There is a bin-by-bin uncertainty larger than 100%. Make sure there is no problem with the bin-by-bin uncertainties in the root file",histfile,"in",self.analysis,self.category,". Please check:",shape_name,"bin-down:",hist_down.GetBinContent(bin),"bin-center:",hist.GetBinContent(bin),"bin-up:",hist_up.GetBinContent(bin)
		           if not process_name+str(bin) in uncertainties_set:
   		               uncertainties_set+=[process_name+str(bin)]
                               out_line  += "hin->SetBinError(%(bin)i,%(uncertainty)f); \n" % {"bin":bin, "uncertainty":uncertainty}
			   elif uncertainty!=0:
                               out_line  += "hin->SetBinError(%(bin)i,sqrt(pow(hin->GetBinError(%(bin)i),2)+pow(%(uncertainty)f,2))); \n" % {"bin":bin, "uncertainty":uncertainty}
                         output_file.write(out_line)
                         if options.verbose :
                             if out_line :
                                 print out_line
             if not move_on:
                 output_file.write(line)
	     else:
                 output_file.write("break; \n")
                 

## run periods
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
        }
for key in categories :
    for idx in range(len(categories[key])) : categories[key][idx] = categories[key][idx].rstrip(',')
## fitresults
fitresults = options.fitresults.format(ANALYSIS=options.analysis)
## post-fit plots for all channels in sm and mssm
category_mapping_classic = {
    "pass" : "passOS",
    "fail" : "failOS",
    }
category_mapping = {
    "Comb3L" : category_mapping_classic,
    "Comb3M" : category_mapping_classic,
    "Comb3T" : category_mapping_classic,
    }
for chn in channels :
    for per in periods :
        for cat in categories[chn] :
            histfile = "taupog_{CHN}.input_{PER}.root".format(CHN=chn, PER=per) 
            process_weight, process_shape_weight, process_uncertainties, process_shape_uncertainties = parse_dcard("datacards/taupog_{CHN}_{CAT}_{PER}.txt".format(CHN=chn, CAT=cat, PER=per), fitresults, "ANYBIN")
            print cat
            plots = Analysis(options.analysis, histfile, category_mapping_classic[cat],
                       process_weight, process_shape_weight, process_uncertainties, process_shape_uncertainties,
                       "templates/{AN}_template.C".format(AN=options.analysis),
                       "taupog_{CHN}_{CAT}_{PER}.C".format(CHN=chn, CAT=cat, PER=per)
            )
            plots.run()

