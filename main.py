import logging
import random
import time
import json
import os
import boto3

# Ensure log directory exists
log_dir = "/var/log/aws_logs"
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, "instance_logs.txt")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s]: %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),  # Save logs to a file
        logging.StreamHandler()  # Print logs to console
    ]
)
logger = logging.getLogger("InstanceLogger")

# Shared transaction counter stored in a file for consistency between instances
transaction_counter_file = "/var/log/aws_logs/transaction_counter.txt"

# Initialize transaction counter if not present
if not os.path.exists(transaction_counter_file):
    with open(transaction_counter_file, "w") as f:
        f.write("1")

# Initialize CloudWatch client
cloudwatch = boto3.client("cloudwatch", region_name="us-east-1")  # Change region if needed

# Define the namespace for metrics
CLOUDWATCH_NAMESPACE = "EC2InstanceMetrics_instance_B"

def get_next_transaction_id():
    with open(transaction_counter_file, "r+") as f:
        transaction_id = int(f.read().strip())
        f.seek(0)
        f.write(str(transaction_id + 1))
        f.truncate()
    return str(transaction_id)

def emit_metric(metric_name, value, instance_name):
    """ Sends custom metric data to CloudWatch """
    cloudwatch.put_metric_data(
        Namespace=CLOUDWATCH_NAMESPACE,
        MetricData=[
            {
                "MetricName": metric_name,
                "Dimensions": [
                    {"Name": "InstanceName", "Value": instance_name}
                ],
                "Value": value,
                "Unit": "Count"
            }
        ]
    )

def generate_logs(instance_name):
    while True:
        transaction_id = get_next_transaction_id()
        log_entries = random.randint(3, 4)
        error_count = 0

        for i in range(log_entries):
            log_data = {
                "transaction_id": transaction_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "instance": instance_name,
                "log_message": f"Processing step {i + 1}"
            }

            if random.random() < 0.3:  # Simulate an error
                log_data["log_level"] = "ERROR"
                log_data["log_message"] = "An error occurred during processing"
                logger.warning(json.dumps(log_data))
                error_count += 1
            else:
                log_data["log_level"] = "INFO"
                logger.info(json.dumps(log_data))

            time.sleep(random.uniform(1, 2))  # Simulate processing time

        # Emit metrics to CloudWatch
        emit_metric("TransactionsProcessed_emit_from_instanceB", 1, instance_name)  # 1 transaction processed
        if error_count > 0:
            emit_metric("ErrorsOccurred_emit_from_instanceB", error_count, instance_name)  # Track errors per transaction

        logger.info(json.dumps({
            "transaction_id": transaction_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "instance": instance_name,
            "log_message": "Transaction completed"
        }))

        time.sleep(3)

if __name__ == "__main__":
    instance_name = "Instance 2"  # Change to "Instance 2" for the second EC2 instance
    generate_logs(instance_name)
