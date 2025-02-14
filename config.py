import os

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '1978'),
    'database': os.environ.get('DB_NAME', 'social'),
    'port': int(os.environ.get('DB_PORT', '3310')),
    'auth_plugin': 'mysql_native_password'
}
