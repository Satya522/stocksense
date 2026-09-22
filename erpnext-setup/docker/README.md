# ERPNext Docker Connection Notes

## Connecting to your existing ERPNext container

Since ERPNext is already running in Docker on your machine, here are the key
connection details you'll need throughout this project.

### Find your running containers

```bash
docker ps
```

Look for containers related to ERPNext / Frappe (typically named something like
`erpnext-worker`, `erpnext-frontend`, `frappe-bench`, etc.).

### ERPNext Web Interface

- **Default URL:** `http://localhost:8000`
- **Default admin:** `Administrator`
- **Password:** (whatever you set during installation)

### MariaDB Database Access

ERPNext uses MariaDB. To find the database container:

```bash
docker ps | findstr mariadb
```

To connect directly to MariaDB inside Docker:

```bash
docker exec -it <mariadb_container_name> mysql -u root -p
```

### Key database details for .env and Power BI

| Setting   | Typical Value |
|-----------|---------------|
| DB_HOST   | `localhost` or `127.0.0.1` |
| DB_PORT   | `3306` (check your docker-compose if mapped differently) |
| DB_USER   | `root` |
| DB_NAME   | Your ERPNext site name (e.g., `_1bd4c572c4ab6149`) — run `SHOW DATABASES;` to find it |

### Useful Docker commands

```bash
# View logs
docker logs <container_name> --tail 100

# Restart ERPNext
docker compose restart

# Access bench console
docker exec -it <frappe_container> bench console
```
