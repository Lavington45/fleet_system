import requests
import time
import random
import json
import logging
from datetime import datetime
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fleet_simulator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
URL = "http://127.0.0.1:5000/api/update_vehicle"
BUFFER_FILE = "buffer.json"
ENCRYPTION_KEY = "your-encryption-key-change-in-production"  # In production, store securely
VEHICLES = [f"Vehicle{i}" for i in range(1, 21)]
BASE_LAT = -1.286389
BASE_LON = 36.816667
OFFLINE_THRESHOLD = 3  # Retry 3 times before buffering

# Initialize cipher
cipher = Fernet(Fernet.generate_key())

class FleetDataBuffer:
    def __init__(self, buffer_file):
        self.buffer_file = buffer_file
        self.buffer = self._load_buffer()
        self.retry_counts = {}
        self.connectivity_status = "online"
    
    def _load_buffer(self):
        """Load buffer from file"""
        try:
            with open(self.buffer_file, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} buffered records")
                return data
        except FileNotFoundError:
            logger.info("No existing buffer file, starting fresh")
            return []
        except json.JSONDecodeError:
            logger.warning("Buffer file corrupted, starting fresh")
            return []
    
    def _save_buffer(self):
        """Save buffer to file"""
        try:
            with open(self.buffer_file, 'w') as f:
                json.dump(self.buffer, f, indent=2)
                logger.debug(f"Buffer saved with {len(self.buffer)} records")
        except Exception as e:
            logger.error(f"Error saving buffer: {e}")
    
    def add_to_buffer(self, data):
        """Add data to buffer"""
        buffered_data = {
            "timestamp": datetime.now().isoformat(),
            "vehicle": data["vehicle"],
            "lat": data["lat"],
            "lon": data["lon"],
            "speed": data["speed"],
            "trip_id": data.get("trip_id"),
            "encrypted": False
        }
        self.buffer.append(buffered_data)
        self._save_buffer()
        logger.warning(f"Data buffered for {data['vehicle']} (Total: {len(self.buffer)})")
    
    def get_buffered_data(self, limit=10):
        """Get oldest buffered records"""
        return self.buffer[:limit]
    
    def remove_from_buffer(self, count):
        """Remove synced records from buffer"""
        self.buffer = self.buffer[count:]
        self._save_buffer()
        logger.info(f"Removed {count} synced records from buffer")
    
    def clear_buffer(self):
        """Clear all buffered data"""
        self.buffer = []
        self._save_buffer()
        logger.info("Buffer cleared")
    
    def get_buffer_size(self):
        """Get current buffer size"""
        return len(self.buffer)

class VehicleSimulator:
    def __init__(self, vehicles):
        self.vehicles = vehicles
        self.buffer = FleetDataBuffer(BUFFER_FILE)
        self.current_positions = {}
        self._initialize_positions()
    
    def _initialize_positions(self):
        """Initialize vehicle positions"""
        for vehicle in self.vehicles:
            self.current_positions[vehicle] = {
                "lat": BASE_LAT + random.uniform(-0.1, 0.1),
                "lon": BASE_LON + random.uniform(-0.1, 0.1)
            }
    
    def _generate_realistic_movement(self, vehicle):
        """Generate realistic vehicle movement"""
        current = self.current_positions[vehicle]
        # Small random movements to simulate realistic GPS data
        lat_change = random.uniform(-0.002, 0.002)
        lon_change = random.uniform(-0.002, 0.002)
        
        current["lat"] = max(-90, min(90, current["lat"] + lat_change))
        current["lon"] = max(-180, min(180, current["lon"] + lon_change))
        
        return current
    
    def generate_vehicle_data(self, vehicle):
        """Generate GPS data for a vehicle"""
        position = self._generate_realistic_movement(vehicle)
        
        data = {
            "vehicle": vehicle,
            "lat": round(position["lat"], 8),
            "lon": round(position["lon"], 8),
            "speed": random.randint(20, 120),
            "trip_id": random.randint(1, 1000) if random.random() > 0.3 else None,
            "accuracy": random.randint(5, 15),
            "heading": random.randint(0, 359),
            "altitude": random.randint(1600, 1900)
        }
        
        return data
    
    def send_with_retry(self, data, max_retries=3):
        """Send data with retry logic"""
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    URL,
                    json=data,
                    timeout=5,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    logger.info(f"✓ {data['vehicle']} updated successfully")
                    self.buffer.connectivity_status = "online"
                    return True
                else:
                    logger.warning(f"Server error ({response.status_code}): {response.text}")
                    
            except requests.Timeout:
                logger.warning(f"Timeout sending {data['vehicle']} (attempt {attempt + 1}/{max_retries})")
            except requests.ConnectionError:
                logger.warning(f"Connection error for {data['vehicle']} (attempt {attempt + 1}/{max_retries})")
            except Exception as e:
                logger.error(f"Error sending {data['vehicle']}: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait before retry
        
        logger.critical(f"✗ {data['vehicle']} failed after {max_retries} attempts - BUFFERING")
        self.buffer.connectivity_status = "offline"
        self.buffer.add_to_buffer(data)
        return False
    
    def sync_buffered_data(self):
        """Attempt to sync buffered data"""
        buffered = self.buffer.get_buffered_data(limit=5)
        
        if not buffered:
            return
        
        logger.info(f"Attempting to sync {len(buffered)} buffered records...")
        
        synced_count = 0
        for record in buffered:
            try:
                response = requests.post(
                    URL,
                    json={
                        "vehicle": record["vehicle"],
                        "lat": record["lat"],
                        "lon": record["lon"],
                        "speed": record["speed"],
                        "trip_id": record.get("trip_id")
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    synced_count += 1
                    logger.info(f"↑ Synced buffered data for {record['vehicle']}")
                    
            except Exception as e:
                logger.warning(f"Failed to sync {record['vehicle']}: {e}")
                break
        
        if synced_count > 0:
            self.buffer.remove_from_buffer(synced_count)
            logger.info(f"✓ Synced {synced_count} buffered records")
    
    def run_simulation(self, update_interval=5):
        """Run vehicle simulation"""
        logger.info(f"Starting fleet simulator with {len(self.vehicles)} vehicles")
        logger.info(f"Update interval: {update_interval}s | Buffer file: {BUFFER_FILE}")
        
        iteration = 0
        
        try:
            while True:
                iteration += 1
                
                # Sync buffered data every 10 iterations
                if iteration % 10 == 0:
                    self.sync_buffered_data()
                    logger.info(f"Buffer status: {self.buffer.get_buffer_size()} records pending")
                
                # Send current vehicle data
                for vehicle in self.vehicles:
                    data = self.generate_vehicle_data(vehicle)
                    self.send_with_retry(data)
                
                time.sleep(update_interval)
                
        except KeyboardInterrupt:
            logger.info("\n✓ Simulator stopped by user")
            logger.info(f"Final buffer status: {self.buffer.get_buffer_size()} pending records")
        except Exception as e:
            logger.critical(f"Simulator error: {e}")

def main():
    logger.info("=" * 60)
    logger.info("FLEET MANAGEMENT SYSTEM - VEHICLE SIMULATOR")
    logger.info("=" * 60)
    
    simulator = VehicleSimulator(VEHICLES)
    
    # Run simulation with 3-second update interval
    simulator.run_simulation(update_interval=3)

if __name__ == "__main__":
    main()
