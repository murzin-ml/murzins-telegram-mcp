from dependency_injector import containers, providers

from app.di.repositories import RepositoriesContainer
from app.di.services import ServicesContainer
from settings.app import AppSettings
from settings.telegram import TelegramSettings


class DIContainer(containers.DeclarativeContainer):
    app_settings = providers.Singleton(AppSettings)
    telegram_settings = providers.Singleton(TelegramSettings)

    repositories = providers.Container(
        RepositoriesContainer,
        telegram_settings=telegram_settings,
    )
    services = providers.Container(
        ServicesContainer,
        telegram_settings=telegram_settings,
        repositories=repositories,
    )
