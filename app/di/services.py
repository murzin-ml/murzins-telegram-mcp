from dependency_injector import containers, providers

from app.core.bots.service import BotsService
from app.core.chats.service import ChatsService
from app.core.diagnostics.service import DiagnosticsService
from settings.constants import SECRETS_FILE
from settings.telegram import TelegramSettings


class ServicesContainer(containers.DeclarativeContainer):
    telegram_settings: providers.Dependency[TelegramSettings] = providers.Dependency(instance_of=TelegramSettings)
    repositories = providers.DependenciesContainer()

    bots_service = providers.Singleton(
        BotsService,
        repository=repositories.bots_repository,
        allowed_bots=telegram_settings.provided.allowed_bots,
        reply_timeout_sec=telegram_settings.provided.TG_REPLY_TIMEOUT_SEC,
        quiet_period_sec=telegram_settings.provided.TG_QUIET_PERIOD_SEC,
    )
    chats_service = providers.Singleton(
        ChatsService,
        repository=repositories.chats_repository,
        read_enabled=telegram_settings.provided.TG_READ_ENABLED,
        denied_chats=telegram_settings.provided.denied_chats,
    )
    diagnostics_service = providers.Singleton(
        DiagnosticsService,
        settings=telegram_settings,
        client_provider=repositories.client_provider,
        secrets_file=SECRETS_FILE,
    )
