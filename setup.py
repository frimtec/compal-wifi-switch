""" Set up script """
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(here, "README.md"), "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name="compal-wifi-switch",
    version="0.1.1",
    author="Markus Friedli",
    author_email="frimtec@gmx.ch",
    description="CLI tool to switch on/off the wifi module of a Compal cabelmodem (CH7465LG/Ziggo Connect Box)",
    long_description_content_type="text/markdown",
    long_description=long_descr,
    url="https://github.com/frimtec/compal-wifi-switch",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'compal-wifi-switch=compal_wifi_switch.main:main',
        ],
    },
    install_requires=["compal"],
    include_package_data=True,
    python_requires=">=3.7",
    license="Apache 2",
    keywords="compal CH7465LG connect box cablemodem wifi switch",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
    zip_safe=True
)
