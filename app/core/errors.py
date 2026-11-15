class GenerationError(Exception):
    """Safe public failure information without provider bodies or credentials."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        mode: str = "openai",
        status_code: int = 502,
        issues: list[str] | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.mode = mode
        self.status_code = status_code
        self.issues = issues or []

    def detail(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "mode": self.mode,
            "source": {"openai": "openai", "mock": "demo_template"}.get(self.mode, "unknown"),
            "status": "failed",
            "used_fallback": False,
            "issues": self.issues,
        }
