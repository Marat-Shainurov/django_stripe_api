import requests

from config.settings import FIXER_API_KEY


def get_conversion_rate(base_curr: str, second_curr: str) -> float:
    """
    Returns the latest currency rate (second_curr against base_curr).

    :param base_curr: the base currency, used by the fixer.io API as the 'base' argument's value.
    :param second_curr: the second currency, used by the fixer.io API as the 'symbols' argument's value.
    :return: the final rate (second_curr against base_curr).
    """
    endpoint = f'http://data.fixer.io/api/latest?access_key={FIXER_API_KEY}&base={base_curr}&symbols={second_curr}'
    response = requests.get(endpoint)
    rate = response.json()['rates'][second_curr]
    result = 1 / rate
    return result
