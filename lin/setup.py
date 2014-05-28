import distutils
from distutils.core import setup, Extension

setup(
    name = "Advantech-DAQNavi-bdaqctrl-lib",
    version = "0.01",
    ext_modules = [Extension(
        "_bdaqctrl",
        ["bdaqctrl.i","bdaqctrl.c"],
        swig_opts=["-py3", "-c++", "-module", "bdaqctrl"],  # "-D_BDAQ_C_INTERFACE"
        libraries=["biodaq"],
    )]
)
