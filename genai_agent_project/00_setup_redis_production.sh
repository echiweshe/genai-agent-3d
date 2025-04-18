#!/bin/bash
set -e

echo "🔧 Installing Redis..."
sudo apt update && sudo apt install -y redis-server logrotate

echo "📦 Backing up original Redis config..."
sudo cp /etc/redis/redis.conf /etc/redis/redis.conf.backup

echo "🛠️ Writing production redis.conf..."
cat <<EOF | sudo tee /etc/redis/redis.conf > /dev/null
bind 127.0.0.1
port 6379
supervised systemd
dir /var/lib/redis
logfile /var/log/redis/redis.log
loglevel notice

save 900 1
save 300 10
save 60 10000

maxmemory 512mb
maxmemory-policy allkeys-lru

appendonly yes
appendfilename "appendonly.aof"
EOF

echo "🛠️ Creating redis.service with system hardening..."
cat <<EOF | sudo tee /etc/systemd/system/redis.service > /dev/null
[Unit]
Description=Redis In-Memory Data Store
After=network.target

[Service]
User=redis
Group=redis
ExecStart=/usr/bin/redis-server /etc/redis/redis.conf
ExecStop=/usr/bin/redis-cli shutdown
Restart=always
LimitNOFILE=10000
PrivateTmp=true
ProtectSystem=full
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

echo "🌀 Reloading systemd and restarting Redis..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable redis
sudo systemctl restart redis

echo "🧹 Setting up logrotate for Redis..."
cat <<EOF | sudo tee /etc/logrotate.d/redis > /dev/null
/var/log/redis/redis.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 640 redis adm
    sharedscripts
    postrotate
        /bin/systemctl restart redis.service > /dev/null
    endscript
}
EOF

echo "✅ Redis is now running in production mode."
echo "🪵 Log file: /var/log/redis/redis.log"
echo "🛠️  Monitor: sudo journalctl -u redis -f"
echo "🔍 Redis CLI monitor: redis-cli monitor"
