#!/bin/bash

set -eu
set -o pipefail

source ./env.sh

export TZ="Europe/Moscow"

: "${aws_args:=--region ${S3_REGION} --endpoint-url ${S3_ENDPOINT}}"

send_message() {
    local message="$1"

    curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
        -H "Content-Type: application/json" \
        -d "{
            \"chat_id\": \"${CHAT_ID}\",
            \"text\": \"${message}\",
            \"parse_mode\": \"HTML\"
        }" > /dev/null
}

echo "Creating backup of $POSTGRES_DATABASE database..."
pg_dump --format=plain \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DATABASE" \
        $PGDUMP_EXTRA_OPTS \
        > db.sql

BACKUP_KEEP_DAYS=${BACKUP_KEEP_DAYS:-7}
timestamp=$(date +"%Y-%m-%dT%H:%M:%S")
today=$(echo "$timestamp" | cut -d'T' -f1)
cutoff=$(date -d "$today - $BACKUP_KEEP_DAYS days" +"%Y-%m-%d")

backupName="${POSTGRES_DATABASE}_${timestamp}.sql"
s3_uri_base="s3://${S3_BUCKET}/${S3_PREFIX}/${backupName}"

if [ -n "${PASSPHRASE:-}" ]; then
  echo "Encrypting backup..."
  rm -f db.sql.gpg
  gpg --symmetric --batch --passphrase "$PASSPHRASE" db.sql
  rm db.sql
  local_file="db.sql.gpg"
  s3_uri="${s3_uri_base}.gpg"
else
  local_file="db.sql"
  s3_uri="$s3_uri_base"
fi

echo "Uploading backup to $S3_BUCKET..."
aws $aws_args s3 cp "$local_file" "$s3_uri"
rm "$local_file"

send_message "<b>🛡️ Backup database #${POSTGRES_DATABASE} in project #${PROJECT_NAME} successfully</b>

🏷 File name: <pre><code class='plaintext'>${backupName}</code></pre>
📁 Full path: <pre><code class='plaintext'>${s3_uri_base}</code></pre>
🔄 For restore: <pre><code class='shell'>restore.sh ${timestamp}</code></pre>"

if [ -n "$BACKUP_KEEP_DAYS" ]; then
  echo "Cleaning up old backups..."
  backups_json=$(aws $aws_args s3api list-objects \
    --bucket "${S3_BUCKET}" \
    --prefix "${S3_PREFIX}" \
    --query "Contents[?ends_with(Key, '.sql') || ends_with(Key, '.sql.gpg')].{Key: Key, LastModified: LastModified}" \
    --output json)

  mapfile -t keep_keys < <(echo "$backups_json" | \
    jq -r '.[] | "\(.LastModified) \(.Key)"' | \
    while read -r last_modified key; do
      local_date=$(TZ="Europe/Moscow" date -d "$last_modified" +"%Y-%m-%d")
      echo "$local_date $last_modified $key"
    done | sort -k1,1 -k2,2r | awk '!seen[$1]++ { print $3 }')

  echo "$backups_json" | jq -r '.[] | "\(.Key) \(.LastModified)"' | while read -r key last_modified; do
    backup_date=$(TZ="Europe/Moscow" date -d "$last_modified" +"%Y-%m-%d")
    keep=false
    for keep_key in "${keep_keys[@]}"; do
      if [[ "$key" == "$keep_key" ]]; then
        keep=true
        break
      fi
    done
    if [[ "$backup_date" < "$cutoff" ]]; then
      echo "Deleting backup (older than $BACKUP_KEEP_DAYS days): $key"
      aws $aws_args s3 rm "s3://${S3_BUCKET}/${key}"
    elif [ "$keep" = false ] && [ "$backup_date" != "$today" ]; then
      echo "Deleting old backup: $key"
      aws $aws_args s3 rm "s3://${S3_BUCKET}/${key}"
    else
      echo "Keeping backup: $key (Date: $backup_date)"
    fi
  done

  echo "Old backups cleanup complete."
fi
