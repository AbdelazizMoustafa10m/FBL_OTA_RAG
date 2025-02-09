module.exports = {
  apps: [{
    name: 'fbl-ota-rag',
    script: 'uvicorn',
    args: 'main:app --host 0.0.0.0 --port 8000',
    interpreter: '/Users/abdelazizmoustafa/Desktop/prj/simple_rag/venv/bin/python3',
    env: {
      NODE_ENV: 'production',
    },
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    exp_backoff_restart_delay: 100,
    restart_delay: 1000,
    max_restarts: 10,
    error_file: 'logs/err.log',
    out_file: 'logs/out.log',
    merge_logs: true,
    time: true
  }, {
    name: 'fbl-ota-tunnel',
    script: 'cloudflared',
    args: 'tunnel --config /Users/abdelazizmoustafa/Desktop/prj/simple_rag/cloudflared.yml run',
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    exp_backoff_restart_delay: 100,
    restart_delay: 1000,
    max_restarts: 10,
    error_file: 'logs/tunnel-err.log',
    out_file: 'logs/tunnel-out.log',
    merge_logs: true,
    time: true
  }]
}
