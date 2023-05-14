import aiohttp


class AiohttpSession:
    def __init__(self, limit=3, ssl=False, total=320, sock_connect=160, sock_read=160, trust_env=True):
        self.limit = limit
        self.ssl = ssl
        self.total = total
        self.sock_connect = sock_connect
        self.sock_read = sock_read
        self.trust_env = trust_env

    async def create_session(self) -> aiohttp.client.ClientSession:
        # Функция создает объект сессии.
        conn = aiohttp.TCPConnector(limit=self.limit, ssl=self.ssl)  # Лимит на количество соединений
        timeout = aiohttp.ClientTimeout(
            total=self.total, sock_connect=self.sock_connect, sock_read=self.sock_read)  # Время ожидания

        session = aiohttp.ClientSession(connector=conn, timeout=timeout, trust_env=self.trust_env)
        return session
