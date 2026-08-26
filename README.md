# NextCloud
Hướng dẫn cài đặt nextcloud trên ubuntu

## B1 Chuẩn bị
1. Hệ điều hành ubuntu.  
2. Tạo thư mục để chứa data của nextcloud: mkdir /home/username/Documents/nextcloud  
3. Tạo thư mục chứa volume để nhét data của nextcloudo vào  
4. Cấu hình user/pass trong file docker-compose.yml 

## B2 Các bước cài đặt Nextcloud
1. Chạy nextcloud  
```
docker-compose up -d
```  
2. Truy cập vào trang admin http://ip:8080 để cài ứng dụng nextcloud và tạo tài khoản, mật khẩu admin.
3. Cài đặt cho lên mobile.  
4. Cài đặt preview.  
* Cài các gói thư viện cần thiết  
```
sudo docker exec -it -u 0 nextcloud_app_1 bash
```
Sau khi vào được container thì chạy lệnh sau  
```
apt update && apt install -y libmagickwand-dev imagemagick ghostscript ffmpeg && rm -rf /var/lib/apt/lists/*
``` 
* Cài đặt các định dạng cần gen preview  
```
sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 0 --value="OC\Preview\Movie"
sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 1 --value="OC\Preview\PNG"
sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 2 --value="OC\Preview\JPEG"
sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 3 --value="OC\Preview\GIF"
sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 4 --value="OC\Preview\BMP"
sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 5 --value="OC\Preview\XBitmap"
sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 6 --value="OC\Preview\MP3"
sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 7 --value="OC\Preview\TXT"
sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 8 --value="OC\Preview\MarkDown"
sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 9 --value="OC\Preview\MOV"
sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 10 --value="OC\Preview\MP4"
sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 11 --value="OC\Preview\mov"
sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 12 --value="OC\Preview\mp4"
```

* Vào trang web nextcloud để cài đặt thêm app Preview Generator
  
* Tạo các preview cho hình ảnh và video hiện đang có
```
sudo docker exec -it -u www-data nextcloud_app_1 php occ preview:generate-all -vvv
```
* Lên lịch gen preview định kì cho các file mới
```
sudo crontab -e
```
Gán dòng sau vào cuối cùng, mục tiêu là sau 1 phút thì nó sẽ tạo preview một lần
```
*/1 * * * * docker exec -u www-data nextcloud_app_1 php occ preview:pre-generate >> /home/username/Documents/nextcloud/crontab_gen_preview/crontab.log 2>&1
```
## B3 tạo link cloudflared để truy cập cloud từ bất kì đâu
1. Cài đặt cloudflared
```
 curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
```
```
 sudo dpkg -i cloudflared.deb
```
2. Lệnh chay tunel thủ công
```
sudo cloudflared tunnel --url http://192.168.0.6:8080
```
3. Thiết lập trust domain cho nextcloud
```
sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set trusted_domains 1 --value=domain
```
## B4 thiết lập tailscale để truy cập server từ xa
1. Cài tailscale
```
curl -fsSL https://tailscale.com/install.sh | sh
```
2. Khởi chạy tailscalse
```
sudo tailscale up
```
Hãy copy link mà tailscale log ra và mở trên browser mà bạn đã login tài khoản tailscale để đăng ký device
3. Kiểm tra trạng thái và set khởi động cho tailscalse
```
sudo tailscale status
sudo systemctl enable --now tailscaled
sudo tailscale set --ssh
```


