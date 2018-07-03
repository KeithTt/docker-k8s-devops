# installation

From: https://github.com/coreos/prometheus-operator

rbac:
```shell
kubectl create -f rbac.yml
```

prometheus:
```shell
kubectl create -f prometheus.yml
kubectl create -f prometheus-resource.yml
```

Kubernetes monitoring:
```shell
kubectl create -f kubernetes-monitoring.yml
```

Example app:
```shell
kubectl create -f example-app.yml
```
