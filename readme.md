# python-advantech-DAQNavi-bdaqctrl
bdaqctrl driver for advantech boards for python. There is two versions of driver:
* swig-based
* CFFI-based

## swig-based
Pros:
* Python-native objects creation style
* `cpp` driver model (e.g. `obj.method()`)

Cons:
* Compilation
* Recompilation of driver for each major python version
* Swig — third language

Some instructions and binaries in `old` directory.

### [CFFI](https://cffi.readthedocs.io/en/latest/)
Pros:
* No compilation

Cons:
* c-style api
* «Hard» object creation (via `ffi.new("...")`)


1. Create `_bdaqctlr.h` from `bdaqctrl.h`. You don't need preprocessor to insert system headers, so comment `#  include <stdlib.h>` string and run:
   ```
   c99 -D_BDAQ_C_INTERFACE -E bdaqctrl.h > _bdaqctrl.h
   ```
   to produce header without preprocessor directives.

2. Use library as:
   ```python
   from cffi import FFI


   ffi = FFI()
   with open("_bdaqctrl.h") as fin:

       ffi.cdef(fin.read())

   bdaqctrl = ffi.dlopen("libbiodaq.so")
   info = ffi.new("DeviceInformation *")

   # don't forget to initialize whole structure
   info.Description = "PCI-1756, BID#0"
   info.DeviceNumber = -1
   info.DeviceMode = bdaqctrl.ModeWriteWithReset
   info.ModuleIndex = 0

   di = bdaqctrl.AdxInstantDiCtrlCreate()
   do = bdaqctrl.AdxInstantDoCtrlCreate()

   assert bdaqctrl.Success == bdaqctrl.InstantDiCtrl_setSelectedDevice(di, info)
   assert bdaqctrl.Success == bdaqctrl.InstantDoCtrl_setSelectedDevice(do, info)
   print(bdaqctrl.InstantDiCtrl_getPortCount(di))
   print(bdaqctrl.InstantDoCtrl_getPortCount(do))
   ```
