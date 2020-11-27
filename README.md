# Compal-Wifi-Switch
A command line tool to switch on/off the wifi sender of a Compal CH7465LG cablemodem.

Wifi radiation should be turned off if not used (better for your health and for IT security reasons). 
Unfortunattly the Compal CH7465LG cablemodem does not offer a physical button to switch on/off the wifi module.
There is also no configuration possible to switch the wifi module on/off based on a time schedule (e.g. switch off during night).

The compal-wifi-switch tool can switch wifi on/off via a command line interface. The tool can be installed on a server 
where Python runtime is available (NAS, Raspberry Pi, etc.). To schedule compal-wifi-switch you can use cron or any other 
scheduling mechanism.  

## Installation
1. Install python3.7 or higher
1. Install compal-wifi-switch via ```pip install compal-wifi-switch```.

## Usage
```
usage: compal-wifi-switch [-h] --host HOST --password PASSWORD --switch
                          {on,off} [--band {2g,5g,all}]

Compal-Wifi-Switch configuration

optional arguments:
  -h, --help           show this help message and exit
  --host HOST          host name or IP of compal cablemodem, or use env
                       variable COMPAL_WIFI_SWITCH_HOST
  --password PASSWORD  password of compal cablemodem, or use env variable
                       COMPAL_WIFI_SWITCH_PASSWORD
  --switch {on,off}    wifi power state to set
  --band {2g,5g,all}   band to switch power state for (default = all)
```

## Credits
* Using [compal_CH7465LG_py](https://github.com/ties/compal_CH7465LG_py) by [ties](https://github.com/ties/) to communicate with Compal cable modem.
