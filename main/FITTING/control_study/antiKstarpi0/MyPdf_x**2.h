/*****************************************************************************
 * Project: RooFit                                                           *
 *                                                                           *
  * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/

#ifndef MYPDF_X**2
#define MYPDF_X**2

#include "RooAbsPdf.h"
#include "RooRealProxy.h"
#include "RooCategoryProxy.h"
#include "RooAbsReal.h"
#include "RooAbsCategory.h"
 
class MyPdf_x**2 : public RooAbsPdf {
public:
  MyPdf_x**2() {} ; 
  MyPdf_x**2(const char *name, const char *title,
	      RooAbsReal& _x);
  MyPdf_x**2(const MyPdf_x**2& other, const char* name=0) ;
  virtual TObject* clone(const char* newname) const { return new MyPdf_x**2(*this,newname); }
  inline virtual ~MyPdf_x**2() { }

protected:

  RooRealProxy x ;
  
  Double_t evaluate() const ;

private:

  ClassDef(MyPdf_x**2,1) // Your description goes here...
};
 
#endif