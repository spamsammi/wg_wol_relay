# WireGuard WOL Relay

This script will relay WOL packets from a WireGuard VPN server's subnet to the subnet network that the VPN server is connected to. The default port to sniff for WOL packets is set to 9, but can be changed in the `wg_wol_relay.py` script if needed.

Typically building the exectuable is done on the VPN server itself, but one can run the steps below on another system, copy the executable over to the VPN server, and then create the service file as they see fit.

## Requirements

1. The VPN server (or device building this executable) needs to have the following installed:

    `build-essential python3 pip`

    * `python3.9` is prefered; versions newer than this will potentially still work
2. Traffic from the WireGuard server must be able to accept traffic from the WireGuard network interface. 
    * A configuration similar to below is needed in your WireGuard server's configuration:

        ```
        PostUp = iptables -A FORWARD -i wg0 -j ACCEPT
        PreDown = iptables -D FORWARD -i wg0 -j ACCEPT
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

This will stop the service, disable and remove it, and uninstall the executable from the sytem.

## Testing/Usage

1. Using a WireGuard client, connect to the WireGuard server
2. Send a WOL packet that has the WireGuard server as the destination address and the MAC address of the sleeping computer on the local network
    * Ex. using the moonlight client will do this for you
3. Confirm that the sleeping computer is now on and can be reached through the VPN connection 

## Environment Variables

`WWR_WOL_PORT`: port to sniff WOL packets for (default: 9)
`WWR_SNIFF_INTERFACE`: interface to sniff for WOL packets on (default: `wg0`)

>NOTES
>1.  Avoid setting this to `any`; there may be a race condition on the startup of this service and which network interface this chooses on boot
>2. If routing `all` traffic form your WireGuard client to your server (`AllowedIPs = 0.0.0.0/0`), you can use your outbound internet device (ex. `eth0`, `wlan0`, etc) if you want to. Using your WireGuard interface is the prefered way, however.

## Debugging

To debug the service, check the system log on the VPN server for the service `wg_wol_relay`.

## WOL Packet Structure

Without going into low level detail, the WOL packet just needs the destination IP address of the WireGuard server and the MAC address of the sleeping computer. There are several tools available to do this from the commandline, phone applications, etc.

### Wireguard Client Configuration
1. If routing `all` traffic on your WireGuard client (`AllowedIPs = 0.0.0.0/0`), set your `WWR_SNIFF_INTERFACE` configuration to `wgX` or your outbound internet device (ex. `eth0`, `wlan0`, etc)
2. If routing `some` traffic on your WireGuard client, make sure that the `WWR_SNIFF_INTERFACE` is set to `wgX` and that your WireGuard client has at least `AllowedIPs = <your_WireGuard_servers_vpn_ip_address>/32` (ex. `10.80.1.1/32`).

# Use Case

This script was specifically made to solve the issue of having to create a custom webserver API on or sshing into the VPN server to send a WOL packet directly onto the local network. With either of these approaches, the MAC address is needed for the sleeping computer and it would likely need to be coded somewhere on the VPN server itself. This script also solves having to potentially modify router settings to allow broadcasting from a WOL packet directed at the VPN sever.

This approach simplifies the process by caputring/extracting the MAC address from the WOL packet sent from the WireGuard client to the server and then sending that MAC address in a WOL packet to the local network (like the approaches above) without the need for custom code.

## Specific Use Case

This directly solves waking a PC from a WireGuard client in order to stream a remote desktop session via the streaming application Moonlight.