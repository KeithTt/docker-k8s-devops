#/bin/sh

yum install -y git vim gcc glibc-static telnet
yum install -y curl policycoreutils-python openssh-server
systemctl enable sshd
systemctl start sshd

yum install postfix
systemctl enable postfix
systemctl start postfix

cp gitlab-ce.repo /etc/yum.repos.d/
yum makecache
EXTERNAL_URL="http://gitlab.example.com" yum install -y gitlab-ce

gitlab-ctl reconfigure
