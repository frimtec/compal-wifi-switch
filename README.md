# Compal-Wifi-Switch
[![PyPI](https://img.shields.io/pypi/v/compal-wifi-switch.svg)](https://pypi.org/project/compal-wifi-switch/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/compal-wifi-switch.svg)](https://pypi.org/project/compal-wifi-switch/)
[![license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A command line tool to switch on/off the wifi sender of a Compal CH7465LG cablemodem.

Wifi radiation should be turned off if not used (better for your health and for IT security reasons). 
Unfortunattly the Compal CH7465LG cablemodem does not offer a physical button to switch on/off the wifi module.
There is also no configuration possible to switch the wifi module on/off based on a time schedule (e.g. switch off during night).

The compal-wifi-switch tool can switch wifi on/off via a command line interface. The tool can be installed on a server 
where Python runtime is available (NAS, Raspberry Pi, etc.). To schedule compal-wifi-switch you can use cron or any other 
scheduling mechanism.  

## Installation
### Using pip
1. Install python3.7 or higher
1. Install compal-wifi-switch with ```pip install compal-wifi-switch```.
1. Run compal-wifi-switch with ```compal-wifi-switch --help```.
### Without pip (e.g. on Synology DSM)
1. Download package from [PyPi](https://pypi.org/project/compal-wifi-switch/#files) (tar.gz) to your server.
1. Run the following commands:
```
# Install
user@dsm:~> tar xfv compal-wifi-switch-<version>.tar.gz
user@dsm:~> cd compal-wifi-switch-<version>
user@dsm:~/compal-wifi-switch> python3 setup.py install --user

# Run
user@dsm:~> python3 ~/compal-wifi-switch-<version>/compal_wifi_switch/main.py --help
```

## Usage
```
usage: compal-wifi-switch [-h] --host HOST --password PASSWORD --switch
                          {on,off} [--band {2g,5g,all}] [--version]

Compal-Wifi-Switch configuration

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           host name or IP of compal cablemodem, or use env
                        variable COMPAL_WIFI_SWITCH_HOST
  --password PASSWORD   password of compal cablemodem, or use env variable
                        COMPAL_WIFI_SWITCH_PASSWORD
  --switch {on,off}, -s {on,off}
                        wifi power state to set
  --band {2g,5g,all}, -b {2g,5g,all}
                        band to switch power state for (default = all)
  --version, -v         show program's version number and exit
```

## Credits
* Using [compal_CH7465LG_py](https://github.com/ties/compal_CH7465LG_py) by [ties](https://github.com/ties/) to communicate with Compal cable modem.
