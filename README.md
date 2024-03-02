# WireGuard WOL Relay

This script will relay WOL packets from a WireGuard VPN server's subnet to the subnet network that the VPN server is connected to. The default port to sniff for WOL packets is set to 9, but can be changed in the `wg_wol_relay.py` script if needed.

Typically building the exectuable is done on the VPN server itself, but one can run the steps below on another system, copy the executable over to the VPN server, and then create the service file as they see fit.

## Requirements

1. The VPN server (or device building this executable) needs to have the following installed:

    `build-essential python3 pip`

    * `python3.9` is prefered; versions newer than this will potentially still work
2. **Traffic from the WireGuard server must be able to forward traffic to the local lan/wan**. 
    * A configuration similar to below is needed in your WireGuard server's configuration. This example is allowing all traffic on the WireGuard interface (wg0) to forward traffic to an ethernet interface (eth0) and sets the appropriate rules in UFW to allow this traffic through the firewall (if UFW is used):

        ```
        PostUp = ufw route allow in on wg0 out on eth0
        PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -I POSTROUTING -o eth0 -j MASQUERADE
        PreDown = ufw route delete allow in on wg0 out on eth0
        PreDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
        ```
3. If using `sudo make install` below, the VPN server needs to use `systemd` for the installation script to execute correctly
4. A device on the local network that is setup to wake from WOL packets

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

## Testing/Usage

1. Using a WireGuard client, connect to the WireGuard server
2. Send a WOL packet with to the sleeping computer on the home/local network
3. Confirm that the sleeping computer is now on and can be reached through the VPN connection 

## Debugging

To debug the service, check the system log on the VPN server for the service `wg_wol_relay`.

# Use Case

This script was specifically made to solve the issue of having to create a custom webserver API on or sshing into the VPN server to send a WOL packet directly onto the local network. With either of these approaches, the MAC address is needed for the sleeping computer and it would likely need to be coded somewhere on the VPN server itself.

This approach simplifies the process by caputring/extracting the MAC address from the WOL packet sent from the WireGuard client to the server and then sending that MAC address in a WOL packet to the local network (like the approaches above) without the need for custom code.

**A specific use case that this solves is waking a PC from a WireGuard client in order to stream a remote desktop session via a streaming application (like Moonlight)**