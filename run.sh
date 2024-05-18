#!/bin/bash
KUBECONFIG_DIR="kubeconfigs"
# Build and push the chaperone Docker image

MYHOME=$(pwd)
cd chaperone
docker build -t cryptoandcoffee/akash-provider-chaperone:latest .
docker push cryptoandcoffee/akash-provider-chaperone:latest
cd $MYHOME
cd rpc_switch
# Build and push the rpc-switch Docker image
docker build -t cryptoandcoffee/akash-provider-monitor-rpc-switch:latest .
docker push cryptoandcoffee/akash-provider-monitor-rpc-switch:latest
cd $MYHOME

cd house_cleaner
# Build and push the rpc-switch Docker image
docker build -t cryptoandcoffee/akash-house-cleaner:latest .
docker push cryptoandcoffee/akash-house-cleaner:latest
cd $MYHOME



#    kubectl create serviceaccount -n akash-services monitoring-sa
#    kubectl apply -f ClusterRole.yaml

#KUBECONFIG=$KUBECONFIG_DIR/kubeconfig-sfo-computer

#TESTING
    # Apply the Kubernetes manifests and restart
#    kubectl apply -f manifests/chaperone.yaml
#    kubectl apply -f manifests/house_cleaner.yaml
#    kubectl apply -f manifests/rpc_switch.yaml
#    kubectl rollout restart deployment/chaperone -n akash-services
#    kubectl rollout restart deployment/house-cleaner -n akash-services
#    kubectl rollout restart deployment/rpc-switch -n akash-services
#exit



# Loop through every kubeconfig file in the specified folder
for kubeconfig_file in $KUBECONFIG_DIR/kubeconfig-*; do
    # Set the KUBECONFIG environment variable to the current kubeconfig file
    export KUBECONFIG=$kubeconfig_file

    echo "Processing cluster: $kubeconfig_file"
    kubectl patch statefulset akash-provider -n akash-services -p '{"spec":{"template":{"spec":{"containers":[{"name":"init","image":"ghcr.io/akash-network/provider:0.5.14"},{"name":"akash-provider-0","image":"ghcr.io/akash-network/provider:0.5.14"}]}}}}'
    kubectl patch statefulset akash-provider -n akash-services -p '{"spec":{"template":{"spec":{"initContainers":[{"op": "remove", "name":"init","image":"ghcr.io/akash-network/provider:0.5.14"}],"containers":[{"op": "remove", "name":"akash-provider-0","image":"ghcr.io/akash-network/provider:0.5.14"}]}}}}'
    kubectl patch statefulset akash-provider -n akash-services -p '{"spec":{"template":{"spec":{"initContainers":[{"name":"init","image":"ghcr.io/akash-network/provider:0.5.14"}],"containers":[{"name":"provider","image":"ghcr.io/akash-network/provider:0.5.14"}]}}}}'


    # Create service account and role
    #kubectl create serviceaccount -n akash-services monitoring-sa
    #kubectl apply -f ClusterRole.yaml

    # Apply the Kubernetes manifests and restart
    #kubectl apply -f manifests/chaperone.yaml
    #kubectl apply -f manifests/house_cleaner.yaml
    #kubectl apply -f manifests/rpc_switch.yaml

    #kubectl set image deployment/chaperone chaperone=cryptoandcoffee/akash-provider-chaperone:latest -n akash-services
    #kubectl set image deployment/house-cleaner house-cleaner=cryptoandcoffee/akash-house-cleaner:latest -n akash-services
    #kubectl set image deployment/rpc-switch rpc-switch=cryptoandcoffee/akash-provider-monitor-rpc-switch:latest -n akash-services

    #kubectl rollout restart deployment/chaperone -n akash-services
    #kubectl rollout restart deployment/house-cleaner -n akash-services
    #kubectl rollout restart deployment/rpc-switch -n akash-services

done

#Create service account and role
#kubectl create serviceaccount -n akash-services monitoring-sa
#kubectl apply -f ClusterRole.yaml

# Apply the Kubernetes manifests

#kubectl apply -f manifests/house_cleaner.yaml
#kubectl apply -f manifests/rpc_switch.yaml
