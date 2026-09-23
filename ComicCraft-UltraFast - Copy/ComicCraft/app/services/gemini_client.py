import time
from collections.abc import Callable
from typing import Any

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def _status_code(exc: Exception) -> int | None:
    status = getattr(exc, "status_code", None)
    if status is None:
        status = getattr(exc, "code", None)
    if status is None:
        response = getattr(exc, "response", None)
        status = getattr(response, "status_code", None)
    return status


def generate_content_with_retry(request: Callable[[], Any], max_retries: int = 1) -> Any:
    for attempt in range(max_retries + 1):
        try:
            return request()
        except Exception as exc:
            status_code = _status_code(exc)
            if status_code not in RETRYABLE_STATUS_CODES or attempt == max_retries:
                raise
            time.sleep(1.5 * (2**attempt))
    raise RuntimeError("Gemini request failed.")


def generate_content_with_fallback(
    request_for_model: Callable[[str], Any],
    models: list[str],
    max_retries: int = 1,
) -> Any:
    last_error: Exception | None = None
    for model in dict.fromkeys(models):
        try:
            return generate_content_with_retry(
                lambda: request_for_model(model), max_retries=max_retries
            )
        except Exception as exc:
            last_error = exc
            # Do not waste time trying other models for ordinary bad requests.
            if _status_code(exc) not in RETRYABLE_STATUS_CODES:
                raise
    if last_error is not None:
        raise last_error
    raise RuntimeError("No Gemini models were configured.")
