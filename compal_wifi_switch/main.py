import argparse
import os

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


def status(args):
    modem = Compal(args.host, args.password)
    modem.login()
    wifi_settings = WifiSettings(modem).wifi_settings
    wifi_band_settings = [wifi_settings.radio_2g, wifi_settings.radio_5g]
    print("====================================================")
    print(" WIFI BANDS")
    print("====================================================")
    print(" State Band Hidden SSID")
    print(" ----- ---- ------ ----------------")
    for wifi_band in wifi_band_settings:
        print(f" {('ON' if wifi_band.bss_enable == 1 else 'OFF'):5} {wifi_band.radio:4} "
              f"{('ON' if wifi_band.hidden == 1 else 'OFF'):6} {wifi_band.ssid}")
    print()

    wifi_guest_network_settings = WifiGuestNetworkSettings(modem).wifi_guest_network_settings
    guest_network_interfaces = []
    guest_network_interfaces += wifi_guest_network_settings.guest_networks_2g
    guest_network_interfaces += wifi_guest_network_settings.guest_networks_5g
    print("====================================================")
    print(" WIFI GUEST NETWORKS")
    print("====================================================")
    print(" State Band MAC               Hidden SSID")
    print(" ----- ---- ----------------- ------ ----------------")
    for interface in guest_network_interfaces:
        if interface.ssid is not None or args.verbose:
            print(f" {('ON' if interface.enable == 1 else 'OFF'):5} {interface.radio:4} "
                  f"{interface.guest_mac} {('ON' if interface.hidden == 1 else 'OFF'):6} {interface.ssid}")
    modem.logout()


def switch(args):
    state = args.state
    band = args.band
    guest_networks = args.guest
    enable_guest_networks = len(guest_networks) > 0
    if enable_guest_networks:
        if switch == Switch.OFF:
            print('Argument guest (--guest, -g) not allowed for switch OFF action!')
            exit(1)

    modem = Compal(args.host, args.password)
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
    print(f"Switching wifi {state.name} (band = {band})")

    if band == Band.BAND_2G or band == Band.ALL:
        settings.radio_2g.bss_enable = 1 if state == Switch.ON else 2

    if band == Band.BAND_5G or band == Band.ALL:
        settings.radio_5g.bss_enable = 1 if state == Switch.ON else 2

    if state == Switch.ON:
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

    wifi.update_wifi_settings(settings, args.verbose)

    indexes_to_enable = set()
    for index, guest_band in guest_network_interfaces_to_enable:
        interface = guest_settings_for_band(guest_settings, guest_band)[index]
        print(f"Activating guest networks {interface.guest_mac}")
        interface.enable = 1
        indexes_to_enable.add(index)

    for index in indexes_to_enable:
        wifi_guest_network.update_interface_guest_network_settings(guest_settings, index, args.verbose)

    modem.logout()


def add_modem_arguments(parser):
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
    parser.add_argument('--verbose', action='store_true', help="verbose logging")


def main():
    parser = argparse.ArgumentParser(description="Compal-Wifi-Switch configuration")
    parser.add_argument('--version', '-v', action='version',
                        version='%(prog)s v' + pkg_resources.get_distribution('compal_wifi_switch').version)
    subparsers = parser.add_subparsers(title='command')
    status_parser = subparsers.add_parser('status', help='shows the current status of the cablemodem')
    status_parser.add_argument('status', action='store_true')
    add_modem_arguments(status_parser)
    status_parser.set_defaults(func=status)

    switch_parser = subparsers.add_parser('switch', help='switches the wifi state of the cabelmodem')
    switch_parser.add_argument('switch', action='store_true')
    switch_parser.add_argument('state', type=Switch, choices=list(Switch))
    switch_parser.add_argument('--band', '-b',
                               type=Band,
                               choices=list(Band),
                               default="all",
                               help="band to switch power state for (default = all)")
    switch_parser.add_argument('--guest', '-g',
                               type=str,
                               nargs='*',
                               help="list of guest network mac-addresses to activate while switching ON wifi")
    add_modem_arguments(switch_parser)
    switch_parser.set_defaults(func=switch)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
