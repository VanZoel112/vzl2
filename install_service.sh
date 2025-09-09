#!/bin/bash
"""
VzoelFox Service Installer
Install VzoelFox as a system service for 24/7 operation
Founder: Vzoel Fox's Lutpan
"""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# VzoelFox banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║             🦊 VzoelFox Service Installer            ║"
echo "║           Setup 24/7 System Service                 ║"
echo "║                                                      ║"
echo "║     Founder: Vzoel Fox's Lutpan                      ║"
echo "║     Version: 1.0.0 - Service Edition                ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Get current directory
CURRENT_DIR=$(pwd)
SCRIPT_PATH="$CURRENT_DIR/daemon.py"
SERVICE_NAME="vzoelfox"

echo -e "${YELLOW}🔍 Checking requirements...${NC}"

# Check if daemon.py exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo -e "${RED}❌ daemon.py not found in current directory${NC}"
    exit 1
fi

# Check if running on supported system
if command -v systemctl >/dev/null 2>&1; then
    echo -e "${GREEN}✅ systemd detected${NC}"
    SERVICE_TYPE="systemd"
elif [ -d "/etc/init.d" ]; then
    echo -e "${YELLOW}⚠️ Using init.d (legacy)${NC}"
    SERVICE_TYPE="initd"
else
    echo -e "${RED}❌ No supported service manager found${NC}"
    echo -e "${YELLOW}💡 You can still run manually: python3 daemon.py${NC}"
    exit 1
fi

echo -e "${BLUE}📝 Creating service configuration...${NC}"

# Create systemd service file
if [ "$SERVICE_TYPE" = "systemd" ]; then
    SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
    
    cat > "/tmp/${SERVICE_NAME}.service" << EOF
[Unit]
Description=VzoelFox Telegram Userbot Daemon
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_PATH
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=30

# Environment
Environment=PYTHONPATH=$CURRENT_DIR
Environment=PYTHONUNBUFFERED=1

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=vzoelfox

# Security (optional, uncomment if needed)
# NoNewPrivileges=yes
# ProtectSystem=strict
# ProtectHome=yes
# ReadWritePaths=$CURRENT_DIR

[Install]
WantedBy=multi-user.target
EOF

    echo -e "${YELLOW}🔐 Installing service (requires sudo)...${NC}"
    sudo cp "/tmp/${SERVICE_NAME}.service" "$SERVICE_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Service file installed${NC}"
        
        # Reload systemd and enable service
        sudo systemctl daemon-reload
        sudo systemctl enable "$SERVICE_NAME"
        
        echo -e "${GREEN}✅ Service enabled for auto-start${NC}"
        
        # Show service commands
        echo -e "${BLUE}"
        echo "🚀 Service Management Commands:"
        echo "├── Start:   sudo systemctl start $SERVICE_NAME"
        echo "├── Stop:    sudo systemctl stop $SERVICE_NAME"
        echo "├── Status:  sudo systemctl status $SERVICE_NAME"
        echo "├── Logs:    sudo journalctl -u $SERVICE_NAME -f"
        echo "└── Restart: sudo systemctl restart $SERVICE_NAME"
        echo -e "${NC}"
        
        # Ask if user wants to start now
        read -p "🤖 Start VzoelFox service now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo systemctl start "$SERVICE_NAME"
            sleep 2
            sudo systemctl status "$SERVICE_NAME" --no-pager
        fi
        
    else
        echo -e "${RED}❌ Failed to install service file${NC}"
        exit 1
    fi
    
elif [ "$SERVICE_TYPE" = "initd" ]; then
    # Create init.d script (legacy support)
    INIT_SCRIPT="/etc/init.d/$SERVICE_NAME"
    
    cat > "/tmp/$SERVICE_NAME" << 'EOF'
#!/bin/bash
### BEGIN INIT INFO
# Provides:          vzoelfox
# Required-Start:    $network $remote_fs
# Required-Stop:     $network $remote_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Description:       VzoelFox Telegram Userbot Daemon
### END INIT INFO

USER="$USER"
DAEMON_PATH="$CURRENT_DIR"
DAEMON="$SCRIPT_PATH"
LOCK_FILE="/var/lock/subsys/vzoelfox"

start() {
    if [ -f $LOCK_FILE ]; then
        echo "VzoelFox is already running."
        return 1
    fi
    echo "Starting VzoelFox..."
    cd $DAEMON_PATH
    sudo -u $USER python3 $DAEMON &
    echo $! > $LOCK_FILE
}

stop() {
    if [ ! -f $LOCK_FILE ]; then
        echo "VzoelFox is not running."
        return 1
    fi
    echo "Stopping VzoelFox..."
    PID=$(cat $LOCK_FILE)
    kill -TERM $PID
    rm -f $LOCK_FILE
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        start
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
esac
EOF
    
    echo -e "${YELLOW}🔐 Installing init.d script (requires sudo)...${NC}"
    sudo cp "/tmp/$SERVICE_NAME" "$INIT_SCRIPT"
    sudo chmod +x "$INIT_SCRIPT"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Init script installed${NC}"
        
        # Enable service
        sudo update-rc.d "$SERVICE_NAME" defaults
        
        echo -e "${BLUE}"
        echo "🚀 Service Management Commands:"
        echo "├── Start:   sudo service $SERVICE_NAME start"
        echo "├── Stop:    sudo service $SERVICE_NAME stop"
        echo "├── Restart: sudo service $SERVICE_NAME restart"
        echo "└── Status:  sudo service $SERVICE_NAME status"
        echo -e "${NC}"
        
    else
        echo -e "${RED}❌ Failed to install init script${NC}"
        exit 1
    fi
fi

# Clean up temp files
rm -f "/tmp/${SERVICE_NAME}.service" "/tmp/$SERVICE_NAME"

echo -e "${GREEN}🦊 VzoelFox service installation complete!${NC}"
echo -e "${BLUE}📁 Working Directory: $CURRENT_DIR${NC}"
echo -e "${BLUE}🔧 Service Name: $SERVICE_NAME${NC}"
echo -e "${YELLOW}💡 The service will auto-restart if it crashes${NC}"
echo -e "${YELLOW}📝 Logs are available through system logging${NC}"