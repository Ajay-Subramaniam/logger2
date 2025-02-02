import logging
import random
import time
import json
import os

# Ensure log directory exists
log_dir = "/var/log/aws_logs"
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, "instance_logs.txt")

# Configure logging to save logs to a directory
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s]: %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),  # Save logs to a file
        logging.StreamHandler()  # Also print logs to console
    ]
)
logger = logging.getLogger("InstanceLogger")

# Shared transaction counter stored in a file for consistency between instances
transaction_counter_file = "/var/log/aws_logs/transaction_counter.txt"

# Initialize transaction counter if not present
if not os.path.exists(transaction_counter_file):
    with open(transaction_counter_file, "w") as f:
        f.write("1")

def get_next_transaction_id():
    with open(transaction_counter_file, "r+") as f:
        transaction_id = int(f.read().strip())
        f.seek(0)
        f.write(str(transaction_id + 1))
        f.truncate()
    return str(transaction_id)

def generate_logs(instance_name):
    while True:
        # Retrieve shared transaction ID
        transaction_id = get_next_transaction_id()

        # Both instances will generate 3-4 log entries with the same transaction ID
        log_entries = random.randint(3, 4)

        for i in range(log_entries):
            log_data = {
                "transaction_id": transaction_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "instance": instance_name,
                "log_message": f"Processing step {i + 1}"
            }

            # Introduce an error randomly
            if random.random() < 0.3:
                log_data["log_level"] = "ERROR"
                log_data["log_message"] = "An error occurred during processing"
                logger.warning(json.dumps(log_data))  # Log as WARNING for errors
            else:
                log_data["log_level"] = "INFO"
                logger.info(json.dumps(log_data))  # Log the data as JSON

            time.sleep(random.uniform(1, 2))  # Simulate processing time

        # After completing logs for this transaction ID, wait before starting the next
        logger.info(json.dumps({
            "transaction_id": transaction_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "instance": instance_name,
            "log_message": "Transaction completed"
        }))

        time.sleep(3)  # Pause before starting a new transaction

if __name__ == "__main__":
    instance_name = "Instance 2"  # Change to "Instance 2" for the second EC2 instance
    generate_logs(instance_name)
