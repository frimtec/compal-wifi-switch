import argparse
import os
import json

import pkg_resources

from compal_wifi_switch import (Switch, Band, Commands, Format)


def status(args):
    status_object = Commands.status(args.host, args.password)
    if args.format == Format.JSON:
        print(json.dumps(status_object, indent=2))
    else:
        print("==============================================================")
        print(" Modem")
        print("==============================================================")
        print(f" {'Model' :20}: {status_object['modem']['model']}")
        print(f" {'HW Version' :20}: {status_object['modem']['hw_version']}")
        print(f" {'SW Version' :20}: {status_object['modem']['sw_version']}")
        print(f" {'Serial Number' :20}: {status_object['modem']['cm_serial_number']}")
        print(f" {'Modem MAC Address' :20}: {status_object['modem']['cm_mac_addr']}")
        print(f" {'Operator ID' :20}: {status_object['modem']['operator_id']}")
        print(f" {'Network Mode' :20}: {status_object['modem']['network_mode']}")
        print(f" {'Status' :20}: {status_object['modem']['status']}")
        print(f" {'Uptime' :20}: {status_object['modem']['uptime']}")
        print()
        print("==============================================================")
        print(" WIFI BANDS")
        print("==============================================================")
        print(" State Band Hidden SSID")
        print(" ----- ---- ------ ----------------")
        for wifi_band in status_object['wifi']:
            print(f" {('ON' if wifi_band['enabled'] else 'OFF'):5} {wifi_band['radio']:4} "
                  f"{('ON' if wifi_band['hidden'] else 'OFF'):6} {wifi_band['ssid']}")
        print()
        print("==============================================================")
        print(" WIFI GUEST NETWORKS")
        print("==============================================================")
        print(" State Band MAC               Hidden SSID")
        print(" ----- ---- ----------------- ------ ----------------")
        for interface in status_object['wifi_guest']:
            if interface['ssid'] is not None or args.verbose:
                print(f" {('ON' if interface['enabled'] else 'OFF'):5} {interface['radio']:4} "
                      f"{interface['mac']} {('ON' if interface['hidden'] else 'OFF'):6} {interface['ssid']}")
        print()
        print("==============================================================")
        print(" TELEPHONE LINES")
        print("==============================================================")
        print(" Number Provisioning Hook State")
        print(" ------ ------------ ---- ---------")
        for telephone_line in status_object['telephone_line']:
            print(f" {telephone_line['line_number']:6} {telephone_line['provisioning_state']:12} "
                  f"{'ON' if telephone_line['on_hook'] else 'OFF' :4} {telephone_line['mta_state']}")


def switch(args):
    Commands.switch(args.host, args.password, args.state, args.band, args.guest, args.pause, args.verbose)


def reboot(args):
    Commands.reboot(args.host, args.password)


def add_modem_arguments(parser):
    parser.add_argument('--host',
                        type=str,
                        default=os.environ.get("COMPAL_WIFI_SWITCH_HOST", None),
                        help="host name or IP of compal cablemodem, or use env variable COMPAL_WIFI_SWITCH_HOST")
    parser.add_argument('--password',
                        type=str,
                        default=os.environ.get("COMPAL_WIFI_SWITCH_PASSWORD", None),
                        help="password of compal cablemodem, or use env variable COMPAL_WIFI_SWITCH_PASSWORD")
    parser.add_argument('--verbose', action='store_true', help="verbose logging")


def main():
    parser = argparse.ArgumentParser(description="Compal-Wifi-Switch configuration")
    parser.add_argument('--version', '-v', action='version',
                        version='%(prog)s v' + pkg_resources.get_distribution('compal_wifi_switch').version)
    subparsers = parser.add_subparsers(title='command')
    status_parser = subparsers.add_parser('status', help='shows the current status of the cablemodem')
    status_parser.add_argument('status', action='store_true')
    status_parser.add_argument('--format', '-f',
                               type=Format,
                               choices=list(Format),
                               default="text",
                               help="output format")
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
    switch_parser.add_argument('--guest', '-g', action='store_true',
                               help="activate guest network while switching ON wifi")
    switch_parser.add_argument('--pause', '-p',
                               type=int,
                               default=60,
                               help="number of seconds to pause after wifi state change (default = 60); "
                                    "when the pause is too short, the following modem commands may block forever")
    add_modem_arguments(switch_parser)
    switch_parser.set_defaults(func=switch)

    reboot_parser = subparsers.add_parser('reboot', help='reboots the cabelmodem')
    reboot_parser.add_argument('reboot', action='store_true')
    add_modem_arguments(reboot_parser)
    reboot_parser.set_defaults(func=reboot)

    args = parser.parse_args()

    if args.host is None or args.password is None:
        raise ValueError('Missing value for HOST or PASSWORD arguments!')

    args.func(args)


if __name__ == "__main__":
    main()
