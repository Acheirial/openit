FROM python:3

EXPOSE 80/tcp
LABEL maintainer="Acheirial"

# init TimeZone
ENV TZ=Asia/Shanghai \
    DEBIAN_FRONTEND=noninteractive
RUN ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime; \
    echo ${TZ} > /etc/timezone; \
    dpkg-reconfigure --frontend noninteractive tzdata; \
    rm -rf /var/lib/apt/lists/*

# init apache
RUN apt update; \
    apt install -y --no-install-recommends apache2 curl ca-certificates gzip; \
    rm -rf /var/lib/apt/lists/*

ENV in_docker true
WORKDIR /usr/src/clashcheck

# install requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x fetch-mihomo.sh start.sh && ./fetch-mihomo.sh linux amd64
RUN rm -r /var/www/html; ln -s /usr/src/clashcheck/data /var/www/html

# start apache & start clashcheck with while
CMD ["./start.sh"]
