#!/bin/bash

# 确保脚本的所有后续命令都以 root 用户身份执行
# 这对于解决 actions/checkout 的 EACCES 权限问题至关重要
exec sudo -E bash -c "$*"
