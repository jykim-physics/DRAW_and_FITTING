//
// Belle2 Style
//

#include <cstdio>

#include "Belle2Style.h"

#include "TROOT.h"

void SetBelle2Style ()
{
  static TStyle* belle2Style = 0;
  printf("\nApplying BELLE2 style settings...\n");
  if ( belle2Style==0 ) belle2Style = Belle2Style();
  gROOT->SetStyle("BELLE2");
  gROOT->ForceStyle();
}

TStyle* Belle2Style() 
{
  TStyle *belle2Style = new TStyle("BELLE2","Belle2 style");

  // use plain black on white colors
  Int_t icol=0; // WHITE
  belle2Style->SetFrameBorderMode(icol);
  belle2Style->SetFrameFillColor(icol);
  belle2Style->SetCanvasBorderMode(icol);
  belle2Style->SetCanvasColor(icol);
  belle2Style->SetPadBorderMode(icol);
  belle2Style->SetPadColor(icol);
  belle2Style->SetStatColor(icol);
  //belle2Style->SetFillColor(icol); // don't use: white fill color for *all* objects

  // set the paper & margin sizes
  belle2Style->SetPaperSize(20,26);

  // set margin sizes
  belle2Style->SetPadTopMargin(0.05);
  belle2Style->SetPadRightMargin(0.05);
  belle2Style->SetPadBottomMargin(0.16);
  belle2Style->SetPadLeftMargin(0.16);

  // set title offsets (for axis label)
  belle2Style->SetTitleXOffset(1.0);
  belle2Style->SetTitleYOffset(1.0);

  // use large fonts
  //Int_t font=72; // Helvetica italics
  Int_t font=42; // Helvetica
  Double_t tsize=0.05;  
  belle2Style->SetTextFont(font);
  belle2Style->SetTextSize(tsize);
    
  belle2Style->SetLabelFont(font,"x");
  belle2Style->SetTitleFont(font,"x");
  belle2Style->SetLabelFont(font,"y");
  belle2Style->SetTitleFont(font,"y");
  belle2Style->SetLabelFont(font,"z");
  belle2Style->SetTitleFont(font,"z");
  
  belle2Style->SetLabelSize(tsize,"x");
  belle2Style->SetTitleSize(.065,"x");
  belle2Style->SetLabelSize(tsize,"y");
  belle2Style->SetTitleSize(.065,"y");
  belle2Style->SetLabelSize(tsize,"z");
  belle2Style->SetTitleSize(.065,"z");
    
  belle2Style->SetTitleOffset(1.1,"x");
  belle2Style->SetTitleOffset(1.1,"y");
  belle2Style->SetTitleOffset(1.1,"z");

  belle2Style->SetLabelOffset(0.015,"x");
  belle2Style->SetLabelOffset(0.015,"y");
  belle2Style->SetLabelOffset(0.015,"z");

    
  belle2Style->SetTickLength(0.03,"x");
  belle2Style->SetTickLength(0.02,"y");  // This way we slighty achive equal length ticks for x and y

  // use bold lines and markers
  belle2Style->SetMarkerStyle(20);
  belle2Style->SetMarkerSize(0.9);
  belle2Style->SetHistLineWidth(2);
  belle2Style->SetLineStyleString(2,"[12 12]"); // postscript dashes

  // get rid of X error bars 
  belle2Style->SetErrorX(0.001);
  // get rid of error bar caps
  belle2Style->SetEndErrorSize(0.);

  // do not display any of the standard histogram decorations
  belle2Style->SetOptTitle(0);
  //belle2Style->SetOptStat(1111);
  belle2Style->SetOptStat(0);
  //belle2Style->SetOptFit(1111);
  belle2Style->SetOptFit(0);

  // put tick marks on top and RHS of plots
  belle2Style->SetPadTickX(0);
  belle2Style->SetPadTickY(0);

  belle2Style->SetFrameLineWidth(2);
    
  return belle2Style;

}


