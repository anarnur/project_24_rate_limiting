from slowapi import Limiter
from slowapi.util import get_remote_address

# Идентификатор клиента — IP-адрес из запроса
limiter = Limiter(key_func=get_remote_address)