# !/bin/python3
# isort: skip_file
"""_summary_
"""

from setuptools import setup
from Cython.Build import cythonize

setup(
    name="nonideal_model", ext_modules=cythonize("nonideal_model.pyx"), zip_safe=False
)
