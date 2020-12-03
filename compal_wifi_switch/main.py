import argparse
import os
from typing import List

import pkg_resources

from compal import (Compal, WifiSettings, WifiGuestNetworkSettings)

from compal_wifi_switch import (Switch, Band)


def guest_settings_for_band(guest_settings, band):
    if band == Band.BAND_2G:
        return guest_settings.guest_networks_2g
    else:
        return guest_settings.guest_networks_5g


def find_guest_network(guest_settings, band_selection, mac):
    def find_in_band(band):
        i = 0
        interfaces = guest_settings_for_band(guest_settings, band)
        while i < len(interfaces):
            if interfaces[i].guest_mac == mac:
                return i, band
            i += 1
        return None

    found_entry = None if band_selection == Band.BAND_5G else find_in_band(Band.BAND_2G)
    if found_entry is None:
        found_entry = None if band_selection == Band.BAND_2G else find_in_band(Band.BAND_5G)

    return found_entry


def wifi_power(host: str, passwd: str, switch: Switch, band: Band, guest_networks: List[str], verbose: bool):
    enable_guest_networks = len(guest_networks) > 0
    if enable_guest_networks:
        if switch == Switch.OFF:
            print('Argument guest (--guest, -g) not allowed for switch OFF action!')
            exit(1)

    modem = Compal(host, passwd)
    modem.login()

    wifi_guest_network = WifiGuestNetworkSettings(modem)
    guest_settings = wifi_guest_network.wifi_guest_network_settings

    not_found_guest_networks = []
    guest_network_interfaces_to_enable = []
    for guest_network in guest_networks:
        found_interface = find_guest_network(guest_settings, band, guest_network)
        if found_interface is None:
            not_found_guest_networks.append(guest_network)
        else:
            guest_network_interfaces_to_enable.append(found_interface)

    if len(not_found_guest_networks) > 0:
        print(f"Guest network mac-addresses {not_found_guest_networks} not found for selected band {band}!")
        exit(1)

    wifi = WifiSettings(modem)
    settings = wifi.wifi_settings
    print(f"Switching wifi {switch.name} (band = {band})")

    if band == Band.BAND_2G or band == Band.ALL:
        settings.radio_2g.bss_enable = 1 if switch == Switch.ON else 2

    if band == Band.BAND_5G or band == Band.ALL:
        settings.radio_5g.bss_enable = 1 if switch == Switch.ON else 2

    if switch == Switch.ON:
        band_mode_mask_on = {
            Band.BAND_2G: 1,
            Band.BAND_5G: 2,
            Band.ALL: 3
        }
        settings.band_mode = (settings.band_mode & 3) | band_mode_mask_on.get(band, None)
    else:
        band_mode_mask_off = {
            Band.BAND_2G: 2,
            Band.BAND_5G: 1,
            Band.ALL: 0
        }
        new_mode = settings.band_mode & band_mode_mask_off.get(band, None)
        settings.band_mode = new_mode if new_mode != 0 else 4

    wifi.update_wifi_settings(settings, verbose)

    indexes_to_enable = set()
    for index, guest_band in guest_network_interfaces_to_enable:
        interface = guest_settings_for_band(guest_settings, guest_band)[index]
        print(f"Activating guest networks {interface.guest_mac}")
        interface.enable = 1
        indexes_to_enable.add(index)

    for index in indexes_to_enable:
        wifi_guest_network.update_interface_guest_network_settings(guest_settings, index, verbose)

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
    parser.add_argument('--guest', '-g',
                        type=str,
                        nargs='*',
                        help="list of guest network mac-addresses to activate while switching ON wifi")
    parser.add_argument('--version', '-v', action='version',
                        version='%(prog)s v' + pkg_resources.get_distribution('compal_wifi_switch').version)
    parser.add_argument('--verbose', action='store_true', help="verbose logging")

    args = parser.parse_args()

    wifi_power(args.host, args.password, args.switch, args.band, args.guest, args.verbose)


if __name__ == "__main__":
    main()
