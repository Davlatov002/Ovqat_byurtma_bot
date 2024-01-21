from django.db import models
import uuid

class User(models.Model):
    id = models.UUIDField(default = uuid.uuid4, primary_key=True, unique=True, editable=False)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return self.first_name
    
class Food(models.Model):
    id = models.UUIDField(default = uuid.uuid4, primary_key=True, unique=True, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    price = models.FloatField()
    description = models.TextField()
    image = models.ImageField(upload_to="image/")

    def __str__(self) -> str:
        return self.name

class Order(models.Model):
    CONFIRMATION_CHOICS=(
        ("KO'RIBCHIQILMOQDA", "KO'RIBCHIQILMOQDA"),
        ('TAYORLANMOQDA,','TAYORLANMOQDA'), 
        ('TAYOR','TAYOR'),
    )
    id = models.UUIDField(default = uuid.uuid4, primary_key=True, unique=True, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.ForeignKey(User, related_name="User", on_delete=models.CASCADE)
    description = models.TextField()
    total_price = models.CharField(max_length=255, blank=True, null=True)
    order_confirmation = models.CharField(max_length=50, choices=CONFIRMATION_CHOICS, default="KO'RIBCHIQILMOQDA")

    def __str__(self) -> str:
        return self.name


    