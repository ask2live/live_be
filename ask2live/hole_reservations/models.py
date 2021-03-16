from django.db import models
from users import models as user_models
from holes import models as hole_models
from core import models as core_model
# Create your models here.

class Reservation(core_model.AbstractTimeStamp):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED= "confirmed"
    STATUS_CANCELED = "canceled"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELED, "Canceled"),
    )
    # host                = models.ForeignKey(user_models.User, related_name="hole_reservations", on_delete=models.CASCADE)
    status              = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING)
    target_demand       = models.IntegerField(blank=True, null = True)
    reserve_start_date  = models.DateTimeField(blank=True, null=True)
    finish_date         = models.DateTimeField(blank=True, null = True)
    guests              = models.ManyToManyField(user_models.User, related_name="hole_reservations",blank=True)
    hole                = models.ForeignKey(hole_models.Hole, related_name="hole_reservations",blank=True, on_delete=models.CASCADE)

    def __str__(self):
        usernames = []
        all_member = self.guests.all()
        for member in all_member:
            usernames.append(member.email)
        return ", ".join(usernames)