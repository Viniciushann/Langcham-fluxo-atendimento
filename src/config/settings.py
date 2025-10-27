"""
Configurações do WhatsApp Bot
Gerenciamento de variáveis de ambiente com validação usando Pydantic Settings
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
import logging
from pathlib import Path
import os


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas de variáveis de ambiente.
    Todas as variáveis são validadas automaticamente pelo Pydantic.
    """

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ========== OPENAI API ==========
    openai_api_key: str = Field(
        ...,
        description="Chave de API da OpenAI para GPT-4, Whisper e Embeddings",
        min_length=20
    )

    # ========== SUPABASE ==========
    supabase_url: str = Field(
        ...,
        description="URL do projeto Supabase",
        pattern=r"^https://.*\.supabase\.co$"
    )

    supabase_key: str = Field(
        ...,
        description="Chave da API do Supabase",
        min_length=20
    )

    # ========== REDIS ==========
    redis_host: str = Field(
        default="localhost",
        description="Host do servidor Redis"
    )

    redis_port: int = Field(
        default=6379,
        description="Porta do servidor Redis",
        ge=1,
        le=65535
    )

    redis_password: Optional[str] = Field(
        default=None,
        description="Senha do Redis (opcional)"
    )

    redis_db: int = Field(
        default=0,
        description="Índice do database Redis",
        ge=0,
        le=15
    )

    # ========== WHATSAPP - EVOLUTION API ==========
    whatsapp_api_url: str = Field(
        ...,
        description="URL base da Evolution API",
        pattern=r"^https?://.+"
    )

    whatsapp_api_key: str = Field(
        ...,
        description="Chave de autenticação da Evolution API",
        min_length=10
    )

    whatsapp_instance: str = Field(
        ...,
        description="Nome da instância do WhatsApp",
        min_length=1
    )

    # ========== POSTGRESQL (Memória) ==========
    postgres_connection_string: str = Field(
        ...,
        description="String de conexão PostgreSQL",
        pattern=r"^postgresql://.*"
    )

    # ========== GOOGLE CALENDAR ==========
    google_calendar_credentials_file: str = Field(
        default="credentials.json",
        description="Caminho para o arquivo de credenciais do Google"
    )

    google_calendar_token_file: str = Field(
        default="token.json",
        description="Caminho para o arquivo de token do Google"
    )

    google_calendar_timezone: str = Field(
        default="America/Sao_Paulo",
        description="Timezone para o Google Calendar"
    )

    # ========== CONFIGURAÇÕES DO BOT ==========
    bot_phone_number: str = Field(
        default="555195877046",
        description="Número do próprio bot (para filtrar)",
        pattern=r"^\d{10,15}$"
    )

    message_group_delay: int = Field(
        default=13,
        description="Tempo para aguardar e agrupar mensagens (segundos)",
        ge=5,
        le=60
    )

    max_fragment_size: int = Field(
        default=300,
        description="Tamanho máximo de fragmentos de resposta",
        ge=100,
        le=1000
    )

    # ========== CONFIGURAÇÕES DO AGENTE ==========
    agent_timeout: int = Field(
        default=60,
        description="Timeout em segundos para processamento do agente",
        ge=10,
        le=300
    )

    max_retries: int = Field(
        default=3,
        description="Número máximo de tentativas em caso de falha",
        ge=1,
        le=10
    )

    enable_memory_persistence: bool = Field(
        default=True,
        description="Habilitar persistência de memória no PostgreSQL"
    )

    # ========== APLICAÇÃO ==========
    environment: str = Field(
        default="development",
        description="Ambiente de execução",
        pattern=r"^(development|production|staging)$"
    )

    port: int = Field(
        default=8000,
        description="Porta da aplicação FastAPI",
        ge=1000,
        le=65535
    )

    host: str = Field(
        default="0.0.0.0",
        description="Host da aplicação"
    )

    log_level: str = Field(
        default="INFO",
        description="Nível de log",
        pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )

    # ========== SEGURANÇA ==========
    secret_key: Optional[str] = Field(
        default=None,
        description="Chave secreta para sessões",
        min_length=32
    )

    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="CORS origins permitidas (separadas por vírgula)"
    )

    # ========== PROPRIEDADES COMPUTADAS ==========

    @property
    def cors_origins_list(self) -> List[str]:
        """Retorna lista de CORS origins"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        """Verifica se está em produção"""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Verifica se está em desenvolvimento"""
        return self.environment == "development"

    @property
    def redis_url(self) -> str:
        """Retorna URL completa do Redis"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def bot_whatsapp_jid(self) -> str:
        """Retorna o JID completo do bot no formato WhatsApp"""
        return f"{self.bot_phone_number}@s.whatsapp.net"

    # ========== VALIDADORES ==========

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Valida e converte log level para uppercase"""
        return v.upper()

    @field_validator("whatsapp_api_url")
    @classmethod
    def validate_whatsapp_url(cls, v: str) -> str:
        """Remove trailing slash da URL"""
        return v.rstrip("/")

    def configure_logging(self) -> None:
        """Configura o sistema de logging"""
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bot.log'),
                logging.StreamHandler()
            ]
        )

    def model_post_init(self, __context) -> None:
        """Executado após inicialização do modelo"""
        # Configura logging automaticamente
        self.configure_logging()

        # Log de inicialização
        logger = logging.getLogger(__name__)
        logger.info("=" * 50)
        logger.info("WhatsApp Bot - Configurações Carregadas")
        logger.info("=" * 50)
        logger.info(f"Ambiente: {self.environment}")
        logger.info(f"Host: {self.host}:{self.port}")
        logger.info(f"Redis: {self.redis_host}:{self.redis_port}")
        logger.info(f"Supabase: {self.supabase_url}")
        logger.info(f"WhatsApp Instance: {self.whatsapp_instance}")
        logger.info(f"Log Level: {self.log_level}")
        logger.info("=" * 50)


# ========== SINGLETON ==========
# Instância global das configurações
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Retorna a instância singleton das configurações.
    Carrega apenas uma vez durante a execução da aplicação.

    Returns:
        Settings: Instância configurada

    Example:
        >>> from config.settings import get_settings
        >>> settings = get_settings()
        >>> print(settings.openai_api_key)
    """
    global _settings

    if _settings is None:
        _settings = Settings()

    return _settings


# ========== EXPORTAÇÕES ==========
__all__ = ["Settings", "get_settings"]
