import os
import numpy as np

from setuptools import Extension
from setuptools import setup
from Cython.Build import cythonize

root_dpath = os.path.join(os.getcwd(), "src")
build_dpath = os.path.join(os.getcwd(), "build")

extensions = [
    Extension("src.balances.balances", [
        os.path.join("src", "balances", "balances.pyx"),
        ]
    ),
    Extension("src.orderbook.orderbook", [
        os.path.join("src", "orderbook", "orderbook.pyx"),
        ]
    ),
    Extension("src.tradebook.tradebook", [
        os.path.join("src", "tradebook", "tradebook.pyx"),
        ]
    ),
    Extension("src.candle_buffer.candle_buffer", [
        os.path.join("src", "candle_buffer", "candle_buffer.pyx"),
        ], include_dirs=[
            root_dpath # Relative imports used
        ]
    ),
    Extension("src.indicator.indicator", [
        os.path.join("src", "indicator", "indicator.pyx"),
        ]
    ),
]

setup(
    ext_modules = cythonize(extensions, build_dir=build_dpath),
    include_dirs=[
        np.get_include()
    ]
)