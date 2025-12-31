"""
LLM Request/Response Logger
Logs prompts before sending and responses after receiving with timestamps.
"""
import time
from datetime import datetime
from typing import Optional


class LLMLogger:
    """Simple logger for LLM API calls."""

    @staticmethod
    def _timestamp() -> str:
        """Get current timestamp."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    @staticmethod
    def log_request(model: str, prompt: str, use_case: str = "unknown") -> float:
        """
        Log an LLM request before sending.

        Args:
            model: The model being used
            prompt: The prompt being sent
            use_case: Description of what this call is for

        Returns:
            Start time for calculating duration
        """
        start_time = time.time()
        timestamp = LLMLogger._timestamp()

        # Truncate prompt for display (show first 500 chars)
        prompt_preview = prompt[:500] + "..." if len(prompt) > 500 else prompt

        print(f"\n{'='*60}")
        print(f"[{timestamp}] LLM REQUEST - {use_case}")
        print(f"{'='*60}")
        print(f"Model: {model}")
        print(f"Prompt ({len(prompt)} chars):")
        print(f"{'-'*40}")
        print(prompt_preview)
        print(f"{'='*60}\n")

        return start_time

    @staticmethod
    def log_response(start_time: float, use_case: str = "unknown", tokens_used: Optional[int] = None):
        """
        Log an LLM response after receiving.

        Args:
            start_time: The start time from log_request
            use_case: Description of what this call was for
            tokens_used: Optional token count from response
        """
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        timestamp = LLMLogger._timestamp()

        print(f"\n{'='*60}")
        print(f"[{timestamp}] LLM RESPONSE - {use_case}")
        print(f"{'='*60}")
        print(f"Duration: {duration_ms:.0f}ms ({duration_ms/1000:.2f}s)")
        if tokens_used:
            print(f"Tokens used: {tokens_used}")
        print(f"{'='*60}\n")


# Global instance
llm_logger = LLMLogger()
