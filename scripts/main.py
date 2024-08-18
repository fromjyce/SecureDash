from keras.models import load_model
from sklearn.preprocessing import StandardScaler
from scapy.all import sniff
import numpy as np
from datetime import datetime
import mysql.connector
import requests
import json
import ipaddress

# Load the trained model
model = load_model('scripts/model.h5')
scaler = StandardScaler()
url = "https://api.powerbi.com/beta/5beb351c-3fb8-418f-b612-fe36ace96ef3/datasets/2b4f3d39-802c-4215-8fa6-a55cd6ac4177/rows?experience=power-bi&key=xO4Ca1dOSvwuGABqxIDYIkWYiWG%2FT3hsWfVswi6y45wKXILaIEeogAHIO9I9Vk3IlsQn7ooECCrFb4kCF1iGDA%3D%3D"
headers = {'Content-Type': 'application/json'}

db_config = {
    'user': 'root',
    'password': '###',
    'host': 'localhost',
    'database': 'securedash',
}

cumulative_data = {
    'normal_count': 0,
    'alert_count': 0,
    'normal_source_ip': set(),
    'alert_source_ip': set(),
    'normal_destination_ip': set(),
    'alert_destination_ip': set(),
    'normal_protocol': 0,
    'alert_protocol': 0,
    'normal_total_fwd_packets': 0,
    'alert_total_fwd_packets': 0,
    'normal_total_backward_packets': 0,
    'alert_total_backward_packets': 0,
    'total_normal_packets': 0,
    'total_alert_packets': 0
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
    return "MALIGNANT" if prediction[0][0] > prediction[0][1] else "BENIGN"

def process_packet(packet):
    global cumulative_data
    prediction, source_ip, destination_ip, protocol, flow_duration, total_fwd_packets, total_backward_packets, fwd_packets_length_total, bwd_packets_length_total = predict_packet(packet)
    timestamp = datetime.now().isoformat()
    status = classification(prediction)

    sql_data = {
        'source_ip': source_ip,
        'destination_ip': destination_ip,
        'timestamp': timestamp,
        'protocol': protocol,
        'total_fwd_packets': total_fwd_packets,
        'total_backward_packets': total_backward_packets,
        'status': status
    }

    if status == "MALIGNANT":
        cumulative_data['alert_count'] += 1
        cumulative_data['alert_source_ip'].add(source_ip)
        cumulative_data['alert_destination_ip'].add(destination_ip)
        cumulative_data['alert_protocol'] += protocol
        cumulative_data['alert_total_fwd_packets'] += total_fwd_packets
        cumulative_data['alert_total_backward_packets'] += total_backward_packets
        cumulative_data['total_alert_packets'] += total_fwd_packets + total_backward_packets
    else:
        cumulative_data['normal_count'] += 1
        cumulative_data['normal_source_ip'].add(source_ip)
        cumulative_data['normal_destination_ip'].add(destination_ip)
        cumulative_data['normal_protocol'] += protocol
        cumulative_data['normal_total_fwd_packets'] += total_fwd_packets
        cumulative_data['normal_total_backward_packets'] += total_backward_packets
        cumulative_data['total_normal_packets'] += total_fwd_packets + total_backward_packets
    
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
            'normal_total_fwd_packets': cumulative_data['normal_total_fwd_packets'],
            'alert_total_fwd_packets': cumulative_data['alert_total_fwd_packets'],
            'normal_total_backward_packets': cumulative_data['normal_total_backward_packets'],
            'alert_total_backward_packets': cumulative_data['alert_total_backward_packets'],
            'total_normal_packets': cumulative_data['total_normal_packets'],
            'total_alert_packets': cumulative_data['total_alert_packets'],
            'timestamp': timestamp
        }
    ]
    return data, sql_data

def main(packet):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    while True:
        data, sql_data = process_packet(packet)
        response = requests.post(url, headers=headers, data=json.dumps(data))
        insert_query = ("INSERT INTO packet_data"
                        "(source_ip, destination_ip, timestamp, protocol, total_fwd_packets, total_backward_packets, status)"
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)")
        cursor.execute(insert_query, (sql_data['source_ip'], sql_data['destination_ip'], sql_data['timestamp'], sql_data['protocol'], sql_data['total_fwd_packets'], sql_data['total_backward_packets'],  sql_data['status']))
        conn.commit()

sniff(prn=main)
