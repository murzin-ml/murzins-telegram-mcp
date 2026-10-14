from pathlib import Path

from dotenv import set_key

PRIVATE_MODE = 0o600


def save_secret(*, path: Path, key: str, value: str) -> None:
    """
    Записывает секрет в .env.local с правами только для владельца. Значение
    не логируется и не выводится.

    :param path: Путь к файлу секретов.
    :param key: Имя переменной.
    :param value: Значение.
    """
    path.touch(mode=PRIVATE_MODE, exist_ok=True)
    path.chmod(PRIVATE_MODE)
    set_key(path, key, value, quote_mode="never")
    path.chmod(PRIVATE_MODE)
