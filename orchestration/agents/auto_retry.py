
import logging
from collections.abc import Awaitable, Callable
from agent_framework import ChatContext, ChatMiddleware
from openai import RateLimitError
from tenacity import (
    AsyncRetrying,
    before_sleep_log,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

RETRY_ATTEMPTS = 5
logger = logging.getLogger(__name__)

class RateLimitRetryMiddleware(ChatMiddleware):
    """Chat middleware that retries a single model-call pipeline on rate limit errors.

    Register this middleware on an agent (or at the run level) to automatically
    retry any chat-model call that raises RateLimitError. In tool-loop scenarios,
    the middleware applies independently to each inner model call.
    """

    def __init__(self, *, max_attempts: int = RETRY_ATTEMPTS) -> None:
        """Initialize with the maximum number of retry attempts."""
        self.max_attempts = max_attempts

    async def process(
        self,
        context: ChatContext,
        call_next: Callable[[], Awaitable[None]],
    ) -> None:
        """Retry call_next() on rate limit errors with exponential back-off."""
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_exponential(multiplier=1, min=4, max=10),
            retry=retry_if_exception_type(RateLimitError),
            reraise=True,
            before_sleep=before_sleep_log(logger, logging.WARNING),
        ):
            with attempt:
                await call_next()