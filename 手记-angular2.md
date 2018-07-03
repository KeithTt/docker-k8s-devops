# 通过 Multi-Stage Build 实现多阶段Build Docker镜像

我们在上一次推送中，中给大家介绍了如何完全使用Docker搭建Angular开发和测试环境，今天我们接着这个话题给大家看看如果通过Docker部署Angular项目。

我们先看看假如没有Docker，我们一般怎么去部署Angular项目，这里我们只是简要的说一下，具体大家可以search一下。简单来说，就是两步：

* ng build
* 部署到nginx

## ng build

``ng build`` 可以通过我们上一次的手记很容易的实现，比如：

```bash

➜  demo git:(master) ✗ docker run -it --rm  -v /Users/penxiao/tmp/angular-docker/demo:/app xiaopeng163/angular-docker ng build --prod --build-optimizer

Date: 2018-05-29T04:34:04.908Z
Hash: 20f91a64e38bdd57971e
Time: 20712ms
chunk {0} runtime.a66f828dca56eeb90e02.js (runtime) 1.05 kB [entry] [rendered]
chunk {1} styles.34c57ab7888ec1573f9c.css (styles) 0 bytes [initial] [rendered]
chunk {2} polyfills.2f4a59095805af02bd79.js (polyfills) 59.6 kB [initial] [rendered]
chunk {3} main.9996999996d01fca7c37.js (main) 155 kB [initial] [rendered]
➜  demo git:(master) ✗ ls
README.md         angular.json      dist              e2e               node_modules      package-lock.json package.json      src               tsconfig.json     tslint.json
➜  demo git:(master) ✗ cd dist
➜  dist git:(master) ✗ ls
demo
➜  dist git:(master) ✗ cd demo
➜  demo git:(master) ✗ ls
3rdpartylicenses.txt              index.html                        polyfills.2f4a59095805af02bd79.js styles.34c57ab7888ec1573f9c.css
favicon.ico                       main.9996999996d01fca7c37.js      runtime.a66f828dca56eeb90e02.js
➜  demo git:(master) ✗
```

大家可以看到，通过 ``ng build --prod --build-optimizer`` 可以生成dist目录，然后我们本地测试的话可以通过 ``ng serve`` 起一个简单的本地测试服务器，然后打开浏览器访问了。

## Nginx

如果用nginx，我们只需要把dist/demo扔到Nginx的/usr/share/nginx/html目录，然后重启nginx就可以了，这个过程也可以通过Docker实现。

```bash
docker run -d -p 80:80  -v /Users/penxiao/tmp/angular-docker/demo/dist/demo:/usr/share/nginx/html nginx:1.13.3-alpine
```

然后打开浏览器访问 http://127.0.0.1/ 就可以了。

## 二合一

所谓multi-stage build其实就是一个二合一的过程。

假如我们有一个Angular的项目，然后我们想发布一个image，用户通过这个image创建一个container，然后就能访问到我们的Angular了。怎么实现呢？

### 第一种办法

按照下面的步骤写一个Dockerfile

* 准备一个base的docker image
* 在里面安装node，Angular，还有nginx
* 把Angular项目源码add到里面
* ng build产生dist目录
* 配置nginx html为dist目录内容
* 启动nginx

这种办法行的通，但是问题很多

* 首先，为了满足node，Angular，nginx的运行环境，需要按照很多软件和依赖，导致最终build出来的image特别大
* 要包含我们Angular项目的源码

这时候就可以引入multi-stage build了。

### 第二种办法

其实通过前面的例子我们就会想，可不可以先通过一个docker image build出来一个dist目录，然后再把这个dist目录ADD到一个很小的nginx的docker image里，这样我们启动这个nginx image就能访问我们的Angular项目了。这就是multi-stage build

我们直接看这个Dockerfile

```bash
➜  demo git:(master) ✗ ls
Dockerfile        README.md         angular.json      e2e               node_modules      package-lock.json package.json      src               tsconfig.json     tslint.json
➜  demo git:(master) ✗ more Dockerfile
# 第一个阶段：构建angular

FROM node:8-alpine as builder

COPY package.json package-lock.json ./

RUN npm set progress=false && npm config set depth 0 && npm cache clean --force

RUN npm i && mkdir /ng-app && cp -R ./node_modules ./ng-app

WORKDIR /ng-app

COPY . .

## 构建angular，生产模式
RUN $(npm bin)/ng build --prod --build-optimizer

### 第二阶段，setup到nginx

FROM nginx:1.13.3-alpine

## 删除默认的html
RUN rm -rf /usr/share/nginx/html/*

## 把第一阶段构建的输出dist，copy到nginx的html目录
COPY --from=builder /ng-app/dist/demo /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]

➜  demo git:(master) ✗
```

我们通过这个Dockerfile build出来的image非常小，只有10几兆

```bash
➜  demo git:(master) ✗ docker image ls
REPOSITORY                   TAG                 IMAGE ID            CREATED             SIZE
angular-demo                 latest              972e12e7c209        3 minutes ago       15.7MB
```

这个image可以用于发布，也可以用于部署，启动非常简单，只需要在本地

```bash
docker run -d -p 80:80 angular-demo
```

然后打开浏览器访问 http://127.0.0.1/ 就可以了。

## 最后

通过这两次的手记，相信大家能体会到Docker的强大，可以这么说，在本地只需要有Docker，就基本可以干任何事情。 这里给大家布置个作业，大家可以举一反三。

作业：

不知道大家对sphinx熟悉不熟悉，http://www.sphinx-doc.org/en/master/ 用sphinx可以写出非常漂亮的文档，如果要部署这个文档，步骤和Angular类似，也是需要先把rst文件build成html，然后把html扔个nginx，就可以了。大家可以尝试一下。如何在本地连Python环境都没有的情况下，去创建，维护，部署一个sphinx文档项目。