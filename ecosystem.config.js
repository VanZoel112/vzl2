/**
 * PM2 Ecosystem Configuration
 * Manages multiple bots: VZL2 Userbot & Vzoelmenfess Bot
 *
 * Commands:
 *   pm2 start ecosystem.config.js       - Start all bots
 *   pm2 stop all                        - Stop all bots
 *   pm2 restart all                     - Restart all bots
 *   pm2 logs                            - View all logs
 *   pm2 logs vzl2                       - View vzl2 logs only
 *   pm2 logs vzoelmenfess               - View vzoelmenfess logs only
 *   pm2 monit                           - Monitor all processes
 *   pm2 save                            - Save current process list
 *   pm2 startup                         - Generate startup script
 *
 * ~2025 by Vzoel Fox's Lutpan
 */

module.exports = {
  apps: [
    {
      // VZL2 Userbot (Telethon Python)
      name: 'vzl2',
      script: 'main.py',
      cwd: '/data/data/com.termux/files/home/vzl2',
      interpreter: 'python3',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        PYTHONUNBUFFERED: '1',
        NODE_ENV: 'production'
      },
      error_file: '/data/data/com.termux/files/home/logs/vzl2-error.log',
      out_file: '/data/data/com.termux/files/home/logs/vzl2-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000,
      kill_timeout: 5000
    },

    {
      // Vzoelmenfess Bot (Node.js Telegram Bot)
      name: 'vzoelmenfess',
      script: 'bot.js',
      cwd: '/data/data/com.termux/files/home/vzoelmenfess',
      interpreter: 'node',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        NODE_ENV: 'production'
      },
      error_file: '/data/data/com.termux/files/home/logs/vzoelmenfess-error.log',
      out_file: '/data/data/com.termux/files/home/logs/vzoelmenfess-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000,
      kill_timeout: 5000
    }
  ]
};
