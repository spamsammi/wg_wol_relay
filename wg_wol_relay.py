import os
import logging
import logging.handlers
from scapy.layers.inet import *
from scapy.sendrecv import sniff
from wakeonlan import send_magic_packet

BROADCAST_SIGNAL = "ffffffffffff"
BROADCAST_ADR = "255.255.255.255"
BROADCAST_SIGNAL_LEN = len(BROADCAST_SIGNAL)
WOL_PORT = 9

def setup_syslogging():
    logger = logging.getLogger(os.path.basename(__file__))
    logger.setLevel(logging.INFO)
    handler = logging.handlers.SysLogHandler(address='/dev/log')
    formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def get_mac_adr(packet: scapy.packet) -> str:
    wol_raw = bytes(packet).hex()
    mac_adr_index = wol_raw.rfind(BROADCAST_SIGNAL)
    if mac_adr_index > 0:
        mac_adr_index += BROADCAST_SIGNAL_LEN - 1
        return wol_raw[mac_adr_index:mac_adr_index + BROADCAST_SIGNAL_LEN]
    return None

def handle_wol_packet(packet):
    mac_adr = get_mac_adr(packet)
    if mac_adr:
        # We only care about packets that are not from the local network to relay
        if IP in packet and packet[IP].dst != BROADCAST_ADR:
            logger.info(f"WOL packet captured; relaying '{mac_adr}' to local interface/network.")
            send_magic_packet(mac_adr)
        else:
            # WOL should be ignored anyway; the server that uses this service should be on to run this script
            logger.info("WOL packet ignored; packet coming from local interface/network.")
    else:
        logger.warning("Packet received is not a WOL packet.")

logger = setup_syslogging()
logger.info(f"Sniffing for WOL packets on port {WOL_PORT}...")
sniff(filter=f"udp and port {WOL_PORT}", prn=handle_wol_packet)