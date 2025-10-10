import requests


def has_connection_error(e: Exception) -> bool:
    if isinstance(e, requests.exceptions.ConnectionError):
        return True
    if "connection refused" in str(e).lower():
        return True
    if e.__cause__:
        return has_connection_error(e.__cause__)
    return False
