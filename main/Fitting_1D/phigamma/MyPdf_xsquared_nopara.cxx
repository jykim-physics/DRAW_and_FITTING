/***************************************************************************** 
 * Project: RooFit                                                           * 
 *                                                                           * 
 * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/ 

// Your description goes here... 

#include "Riostream.h" 

#include "MyPdf_xsquared_nopara.h" 
#include "RooAbsReal.h" 
#include "RooAbsCategory.h" 
#include <math.h> 
#include "TMath.h" 

ClassImp(MyPdf_xsquared_nopara); 

 MyPdf_xsquared_nopara::MyPdf_xsquared_nopara(const char *name, const char *title, 
                        RooAbsReal& _x) :
   RooAbsPdf(name,title), 
   x("x","x",this,_x)
 { 
 } 


 MyPdf_xsquared_nopara::MyPdf_xsquared_nopara(const MyPdf_xsquared_nopara& other, const char* name) :  
   RooAbsPdf(other,name), 
   x("x",this,other.x)
 { 
 } 



 Double_t MyPdf_xsquared_nopara::evaluate() const 
 { 
   // ENTER EXPRESSION IN TERMS OF VARIABLE ARGUMENTS HERE 
   return x*x ; 
 } 



