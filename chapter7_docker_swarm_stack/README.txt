# RAFT通俗解释

http://thesecretlivesofdata.com/raft/

# docker swarm init --advertise-addr 192.168.135.176

# docker swarm join --token SWMTKN-1-3d1j9jq5sw1e8kwwtt8iebr231rp5dyjprs4g8f7zg76twed0i-8gc3obh2vb7wg308zznlvhr0p 192.168.135.176:2377
This node joined a swarm as a worker.

# docker node ls

创建一个service
# docker service create --name demo busybox sh -c "while true; do sleep 3600; done"
# docker service ls
# docker service ps demo

水平扩展
# docker service scale demo=3
# docker service ls
# docker service ps demo

删除一个service
# docker service rm demo

部署WordPress
# docker network create -d overlay demo
# docker service create --name mysql --env MYSQL_ROOT_PASSWORD=abc123456 --env MYSQL_DATABASE=wordpress --network=demo --mount type=volume,source=mysql-data,destination=/var/lib/mysql mysql:5.7
# docker service create --name wordpress -p 80:80 --env WORDPRESS_DB_PASSWORD=abc123456 --env WORDPRESS_DB_HOST=mysql --network=demo wordpress
# docker service ps mysql wordpress

Routing Mesh
- Internal：容器和容器之间通过Overlay（VIP）网络访问
- Ingress：可以通过swarm集群的任意节点访问service

Ingress
- 外部访问的负载均衡
- 服务端口被暴露到swarm集群的每个节点
- 内部通过IPVS进行负载均衡

# docker service create --name whoami -p 8000:8000 --network demo jwilder/whoami
# docker service create --name client --network demo busybox sh -c "while true; do sleep 3600; done"
# docker service ls
# docker service ps whoami client
# docker service scale whoami=2

# docker exec -it 23314069ee5f sh
# ping whoami
# ip a

/ # nslookup whoami
Server:    127.0.0.11
Address 1: 127.0.0.11

Name:      whoami
Address 1: 10.0.0.9 bogon

/ # nslookup tasks.whoami
Server:    127.0.0.11
Address 1: 127.0.0.11

Name:      tasks.whoami
Address 1: 10.0.0.10 whoami.1.sb5rocjb61qlgk76gz820proq.demo
Address 2: 10.0.0.13 2c068ea6ae52.demo

# cd /var/run/docker/netns
# nsenter --net=ingress_sbox
# ip a
# iptables -vnL -t mangle
# ipvsadm -ln
Prot LocalAddress:Port Scheduler Flags
  -> RemoteAddress:Port           Forward Weight ActiveConn InActConn
FWM  260 rr
  -> 10.255.0.8:0                 Masq    1      0          0         
  -> 10.255.0.9:0                 Masq    1      0          0

源码：
https://github.com/dockersamples/example-voting-app

https://docs.docker.com/compose/compose-file/#deploy
https://docs.docker.com/engine/reference/commandline/stack_deploy/

使用stack部署wordpress
# docker stack deploy wordpress --compose-file=docker-compose.yml
# docker stack ls
# docker stack ps wordpress
# docker stack services wordpress
# docker stack rm wordpress

使用stack部署voting
# docker stack deploy voting --compose-file=docker-compose.yml

Secret管理
# echo admin123 > ./password
# docker secret create my-pw ./password
# docker secret ls
