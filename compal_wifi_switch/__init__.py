import enum

import time
from compal import (Compal, WifiSettings, WifiGuestNetworkSettings, GetFunction)
from lxml import etree


class Band(enum.Enum):
    BAND_2G = '2g'
    BAND_5G = '5g'
    ALL = 'all'

    def __str__(self):
        return self.value


class Format(enum.Enum):
    JSON = 'json'
    TEXT = 'text'

    def __str__(self):
        return self.value


class Switch(enum.Enum):
    ON = 'on'
    OFF = 'off'

    def __str__(self):
        return self.value


class Commands:

    @staticmethod
    def __guest_settings_for_band(guest_settings, band):
        if band == Band.BAND_2G:
            return guest_settings.guest_networks_2g
        else:
            return guest_settings.guest_networks_5g

    @staticmethod
    def __find_guest_network(guest_settings, band_selection, mac):

        def find_in_band(band):
            i = 0
            interfaces = Commands.__guest_settings_for_band(guest_settings, band)
            while i < len(interfaces):
                if interfaces[i].guest_mac == mac:
                    return i, band
                i += 1
            return None

        found_entry = None if band_selection == Band.BAND_5G else find_in_band(Band.BAND_2G)
        if found_entry is None:
            found_entry = None if band_selection == Band.BAND_2G else find_in_band(Band.BAND_5G)

        return found_entry

    @staticmethod
    def status(host, password):
        modem = Compal(host, password)
        modem.login()

        parser = etree.XMLParser(recover=True)
        global_settings = etree.fromstring(modem.xml_getter(GetFunction.GLOBALSETTINGS, {}).content, parser=parser)
        system_info = etree.fromstring(modem.xml_getter(GetFunction.CM_SYSTEM_INFO, {}).content, parser=parser)

        modem_status = {
            'model': global_settings.find('ConfigVenderModel').text,
            'hw_version': system_info.find('cm_hardware_version').text,
            'sw_version': global_settings.find('SwVersion').text,
            'cm_serial_number': system_info.find('cm_serial_number').text,
            'cm_mac_addr': system_info.find('cm_mac_addr').text,
            'operator_id': global_settings.find('OperatorId').text,
            'network_mode': global_settings.find('GwProvisionMode').text,
            'uptime': system_info.find('cm_system_uptime').text
        }

        wifi_settings = WifiSettings(modem).wifi_settings
        wifi_band_settings = [wifi_settings.radio_2g, wifi_settings.radio_5g]

        wifi_status = []
        for wifi_band in wifi_band_settings:
            wifi_band = {
                'radio': wifi_band.radio,
                'enabled': wifi_band.bss_enable == 1,
                'ssid': wifi_band.ssid,
                'hidden': wifi_band.hidden == 1
            }
            wifi_status.append(wifi_band)

        wifi_guest_network_settings = WifiGuestNetworkSettings(modem).wifi_guest_network_settings
        guest_network_interfaces = []
        guest_network_interfaces += wifi_guest_network_settings.guest_networks_2g
        guest_network_interfaces += wifi_guest_network_settings.guest_networks_5g

        wifi_guest_status = []
        for interface in guest_network_interfaces:
            entry = {
                'radio': interface.radio,
                'enabled': interface.enable == 1,
                'mac': interface.guest_mac,
                'ssid': interface.ssid,
                'hidden': interface.hidden == 1 == 1
            }
            wifi_guest_status.append(entry)
        modem.logout()

        return {
            'modem': modem_status,
            'wifi': wifi_status,
            'wifi_guest': wifi_guest_status
        }

    @staticmethod
    def switch(host, password, state, band, guest, pause, verbose=False):
        guest_networks = guest
        enable_guest_networks = len(guest_networks) > 0
        if enable_guest_networks:
            if state == Switch.OFF:
                raise ValueError('Argument guest (--guest, -g) not allowed for switch OFF action!')

        modem = Compal(host, password)
        modem.login()

        wifi_guest_network = WifiGuestNetworkSettings(modem)
        guest_settings = wifi_guest_network.wifi_guest_network_settings

        not_found_guest_networks = []
        guest_network_interfaces_to_enable = []
        for guest_network in guest_networks:
            found_interface = Commands.__find_guest_network(guest_settings, band, guest_network)
            if found_interface is None:
                not_found_guest_networks.append(guest_network)
            else:
                guest_network_interfaces_to_enable.append(found_interface)

        if len(not_found_guest_networks) > 0:
            raise ValueError(f"Guest network mac-addresses {not_found_guest_networks} not found for selected band {band}!")

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
                interface = Commands.__guest_settings_for_band(guest_settings, guest_band)[index]
                print(f"Activating guest networks {interface.guest_mac}")
                interface.enable = 1
                indexes_to_enable.add(index)

            for index in indexes_to_enable:
                wifi_guest_network.update_interface_guest_network_settings(guest_settings, index, verbose)

            modem.logout()

        print("Finished.")
