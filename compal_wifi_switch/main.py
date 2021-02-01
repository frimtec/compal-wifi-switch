import argparse
import os

import pkg_resources

from compal_wifi_switch import (Switch, Band)

from .commands import Commands


def status(args):
    Commands.status(args.host, args.password, args.verbose)


def switch(args):
    Commands.switch(args.host, args.password, args.state, args.band, args.guest, args.pause, args.verbose)


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
                               default=[],
                               help="list of guest network mac-addresses to activate while switching ON wifi")
    switch_parser.add_argument('--pause', '-p',
                               type=int,
                               default=45,
                               help="number of seconds to pause after wifi state change (default = 45); "
                                    "when the pause is too short, the following modem commands may block forever")
    add_modem_arguments(switch_parser)
    switch_parser.set_defaults(func=switch)

    args = parser.parse_args()

    if args.host is None or args.password is None:
        print("ERROR: Missing value for HOST or PASSWORD arguments!")
        exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
