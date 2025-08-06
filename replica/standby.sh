#!/bin/bash
set -e

# Agar katalog bo‘sh emas bo‘lsa — bu skip qilinadi
if [ "$(ls -A /var/lib/postgresql/data)" ]; then
    echo "⚠️ Katalog bo‘sh emas. Nusxa olinmaydi."
    exit 0
fi

echo "🕒 db_master kutilyapti..."

for i in {1..30}; do
    if pg_isready -h db_master -p 5432 > /dev/null; then
        echo "✅ db_master tayyor. Nusxa olinmoqda..."
        break
    fi
    echo "⏳ db_master hali yo‘q. Urinish #$i..."
    sleep 2
done

PGPASSWORD=$POSTGRES_PASSWORD pg_basebackup -h db_master -D /var/lib/postgresql/data -U $POSTGRES_USER -Fp -Xs -P -R

echo "✅ Replica muvaffaqiyatli nusxa olindi."
