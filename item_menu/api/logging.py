import logging
from functools import wraps
from typing import Callable, Any


def query_log(func: Callable[..., Any]) -> Callable[..., Any]:
    """
   Обработчик-декоратор для логирования запросов и мутаций
   """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        method = func.__qualname__
        method_params = '' if not kwargs else ' with params: {}'.format({**kwargs})

        try:
            output = await func(*args, **kwargs)
            logging.debug(
                'Successfully resolved {method}{method_params}'.format(
                    method=method, method_params=method_params
                )
            )
        except Exception as e:
            logging.error(
                'Error while resolve {method}{method_params}: {e}'.format(
                    method=method, method_params=method_params, e=e
                )
            )
            output = e

        return output
    return wrapper
