#/bin/sh

yum install -y git vim gcc glibc-static telnet bridge-utils

# install docker
curl -fsSL get.docker.com -o get-docker.sh
sh get-docker.sh

# start docker service
groupadd docker
gpasswd -a vagrant docker
systemctl start docker

rm -rf get-docker.sh
