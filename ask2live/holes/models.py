from django.db import models
from django.db.models import IntegerField, Model
from users import models as user_models
from django_mysql.models import ListTextField
# Create your models here.


class Hole(models.Model):
    title           = models.CharField(max_length=200)    # 세션 제목
    subtitle        = models.CharField(max_length=400) # 세션 부제
    description     = models.TextField()            # 세션 설명
    create_date     = models.DateTimeField(auto_now_add=True)        # 세션을 생성한 날짜
    reserved_date   = models.DateTimeField(blank=True, null = True)      # 세션을 예약한 날짜
    finished_date   = models.DateTimeField(blank=True, null = True)      # 세션이 종료된 날짜    
    wish_user_list  = models.IntegerField(blank=True, null = True)      # 세션을 예약한 유저 목록(id)
    status          = models.IntegerField(blank=True, null = True)
    target_demand   = models.IntegerField(blank=True, null = True)
    rating          = models.IntegerField(blank=True, null = True)
    # ====================== 나중에 models.ForeignKey로 변경 ======================
    host         = models.ForeignKey("users.User", related_name="hole",blank=True, on_delete=models.CASCADE)
    question_id     = models.IntegerField(blank=True, null = True)
    live_id         = models.IntegerField(blank=True, null = True)
    
    def __str__(self):
        return self.title


class LiveHole(models.Model):
    livehole_user_ids = ListTextField(
        base_field= IntegerField(),
        size=30,  # Maximum of 30 ids in list
    )
    hole = models.ForeignKey(Hole,related_name="livehole", on_delete=models.CASCADE, blank=True)
    
    def __str__(self):
        return str(self.hole)