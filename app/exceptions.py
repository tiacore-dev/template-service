class InvalidTemplateError(Exception):
    """Ошибка, связанная с неподходящим шаблоном или данными."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
