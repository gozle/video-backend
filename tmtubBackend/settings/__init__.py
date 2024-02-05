import os

from dotenv import load_dotenv

# dotenv config
load_dotenv()

environ = os.environ.get("DJANGO_SETTINGS", "local")

if environ == "local":
    from .local import *

if environ == "dev":
    from .dev import *

else:
    from .production import *
