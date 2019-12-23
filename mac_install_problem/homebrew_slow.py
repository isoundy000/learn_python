#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/5 20:57

# Mac入门--通过homebrew下载过慢问题
# 使用国内的镜像替换homebrew镜像，对镜像进行加速源
# 原先我们执行brew命令安装的时候，跟3个仓库地址有关
# 1 brew.git
# 2 homebrew-core.git
# 3 homebrew-bottles
# 把三个仓库地址全部替换成国内Alibaba提供的地址
# 1 替换/还原brew.git仓库地址
# 替换成阿里巴巴的 brew.git 仓库地址:
# cd "$(brew --repo)"
# git remote set-url origin https://mirrors.aliyun.com/homebrew/brew.git
# =======================================================

# 还原为官方提供的 brew.git 仓库地址
# cd "$(brew --repo)"
# git remote set-url origin https://github.com/Homebrew/brew.git

# 2 替换/还原homebrew-core.git仓库地址
# 替换成阿里巴巴的 homebrew-core.git 仓库地址:
# cd "$(brew --repo)/Library/Taps/homebrew/homebrew-core"
# git remote set-url origin https://mirrors.aliyun.com/homebrew/homebrew-core.git
# =======================================================

# 还原为官方提供的 homebrew-core.git 仓库地址
# cd "$(brew --repo)/Library/Taps/homebrew/homebrew-core"
# git remote set-url origin https://github.com/Homebrew/homebrew-core.git

# 3 替换/还原homebrew-bottles
#  3.1 这个步骤跟你的macOs系统使用的shell版本有关系，首先查看shell版本
# echo $SHELL
# 如果你的输出结果是 /bin/zsh，参考?的 zsh 终端操作方式
# 如果你的输出结果是 /bin/bash，参考?的 bash 终端操作方式

# 3.2 zsh终端操作方式
# 替换成阿里巴巴的 homebrew-bottles 访问地址:
# echo 'export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.aliyun.com/homebrew/homebrew-bottles' >> ~/.zshrc
# source ~/.zshrc
# =======================================================

# 还原为官方提供的 homebrew-bottles 访问地址
# vi ~/.zshrc
# 然后，删除 HOMEBREW_BOTTLE_DOMAIN 这一行配置
# source ~/.zshrc

# 3.3 bash终端操作方式
# 替换 homebrew-bottles 访问 URL:
# echo 'export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.aliyun.com/homebrew/homebrew-bottles' >> ~/.bash_profile
# source ~/.bash_profile
# =======================================================

# 还原为官方提供的 homebrew-bottles 访问地址
# vi ~/.bash_profile
# 然后，删除 HOMEBREW_BOTTLE_DOMAIN 这一行配置
# source ~/.bash_profile