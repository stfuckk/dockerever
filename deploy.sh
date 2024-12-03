#!/bin/bash

# Define the version of node_exporter you want to install
VERSION="1.8.2"

if systemctl is-active --quiet node_exporter; then
    echo "node_exporter is already installed! Skip installation..."
else
    # Download the node_exporter tarball
    wget https://github.com/prometheus/node_exporter/releases/download/v$VERSION/node_exporter-$VERSION.linux-amd64.tar.gz

    # Extract the tarball
    tar xvfz node_exporter-$VERSION.linux-amd64.tar.gz

    # Move the node_exporter binary to /usr/local/bin
    sudo cp node_exporter-$VERSION.linux-amd64/node_exporter /usr/local/bin/

    # Create a node_exporter user
    sudo useradd -rs /bin/false node_exporter

    # Create a systemd service file for node_exporter
    echo "[Unit]
    Description=Node Exporter
    Wants=network-online.target
    After=network-online.target

    [Service]
    User=node_exporter
    Group=node_exporter
    Type=simple
    ExecStart=/usr/local/bin/node_exporter

    [Install]
    WantedBy=multi-user.target" | sudo tee /etc/systemd/system/node_exporter.service

    # Reload systemd to recognize the new service
    sudo systemctl daemon-reload

    # Enable the node_exporter service to start on boot
    sudo systemctl enable node_exporter

    # Start the node_exporter service
    sudo systemctl start node_exporter

    # Clean up: remove the downloaded archive and extracted folder
    rm node_exporter-$VERSION.linux-amd64.tar.gz
    rm -rf node_exporter-$VERSION.linux-amd64
fi

cd ./docker || exit
if [ -f docker-compose.yml ]; then
    sudo docker compose down
    sudo docker image prune -f
    sudo docker compose up --build --force-recreate -d
else
    echo "Error: docker-compose.yml not found."
fi