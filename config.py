import os

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'dpg-cunkaeggph6c73eujvqg-a'),
    'port': int(os.environ.get('DB_PORT', 5432)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'your_password_here'),
    'database': os.environ.get('DB_NAME', 'social_4stp')
}
