from django.db import models
from django.contrib.auth.models import AbstractUser
from holes import models as hole_models
from core import models as core_model
# token authentication
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.utils.translation import ugettext_lazy as _


from django.contrib.auth.base_user import BaseUserManager

# class CustomUserManager(BaseUserManager):
#     """
#     Custom user model manager where email is the unique identifiers
#     for authentication instead of usernames.
#     """
#     def create_user(self, email, password, **extra_fields):
#         """
#         Create and save a User with the given email and password.
#         """
#         if not email:
#             raise ValueError(_('The Email must be set'))
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save()
#         return user

#     def create_superuser(self, email, password, **extra_fields):
#         """
#         Create and save a SuperUser with the given email and password.
#         """
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('is_active', True)

#         if extra_fields.get('is_staff') is not True:
#             raise ValueError(_('Superuser must have is_staff=True.'))
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError(_('Superuser must have is_superuser=True.'))
#         return self.create_user(email, password, **extra_fields)

def nameFile(instance, filename):
    return '/'.join(['profile_images',filename])


# Create your models here.
class User(AbstractUser):
    # LOGIN_EMAIL = "email"
    # LOGIN_KAKAO = "kakao"
    # LOGIN_CHOICES = ((LOGIN_EMAIL,"Email"), (LOGIN_KAKAO, "Kakao"))

    # SOCIAL_INSTAGRAM = "instagram"
    # SOCIAL_ACCOUNT = ((SOCIAL_INSTAGRAM, "Instagram"),)
    
    # username이 required인 문제 피하기
    # username= None
    # email = models.EmailField(_('email address'), unique=True)
    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = []

    """ user model attribute"""
    # username = models.CharField(max_length=100,unique=True) # 이거 나중에 unique=True로 만들어야 함.
    profile_image = models.ImageField(blank=True, max_length=255, 
        upload_to = nameFile
    )
    bio = models.TextField(default="", blank=True)
    work_company = models.CharField(max_length=100,default="",blank=True)
    work_field = models.CharField(max_length=100, default="", blank=True) # 일하는 분야
    uid = models.BigIntegerField(blank=True, default=0)
    # hole_open_auth = models.BooleanField(default=False, blank=True) # 세션 열 수 있는 권한(호스트 여부)
    # login_method = models.CharField(max_length = 50, choices=LOGIN_CHOICES, default=LOGIN_EMAIL)
    # social_account = models.CharField(max_length=50, choices=SOCIAL_ACCOUNT, null=True, blank=True)
    # rating = models.IntegerField(default=0) # 호스트들의 평점

    # objects = CustomUserManager()

    def get_photo_url(self):
        profile_img = self.profile_image
        return profile_img.url

# token authentication
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender,instance=None, created=False, **kwargs):
    if created:
        token = Token.objects.create(user=instance) # 유저가 생성되면 토큰이 만들어짐.
        print("토큰 만들 때 token:", token.key)

class UserFollowing(core_model.AbstractTimeStamp):
    user_id = models.ForeignKey(User,related_name="following", on_delete=models.CASCADE) # 내가 following
    following_user_id = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE) # 나를 following
    created = models.DateTimeField(auto_now_add=True, db_index=True) # db_index는?

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'following_user_id'], name="unique_followers")
        ]
