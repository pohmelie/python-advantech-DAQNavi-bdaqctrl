from cffi import FFI


ffi = FFI()
with open("_bdaqctrl.h") as fin:

    ffi.cdef(fin.read())

bdaqctrl = ffi.dlopen("libbiodaq.so")
info = ffi.new("DeviceInformation *")
info.Description = "PCI-1756, BID#0"
di = bdaqctrl.AdxInstantDiCtrlCreate()
do = bdaqctrl.AdxInstantDoCtrlCreate()

assert bdaqctrl.Success == bdaqctrl.InstantDiCtrl_setSelectedDevice(di, info)
assert bdaqctrl.Success == bdaqctrl.InstantDoCtrl_setSelectedDevice(do, info)
print(bdaqctrl.InstantDiCtrl_getPortCount(di))
print(bdaqctrl.InstantDoCtrl_getPortCount(do))
