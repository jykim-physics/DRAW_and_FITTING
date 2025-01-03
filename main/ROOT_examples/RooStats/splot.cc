//
// This is a simple ROOT example showing how to make an sPlot using RooStats and RooFit.
// The method for making sPlots is described in the paper by Pvik and De Liberder, 
// Nucl. Instrum. Meth. A555 356 (2005) [arXiv:physics/0402083] and following the usage
// conventions intruduced by the authors to the BaBar Collaboration.
//
// The fit model used is a one dimensional fit to some variable x, where the signal
// is denoted by index 1 and background by index 2 in the variable names.  Both
// categories of event are described by Gaussian distribtuions.  The categories are
// also described by the distribtuions y.
//
// In this case y is not used in the fit in order to make sPlots of y.  Likewise x is not
// used in the fit when making sPlots of x.  This way the reweighting of events is done 
// exluding the variable being projected.  Any discrepancy between the reweighted data 
// and PDF would indicate a flaw in the assumed likelihood model (for example a missing 
// background).  It is for this reason that we do not include information for both x and
// y in the liklihood when making splots.
//
// Adrian Bevan, Queen Mary University of London (2015)
//=======================================================================================
using namespace RooStats;

void splot() {
  gSystem->Load("libRooFit");
  gSystem->Load("libRooStats.so");

  RooRealVar x("x", "x", -10.0, 10.0);
  RooRealVar y("y", "y", -10.0, 10.0);

  // declare the signal and background shapes and parameters for the 
  // x and y pdfs.  Signal is denoted by 1, background by 2.
  RooRealVar muX1("muX1", "", -3.0);
  RooRealVar muX2("muX2", "", 5.0);
  RooRealVar sX1("sX1", "", 2.0);
  RooRealVar sX2("sX2", "", 2.0);

  RooRealVar muY1("muY1", "", -3.0);
  RooRealVar muY2("muY2", "", 3.0);
  RooRealVar sY1("sY1", "", 2.0);
  RooRealVar sY2("sY2", "", 10.0);

  RooGaussian gx1("gx1", "", x, muX1, sX1);
  RooGaussian gx2("gx2", "", x, muX2, sX2);
  RooGaussian gy1("gy1", "", y, muY1, sY1);
  RooGaussian gy2("gy2", "", y, muY2, sY2);

  // make the total PDF (used for toy Monte Carlo simulated data generation).
  RooProdPdf signal("signal", "", gx1, gy1);
  RooProdPdf bg("bg", "", gx2, gy2);

  // define event yields
  RooRealVar nSig("nSig", "", 1000., 0.0, 10000);
  RooRealVar nBG("nBG", "", 2000., 0.0, 10000);

  // construct the total PDF and the corresponding PDFS for x and y only.
  RooAddPdf totalPdf("totalPdf", "", RooArgList(signal, bg), RooArgList(nSig, nBG));
  RooAddPdf xPdf("xPdf", "", RooArgList(gx1, gx2), RooArgList(nSig, nBG));
  RooAddPdf yPdf("yPdf", "", RooArgList(gy1, gy2), RooArgList(nSig, nBG));

  // generate a sample of data to fit to and extract xplots from.
  RooDataSet * data = totalPdf.generate(RooArgList(x,y), nSig->getVal() + nBG->getVal() );
  data->SetName("data");
  data->Print("v");

  //============================================================================
  // First fit the total mode, and having done that project out the total PDF and 
  // background as one would do usually.  This provides a benchmark for reference.
  //============================================================================
  totalPdf.fitTo(*data, "etrm");
  RooPlot *frame_x = x.frame(20);
  RooPlot *frame_y = y.frame(20);
  data.plotOn(frame_x);
  totalPdf.plotOn(frame_x);
  totalPdf->plotOn(frame_x,  RooFit::LineColor(kRed),  RooFit::LineStyle(kDashed), RooFit::Components(bg.GetName()) );

  data.plotOn(frame_y);
  totalPdf.plotOn(frame_y);
  totalPdf->plotOn(frame_y,  RooFit::LineColor(kRed),  RooFit::LineStyle(kDashed), RooFit::Components(bg.GetName()) );

  TCanvas can("can", "");
  can.Divide(1,2);
  can.cd(1);
  frame_x.Draw();
  can.cd(2);
  frame_y.Draw();
  can.Print("projectionPlots.pdf");



  //============================================================================
  // Fit the data for x in order to make splots of y
  //============================================================================
  RooFitResult * r = (RooFitResult*)xPdf.fitTo(*data, "etrm", RooFit::Save());
  r->Print("v");

  // Create the sPlot data from the fit to x.  The sweights computed here are valid for plotting y
  RooStats::SPlot* sDataX = new RooStats::SPlot("sData","An SPlot", *data, &xPdf, RooArgList(nSig, nBG) );
  std::cout << std::endl <<  "Yield of signal is " << nSig.getVal() << ".  From sWeights it is " << sDataX->GetYieldFromSWeight("nSig") << std::endl;
  std::cout << "Yield of background is " << nBG.getVal() << ".  From sWeights it is " << sDataX->GetYieldFromSWeight("nBG") << std::endl << std::endl;

  // create weighted data sets
  RooDataSet * dataw_sig = new RooDataSet(data->GetName(),data->GetTitle(),data,*data->get(),0,"nSig_sw") ;
  RooDataSet * dataw_bg  = new RooDataSet(data->GetName(),data->GetTitle(),data,*data->get(),0,"nBG_sw") ;

  std::cout << "Making splots of the signal and background" << std::endl;
  RooPlot* frame_sig_y = y.frame(20) ;
  frame_sig_y->SetTitle("sPlot for the signal y distribution");
  dataw_sig->plotOn(frame_sig_y, RooFit::DataError(RooAbsData::SumW2) ) ;

  RooPlot* frame_bg_y = y.frame(20) ;
  frame_bg_y->SetTitle("sPlot for the background y distribtuion");
  dataw_bg->plotOn(frame_bg_y, RooFit::DataError(RooAbsData::SumW2) ) ;

  // plot PDFs onto the sPlots; if the sPlot correctly reweights the data then the signal / background only shapes should
  // provide an adequate description of the data.
  gy1.plotOn(frame_sig_y);
  gy2.plotOn(frame_bg_y);

  can.cd(1);
  frame_sig_y->Draw();
  can.cd(2);
  frame_bg_y->Draw();
  can.Print("splot_y.pdf");



  //============================================================================
  // Fit the data for x in order to make splots of y
  //============================================================================
  RooFitResult * ry = (RooFitResult*)yPdf.fitTo(*data, "etrm", RooFit::Save());
  ry->Print("v");

  // Create the sPlot data from the fit to x.  The sweights computed here are valid for plotting y
  RooStats::SPlot* sDataY = new RooStats::SPlot("sData","An SPlot", *data, &yPdf, RooArgList(nSig, nBG) );
  std::cout << std::endl <<  "Yield of signal is " << nSig.getVal() << ".  From sWeights it is " << sDataY->GetYieldFromSWeight("nSig") << std::endl;
  std::cout << "Yield of background is " << nBG.getVal() << ".  From sWeights it is " << sDataY->GetYieldFromSWeight("nBG") << std::endl << std::endl;

  // create weighted data sets
  RooDataSet * dataw_sig = new RooDataSet(data->GetName(),data->GetTitle(),data,*data->get(),0,"nSig_sw") ;
  RooDataSet * dataw_bg  = new RooDataSet(data->GetName(),data->GetTitle(),data,*data->get(),0,"nBG_sw") ;

  std::cout << "Making splots of the signal and background" << std::endl;
  RooPlot* frame_sig_x = x.frame(20) ;
  frame_sig_x->SetTitle("sPlot for the signal x distribution");
  dataw_sig->plotOn(frame_sig_x, RooFit::DataError(RooAbsData::SumW2) ) ;

  RooPlot* frame_bg_x = x.frame(20) ;
  frame_bg_x->SetTitle("sPlot for the background x distribtuion");
  dataw_bg->plotOn(frame_bg_x, RooFit::DataError(RooAbsData::SumW2) ) ;

  // plot PDFs onto the sPlots; if the sPlot correctly reweights the data then the signal / background only shapes should
  // provide an adequate description of the data.
  gx1.plotOn(frame_sig_x);
  gx2.plotOn(frame_bg_x);

  can.cd(1);
  frame_sig_x->Draw();
  can.cd(2);
  frame_bg_x->Draw();
  can.Print("splot_x.pdf");

  std::cout << "splot.cc done" << std::endl;
}
