#!/data/data/com.termux/files/usr/bin/bash
# Restart All Vzoel Bots
# ~2025 by Vzoel Fox's Lutpan

echo "🔄 Restarting all bots..."
echo ""

pm2 restart all

echo ""
echo "✅ All bots restarted!"
echo ""
pm2 list
echo ""
