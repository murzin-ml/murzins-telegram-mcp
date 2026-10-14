from dependency_injector import containers, providers

from app.core.bots.repository import BotsRepository
from app.core.chats.repository import ChatsRepository
from app.infra.adapters.telegram import TelegramClientProvider
from settings.telegram import TelegramSettings


class RepositoriesContainer(containers.DeclarativeContainer):
    telegram_settings: providers.Dependency[TelegramSettings] = providers.Dependency(instance_of=TelegramSettings)

    client_provider = providers.Singleton(TelegramClientProvider, settings=telegram_settings)

    bots_repository = providers.Singleton(BotsRepository, client_provider=client_provider)
    chats_repository = providers.Singleton(ChatsRepository, client_provider=client_provider)
