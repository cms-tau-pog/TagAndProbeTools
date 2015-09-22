
#include <iostream>

#include <TH1F.h>
#include <TFile.h>
#include <TROOT.h>
#include <TString.h>
#include <TSystem.h>
#include <Rtypes.h>
#include <fstream>
#include <iomanip>

#include <TMath.h>
#include <TAxis.h>
#include <TCanvas.h>
#include <TLegend.h>
#include <TAttLine.h>
#include <TPaveText.h>
#include "../interface/HttStyles.h"
#include "../src/HttStyles.cc"

static const float SIGNAL_SCALE = 1.;

static const bool BLIND_DATA = false; //false;
float blinding_SM(float mass){ return (100<mass && mass<150); }
float blinding_MSSM(float mass){ return (100<mass); }
float maximum(TH1F* h, bool LOG=false){
  if(LOG){
    if(h->GetMaximum()>1000){ return 1000.*TMath::Nint(500*h->GetMaximum()/1000.); }
    if(h->GetMaximum()>  10){ return   10.*TMath::Nint( 50*h->GetMaximum()/  10.); }
    return 50*h->GetMaximum(); 
  }
  else{
    return 1.1*h->GetMaximum(); 
  }
}


TH1F* refill(TH1F* hin, const char* sample, bool data=false)
/*
  refill histograms, divide by bin width and correct bin errors. For MC histograms set 
  bin errors to zero.
*/
{
  if(hin==0){
    std::cout << "hist not found: " << sample << "  -- close here" << std::endl;
    exit(1);  
  }
  TH1F* hout = (TH1F*)hin->Clone(); hout->Clear();
  double erreur=0;
  for(int i=0; i<hout->GetNbinsX(); ++i){
    if(data){
      hout->SetBinContent(i+1, BLIND_DATA && blinding_SM(hin->GetBinCenter(i+1)) ? 0. : hin->GetBinContent(i+1)/hin->GetBinWidth(i+1));
      hout->SetBinError  (i+1, BLIND_DATA && blinding_SM(hin->GetBinCenter(i+1)) ? 0. : hin->GetBinError(i+1)/hin->GetBinWidth(i+1));
    }
    else{
      hout->SetBinContent(i+1, hin->GetBinContent(i+1)/hin->GetBinWidth(i+1));
      hout->SetBinError(i+1, 0.);
    }
  }
  return hout;
}


void rescale(TH1F* hin, unsigned int idx)
/*
  rescale histograms according to fit results. The keywords like $Ztt will be replaced 
  by a cout statement and a scaling command.
*/
{
  switch(idx){
  case 1:  
  $QCD
  case 2: 
  $W
  case 3: 
  $TT
  case 4: 
  $DYB
  case 5: 
  $DYS120
  default :
    std::cout << "error histograms not known?!?" << std::endl;
  }
}

