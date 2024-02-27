from scapy.layers.inet import *
from scapy.sendrecv import sniff
from wakeonlan import send_magic_packet

BROADCAST_SIGNAL = "ffffffffffff"
BROADCAST_SIGNAL_LEN = len(BROADCAST_SIGNAL)
WOL_PORT = 9

def get_mac_adr(packet: scapy.packet) -> str:
    wol_raw = bytes(packet).hex()
    mac_adr_index = wol_raw.rfind(BROADCAST_SIGNAL)
    if mac_adr_index > 0:
        mac_adr_index += BROADCAST_SIGNAL_LEN - 1
        return wol_raw[mac_adr_index:mac_adr_index + BROADCAST_SIGNAL_LEN]

def handle_wol_packet(packet):
    mac_adr = get_mac_adr(packet)
    send_magic_packet(mac_adr)

print("Sniffing for WOL...")
sniff(filter=f"udp and port {WOL_PORT}", prn=handle_wol_packet)