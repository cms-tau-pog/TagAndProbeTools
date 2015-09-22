rm -rf setups
rm -rf aux
rm -rf LIMITS
mkdir -p setups aux
cp -r HiggsAnalysis/TagAndProbeTools/setup setups/std
add_bbb_errors.py -f 'Comb3L:13TeV:pass,fail:QCD,DYB,TT,W,DYS120' -i setups/std -o setups/std-bin-by-bin  --threshold 0.10
mkdir -p aux/std/sm
setup-datacards.py -i setups/std-bin-by-bin -o aux/std/sm -c "Comb3L" --tauid-categories-Comb3L "pass fail" -p 13TeV -a tauid 110
mkdir -p LIMITS/std
setup-taupog.py -i aux/std/sm -o LIMITS/std/tauid -s chn  -p 13TeV -c 'Comb3L' --tauid-categories-Comb3L "pass fail" -a tauid
limit.py --max-likelihood --stable --rMin 0.5 --rMax 1.2 LIMITS/std/tauid/Comb3L/0/ --physics-model tmp=HiggsAnalysis.CombinedLimit.PhysicsModel:tagAndProbe --physics-model-options anticorrelation=1.7411857
cd HiggsAnalysis/TagAndProbeTools/test
python mlfit_and_copy.py $CMSSW_BASE/src/LIMITS/std/tauid/Comb3L/0
python produce_macros.py -p 13TeV -c Comb3L --tauid-categories-Comb3L='pass fail' -a tauid
python include_ID_shift.py -d Comb3L -s DYS120
root -l -q script_postfit_pass.C++
root -l -q script_postfit_fail.C++
cd ../../..


