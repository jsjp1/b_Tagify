#!/bin/bash

DATE=$(date +%F_%H-%M-%S)
BACKUP_DIR="/var/lib/postgresql/backups"
mkdir -p $BACKUP_DIR
pg_dump -U test -h localhost -F c -b -v -f "$BACKUP_DIR/backup_$DATE.dump" tagi_test

find $BACKUP_DIR -type f -name "*.dump" -mtime +7 -delete