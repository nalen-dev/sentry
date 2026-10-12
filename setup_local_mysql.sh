#!/bin/bash

echo "Starting MySQL service..."
service mysql start

echo "Creating database 'dtscontroler'..."
mysql -e "CREATE DATABASE IF NOT EXISTS dtscontroler;"

echo "Importing backup data (this may take a minute due to 200MB size)..."
mysql dtscontroler < dts_backup_latest.sql

echo "Creating a dedicated user 'dbeaver' for remote access..."
# Use a strong password to satisfy policy requirements
mysql -e "CREATE USER IF NOT EXISTS 'dbeaver'@'%' IDENTIFIED BY 'Admin!12345Dbeaver';" || mysql -e "ALTER USER 'dbeaver'@'%' IDENTIFIED BY 'Admin!12345Dbeaver';"
mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'dbeaver'@'%' WITH GRANT OPTION;"
mysql -e "FLUSH PRIVILEGES;"

echo "=========================================="
echo "✅ MySQL Local Setup Completed Successfully!"
echo "=========================================="
