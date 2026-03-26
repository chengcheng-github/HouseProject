FROM python:3.9.12-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt
COPY ./requirements.txt /tmp

# 安装Python依赖
RUN pip3 install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r /tmp/requirements.txt

# 复制应用代码
COPY .  /application/

# 设置工作目录
WORKDIR /application/