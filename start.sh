#!/bin/bash
# Vzoel Fox's Lutpan - PM2 Start Script

cd /data/data/com.termux/files/home/vzl2

echo "🦊 Starting Vzoel Fox's Lutpan with PM2..."

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "❌ PM2 not installed. Installing..."
    npm install -g pm2
fi

# Stop if already running
pm2 stop vzl2 2>/dev/null || true
pm2 delete vzl2 2>/dev/null || true

# Start with ecosystem config
pm2 start ecosystem.config.js

# Save PM2 process list
pm2 save

# Show status
pm2 status

echo ""
echo "✅ Vzoel Fox's Lutpan started!"
echo ""
echo "Commands:"
echo "  pm2 status       - Check status"
echo "  pm2 logs vzl2    - View logs"
echo "  pm2 restart vzl2 - Restart bot"
echo "  pm2 stop vzl2    - Stop bot"
echo "  pm2 monit        - Monitor resources"
