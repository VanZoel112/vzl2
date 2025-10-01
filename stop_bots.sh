#!/data/data/com.termux/files/usr/bin/bash
# Stop All Vzoel Bots
# ~2025 by Vzoel Fox's Lutpan

echo "🛑 Stopping all bots..."
echo ""

pm2 stop all

echo ""
echo "✅ All bots stopped!"
echo ""
pm2 list
echo ""
