from django.contrib.auth import get_user_model
from whohas.models import WhohasHomePage

User = get_user_model()

owner = User.objects.get(username="robert")

items = [
    {"name": "Vrtačka", "description": "Aku vrtačka Bosch"},
    {"name": "Žebřík", "description": "Hliníkový žebřík"},
]

for data in items:
    item = WhohasHomePage(owner=owner, **data)
    item.full_clean()
    item.save()
    print(f"Vytvořeno: {item.name}, ID: {item.pk}")

