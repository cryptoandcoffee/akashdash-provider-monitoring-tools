import json
import time
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
BANNED_IMAGE_NAMES = ["honeygain", "qbittorrent", "utorrent", "bittorrent", "deluge", "transmission", "vuze", "frostwire", "tixati", "bitcomet", "bitlord", "ekho", "dperson", "emule", "popcorntime", "headphones", "jackett", "lidarr", "mylar3", "prowlarr", "sickrage", "webtop", "dvpn", "mullvad", "softether", "openvpn", "wireguard", "nordvpn", "expressvpn", "ipvanish", "cyberghost", "tunnelbear", "vyprvpn", "hotspotshield", "surfshark", "dante", "3proxy", "ss5", "sunssh", "wingate", "ccproxy", "antinat", "srelay", "delegate", "shadowsocks"]
BLOCKED_PROCESSES = ["torrent", "transmission-cli", "transmission-daemon", "qbittorrent-nox", "deluged", "deluge-web", "vuze", "frostwire", "tixati", "bitcomet", "bitlord", "ekho", "emule", "popcorntime", "headphones", "jackett", "lidarr", "mylar3", "prowlarr", "sickrage", "webtop", "openvpn", "wireguard", "nordvpnd", "expressvpnd", "ipvanish", "cyberghost", "tunnelbear", "vyprvpnd", "hotspotshield", "surfshark", "dante", "3proxy", "ss5", "sunssh", "wingate", "ccproxy", "antinat", "srelay", "delegate", "ss-local", "ss-server"]
BANNED_FILE_EXTENSIONS = [".torrent", ".magnet"]

def run_command(command):
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        return output.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running command '{command}': {e}")
        return None

def check_banned_image(pod):
    for container in pod["spec"]["containers"]:
        image = container["image"].lower()
        if any(banned_name.lower() in image for banned_name in BANNED_IMAGE_NAMES):
            return image
    return None

def check_blocked_process(namespace, pod_name):
    command = ["kubectl", "exec", "-n", namespace, pod_name, "--", "ps", "aux"]
    output = run_command(command)
    if output:
        processes = output.split("\n")
        for process in processes:
            if any(blocked_process.lower() in process.lower() for blocked_process in BLOCKED_PROCESSES):
                return process
    return None

def get_running_pods_with_label(label):
    command = f"kubectl get pods --all-namespaces -l {label} -o json"
    output = run_command(command)
    if output:
        return json.loads(output)
    return None

def delete_namespace(namespace):
    command = f"kubectl delete namespace {namespace}"
    run_command(command)
    logging.info(f"Deleted namespace: {namespace}")

def detect_and_delete_banned_namespaces():
    pods_data = get_running_pods_with_label("akash.network=true")
    if pods_data:
        banned_pods = []
        for pod in pods_data["items"]:
            if pod["status"]["phase"] == "Running":
                namespace = pod["metadata"]["namespace"]
                pod_name = pod["metadata"]["name"]

                banned_image = check_banned_image(pod)
                if banned_image:
                    banned_pods.append(pod)
                    logging.info(f"Banned image found: {banned_image} in pod {pod_name} in namespace {namespace}")

                blocked_process = check_blocked_process(namespace, pod_name)
                if blocked_process:
                    banned_pods.append(pod)
                    logging.info(f"Blocked process found: {blocked_process} in pod {pod_name} in namespace {namespace}")

        if banned_pods:
            namespaces = set(pod["metadata"]["namespace"] for pod in banned_pods)
            for namespace in namespaces:
                delete_namespace(namespace)
        else:
            logging.info("No running pods with banned processes, images, or files found")
    else:
        logging.info("No running pods found with label 'akash.network=true'")

def main():
    while True:
        detect_and_delete_banned_namespaces()
        time.sleep(15)  # Wait for 15 seconds before checking again

if __name__ == "__main__":
    main()
