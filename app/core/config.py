from decouple import config


SECRET_KEY = config("SECRET_KEY", default="change-this-secret-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(config("ACCESS_TOKEN_EXPIRE_MINUTES", default=60))
RESEND_API_KEY = "re_8TzrfUwP_PswxmBXADCu6yky8r31SHUGx"
FRONTEND_URL = "http://localhost:5173/"
MAPBOX_ACCESS_TOKEN = config("MAPBOX_ACCESS_TOKEN")
