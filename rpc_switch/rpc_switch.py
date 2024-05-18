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

def is_akash_provider_pod_running():
    try:
        # Use kubectl to check if the akash-provider pod is running
        cmd = f"kubectl get pods -l app={TARGET_STATEFULSET_NAME} -n {TARGET_STATEFULSET_NAMESPACE} --field-selector=status.phase=Running --no-headers"
        output = subprocess.check_output(cmd, shell=True, text=True).strip()
        return bool(output)
    except subprocess.CalledProcessError:
        return False

def is_akash_provider_pod_terminating():
    try:
        # Use kubectl to check if the akash-provider pod is terminating
        cmd = f"kubectl get pods -l app={TARGET_STATEFULSET_NAME} -n {TARGET_STATEFULSET_NAMESPACE} --field-selector=status.phase=Terminating --no-headers"
        output = subprocess.check_output(cmd, shell=True, text=True).strip()
        return bool(output)
    except subprocess.CalledProcessError:
        return False

def is_akash_node_pod_running():
    try:
        # Use kubectl to check if the akash-node-1 pod is running
        cmd = f"kubectl get pods -l app={AKASH_NODE_POD_NAME} -n {AKASH_NODE_POD_NAMESPACE} --field-selector=status.phase=Running --no-headers"
        output = subprocess.check_output(cmd, shell=True, text=True).strip()
        return bool(output)
    except subprocess.CalledProcessError:
        return False

def get_akash_provider_akash_node_env():
    try:
        # Use kubectl to get the AKASH_NODE environment variable value
        cmd = f"kubectl get pods -l app={TARGET_STATEFULSET_NAME} -n {TARGET_STATEFULSET_NAMESPACE} -o jsonpath='{{.items[0].spec.containers[0].env[?(@.name==\"AKASH_NODE\")].value}}'"
        akash_node_env = subprocess.check_output(cmd, shell=True, text=True).strip()
        return akash_node_env
    except subprocess.CalledProcessError as e:
        logging.error(f"Error getting akash-provider AKASH_NODE environment variable: {e}")
        return None

def update_akash_node_env(rpc_endpoint):
   current_env_value = get_akash_provider_akash_node_env()
   if current_env_value != rpc_endpoint:
       try:
           # Update AKASH_NODE environment variable using kubectl
           cmd = f"kubectl set env statefulset/{TARGET_STATEFULSET_NAME} AKASH_NODE='{rpc_endpoint}' -n {TARGET_STATEFULSET_NAMESPACE}"
           subprocess.run(cmd, shell=True, check=True)
           logging.info(f"Updated AKASH_NODE to {rpc_endpoint}")
           cmd = f"kubectl scale statefulset akash-provider --replicas=0 -n akash-services --timeout=0s"
           cmd = f"kubectl scale statefulset akash-provider --replicas=1 -n akash-services --timeout=0s"
       except subprocess.CalledProcessError as e:
           logging.error(f"Error updating AKASH_NODE: {e.stderr.decode('utf-8')}")
   else:
       logging.info(f"AKASH_NODE already set to {rpc_endpoint}, no update needed")

def check_rpc_endpoint():
   try:
       # Check RPC endpoint availability
       response = requests.get(f"{LOCAL_NODE_RPC_ENDPOINT}/status", timeout=5)
       response.raise_for_status()
       status_data = response.json()
       catching_up = status_data["result"]["sync_info"]["catching_up"]
       if catching_up:
           return False
       return True
   except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
       return False

def check_and_update_rpc_endpoint():
   try:
       # Check if the akash-node-1 pod is running
       if is_akash_node_pod_running():
           if check_rpc_endpoint():
               # Update to local RPC endpoint if it's available and not catching up
               update_akash_node_env(LOCAL_NODE_RPC_ENDPOINT)
           else:
               # Switch to remote RPC endpoint if local is catching up or unavailable
               update_akash_node_env(REMOTE_RPC_ENDPOINT)
       else:
           # Switch to remote RPC endpoint if Akash node pod is not running
           update_akash_node_env(REMOTE_RPC_ENDPOINT)
   except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
       logging.error(f"Error checking RPC endpoint: {e}")
       update_akash_node_env(REMOTE_RPC_ENDPOINT)

while True:
   check_and_update_rpc_endpoint()
   time.sleep(6)  # Wait for 6 seconds before checking again
