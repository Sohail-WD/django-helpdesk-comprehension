import json
from functools import lru_cache

from django.conf import settings


@lru_cache(maxsize=1)
def load_company_config():
    path = settings.BASE_DIR / "demo_data" / "company.json"
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)
