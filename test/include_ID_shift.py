import re
import ROOT
from RecoLuminosity.LumiDB import argparse

def get_svar(fname):
    '''Obtains the sigma variation of fit parameter (factor) from the fit result file ffile'''
    ffile = open(fname,'r')
    for line in ffile.readlines():
        if line.startswith("SF"):
            matcher = re.compile('[+]\d+\.\d+(?![+]|\d)')
            matches = matcher.findall(line)
            svar = 0
            if matches:
                svar = float(matches[0]) 
            #print svar
            return svar

def get_sunc(fname):
    '''Obtains the uncertainty of fit parameter (factor) from the fit result file ffile'''
    ffile = open(fname,'r')
    for line in ffile.readlines():
        if line.startswith("SF"):
            matcher = re.compile('[-] \d+\.\d+')
            matches = matcher.findall(line)
            svar = 0
            if matches:
                a,b=(matches[0].split())
                svar = float(b)
            #print svar
            return svar

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--signal', dest='signal_name', default='DYS120',help='Signal name')
parser.add_argument('-d', '--discriminator', dest='disc', default='Comb3L',help='Discriminator')
parser.add_argument('-a', '--analysis', dest='ana', default='tauid', help='Analysis')
args = parser.parse_args()

dir=''

if args.ana=="tauid":
   dir="setup"

pass_input_file = open("taupog_"+args.disc+"_pass_13TeV.C",'r')
pass_output_file = open("taupog_"+args.disc+"Comb3L_pass_13TeV_test.C",'w')
root_file=ROOT.TFile("root/taupog_"+args.disc+".input_13TeV.root","r")
pass_directory=root_file.Get("passOS")
pass_hist=pass_directory.Get(args.signal_name)

texte = ""
texte=texte+"hin->Scale(%.3f);"%(get_svar("fitresults/mlfit.txt")) 
texte=texte+"\n"
for bin in range(1,pass_hist.GetNbinsX()+1):
        texte=texte+"hin->SetBinError(%i,sqrt(pow(hin->GetBinError(%i),2)+pow(%.3f*hin->GetBinContent(%i),2)));"%(bin,bin,get_sunc("fitresults/mlfit.txt"),bin)
	texte=texte+"\n"
texte=texte+"break;"
for line in pass_input_file:
	line = line.replace("$DYS120", texte)	
        pass_output_file.write(line)

fail_input_file = open("taupog_"+args.disc+"_fail_13TeV.C",'r')
fail_output_file = open("taupog_"+args.disc+"_fail_13TeV_test.C",'w')
fail_directory=root_file.Get("failOS")
fail_hist=fail_directory.Get(args.signal_name)

norm_tauID_file=open("../"+dir+"/"+args.disc+"/norm.txt","r")
tauID_factor=float(norm_tauID_file.readline())

texte = ""
scale_fail=1+(((1-get_svar("fitresults/mlfit.txt"))/0.5)*tauID_factor)
unc_fail=(1+(((1-get_svar("fitresults/mlfit.txt"))/0.5)*tauID_factor))*get_sunc("fitresults/mlfit.txt")

texte=texte+"hin->Scale(%.3f);"%(scale_fail)
texte=texte+"\n"
for bin in range(1,fail_hist.GetNbinsX()+1):
        texte=texte+"hin->SetBinError(%i,sqrt(pow(hin->GetBinError(%i),2)+pow(%.3f*hin->GetBinContent(%i),2)));"%(bin,bin,unc_fail,bin)
        texte=texte+"\n"
texte=texte+"break;"
for line in fail_input_file:
        line = line.replace("$DYS120", texte)
        fail_output_file.write(line)



