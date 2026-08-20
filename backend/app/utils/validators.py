from pydantic import AnyHttpUrl


def validate_repository_url(url: str) -> str:
    AnyHttpUrl(url)
    return url
