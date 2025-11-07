#!/bin/bash
echo "Resetting databases..."

# Reset User DB
docker exec -i user_db psql -U user -d user_db -f /docker-entrypoint-initdb.d/user.sql

# Reset Task DB
docker exec -i task_db psql -U user -d task_db -f /docker-entrypoint-initdb.d/task.sql

# Reset Notification DB
docker exec -i notification_db psql -U user -d notification_db -f /docker-entrypoint-initdb.d/notification.sql

echo "✅ Databases have been reset successfully!"