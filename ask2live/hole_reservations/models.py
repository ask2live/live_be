from django.db import models
from users import models as user_models
from holes import models as hole_models
from core import models as core_model
# Create your models here.

class Reservation(core_model.AbstractTimeStamp):
    STATUS_PENDING = "PENDING"
    STATUS_CONFIRMED= "CONFIRMED"
    STATUS_HOST_CONFIRMED= "HOST_CONFIRMED"
    STATUS_CANCELED = "CANCELED"
    STATUS_CHOICES = (
        (STATUS_PENDING, "PENDING"),
        (STATUS_CONFIRMED, "CONFIRMED"),
        (STATUS_HOST_CONFIRMED, "HOST_CONFIRMED"),
        (STATUS_CANCELED, "CANCELED"),
    )
    # host                = models.ForeignKey(user_models.User, related_name="hole_reservations", on_delete=models.CASCADE)
    status              = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)
    target_demand       = models.IntegerField(blank=True, default=0)
    current_demand      = models.IntegerField(default=0)
    reserve_date  = models.DateTimeField(blank=True, null=True)
    finish_date         = models.DateTimeField(blank=True, null = True)
    guests              = models.ManyToManyField(user_models.User, related_name="hole_reservations",blank=True, default="")
    hole                = models.OneToOneField(hole_models.Hole, related_name="hole_reservations",blank=True, on_delete=models.CASCADE)

    def guests_list(self): # 어드민에 게스트 리스트 보여주기, for loop 안 돌리고도 보여주기가 가능.
        return list(self.guests.values_list('email',flat=True))
    #     # return self.hole
    #     usernames = []
    #     all_member = self.guests.all()
    #     for member in all_member:
    #         usernames.append(member.email)
    #     return ", ".join(usernames)