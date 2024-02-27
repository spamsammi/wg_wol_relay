from scapy.layers.inet import *
from scapy.sendrecv import sniff
from wakeonlan import send_magic_packet

BROADCAST_SIGNAL = "ffffffffffff"
BROADCAST_SIGNAL_LEN = len(BROADCAST_SIGNAL)
MOONLIGHT_WOL_PORTS = [9]

def handle_wol_packet(packet):
    if UDP in packet and packet[UDP].dport in MOONLIGHT_WOL_PORTS:
        wol_raw = bytes(packet).hex()
        mac_adr_index = wol_raw.rfind(BROADCAST_SIGNAL) + BROADCAST_SIGNAL_LEN - 1
        madc_adr = wol_raw[mac_adr_index:mac_adr_index + BROADCAST_SIGNAL_LEN]
        send_magic_packet(madc_adr)

print("Sniffing for WOL...")
sniff(filter="udp", prn=handle_wol_packet)