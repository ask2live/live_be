from django.db import models
from django.contrib.auth.models import AbstractUser
from holes import models as hole_models
# Create your models here.
class User(AbstractUser):
    LOGIN_EMAIL = "email"
    LOGIN_KAKAO = "kakao"
    LOGIN_CHOICES = ((LOGIN_EMAIL,"Email"), (LOGIN_KAKAO, "Kakao"))

    SOCIAL_INSTAGRAM = "instagram"
    SOCIAL_ACCOUNT = ((SOCIAL_INSTAGRAM, "Instagram"),)

    """ user model attribute"""
    profile_image = models.ImageField(blank=True)
    session_open_auth = models.BooleanField(default=False, blank=True) # 세션 열 수 있는 권한(호스트 여부)
    work_field = models.TextField(default="", blank=True) # 관심분야
    login_method = models.CharField(max_length = 50, choices=LOGIN_CHOICES, default=LOGIN_EMAIL)
    followed_count = models.IntegerField(default=0) # 나를 팔로잉하는 사람 수
    following_count = models.IntegerField(default=0) # 내가 팔로잉하는 사람 수
    social_account = models.CharField(max_length=50, choices=SOCIAL_ACCOUNT, null=True, blank=True)
    bio = models.TextField(default="", blank=True)
    rating = models.IntegerField(default=0) # 호스트들의 평점
    # session = models.ForeignKey(hole_models.Hole, related_name="users", on_delete=models.CASCADE, null=True) # 유저가 진행한 세션 리스트 
    # request = models.ForeignKey() # 유저가 세션 오픈을 원해서 요청했던 세션 리스트
