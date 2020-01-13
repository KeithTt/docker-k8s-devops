# Docker最佳实践：构建最小镜像

镜像大小其实是衡量我们容器打包技术的重要指标，我们应该在不影响应用正常运行的情况下，尽量让我们的容器镜像变得更小，这样，不管是从安全还是维护效率角度来讲，都是最佳实践。

本文我们从两种情况阐述我们的问题和解决方案，我们从实现我们的application的编程语言角度，按照语言是解释型还是编译型语言来演示如何解决容器镜像体积大的问题。

## 解释型语言

大部分的脚本语言都是解释型语言，像Ruby，Python，PHP等，我们只需要把我们的代码扔给解释器，解释器去运行就好了，但是这里的解释器有大有小，为什么？

首先Docker为一些“懒人”准备了一种Docker Image，比如Python，那么我们可以非常方便的从DockerHub上拉取某一个版本的Python镜像，比如Python3.6

```bash
$ docker image ls
python                         3.6.5               a5b7afcfdcc8        2 weeks ago         912MB
python                         3.6.5-alpine        27e79c0fa4d2        2 months ago        87.4MB
```

我们会看到，同样是3.6.5， alpine linux的docker image就小了非常非常多，是普通的python3.6.5十分之一大小，为什么呢？
主要是因为为了照顾“懒人”，Python:3.6.5 image预先安装了大量python的工具和编译的头文件等，包括C的编译环境等等。

而python:3.6.5-alpine 基本上除了Linux系统必须的一些文件以外，基本只包含基本的Python运行环境，例如像 `gcc` 等工具是不会预先安装的，都是用户需要的时候自行安装。

所以进一步来讲，我们要打包我们的Python应用，使用以上这两种base image的效果就显而易见了，一个打包完的image会上G大小，另一个只有100M左右。

例如下面是一个python flask的Dockerfile

```shell
FROM python:3.6-alpine

LABEL maintainer="XYZ <xxx@xxx.com>"

RUN apk add --no-cache gcc musl-dev

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8000

CMD []

```

## 编译型语言

使用编译型语言（例如C，Go等）编写的应用程序打包成Docker镜像，这里面的优化空间就更大了，我们以Go语言为例。

假如我们有一个Go APP，假如使用普通的go image，那么我们构建出来的镜像会很大，
例如这个app (https://github.com/golang/example/blob/master/outyet/Dockerfile)

```bash
FROM golang:onbuild
EXPOSE 8080
```

构建完的docker image 700多M。

```bash
$ docker images go-demo
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
go-demo             latest              f562d6efa39c        21 seconds ago      707MB
```

然后利用前面我们讲的，我们可以替换base image，选择一个alpine的base image，例如：

```bash
FROM golang:alpine
WORKDIR /app
ADD . /app
RUN cd /app && go build -o goapp
EXPOSE 8080
ENTRYPOINT ./goapp
```

构建的image，只有不到400M。

```bash
 $ docker images go-demo
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
go-demo             latest              f562d6efa39c        3 minutes ago       707MB
$ docker images go-demo-alpine
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
go-demo-alpine      latest              a16d2986dbd1        9 seconds ago       385MB
```

但是，我们还可以让我们的image变得更小。根据我们之前讲的分阶段build，我们可以分阶段build我们的APP，然后最终只需要在一个很小的image里，运行我们程序编译后的结果即可，例如

```bash
FROM golang:alpine AS build-env
WORKDIR /app
ADD . /app
RUN cd /app && go build -o goapp

FROM alpine
RUN apk update && \
   apk add ca-certificates && \
   update-ca-certificates && \
   rm -rf /var/cache/apk/*
WORKDIR /app
COPY --from=build-env /app/goapp /app
EXPOSE 8080
ENTRYPOINT ./goapp
```

这样，又能省掉一部分空间。只有13M，惊不惊喜！！！

```bash
$ docker images go-demo-muti-build
REPOSITORY           TAG                 IMAGE ID            CREATED             SIZE
go-demo              latest              f562d6efa39c        3 minutes ago       707MB
go-demo-alpine       latest              a16d2986dbd1        9 seconds ago       385MB
go-demo-muti-build   latest              1b1237a8fe0e        20 seconds ago      13.5MB
```

## 总结

所以，我们每次build自己的docker image的时候，一定要思考一下，怎么才能让我们的docker image变得更加小巧，
更小的image其实也是更安全的，因为冗余的软件包少，那么漏洞就相应的少，另外小的docker image方便移动，不管是docker push还是pull，速度都很快。
