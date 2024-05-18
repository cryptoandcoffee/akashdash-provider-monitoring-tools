import os
import json
import requests
import time
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get environment variables
RPC_ENDPOINT = os.environ.get("RPC_ENDPOINT")
TARGET_STATEFULSET_NAME = "akash-provider"
TARGET_STATEFULSET_NAMESPACE = "akash-services"
AKASH_NODE_POD_NAME = "akash-node"
AKASH_NODE_POD_NAMESPACE = "akash-services"
LOCAL_NODE_RPC_ENDPOINT = f"http://akash-node-1:26657"
REMOTE_RPC_ENDPOINT = "http://rpc.sfo.computer:26657"
INTERVAL = int(os.environ.get("INTERVAL", 15))  # Default interval is 60 seconds if not specified
CHORES_INTERVAL = 4 * 60 * 60  # Restart interval in seconds (4 hours)

# Environment setup
os.environ["AKASH_NODE"] = "http://akash-node-1:26657"

# Default to live mode unless "--sim" is specified
SIM_MODE = "--sim" in os.sys.argv
#SIM_MODE = "--live" not in os.sys.argv

# Run shell command
def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Error executing command: {command}")
        logging.error(f"Error details: {result.stderr}")
    return result.stdout.strip()

# Delete terminating namespaces
def delete_terminating_namespaces():
    proxy_process = subprocess.Popen(["kubectl", "proxy"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        namespaces = run_command("kubectl get ns | grep Terminating | awk '{print $1}'").split('\n')
        for ns in namespaces:
            if ns:
                if not SIM_MODE:
                    logging.info(f"Deleting terminating namespace: {ns}")
                    run_command(f'curl -X PUT -H "Content-Type: application/json" --data-binary \'{{"kind":"Namespace","apiVersion":"v1","metadata":{{"name":"{ns}"}}, "spec":{{"finalizers":[]}}}}\' http://localhost:8001/api/v1/namespaces/{ns}/finalize')
                else:
                    logging.info(f"Simulation: Would delete terminating namespace: {ns}")
                    logging.info(f"Simulation: The following resources would be deleted in namespace {ns}:")
                    resources = run_command(f"kubectl get all -n {ns}")
                    if resources:
                        logging.info(resources)
                    else:
                        logging.info("No resources found in the namespace.")
    finally:
        proxy_process.kill()

# Delete evicted pods
def delete_evicted_pods():
    evicted_pods = json.loads(run_command("kubectl get pods --all-namespaces -o json"))
    for item in evicted_pods.get('items', []):
        if item['status'].get('phase') == 'Failed' and item['status'].get('reason') == 'Evicted':
            pod_name = item['metadata']['name']
            namespace = item['metadata']['namespace']
            if not SIM_MODE:
                logging.info(f"Deleting evicted pod: {pod_name} in namespace {namespace}")
                run_command(f"kubectl delete pod {pod_name} -n {namespace}")
            else:
                logging.info(f"Simulation: Would delete evicted pod: {pod_name} in namespace {namespace}")
                logging.info(f"Simulation: The following details would be deleted for pod {pod_name}:")
                logging.info(json.dumps(item, indent=2))

# Delete terminating pods
def delete_terminating_pods():
    terminating_pods = json.loads(run_command("kubectl get pods --all-namespaces -o json"))
    for item in terminating_pods.get('items', []):
        if item['metadata'].get('deletionTimestamp'):
            pod_name = item['metadata']['name']
            namespace = item['metadata']['namespace']
            if not SIM_MODE:
                logging.info(f"Deleting terminating pod: {pod_name} in namespace {namespace}")
                run_command(f"kubectl delete pod {pod_name} -n {namespace} --force --grace-period=0")
            else:
                logging.info(f"Simulation: Would delete terminating pod: {pod_name} in namespace {namespace}")
                logging.info(f"Simulation: The following details would be deleted for pod {pod_name}:")
                logging.info(json.dumps(item, indent=2))



# Restart operator-inventory deployment
def restart_operator_inventory():
    logging.info("Restarting operator-inventory deployment...")
    run_command("kubectl rollout restart deployment/operator-inventory -n akash-services")

# Main execution loop
if __name__ == "__main__":
    if SIM_MODE:
        logging.info("Simulation mode enabled. No real changes will be made.")
    else:
        logging.info("Live mode enabled. Real changes will be made to the cluster.")

    last_chores_time = 0

    while True:
        try:
            logging.info("Starting a new cycle of cluster maintenance tasks...")
            delete_terminating_namespaces()
            delete_evicted_pods()
            delete_terminating_pods()

            current_time = time.time()
            if current_time - last_chores_time >= CHORES_INTERVAL:
                logging.info("Running Chores!...")
                restart_operator_inventory()
                last_chores_time = current_time

            logging.info("Completed one cycle of cluster maintenance tasks.")
        except Exception as e:
            logging.error(f"An error occurred during cluster maintenance: {e}")

        logging.info(f"Waiting {INTERVAL} seconds before the next run...")
        time.sleep(INTERVAL)
