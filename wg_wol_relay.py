# Script used to be used as a serivce to capture WOL packets coming from a layer 3 VPN server (in this case Wireguard)
# and forward them to the local network that the server is connected to.
#   NOTE: In order for this script to work, the VPN server MUST have it's traffic forwarding from the virtual
#   network interface (ex. wg0) to a local network interface (ex. eth0/wlan0) that is connected to a local network.
#
#   An example of this would be a pi Wireguard VPN server that lets a user connect to their home network via a VPN client.
#   A specific use case for this would be using a streaming client like Moonlight to wake up a PC in the user's home network
#   by forwarding the WOL packet from the VPN server to the local network.

import os
import logging
import logging.handlers
from logging import Logger
from scapy.all import *
from scapy.layers.inet import *
from scapy.sendrecv import sniff
from wakeonlan import send_magic_packet

# Environment variables
WWR_WOL_PORT = int(os.getenv("WWR_WOL_PORT", 9))
WWR_SNIFF_INTERFACE = os.getenv("WWR_SNIFF_INTERFACE", "wg0")

BROADCAST_SIGNAL = b'\xff' * 6
IPV4_BROADCAST_ADR = "255.255.255.255"
IPV6_MULTICAST_ADR = "ff02::1"

def setup_syslogging() -> Logger:
    """
    Set up logger that will log to syslog.

    Returns:
        Logger: The logger object used by this script to write to syslog.
    """
    logger = logging.getLogger(os.path.basename(__file__))
    logger.setLevel(logging.INFO)
    handler = logging.handlers.SysLogHandler(address='/dev/log')
    formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def get_mac_adr_from_wol_packet(packet: scapy.packet) -> str:
    """
    Attempts to retrieve a MAC address from a WOL packet. WOL packets will have a broadcast signal and should have 
    multiple repittions of a MAC address, so just grab first one.
    
    Returns:
        str:    The target MAC address if one was found
        None:   If the boradcast signal was not found in the packet or an error occured getting the MAC address
    """
    try:
        if packet.haslayer(Raw):
            raw_data = packet[Raw].load
            if raw_data.startswith(BROADCAST_SIGNAL):
                return raw_data[6:12].hex(':')
    except IndexError as e:
        logger.error("MAC address not found after broadcast signal in packet: ", e)
        return None
    except Exception as e:
        logger.error("Error occurred extracting MAC address from packet: ", e)
        return None

def handle_wol_packet(packet: scapy.packet) -> None:
    """
    Forwards a WOL packet from a non-local network to the local network and will ignore any WOL packets coming
    from the local network.

    NOTE: It is highly suggested to only pick a port that is expected to receive WOL packets as this function will
    look for the next 12 hexadecimal characters after a broadcast signal to find the MAC address from a WOL packet. 
    A well-know port for WOL is 9.

    Returns:
        None 
    """
    mac_adr = get_mac_adr_from_wol_packet(packet)
    if mac_adr:
        if (IP in packet and packet[IP].dst != IPV4_BROADCAST_ADR) or (IPv6 in packet and packet[IPv6].dst != IPV6_MULTICAST_ADR):
            logger.info(f"WOL packet captured; relaying '{mac_adr}' to local interface/network.")
            send_magic_packet(mac_adr)
        else:
            logger.info("WOL packet ignored; packet coming from local interface/network.")
    else:
        logger.warning("Packet received is not a WOL packet.")

if __name__ == "__main__":
    """
    Sets up logging for syslog and begins sniffing for WOL packets using scapy
    """
    logger = setup_syslogging()
    logger.info(f"Sniffing for WOL packets on port {WWR_WOL_PORT} on interface {WWR_SNIFF_INTERFACE}...")
    try:
        sniff(
            iface=WWR_SNIFF_INTERFACE,
            filter=f"udp and port {WWR_WOL_PORT}",
            prn=handle_wol_packet,
        )
    except Exception as e:
        logger.error("An error occured sniffing for WOL packets on the network: ", e)