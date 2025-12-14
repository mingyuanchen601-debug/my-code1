import json
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [RADAR] - %(message)s')

class CiscoSignalProcessor:
    def __init__(self):
        # Define Signal Strength Thresholds (Unit: dBm)
        # The higher the value (closer to 0), the stronger the signal/closer the distance.
        self.RSSI_THRESHOLD_IMMEDIATE = -45  # Immediate (< 2 meters / Right under the AP)
        self.RSSI_THRESHOLD_NEAR = -65       # Near (Same room / Effective coverage)
        self.RSSI_THRESHOLD_FAR = -75        # Far (Edge of coverage / Behind a wall)
        
        # Watch List (e.g., VIP Client MAC addresses or Asset Tags)
        self.WATCH_LIST = ["00:11:22:33:44:55", "AA:BB:CC:DD:EE:FF"]

    def analyze_packet(self, data_packet):
        """
        Core Analysis Function: Process a single signal data packet.
        """
        try:
            # 1. Extract key telemetry data
            mac_address = data_packet.get('deviceMac')
            rssi = int(data_packet.get('rssi', -100)) # Default to a very low value if missing
            detecting_ap = data_packet.get('apMac')   # Which AP heard this signal
            ssid_probed = data_packet.get('ssid', 'N/A') # The Wi-Fi name the device is searching for
            
            # 2. Determine signal quality/proximity
            distance_category = self._calculate_proximity(rssi)
            
            # 3. Trigger business logic
            self._trigger_events(mac_address, rssi, distance_category, detecting_ap, ssid_probed)
            
        except Exception as e:
            logging.error(f"Packet parsing error: {e}")

    def _calculate_proximity(self, rssi):
        """
        Convert dBm values into human-readable distance semantics.
        """
        if rssi >= self.RSSI_THRESHOLD_IMMEDIATE:
            return "IMMEDIATE (< 2m)"
        elif rssi >= self.RSSI_THRESHOLD_NEAR:
            return "NEAR (2m - 10m)"
        elif rssi >= self.RSSI_THRESHOLD_FAR:
            return "FAR (> 10m)"
        else:
            return "NOISE (Weak signal - Ignore)"

    def _trigger_events(self, mac, rssi, distance, ap_mac, ssid):
        """
        Execute actions based on analysis results.
        """
        # Filter out weak signals to reduce system noise
        if "NOISE" in distance:
            return

        # Format the log output
        log_msg = f"Device: {mac} | Signal: {rssi}dBm | Status: {distance} | AP: {ap_mac}"
        
        # Scenario A: Device is in the Watch List
        if mac in self.WATCH_LIST:
            logging.warning(f" TARGET DETECTED! {log_msg}")
            # Placeholder: Hook into SMS API or Security Alert System here
            
        # Scenario B: High Signal Intensity (e.g., User standing at the counter)
        elif "IMMEDIATE" in distance:
            logging.info(f" Active User: {log_msg} | Probing: {ssid}")
        
        # Scenario C: General Logging
        else:
            # Pass to avoid cluttering logs in production
            pass

# --- Mock Data Stream Input ---
def mock_cisco_data_stream():
    """
    Simulates the JSON stream received from Cisco Spaces.
    """
    processor = CiscoSignalProcessor()
    
    # Mock Data Source
    mock_data = [
        # A passerby with a weak signal
        {"deviceMac": "11:22:33:44:55:66", "rssi": -85, "apMac": "AP_Lobby_01", "ssid": "FreeWiFi"},
        # A user walking closer
        {"deviceMac": "AA:BB:CC:DD:EE:FF", "rssi": -60, "apMac": "AP_Lobby_01", "ssid": "CorpNet"},
        # A device right under the AP (Strong signal)
        {"deviceMac": "00:11:22:33:44:55", "rssi": -40, "apMac": "AP_Library_Desk", "ssid": "Library_Guest"},
    ]

    print("--- Cisco Wireless Signal Monitor Started ---")
    while True:
        import random
        # Randomly select a mock packet
        packet = random.choice(mock_data)
        
        # Add random fluctuation to simulate real-world RSSI jitter
        packet['rssi'] += random.randint(-3, 3) 
        
        processor.analyze_packet(packet)
        time.sleep(1.5) # Simulate data arrival interval

if __name__ == "__main__":
    mock_cisco_data_stream()
