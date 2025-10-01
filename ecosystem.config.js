module.exports = {
  apps: [{
    name: 'vzl2',
    script: 'main.py',
    interpreter: 'python',
    cwd: '/data/data/com.termux/files/home/vzl2',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production',
    },
    error_file: './logs/vzl2-error.log',
    out_file: './logs/vzl2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    restart_delay: 4000,
    max_restarts: 10,
    min_uptime: '10s',
  }]
};
