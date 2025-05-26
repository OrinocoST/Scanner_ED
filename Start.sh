#!/bin/bash

SERVICE_NAME=laser_tmux
SCRIPT_PATH="/home/pi/Desktop/AssaAbloy_ED/main.py"
TMUX_SESSION=laser_session

echo "Configurando servicio con tmux para ejecución persistente de $SCRIPT_PATH..."

# Asegurar que tmux esté instalado
if ! command -v tmux &> /dev/null; then
  echo "Instalando tmux..."
  sudo apt update
  sudo apt install -y tmux
fi

# Crear el servicio systemd
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Sistema Assa-Abloy con tmux
After=network.target

[Service]
Type=oneshot
RemainAfterExit=true
ExecStart=/usr/bin/tmux new-session -d -s ${TMUX_SESSION} "python3 ${SCRIPT_PATH}"
ExecStop=/usr/bin/tmux kill-session -t ${TMUX_SESSION}
User=pi
WorkingDirectory=/home/pi/Desktop/AssaAbloy_ED

[Install]
WantedBy=multi-user.target
EOF

# Recargar systemd y habilitar
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}.service
sudo systemctl restart ${SERVICE_NAME}.service

echo "Servicio creado y ejecutándose. Usa 'tmux attach -t ${TMUX_SESSION}' para verlo."
