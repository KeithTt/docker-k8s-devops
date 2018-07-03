https://hub.docker.com/_/mysql/
https://hub.docker.com/_/wordpress/

https://docs.docker.com/compose/compose-file/

拉取镜像
# docker pull mysql:5.7 wordpress

运行数据库
# docker run -d --name mysql -v mysql:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=abc123456 -e MYSQL_DATABASE=wordpress mysql:5.7

运行wordpress
# docker run -d -e WORDPRESS_DB_HOST=mysql:3306 --link mysql -p 8080:80 --name wordpress wordpress
