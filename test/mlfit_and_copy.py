#!/usr/bin/env python
from optparse import OptionParser, OptionGroup

parser = OptionParser(usage="usage: %prog [options] ARG",
                      description="This is a script to build up the necessary enviroment for postfit plots - including the max-likelihood calculation. ARG corresponds to the mass directory where to find the datacards that will be used or that have been used for the max-likelihood fit.")
parser.add_option("-a", "--analysis", dest="analysis", default="sm", type="string", help="Type of analysis (sm or mssm). Lower case is required. [Default: \"sm\"]")
(options, args) = parser.parse_args()

if len(args) < 1 :
    parser.print_usage()
    exit(1)

import os
import sys

dir = args[0]

def system(command):
    """ Version that dies immediately on a command failure """
    result = os.system(command)
    if result:
        sys.exit(result)

system("mkdir -p datacards")
system("mkdir -p root")
system("mkdir -p fitresults")

#if options.analysis == "tauid" :
print "cp -v %s/out/mlfit.txt ./fitresults/mlfit.txt" % dir
system("cp -v %s/out/mlfit.txt ./fitresults/mlfit.txt" % dir)
system("cp -v %s/*.txt ./datacards" % dir)
system("cp -v %s/../common/*TeV.root ./root" % dir)
system("rm datacards/tmp*")

