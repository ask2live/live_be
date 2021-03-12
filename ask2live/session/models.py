from django.db import models
from users import models as user_models

# Create your models here.


class Session(models.Model):
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
    host_id         = models.ForeignKey("users.User", related_name="users",blank=True, on_delete=models.CASCADE)
    question_id     = models.IntegerField(blank=True, null = True)
    live_id         = models.IntegerField(blank=True, null = True)
    
    def __str__(self):
        return self.title