void 
TAUPOG_TAUID(bool scaled=true, bool log=false, float min=0.1, float max=-1., const char* inputfile="root/$HISTFILE", const char* directory="$CATEGORY")
{
  // define common canvas, axes pad styles
  SetStyle(); gStyle->SetLineStyleString(11,"20 10");

  // determine category tag
  const char* category_extra = "";

  const char* dataset;
  if(std::string(inputfile).find("7TeV")!=std::string::npos){dataset = "CMS Preliminary,  H#rightarrow#tau#tau, 4.9 fb^{-1} at 7 TeV";}
  if(std::string(inputfile).find("8TeV")!=std::string::npos){dataset = "CMS, #sqrt{s} = 8 TeV, L = 19.7 fb^{-1}";}
  if(std::string(inputfile).find("13TeV")!=std::string::npos){dataset = "CMS, #sqrt{s} = 13 TeV, L = 1.0 fb^{-1}";}
  
  TFile* input = new TFile(inputfile);
  TH1F* DYB  = refill((TH1F*)input->Get(TString::Format("%s/DYB"   , directory)), "DYB"); InitHist(DYB, "", "", kAzure-8, 1001);
  TH1F* TT    = refill((TH1F*)input->Get(TString::Format("%s/TT"     , directory)), "TT"  ); InitHist(TT  , "", "", kBlue-4, 1001);
  TH1F* W  = refill((TH1F*)input->Get(TString::Format("%s/W"   , directory)), "W"); InitHist(W, "", "", kViolet+6, 1001);
  TH1F* QCD    = refill((TH1F*)input->Get(TString::Format("%s/QCD"     , directory)), "QCD"  ); InitHist(QCD  , "", "", kPink+1, 1001);
  TH1F* DYS120  = refill((TH1F*)input->Get(TString::Format("%s/DYS120"   , directory)), "DYS120"); InitHist(DYS120, "", "", kTeal-8, 1001);
  TH1F* data   = refill((TH1F*)input->Get(TString::Format("%s/data_obs", directory)), "data", true);
  //InitHist(data, "#bf{m_{vis} [GeV] [GeV]}", "#bf{dN/dm_{vis} [GeV] [1/GeV]}"); InitData(data);
  InitHist(data, "#bf{m_{vis}}", "#bf{dN/dm_{vis} }"); InitData(data);

  TH1F* ref=(TH1F*)QCD->Clone("ref");
  ref->Add(W  );
  ref->Add(TT);
  ref->Add(DYB  );
  ref->Add(DYS120  );

  double unscaled[8];
  unscaled[0] = QCD->Integral();
  unscaled[1] = W  ->Integral();
  unscaled[2] = TT->Integral();
  unscaled[3] = DYB  ->Integral();
  unscaled[4] = DYS120  ->Integral();

  double erreur=0;

//*********************************************
  TH1F *QCD2 = (TH1F*)QCD->Clone();
  TH1F *TT2 = (TH1F*)TT->Clone();
  TH1F *W2 = (TH1F*)W->Clone();
  TH1F *DYB2 = (TH1F*)DYB->Clone();
  TH1F *DYS1202 = (TH1F*)DYS120->Clone();

  W2->Add(QCD2);
  TT2->Add(W2);
  DYB2  ->Add(TT2);
  DYS1202->Add(DYB2  );

  TCanvas* canvas   = new TCanvas("cc", "cc",600,800);

  TPad*    upperPad = new TPad("upperPad", "upperPad",
                               .005, .2525, .995, .995);
  TPad*    lowerPad = new TPad("lowerPad", "lowerPad",
                               .005, .005, .995, .2475);
  upperPad->Draw();lowerPad->Draw();
  upperPad->cd();

  if(log){ upperPad->SetLogy(1); }
#if defined MSSM
  if(!log){ data->GetXaxis()->SetRange(0, data->FindBin(250)); } else{ data->GetXaxis()->SetRange(0, data->FindBin(1000)); };
#else
  data->GetXaxis()->SetRange(0, data->FindBin(250));
#endif

  data->SetNdivisions(505);
  data->SetMinimum(min);
  data->SetMaximum(max>0 ? max : std::max(maximum(data, log), maximum(DYS120, log)));
  data->GetXaxis()->SetTitleFont(63);data->GetXaxis()->SetTitleSize(18); data->GetXaxis()->SetTitleOffset(2.5);
  data->GetYaxis()->SetTitleFont(63);data->GetYaxis()->SetTitleSize(18); data->GetYaxis()->SetTitleOffset(3.5);
  data->Draw("e");

  DYS1202  ->Draw("histsame"); 
  DYB2->Draw("histsame");
  TT2  ->Draw("histsame");
  W2->Draw("histsame");
  QCD2->Draw("histsame");
   // Ztt2  ->Draw("histsame");
  data->Draw("esame");

  TLegend* leg2 = new TLegend(0.50, 0.65, 0.95, 0.90);
  SetLegendStyle(leg2);
  leg2->AddEntry(data , "Observed"                       , "LP");
  leg2->AddEntry(DYS1202, "Z#rightarrow #tau_{h}#tau_{#mu}"                   , "F" );
  leg2->AddEntry(DYB2, "DY others"                            , "F" );
  leg2->AddEntry(TT2  , "t#bar{t}"      , "F" );
  leg2->AddEntry(W2, "W + jets"                       , "F" );
  leg2->AddEntry(QCD2  , "QCD multijet"           , "F" );
  leg2->Draw("same");
  CMSPrelim(dataset, "", 0.16, 0.835);
  canvas->Update();		       
  lowerPad->cd();
  TH1F* zero_2 = (TH1F*)ref ->Clone("zero"); zero_2->Clear();
  TH1F* rat1_2 = (TH1F*)data->Clone("rat");
  rat1_2->Divide(DYS1202);
  for(int ibin=0; ibin<rat1_2->GetNbinsX(); ++ibin){
    if(rat1_2->GetBinContent(ibin+1)>0){
      // catch cases of 0 bins, which would lead to 0-alpha*0-1
      rat1_2->SetBinContent(ibin+1, rat1_2->GetBinContent(ibin+1)-1.);
    }
    zero_2->SetBinContent(ibin+1, 0.);
  }
  rat1_2->SetLineColor(kBlack);
  rat1_2->SetFillColor(kGray );
  rat1_2->SetMaximum(+0.3);
  rat1_2->SetMinimum(-0.3);
  rat1_2->GetYaxis()->CenterTitle();
  rat1_2->GetYaxis()->SetTitle("#bf{Data/MC-1}"); rat1_2->GetYaxis()->SetTitleFont(63); rat1_2->GetYaxis()->SetTitleSize(18);rat1_2->GetYaxis()->SetTitleOffset(1.5);
  rat1_2->GetXaxis()->SetTitle("#bf{m_{vis} (GeV) }"); rat1_2->GetXaxis()->SetTitleFont(63); rat1_2->GetXaxis()->SetTitleSize(18); rat1_2->GetXaxis()->SetTitleOffset(2.5);
  rat1_2->Draw();
  zero_2->SetLineColor(kBlack);
  zero_2->Draw("same");
  canvas->Update();


  if(scaled){
    rescale(DYS120, 5);
    rescale(DYB, 4);
    rescale(TT,   3);
    rescale(W, 2);
    rescale(QCD,   1);
  }

  TH1F* scales[8];
  scales[0] = new TH1F("scales-QCD", "", 8, 0, 8);
  scales[0]->SetBinContent(1, unscaled[0]>0 ? (QCD->Integral()/unscaled[0]-1.) : 0.);
  scales[1] = new TH1F("scales-W"  , "", 8, 0, 8);
  scales[1]->SetBinContent(2, unscaled[1]>0 ? (W  ->Integral()/unscaled[1]-1.) : 0.);
  scales[2] = new TH1F("scales-TT", "", 8, 0, 8);
  scales[2]->SetBinContent(3, unscaled[2]>0 ? (TT->Integral()/unscaled[2]-1.) : 0.);
  scales[3] = new TH1F("scales-DYB"  , "", 8, 0, 8);
  scales[3]->SetBinContent(4, unscaled[3]>0 ? (DYB  ->Integral()/unscaled[3]-1.) : 0.);
  scales[4] = new TH1F("scales-DYS120", "", 8, 0, 8);
  scales[4]->SetBinContent(5, unscaled[4]>0 ? (DYS120->Integral()/unscaled[4]-1.) : 0.);
  W->Add(QCD);
  TT->Add(W);
  DYB  ->Add(TT);
  DYS120->Add(DYB);

  /*
    mass plot before and after fit
  */



  TCanvas* canv = MakeCanvas("canv", "histograms", 600, 600);
  canv->cd();
  if(log){ canv->SetLogy(1); }
  data->GetXaxis()->SetRange(0, data->FindBin(250));

  data->SetNdivisions(505);
  data->SetMinimum(min);
  data->SetMaximum(max>0 ? max : std::max(maximum(data, log), maximum(DYS120, log)));
  data->Draw("e");

  TH1F* errorBand = (TH1F*)DYS120 ->Clone();
  errorBand  ->SetMarkerSize(0);
  errorBand  ->SetFillColor(1);
  errorBand  ->SetFillStyle(3013);
  errorBand  ->SetLineWidth(1);
  for(int idx=0; idx<errorBand->GetNbinsX(); ++idx){
    if(errorBand->GetBinContent(idx)>0){
      std::cout << "Uncertainties on summed background samples: " << errorBand->GetBinError(idx)/errorBand->GetBinContent(idx) << std::endl;
      break;
    }
  }
  DYS120  ->Draw("histsame");
  DYB->Draw("histsame");
  TT->Draw("histsame");
  W->Draw("histsame");
  QCD->Draw("histsame");
    $DRAW_ERROR
  data->Draw("esame");
  canv->RedrawAxis();

  CMSPrelim(dataset, "", 0.16, 0.835);  
  TPaveText* chan     = new TPaveText(0.20, 0.74+0.061, 0.32, 0.74+0.161, "NDC");
  chan->SetBorderSize(   0 );
  chan->SetFillStyle(    0 );
  chan->SetTextAlign(   12 );
  chan->SetTextSize ( 0.05 );
  chan->SetTextColor(    1 );
  chan->SetTextFont (   62 );
  //chan->AddText("e#mu");
  chan->Draw();


  TLegend* leg = new TLegend(0.55, 0.58, 0.92, 0.90);
  SetLegendStyle(leg);
  leg->AddEntry(data , "Observed"                       , "LP");
  leg->AddEntry(DYS120, "Z#rightarrow #tau_{h}#tau_{#mu}"                   , "F" );
  leg->AddEntry(DYB, "DY others"                            , "F" );
  leg->AddEntry(TT  , "t#bar{t}"                    , "F" );
  leg->AddEntry(W, "W + jets"                       , "F" );
  leg->AddEntry(QCD  , "QCD"           , "F" );
  $ERROR_LEGEND
  leg->Draw();


  /*
    Ratio Data over MC
  */
  TCanvas *canv0 = MakeCanvas("canv0", "histograms", 600, 400);
  canv0->SetGridx();
  canv0->SetGridy();
  canv0->cd();

  TH1F* zero = (TH1F*)ref ->Clone("zero"); zero->Clear();
  TH1F* rat1 = (TH1F*)data->Clone("rat"); 
  rat1->Divide(DYS120);
  for(int ibin=0; ibin<rat1->GetNbinsX(); ++ibin){
    if(rat1->GetBinContent(ibin+1)>0){
      // catch cases of 0 bins, which would lead to 0-alpha*0-1
      rat1->SetBinContent(ibin+1, rat1->GetBinContent(ibin+1)-1.);
    }
    zero->SetBinContent(ibin+1, 0.);
  }
  rat1->SetLineColor(kBlack);
  rat1->SetFillColor(kGray );
  rat1->SetMaximum(+0.3);
  rat1->SetMinimum(-0.3);
  rat1->GetYaxis()->CenterTitle();
  rat1->GetYaxis()->SetTitle("#bf{#frac{Data-Simulation}{Simulation}}");
  rat1->GetXaxis()->SetTitle("#bf{m_{vis} (GeV)}");	
  rat1->GetXaxis()->SetTitleOffset(2.8);
  rat1->GetYaxis()->SetTitleOffset(2.8);
  rat1->GetXaxis()->SetTitleSize(30);
  rat1->GetYaxis()->SetTitleSize(20);
  rat1->GetXaxis()->SetLabelSize(0.1);
  rat1->GetYaxis()->SetLabelSize(0.1);
  rat1->Draw();
  zero->SetLineColor(kBlack);
  zero->Draw("same");
  canv0->RedrawAxis();

  TCanvas* canvasPost   = new TCanvas("ccPost", "ccPost",600,800);
  
  TPad*    upperPadPost = new TPad("upperPadPost", "upperPadPost",
                               .005, .1505, .995, .995);
  TPad*    lowerPadPost = new TPad("lowerPadPost", "lowerPadPost",
                               .005, .008, .995, .2475);
  //data->Draw(""); 
  lowerPadPost->SetBottomMargin(0.3);
  lowerPadPost->SetLeftMargin(0.18);
  upperPadPost->SetLeftMargin(0.18);
  upperPadPost->Draw();lowerPadPost->Draw();
  upperPadPost->cd();
  
  data->GetYaxis()->SetTitleOffset(2.2);
  data->GetYaxis()->SetTitleSize(30);
  data->GetYaxis()->SetLabelSize(0.03);
  data->SetName("Data");
  QCD->SetName("A");
  TT->SetName("B");
  W->SetName("C");
  DYS120->SetName("D");
  DYB->SetName("E");
  errorBand->SetName("F");
  zero->SetName("G");
  data->Draw("e");
  DYS120->Draw("histsame");
  DYB->Draw("histsame");
  TT->Draw("histsame");
  W->Draw("histsame");
  QCD->Draw("histsame");
    $DRAW_ERROR
  data->Draw("esame");
  leg->Draw("same");
  CMSPrelim(dataset, "", 0.16, 0.835);
  upperPadPost->RedrawAxis();
  lowerPadPost->cd();
  rat1->SetLabelSize(0.12);
  rat1->GetXaxis()->SetTitleOffset(3.5);
  rat1->Draw();
  zero->Draw("same");
  canvasPost->Update();

  /*
    prepare output
  */
  bool isFourteenTeV = std::string(inputfile).find("14TeV")!=std::string::npos;
  canvasPost->Print(TString::Format("tauid_%s_datamc_%sscaled_%s_%sPost.png", directory, scaled ? "re" : "un", isFourteenTeV ? "14TeV" : "13TeV", log ? "LOG" : "")); 
  canvasPost->Print(TString::Format("tauid_%s_datamc_%sscaled_%s_%sPost.pdf", directory, scaled ? "re" : "un", isFourteenTeV ? "14TeV" : "13TeV", log ? "LOG" : ""));
  canvasPost->SaveSource(TString::Format("tauid_%s_datamc_%sscaled_%sPost.C", directory, scaled ? "re" : "un", isFourteenTeV ? "14TeV" : "13TeV"));
  canvasPost->Print(TString::Format("tauid_%s_datamc_%sscaled_%sPost.root", directory, scaled ? "re" : "un", isFourteenTeV ? "14TeV" : "13TeV"));
  canvas->Print(TString::Format("tauid_%s_datamc_%sscaled_%s_%s.png", directory, scaled ? "re" : "un", isFourteenTeV ? "14TeV" : "13TeV", log ? "LOG" : ""));
  canvas->Print(TString::Format("tauid_%s_datamc_%sscaled_%s_%s.pdf", directory, scaled ? "re" : "un", isFourteenTeV ? "14TeV" : "13TeV", log ? "LOG" : ""));
}
