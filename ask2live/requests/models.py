from django.db import models
from users import models as user_models
from holes import models as hole_models
# Create your models here.
class Request(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    questions = models.TextField(null = True)
    user = models.ForeignKey(user_models.User, related_name="request", on_delete=models.CASCADE)
    hole = models.ForeignKey(hole_models.Hole, related_name="request", on_delete=models.CASCADE)
