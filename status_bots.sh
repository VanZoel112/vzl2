#!/data/data/com.termux/files/usr/bin/bash
# Check Status of All Vzoel Bots
# ~2025 by Vzoel Fox's Lutpan

echo "📊 Vzoel Bots Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

pm2 list

echo ""
echo "💾 Memory Usage:"
pm2 jlist | grep -E "name|memory" | head -20

echo ""
echo "⏱️  Uptime:"
pm2 jlist | grep -E "name|pm_uptime" | head -20

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 Commands:"
echo "   pm2 logs vzl2            - View VZL2 logs"
echo "   pm2 logs vzoelmenfess    - View Menfess logs"
echo "   pm2 monit                - Live monitoring"
echo ""
