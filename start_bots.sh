#!/data/data/com.termux/files/usr/bin/bash
# Start All Vzoel Bots with PM2
# ~2025 by Vzoel Fox's Lutpan

echo "🤖 Starting Vzoel Bots..."
echo ""

# Start PM2 ecosystem
pm2 start ~/ecosystem.config.js

echo ""
echo "✅ All bots started!"
echo ""
echo "📊 Process Status:"
pm2 list

echo ""
echo "💡 Useful Commands:"
echo "   pm2 logs              - View all logs"
echo "   pm2 monit             - Monitor processes"
echo "   pm2 stop all          - Stop all bots"
echo "   pm2 restart all       - Restart all bots"
echo ""
