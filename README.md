# Wireguard WOL Relay

This script will relay WOL packets from a Wireguard VPN server's subnet to the subnet network that the VPN server is connected to. The default port to sniff for WOL packets is set to 9, but can be changed in the `wg_wol_relay.py` script if needed.

Typically building the exectuable is done on the VPN server itself, but one can run the steps below on another system, copy the executable over to the VPN server, and then create the service file as they see fit.

## Requirements

1. The VPN server (or device building this executable) needs to have the following installed:

    `build-essential python3 pip`

    * `python3.9` is prefered; versions newer than this will potentially still work
2. **Traffic from the Wireguard server must be able to forward traffic to the local lan/wan**. 
    * A configuration similar to below is needed in your Wireguard server's configuration. This example is allowing all traffic on the Wireguard interface (wg0) to forward traffic to an ethernet interface (eth0) and sets the appropriate rules in UFW to allow this traffic through the firewall (if UFW is used):

        ```
        PostUp = ufw route allow in on wg0 out on eth0
        PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -I POSTROUTING -o eth0 -j MASQUERADE
        PreDown = ufw route delete allow in on wg0 out on eth0
        PreDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
        ```
3. If using `sudo make install` below, the VPN server needs to use `systemd` for the installation script to execute correctly

## Install

1. Clone this repository to the VPN server
2. Run `make build`

    * This will use the systems current `python3` version; if there is any build issues, it is recommended to use `make build VERSIONED=true` to build the executable from `python3.9` and use the version locked pip dependencies from `requirements-3.9.txt`

3. Run `sudo make install`

The executable should now be running and will start on a reboot.

## Uninstall

1. Navigate to this repository on the VPN server
2. Run `sudo make uninstall`

This will stop the service, disable and remove it, and uninstall the executable from the ssytem.

## Debugging

To debug the service, check the system log on the VPN server for the service `wg_wol_relay`