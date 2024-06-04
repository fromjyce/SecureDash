from scapy.all import sniff
import numpy as np

def extract_features(packet):
    features = [
        packet.getlayer("IP").src if packet.haslayer("IP") else None,
        packet.getlayer("IP").dst if packet.haslayer("IP") else None,
        packet.proto if packet.haslayer("IP") else None, # Protocol
        int(packet.time), # Flow Duration
        packet.getlayer("IP").len if packet.haslayer("IP") else 0, # Total Fwd Packets
        0 if not packet.getlayer("TCP") else packet.getlayer("TCP").ack,  # Total Backward Packets
        sum(len(layer.payload) for layer in packet), # Fwd Packets Length Total
        sum(len(layer.payload) for layer in packet) if not packet.getlayer("TCP") else packet.getlayer("TCP").ack, # Bwd Packets Length Total
        max(len(layer.payload) for layer in packet), # Fwd Packet Length Max
        min(len(layer.payload) for layer in packet),  # Fwd Packet Length Min
        int(sum(len(layer.payload) for layer in packet) / len(packet.layers())), # Fwd Packet Length Mean
        int(np.std([len(layer.payload) for layer in packet])),  # Fwd Packet Length Std
        max(len(layer.payload) for layer in packet) if not packet.getlayer("TCP") else packet.getlayer("TCP").ack,  # Bwd Packet Length Max
        min(len(layer.payload) for layer in packet) if not packet.getlayer("TCP") else packet.getlayer("TCP").ack,  # Bwd Packet Length Min
        int(sum(len(layer.payload) for layer in packet) / len(packet.layers()) if not packet.getlayer("TCP") else packet.getlayer("TCP").ack),  # Bwd Packet Length Mean
        int(np.std([len(layer.payload) for layer in packet]) if not packet.getlayer("TCP") else packet.getlayer("TCP").ack),  # Bwd Packet Length Std
        0 if packet.time == 0 else int(len(packet.layers()) / packet.time),  # Flow Bytes/s
        0 if packet.time == 0 else int(1 / packet.time),          # Flow Packets/s
        0,  # Flow IAT Mean
        0,  # Flow IAT Std
        0,  # Flow IAT Max
        0,  # Flow IAT Min
        0,  # Fwd IAT Total
        0,  # Fwd IAT Mean
        0,  # Fwd IAT Std
        0,  # Fwd IAT Max
        0,  # Fwd IAT Min
        0,  # Bwd IAT Total
        0,  # Bwd IAT Mean
        0,  # Bwd IAT Std
        0,  # Bwd IAT Max
        0,  # Bwd IAT Min
        1 if 'TCP' in packet and packet['TCP'].flags.PSH else 0,  # Fwd PSH Flags
        1 if 'TCP' in packet and packet['TCP'].flags.PSH else 0,  # Bwd PSH Flags
        1 if 'TCP' in packet and packet['TCP'].flags.URG else 0,  # Fwd URG Flags
        1 if 'TCP' in packet and packet['TCP'].flags.URG else 0,  # Bwd URG Flags
        len(packet['TCP']) if 'TCP' in packet else 0,  # Fwd Header Length
        0,  # Bwd Header Length
        0,  # Fwd Packets/s
        0,  # Bwd Packets/s
        len(packet),  # Packet Length Min
        len(packet),  # Packet Length Max
        len(packet),  # Packet Length Mean
        0,  # Packet Length Std
        0,  # Packet Length Variance
        0,  # FIN Flag Count
        0,  # SYN Flag Count
        0,  # RST Flag Count
        1 if 'TCP' in packet and packet['TCP'].flags.PSH else 0,  # PSH Flag Count
        0,  # ACK Flag Count
        1 if 'TCP' in packet and packet['TCP'].flags.URG else 0,  # URG Flag Count
        0,  # CWE Flag Count
        0,  # ECE Flag Count
        0,  # Down/Up Ratio
        len(packet),  # Avg Packet Size
        len(packet) if 'TCP' in packet else 0,  # Avg Fwd Segment Size
        0,  # Avg Bwd Segment Size
        len(packet) if 'TCP' in packet and packet['TCP'].flags.PSH else 0,  # Fwd Avg Bytes/Bulk
        1 if 'TCP' in packet and packet['TCP'].flags.PSH else 0,  # Fwd Avg Packets/Bulk
        1 if 'TCP' in packet and packet['TCP'].flags.PSH else 0,  # Fwd Avg Bulk Rate
        0,  # Bwd Avg Bytes/Bulk
        0,  # Bwd Avg Packets/Bulk
        0,  # Bwd Avg Bulk Rate
        0,  # Subflow Fwd Packets
        0,  # Subflow Fwd Bytes
        0,  # Subflow Bwd Packets
        0,  # Subflow Bwd Bytes
        0,  # Init Fwd Win Bytes
        0,  # Init Bwd Win Bytes
        0,  # Fwd Act Data Packets
        0,  # Fwd Seg Size Min
        0,  # Active Mean
        0,  # Active Std
        0,  # Active Max
        0,  # Active Min
        0,  # Idle Mean
        0,  # Idle Std
        0,  # Idle Max
        0   # Idle Min 
    ]
    print(features)

sniff(prn=extract_features)

