from pydantic import BaseSettings, Field

class Config(BaseSettings):
    api_key_openai: str = Field("")
    api_key_voicevox: str = Field("u9J87-E5l-03809")
    url_database:  str = Field("")

config = Config()
