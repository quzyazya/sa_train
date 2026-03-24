from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str 

    @property
    def DATABASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def DATABASE_URL_psycopg(self):
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

settings = Settings()

# ОТЛАДКА: выводим байты строки подключения
# url = settings.DATABASE_URL_psycopg
# print(f"URL: {url}")
# print(f"Байты URL: {url.encode('utf-8')}")
# print(f"Длина URL: {len(url)}")
# print(f"Байт в позиции 61 (если есть): {url[61:70] if len(url) > 61 else 'N/A'}")