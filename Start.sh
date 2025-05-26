# Añadir la configuración de IP estática al script Start.sh ya existente

start_sh_ip_static = """#!/bin/bash

echo "🔧 Configurando Raspberry Pi para entorno embebido sin GUI..."

# 1. Desinstalar entorno gráfico
echo "🧹 Eliminando entorno gráfico innecesario..."
sudo apt purge --autoremove -y xserver-common lightdm lxde* openbox x11-common raspberrypi-ui-mods lxappearance gpicview lxterminal gvfs* gnome* x11* lightdm*

# 2. Limpiar paquetes residuales
sudo apt autoremove -y
sudo apt clean

# 3. Activar autologin en consola
echo "🔁 Estableciendo arranque en consola con login automático..."
sudo raspi-config nonint do_boot_behaviour B2

# 4. Instalar tmux si no existe
if ! command -v tmux &> /dev/null; then
  echo "📦 Instalando tmux..."
  sudo apt update
  sudo apt install -y tmux
fi

# 5. Configurar ~/.bash_profile para ejecutar el sistema automáticamente
echo "📝 Configurando ~/.bash_profile..."
cat <<EOL > ~/.bash_profile
# Autoejecutar sistema Scanner_ED con tmux al iniciar sesión en consola
if [ -z "\\$TMUX" ]; then
  tmux new-session -A -s laser_session 'python3 /home/pi/Desktop/Scanner_ED/main.py'
fi
EOL

# 6. Configurar IP estática en eth0
echo "🌐 Configurando IP estática para eth0..."
sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.bak
echo '
interface eth0
static ip_address=192.168.10.80/24
static routers=
static domain_name_servers=
static domain_search=
' | sudo tee -a /etc/dhcpcd.conf

echo "✅ Configuración completa. Reinicia la Raspberry Pi para aplicar los cambios:"
echo "   sudo reboot"
"""

# Guardar como Start.sh
start_sh_path = "/mnt/data/Start.sh"
with open(start_sh_path, "w") as f:
    f.write(start_sh_ip_static)

import os
os.chmod(start_sh_path, 0o755)

start_sh_path
