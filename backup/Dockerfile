FROM debian:bullseye-slim

ARG TARGETARCH
ARG POSTGRES_VERSION

WORKDIR /root
COPY scripts/* .

RUN apt-get update && apt-get install -y \
    jq \
    curl \
    gnupg \
    lsb-release \
    ca-certificates \
    awscli \
    openssl \
    && update-ca-certificates \
    && curl -L https://github.com/ivoronin/go-cron/releases/download/v0.0.5/go-cron_0.0.5_linux_${TARGETARCH}.tar.gz -o /usr/local/bin/go-cron.tar.gz \
    && tar -xzvf /usr/local/bin/go-cron.tar.gz -C /usr/local/bin \
    && rm /usr/local/bin/go-cron.tar.gz \
    && curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update \
    && apt-get install -y postgresql-client-${POSTGRES_VERSION} \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN chmod +x ./*.sh /usr/local/bin/go-cron

ENV POSTGRES_DATABASE ''
ENV POSTGRES_HOST ''
ENV POSTGRES_PORT 5432
ENV POSTGRES_USER ''
ENV POSTGRES_PASSWORD ''
ENV PGDUMP_EXTRA_OPTS ''
ENV S3_ACCESS_KEY_ID ''
ENV S3_SECRET_ACCESS_KEY ''
ENV S3_BUCKET ''
ENV S3_REGION 'us-west-1'
ENV S3_PATH 'backup'
ENV S3_ENDPOINT ''
ENV S3_S3V4 'no'
ENV SCHEDULE ''
ENV PASSPHRASE ''
ENV BACKUP_KEEP_DAYS ''
ENV BACKUP_ALERT_PROJECT_NAME ''
ENV BACKUP_ALERT_BOT_TOKEN ''
ENV BACKUP_ALERT_CHAT_ID ''

ENTRYPOINT ["./run.sh"]
