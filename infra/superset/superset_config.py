"""Local Superset metadata profile; secrets must be operator configured."""

import os

SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "")
if len(SECRET_KEY) < 32:
    raise RuntimeError("Configure a Superset secret of at least 32 characters")
SQLALCHEMY_DATABASE_URI = "sqlite:////app/superset_home/superset.db"
WTF_CSRF_ENABLED = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
FEATURE_FLAGS = {"ENABLE_TEMPLATE_PROCESSING": False, "EMBEDDED_SUPERSET": False}
ROW_LIMIT = 100
SAMPLES_ROW_LIMIT = 100
