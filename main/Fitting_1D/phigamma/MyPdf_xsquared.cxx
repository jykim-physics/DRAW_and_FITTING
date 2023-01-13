/***************************************************************************** 
 * Project: RooFit                                                           * 
 *                                                                           * 
 * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/ 

// Your description goes here... 

#include "Riostream.h" 

#include "MyPdf_xsquared.h" 
#include "RooAbsReal.h" 
#include "RooAbsCategory.h" 
#include <math.h> 
#include "TMath.h" 

ClassImp(MyPdf_xsquared); 

 MyPdf_xsquared::MyPdf_xsquared(const char *name, const char *title, 
                        RooAbsReal& _x,
                        RooAbsReal& _c0) :
   RooAbsPdf(name,title), 
   x("x","x",this,_x),
   c0("c0","c0",this,_c0)
 { 
 } 


 MyPdf_xsquared::MyPdf_xsquared(const MyPdf_xsquared& other, const char* name) :  
   RooAbsPdf(other,name), 
   x("x",this,other.x),
   c0("c0",this,other.c0)
 { 
 } 



 Double_t MyPdf_xsquared::evaluate() const 
 { 
   // ENTER EXPRESSION IN TERMS OF VARIABLE ARGUMENTS HERE 
   return c0*x*x ; 
 } 



