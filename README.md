Tag and probe tools to measure the tau ID efficiency, electron to tau fake rate and muon to tau fake rate within the TAU POG.

Installation
------------

Setup environment and install Higgs Combine package:

```shell
setenv SCRAM_ARCH slc6_amd64_gcc481
cmsrel CMSSW_7_1_5 ### must be a 7_1_X release  >= 7_1_5;  (7.0.X and 7.2.X are NOT supported either) 
cd CMSSW_7_1_5/src 
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v5.0.1
scramv1 b clean; scramv1 b # always make a clean build, as scram doesnt always see updates to src/LinkDef.h
cd ../..
```

Get the Tag and Probe package:

```shell
cd HiggsAnalysis
git clone https://github.com/cecilecaillol/TauPOG_TnPTools.git
cd ..
scram b -j 4
cp HiggsAnalysis/TagAndProbeTools/maxlikelihoodFit.sh .
```

Make some modifications in Higgs Combine package (to be included centrally later) to define the TnP physics model and how to take into account the anticorrelation in the fit:

```shell
cp /afs/cern.ch/user/c/ccaillol/public/ModelTools.py HiggsAnalysis/CombinedLimit/python/.
cp /afs/cern.ch/user/c/ccaillol/public/PhysicsModel.py HiggsAnalysis/CombinedLimit/python/.
cp /afs/cern.ch/user/c/ccaillol/public/ProcessNormalization.h HiggsAnalysis/CombinedLimit/interface/.
cp /afs/cern.ch/user/c/ccaillol/public/ProcessNormalization.cc HiggsAnalysis/CombinedLimit/src/.
```

Preparation:
-----------

All input files should be in HiggsAnalysis/TagAndProbeTools/setup-(ANALYSIS NAME)/(DISCRIMINATOR NAME). For example HiggsAnalysis/TagAndProbeTools/setup-mufr/MVA3T. The files in such a repository are:
 * unc-(ANALYSIS NAME)-13TeV-fail.vals (defined as usual in HiggsTauTau anlysis tools)
 * unc-(ANALYSIS NAME)-13TeV-pass.vals
 * unc-(ANALYSIS NAME)-13TeV-fail.conf
 * unc-(ANALYSIS NAME)-13TeV-pass.conf
 * cgs-(ANALYSIS NAME)-13TeV-fail.conf
 * cgs-(ANALYSIS NAME)-13TeV-pass.conf
 * taupog_(DISCRIMINATOR NAME).inputs-(ANALYSIS NAME)-13TeV.root (input root file with 2 directories: "passOS" and "failOS")
 * norm.txt (file that contains only one number, which describes the anticorrelation between the pass and the fail regions. This number is defined as the factor that would multiply the signal yield in the fail region, minus one, in case the signal in the pass region would be reduced by half. For example, if there are 200 events in pass and 100 events in fail and if the signal yield in pass is reduced by half, the signal yield in fail is multiplied by 2, so the number in the file is 2-1=1.00)

Run the maximum likelihood fit and make postfit plots:
-----------------------------------------------------

```shell
sh maxlikelihoodFit.sh
```

The file "maxlikelihoodFit.sh" is currently hardcoded for the tau id efficiency measurement combined 3 Hits Loose isolation. Just change the values to run other analyses or working points. The codes in HiggsAnalysis/TagAndProbeTools/ are not adapted to all analysis and working point yet, this can be added. There is only one template for postfit plots now, it has to be adapted to mu and ele fake rate measurements.

 
