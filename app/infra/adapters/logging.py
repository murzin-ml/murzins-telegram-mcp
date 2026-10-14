import logging
import sys


def configure_logging(*, level: str) -> None:
    """
    Транспорт stdio занимает stdout, поэтому логи уходят только в stderr.

    :param level: Уровень логирования.
    """
    logging.basicConfig(
        level=level,
        stream=sys.stderr,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    # Telethon шумит на INFO при каждом переподключении
    logging.getLogger("telethon").setLevel(max(logging.WARNING, logging.getLogger().level))
