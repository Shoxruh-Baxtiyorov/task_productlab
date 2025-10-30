#!/bin/bash

set -eu

if [ -z "$SCHEDULE" ]; then
  ./backup.sh
  ./clear_docker_cache.sh
else
  exec go-cron "$SCHEDULE" /bin/bash backup.sh
  exec go-cron "$SCHEDULE" /bin/bash clear_docker_cache.sh
fi