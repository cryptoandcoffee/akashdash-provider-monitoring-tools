
# akash-provider-monitoring-tools

## Overview

`akash-provider-monitoring-tools` is a suite of tools designed to monitor and maintain Akash provider clusters. It includes utilities for cleaning up the cluster, switching RPC endpoints, and monitoring deployments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [License](#license)

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Docker
- Kubernetes CLI (`kubectl`)
- Access to an Akash provider cluster

## Installation

Follow these steps to set up and install `akash-provider-monitoring-tools`.

### 1. Clone the Repository

```bash
git clone https://github.com/cryptoandcoffee/akash-provider-monitoring-tools.git
cd akash-provider-monitoring-tools
```

### 2. Build and Push Docker Images

Run the provided script to build and push the Docker images for the tools.

```bash
chmod +x run.sh
./run.sh
```

This script will build and push Docker images for:
- `akash-provider-chaperone`
- `akash-provider-monitor-rpc-switch`
- `akash-house-cleaner`

### 3. Create Service Account and Roles

Create the necessary service account and roles in your Kubernetes cluster.

```bash
kubectl create serviceaccount -n akash-services monitoring-sa
kubectl apply -f ClusterRole.yaml
```

## Configuration

Update the following configuration files with your environment-specific details:

- `manifests/chaperone.yaml`
- `manifests/rpc_switch.yaml`
- `manifests/house_cleaner.yaml`

For example, update the `DISCORD_WEBHOOK_URL`, `PUSHOVER_API_TOKEN`, and `PUSHOVER_USER_KEY` environment variables in `chaperone.yaml`.

## Usage

### Deploy the Tools

Apply the Kubernetes manifests to deploy the tools.

```bash
kubectl apply -f manifests/chaperone.yaml
kubectl apply -f manifests/house_cleaner.yaml
kubectl apply -f manifests/rpc_switch.yaml
```

### Restart Deployments

Restart the deployments to ensure the latest images are used.

```bash
kubectl rollout restart deployment/chaperone -n akash-services
kubectl rollout restart deployment/house-cleaner -n akash-services
kubectl rollout restart deployment/rpc-switch -n akash-services
```

### Monitor the Cluster

The tools will automatically start monitoring the cluster, switching RPC endpoints, and cleaning up evicted or terminating pods and namespaces.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](./LICENSE) file for details.

---

For more details, refer to the individual Python scripts and Dockerfiles in the repository.

---

Feel free to contribute to this project by opening issues or submitting pull requests on the [GitHub repository](https://github.com/cryptoandcoffee/akash-provider-monitoring-tools).
