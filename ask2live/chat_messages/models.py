from django.db import models

# User랑 LiveHole 모델 임포트
from users import models as user_models
from holes import models as hole_models
from core import models as core_model
# Create your models here.

class Message(core_model.AbstractTimeStamp):
    text = models.TextField()
    sender = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True)
    livehole = models.ForeignKey(hole_models.LiveHole, on_delete=models.CASCADE,related_name="messages")
    sent_timestamp = models.DateTimeField(auto_now_add = True, editable=False, blank=True)
    
    def __str__(self):
        return str(self.sender) + ' - ' + str(self.livehole)
