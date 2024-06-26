from keras.models import load_model
from sklearn.preprocessing import StandardScaler
from scapy.all import sniff
import numpy as np
from datetime import datetime
import requests
import json
import ipaddress

# Load the trained model
model = load_model('{your_model_name}')
scaler = StandardScaler()
url = "{your_push_url}"
headers = {'Content-Type': 'application/json'}

cumulative_data = {
    'normal_count': 0,
    'alert_count': 0,
    'normal_source_ip': set(),
    'alert_source_ip': set(),
    'normal_destination_ip': set(),
    'alert_destination_ip': set(),
    'normal_protocol': 0,
    'alert_protocol': 0,
    'normal_flow_duration': 0,
    'alert_flow_duration': 0,
    'normal_total_fwd_packets': 0,
    'alert_total_fwd_packets': 0,
    'normal_total_backward_packets': 0,
    'alert_total_backward_packets': 0,
    'normal_fwd_packets_length_total': 0,
    'alert_fwd_packets_length_total': 0,
    'normal_bwd_packets_length_total': 0,
    'alert_bwd_packets_length_total': 0,
    'total_normal_packets': 0,
    'total_alert_packets': 0,
    'total_normal_packets_length': 0,
    'total_alert_packets_length': 0
}

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
    return features

def get_features(features):
    return features[0], features[1], features[2], features[3], features[4], features[5], features[6], features[7]

def predict_packet(packet):
    features = extract_features(packet)
    source_ip, destination_ip, protocol, flow_duration, total_fwd_packets, total_backward_packets, fwd_packets_length_total, bwd_packets_length_total = get_features(features)
    needed_features = features[2:]
    needed_features = np.array(needed_features).reshape((1, len(needed_features)))
    scaled_features = scaler.fit_transform(needed_features)
    prediction = model.predict(scaled_features)
    return prediction, source_ip, destination_ip, protocol, flow_duration, total_fwd_packets, total_backward_packets, fwd_packets_length_total, bwd_packets_length_total

def classification(prediction):
    return "ALERT" if prediction[0][0] > prediction[0][1] else "NORMAL"

def process_packet(packet):
    global cumulative_data
    prediction, source_ip, destination_ip, protocol, flow_duration, total_fwd_packets, total_backward_packets, fwd_packets_length_total, bwd_packets_length_total = predict_packet(packet)
    timestamp = datetime.now().isoformat()
    status = classification(prediction)

    if status == "ALERT":
        cumulative_data['alert_count'] += 1
        cumulative_data['alert_source_ip'].add(source_ip)
        cumulative_data['alert_destination_ip'].add(destination_ip)
        cumulative_data['alert_protocol'] += protocol
        cumulative_data['alert_flow_duration'] += flow_duration
        cumulative_data['alert_total_fwd_packets'] += total_fwd_packets
        cumulative_data['alert_total_backward_packets'] += total_backward_packets
        cumulative_data['alert_fwd_packets_length_total'] += fwd_packets_length_total
        cumulative_data['alert_bwd_packets_length_total'] += bwd_packets_length_total
        cumulative_data['total_alert_packets'] += total_fwd_packets + total_backward_packets
        cumulative_data['total_alert_packets_length'] += fwd_packets_length_total + bwd_packets_length_total
    else:
        cumulative_data['normal_count'] += 1
        cumulative_data['normal_source_ip'].add(source_ip)
        cumulative_data['normal_destination_ip'].add(destination_ip)
        cumulative_data['normal_protocol'] += protocol
        cumulative_data['normal_flow_duration'] += flow_duration
        cumulative_data['normal_total_fwd_packets'] += total_fwd_packets
        cumulative_data['normal_total_backward_packets'] += total_backward_packets
        cumulative_data['normal_fwd_packets_length_total'] += fwd_packets_length_total
        cumulative_data['normal_bwd_packets_length_total'] += bwd_packets_length_total
        cumulative_data['total_normal_packets'] += total_fwd_packets + total_backward_packets
        cumulative_data['total_normal_packets_length'] += fwd_packets_length_total + bwd_packets_length_total
    
    data = [
        {
            'normal_count': cumulative_data['normal_count'],
            'alert_count': cumulative_data['alert_count'],
            'status_count': cumulative_data['normal_count'] + cumulative_data['alert_count'],
            'normal_source_ip': len(cumulative_data['normal_source_ip']),
            'alert_source_ip': len(cumulative_data['alert_source_ip']),
            'normal_destination_ip': len(cumulative_data['normal_destination_ip']),
            'alert_destination_ip': len(cumulative_data['alert_destination_ip']),
            'normal_protocol': cumulative_data['normal_protocol'],
            'alert_protocol': cumulative_data['alert_protocol'],
            'normal_flow_duration': cumulative_data['normal_flow_duration'],
            'alert_flow_duration': cumulative_data['alert_flow_duration'],
            'normal_total_fwd_packets': cumulative_data['normal_total_fwd_packets'],
            'alert_total_fwd_packets': cumulative_data['alert_total_fwd_packets'],
            'normal_total_backward_packets': cumulative_data['normal_total_backward_packets'],
            'alert_total_backward_packets': cumulative_data['alert_total_backward_packets'],
            'normal_fwd_packets_length_total': cumulative_data['normal_fwd_packets_length_total'],
            'alert_fwd_packets_length_total': cumulative_data['alert_fwd_packets_length_total'],
            'normal_bwd_packets_length_total': cumulative_data['normal_bwd_packets_length_total'],
            'alert_bwd_packets_length_total': cumulative_data['alert_bwd_packets_length_total'],
            'total_normal_packets': cumulative_data['total_normal_packets'],
            'total_alert_packets': cumulative_data['total_alert_packets'],
            'total_normal_packets_length': cumulative_data['total_normal_packets_length'],
            'total_alert_packets_length': cumulative_data['total_alert_packets_length'],
            'timestamp': timestamp
        }
    ]
    return data

def main(packet):
    while True:
        data = process_packet(packet)
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(f"Data sent to Power BI: {response.status_code}")

sniff(prn=main)