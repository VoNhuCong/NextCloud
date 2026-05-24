# NextCloud
Hướng dẫn cài đặt nextcloud trên ubuntu

# Chuẩn bị
Bước 1: hệ điều hành ubuntu
Bước 2: tạo thư mục để chứa data của nextcloud
mkdir /home/username/Documents/nextcloud
Bước 3: tạo thư mục chứa volume để nhét data của nextcloudo vào
Bước 4: tạo file docker-compose.yaml trong thư mục nextcloud
===============================================
version: '2'

services:
  db:
    image: mariadb:10.6
    restart: always
    command: --transaction-isolation=READ-COMMITTED --binlog-format=ROW
    volumes:
      - db:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=yourpass
      - MYSQL_PASSWORD=yourpass
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud

  app:
    image: nextcloud
    restart: always
    ports:
      - 8080:80
    links:
      - db
    volumes:
      # Thay đổi dòng này:
      - /home/username/Documents/nextcloud/NCDate:/var/www/html
    environment:
      - MYSQL_PASSWORD=yourpass
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_HOST=db
volumes:
  db:
===========================================================

# Các bước cài đặt
Bước 1: Chạy docker-compose up -d
Bước 2: Truy cập vào trang admin http://ip:8080 tạo tài khoản và mật khẩu admin
Bước 3: cài đặt cho lên mobile
Bước 4: Cài đặt preview
	4.1 Vào container: sudo docker exec -it -u 0 nextcloud_app_1 bash
	Sau khi vào được container thì chạy lệnh sau
	apt update && apt install -y libmagickwand-dev imagemagick ghostscript ffmpeg && rm -rf /var/lib/apt/lists/*
  4.2 
	sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 0 --value="OC\Preview\Movie"
  sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 1 --value="OC\Preview\PNG"
	sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 2 --value="OC\Preview\JPEG"
	sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 3 --value="OC\Preview\GIF"
	sudo docker exec -it -u www-data nextclou _app_1 php occ config:system:set enabledPreviewProviders 4 --value="OC\Preview\BMP"
	sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 5 --value="OC\Preview\XBitmap"
	sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 6 --value="OC\Preview\MP3"
	sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 7 --value="OC\Preview\TXT"
	sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 8 --value="OC\Preview\MarkDown"
  sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 9 --value="OC\Preview\MOV"
	sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 10 --value="OC\Preview\MP4"
	sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 11 --value="OC\Preview\mov"
	sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set enabledPreviewProviders 12 --value="OC\Preview\mp4"

  4.3 Vào trang web nextcloud để cài đặt thêm app Preview Generator
  
	4.4 sudo docker exec -it -u www-data nextcloud_app_1 php occ preview:generate-all -vvv
  
	4.5 sudo crontab -e
	Gán dòng sau vào cuối cùng, mục tiêu là sau 1 phút thì nó sẽ tạo preview một lần
	*/1 * * * * docker exec -u www-data nextcloud_app_1 php occ preview:pre-generate >> /home/username/Documents/nextcloud/crontab_gen_preview/crontab.log 2>&1

	sudo cloudflared tunnel --url http://192.168.0.6:8080
	sudo docker exec -it -u www-data nextcloud_app_1 php occ config:system:set trusted_domains 1 --
value=tiger-related-blades-completing.trycloudflare.com

