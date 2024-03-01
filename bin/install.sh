#!/bin/bash
# This script will install the Wireguard WOL Relay Service. This service will attempt to capture WOL packets from
# a layer 3 VPN network (such as Wireguard), and forward these WOL packets to a local interface/network

SCRIPT_DIR=$(dirname "$0")
SERVICE_NAME="wg_wol_relay"
SERVICE_FILE="${SERVICE_NAME}.service"
SERVICE_PATH="/etc/systemd/system/${SERVICE_FILE}"
EXECUTABLE_BUILD_PATH="${SCRIPT_DIR}/../dist/${SERVICE_NAME}"
EXECUTABLE_PATH="/usr/local/bin/${SERVICE_NAME}"

install() {
    echo "Installing '$SERVICE_NAME' executable to '$EXECUTABLE_PATH'..."
    cp ${EXECUTABLE_BUILD_PATH} ${EXECUTABLE_PATH}

    echo "Creating service file in '$SERVICE_PATH'..."
    cat << EOF > ${SERVICE_PATH}
[Unit]
Description=Wireguard WOL Relay Serivce
After=network-online.target

[Service]
Type=simple
ExecStart=${EXECUTABLE_PATH}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    echo "Adjusting permissions on '$SERVICE_NAME' service..."
    chmod 644 ${SERVICE_PATH}

    echo "Reloading systemd daemon"
    systemctl daemon-reload

    echo "Enabling '$SERVICE_NAME' service"...
    systemctl enable ${SERVICE_NAME}

    echo "Starting '$SERVICE_NAME' service..."
    systemctl start ${SERVICE_NAME}

    echo "Installation completed."
}

uninstall() {
    echo "Stopping '$SERVICE_NAME' service..."
    systemctl stop ${SERVICE_NAME}

    echo "Disabling '$SERVICE_NAME' service..."
    systemctl disable ${SERVICE_NAME}

    echo "Removing service file in '$SERVICE_PATH'..."
    rm ${SERVICE_PATH}

    echo "Uninstalling '$SERVICE_NAME' executable from '$EXECUTABLE_PATH'..."
    rm ${EXECUTABLE_PATH}

    echo "Uninstall completed."
}

if [ "$1" == "-u" ]; then
    uninstall
else
    install
fi