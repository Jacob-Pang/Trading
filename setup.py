import os
import numpy as np

from glob import glob
from setuptools import Extension
from setuptools import setup, find_packages
from Cython.Build import cythonize
from os.path import basename, splitext

root_dpath = os.path.join(os.getcwd(), "src")
build_dpath = os.path.join(os.getcwd(), "build")

extensions = [
    Extension("src.trading.orderbook.orderbook", [
        os.path.join("src", "trading", "orderbook", "orderbook.pyx"),
        ]
    ),
    Extension("src.trading.tradebook.tradebook", [
        os.path.join("src", "trading", "tradebook", "tradebook.pyx"),
        ]
    ),
    Extension("src.trading.candle_buffer.candle_buffer", [
        os.path.join("src", "trading", "candle_buffer", "candle_buffer.pyx"),
        ], include_dirs=[
            root_dpath # Relative imports used
        ]
    ),
    Extension("src.trading.indicator.indicator", [
        os.path.join("src", "trading", "indicator", "indicator.pyx"),
        ]
    ),
    Extension("src.trading.market.cost_engine.cost_engine", [
        os.path.join("src", "trading", "market", "cost_engine", "cost_engine.pyx"),
        ]
    ),
]

setup(
    name="trading",
    version="1.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[
        splitext(basename(path))[0] for path in glob("src/*.py")
    ],
    include_package_data=True,
    ext_modules = cythonize(extensions, build_dir=build_dpath),
    include_dirs=[
        np.get_include()
    ]
)