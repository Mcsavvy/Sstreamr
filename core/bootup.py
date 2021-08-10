from .models import User

def freshStart():
    root = User.objects.create(
        username="root",
        email="phishink5@gmail.com",
        is_superuser=True,
        is_staff=True
    )
    root.set_password("Hood@roo1")
    root.save()
    return "OK"
