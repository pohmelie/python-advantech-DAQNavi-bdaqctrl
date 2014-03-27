%module bdaqctrl

%typemap(in) HANDLE {
    $1 = (void *)(PyInt_AsLong($input));
}

%typemap(out) HANDLE {
    $result = PyInt_FromLong((int)($1));
}

%{
#include "bdaqctrl.h"
%}

%include <windows.i>
%include "bdaqctrl.h"
