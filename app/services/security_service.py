from app.core.config import settings

def verify_default_security_code(code: str) -> bool:
    return code == settings.default_security_code