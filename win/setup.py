import distutils
from distutils.core import setup, Extension

setup(
    name = "Advantech-DAQNavi-bdaqctrl-lib",
    version = "0.01",
    ext_modules = [Extension(
        "_bdaqctrl",
        ["bdaqctrl.i","bdaqctrl.cpp"],
        swig_opts=['-py3', "-D_BDAQ_C_INTERFACE", "-DWIN32", "-Wall", '-module','bdaqctrl'],  # '-c++',
    )]
)
