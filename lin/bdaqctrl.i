%module bdaqctrl
%include <typemaps.i>
%include "carrays.i"
%include <python/cwstring.i>

%array_class(unsigned char, UCharArray)

%{
#include "bdaqctrl.h"
%}

%include "bdaqctrl.h"
