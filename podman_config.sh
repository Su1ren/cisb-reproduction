#!/bin/bash
# 备份原配置文件
sudo cp /etc/containers/registries.conf /etc/containers/registries.conf.bak

# 写入阿里云镜像源配置
sudo tee /etc/containers/registries.conf <<EOF
unqualified-search-registries = ["docker.io"]

[[registry]]
prefix = "docker.io"
location = "hub-mirror.c.163.com"
insecure = true
EOF

# 验证配置
podman info --format '{{.Registries.Search}}'