import argparse
import os
import pkg_resources

from compal import (Compal, WifiSettings)

from compal_wifi_switch import (Switch, Band)


def wifi_power(host: str, passwd: str, switch: Switch, band: Band):
    modem = Compal(host, passwd)
    modem.login()

    wifi = WifiSettings(modem)
    settings = wifi.wifi_settings
    print('Switching wifi {} (band = {})'.format(switch.name, band))

    if band == Band.BAND_2G or band == Band.ALL:
        settings.radio_2g.bss_enable = 1 if switch == Switch.ON else 2

    if band == Band.BAND_5G or band == Band.ALL:
        settings.radio_5g.bss_enable = 1 if switch == Switch.ON else 2

    band_mode_mask = {
        Band.BAND_2G: 1,
        Band.BAND_5G: 2,
        Band.ALL: 3
    }

    if switch == Switch.ON:
        settings.band_mode = (settings.band_mode & 3) | band_mode_mask.get(band, None)
    else:
        new_mode = settings.band_mode ^ band_mode_mask.get(band, None)
        settings.band_mode = new_mode if new_mode != 0 else 4

    wifi.update_wifi_settings(settings)
    modem.logout()


def main():
    parser = argparse.ArgumentParser(description="Compal-Wifi-Switch configuration")
    parser.add_argument('--host',
                        type=str,
                        default=os.environ.get("COMPAL_WIFI_SWITCH_HOST", None),
                        required=True,
                        help="host name or IP of compal cablemodem, or use env variable COMPAL_WIFI_SWITCH_HOST")
    parser.add_argument('--password',
                        type=str,
                        default=os.environ.get("COMPAL_WIFI_SWITCH_PASSWORD", None),
                        required=True,
                        help="password of compal cablemodem, or use env variable COMPAL_WIFI_SWITCH_PASSWORD")
    parser.add_argument('--switch', '-s',
                        type=Switch,
                        choices=list(Switch),
                        required=True,
                        help="wifi power state to set")
    parser.add_argument('--band', '-b',
                        type=Band,
                        choices=list(Band),
                        default="all",
                        help="band to switch power state for (default = all)")
    parser.add_argument('--version', '-v', action='version',
                        version='%(prog)s v' + pkg_resources.get_distribution('compal_wifi_switch').version)
    args = parser.parse_args()

    wifi_power(args.host, args.password, args.switch, args.band)


if __name__ == "__main__":
    main()
