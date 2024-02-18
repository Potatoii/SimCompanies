<p align="center">
   <img src="https://d1fxy698ilbz6u.cloudfront.net/static/images/new_logo-300x300.b5c0ea3d6485.png" width="200" height="200" alt="logo"/>
</p>

<div align="center">

# SimBot

*✨ Simcompanies建筑物监控 ✨*

<img src="https://img.shields.io/badge/python-3.11-blue?logo=python&logoColor=edb641" alt="python">

*✨ 让你的工人不再摸鱼 ✨*

</div>

## 简介

SimBot是一个Python的simcompanies建筑物监控, 每5-6分钟检查一下你的建筑物有没有在摸鱼

## 开始

### 配置

在项目目录中有一个`config.toml`文件, 拷贝一个并命名为`config.local.toml`, 填写内容(邮件通知和Bark通知至少填一个)

### 运行

1. 安装并切换到python3.11环境(virtualenv | conda | etc.)
2. 安装项目依赖

   ```bash
   pip install -r requirements.txt
   ```
3. 运行项目

   ```bash
   python main.py
   ```

### Docker

1. 在本地创建配置文件`config.local.toml`

2. ```bash
   docker-compose up -d
   ```

## 通知方式

### 邮箱

使用**SMTP**配置, 具体使用方法参考邮箱设置中的说明

举例: QQ邮箱的SMTP配置

```json
{
  "host": "smtp.qq.com",
  "port": 465,
  "username": "你的邮箱地址",
  "password": "QQ邮箱的授权码"
}
```

- 163邮箱host改成smtp.163.com相同
- gmail直接使用邮箱和密码即可

### Bark

Bark是一款开源的IOS自定义通知App, 链接[Finb/Bark](https://github.com/Finb/Bark)

<img src="https://camo.githubusercontent.com/0e5564bc970291ae1ddbc1cee4bdc1e5374d027a7001fe79fc1b862401f1bfe6/68747470733a2f2f7778342e73696e61696d672e636e2f6d77323030302f30303372596671706c7931677264316d65717276636a3630626930387a74396930322e6a7067"  width="320" height="260" alt="bark"/>

复制这里的链接, 截取图中"Your Key"的内容填在SimBot的**config.local.toml**的**bark_key**中, 即可开始使用Bark通知
