from lxml import etree
import time
from compal import (Compal, WifiSettings, WifiGuestNetworkSettings, GetFunction)
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


class Commands:

    @staticmethod
    def status(host, password, verbose=False):
        modem = Compal(host, password)
        modem.login()

        parser = etree.XMLParser(recover=True)
        global_settings = etree.fromstring(modem.xml_getter(GetFunction.GLOBALSETTINGS, {}).content, parser=parser)
        system_info = etree.fromstring(modem.xml_getter(GetFunction.CM_SYSTEM_INFO, {}).content, parser=parser)

        print("==============================================================")
        print(" Modem")
        print("==============================================================")
        print(f" {('Model'):20}: {global_settings.find('ConfigVenderModel').text}")
        print(f" {('HW Version'):20}: {system_info.find('cm_hardware_version').text}")
        print(f" {('SW Version'):20}: {global_settings.find('SwVersion').text}")
        print(f" {('Serial Number'):20}: {system_info.find('cm_serial_number').text}")
        print(f" {('Modem MAC Address'):20}: {system_info.find('cm_mac_addr').text}")
        print(f" {('Operator ID'):20}: {global_settings.find('OperatorId').text}")
        print(f" {('Network Mode'):20}: {global_settings.find('GwProvisionMode').text}")
        print(f" {('Uptime'):20}: {system_info.find('cm_system_uptime').text}")
        print()

        wifi_settings = WifiSettings(modem).wifi_settings
        wifi_band_settings = [wifi_settings.radio_2g, wifi_settings.radio_5g]
        print("==============================================================")
        print(" WIFI BANDS")
        print("==============================================================")
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
        print("==============================================================")
        print(" WIFI GUEST NETWORKS")
        print("==============================================================")
        print(" State Band MAC               Hidden SSID")
        print(" ----- ---- ----------------- ------ ----------------")
        for interface in guest_network_interfaces:
            if interface.ssid is not None or verbose:
                print(f" {('ON' if interface.enable == 1 else 'OFF'):5} {interface.radio:4} "
                      f"{interface.guest_mac} {('ON' if interface.hidden == 1 else 'OFF'):6} {interface.ssid}")
        modem.logout()

    @staticmethod
    def switch(host, password, state, band, guest, pause, verbose=False):
        guest_networks = guest
        enable_guest_networks = len(guest_networks) > 0
        if enable_guest_networks:
            if state == Switch.OFF:
                print('Argument guest (--guest, -g) not allowed for switch OFF action!')
                exit(1)

        modem = Compal(host, password)
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

        wifi.update_wifi_settings(settings, verbose)

        modem.logout()
        print(f"Wait {pause}s till wifi state is changed ...")
        time.sleep(pause)

        if enable_guest_networks:
            modem.login()
            wifi_guest_network = WifiGuestNetworkSettings(modem)
            guest_settings = wifi_guest_network.wifi_guest_network_settings

            indexes_to_enable = set()
            for index, guest_band in guest_network_interfaces_to_enable:
                interface = guest_settings_for_band(guest_settings, guest_band)[index]
                print(f"Activating guest networks {interface.guest_mac}")
                interface.enable = 1
                indexes_to_enable.add(index)

            for index in indexes_to_enable:
                wifi_guest_network.update_interface_guest_network_settings(guest_settings, index, verbose)

            modem.logout()

        print("Finished.")
