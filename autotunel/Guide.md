## B1 Chuẩn bị
### Kill một process
```
sudo kill -9 326429 326447 326449 326496 326497
sudo pkill -9 -f 'autotunel.py'
```
### Kiểm tra còn đang chạy không 
ps aux | grep autotunel

## B2 Tạo service
### Tạo file
sudo vim /etc/systemd/system/autotunel.service
### Dán vào
[Unit]
Description=Auto Cloudflare Tunnel for Nextcloud
After=network-online.target docker.service
Wants=network-online.target
Requires=docker.service

[Service]
Type=simple

User=root
Group=root

WorkingDirectory=/home/vncong/Documents/autotunel

ExecStart=/usr/bin/python3 /home/vncong/Documents/autotunel/autotunel.py

Restart=always
RestartSec=10

Environment=PYTHONUNBUFFERED=1

StandardOutput=append:/home/vncong/Documents/autotunel/autotunel.log
StandardError=append:/home/vncong/Documents/autotunel/autotunel.log

[Install]
WantedBy=multi-user.target

### Khỏi động lại systemd
sudo systemctl daemon-reload
sudo systemctl enable autotunel.service
sudo systemctl status autotunel.service

### Check log
sudo journalctl -u autotunel.service -n 100 --no-pager
sudo journalctl -u autotunel.service -f
tail -f ~/Documents/autotunel/autotunel.log




