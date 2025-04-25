import psycopg2
from cryptography.fernet import Fernet

from utils.settings import settings

secured_fields_key = settings.django_secured_fields_key
fernet = Fernet(secured_fields_key)


def decrypt_django_user_password() -> str | None:
    connection = psycopg2.connect(
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port
    )

    cursor = connection.cursor()
    cursor.execute("SELECT token_password FROM user_erp_api WHERE user_id = 2;")
    result = cursor.fetchone()

    if result and result[0]:
        encrypted_value = result[0]
        decrypted_bytes = fernet.decrypt(encrypted_value.encode('utf-8'))
        decrypted_password = decrypted_bytes.decode('utf-8')
        return decrypted_password

    cursor.close()
    connection.close()

    return None
