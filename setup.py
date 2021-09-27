import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="mpl_flow",
    version="1.0.0",
    description="Draw flowcharts and more with matplotlib",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Marco Necci",
    license="MIT License",
    install_requires=["matplotlib", "numpy"],
    py_modules=['mpl_flow'],
)

