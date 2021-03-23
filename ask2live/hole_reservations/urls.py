from django.urls import path, include

from .views import (
    ReservationList,
    reserve_create_view,
    reserve_update_view,
    reserve_delete_view,
)

app_name="hole_reservations"

urlpatterns = [
    path('reservation_list/', ReservationList.as_view(), name="reservation"),
    path('create/<int:hole_id>/', reserve_create_view, name="create"),
    path('update/<int:hole_id>/', reserve_update_view, name="update"),
    path('delete/<int:hole_id>/', reserve_delete_view, name="delete"),
    # path('logout', Logout.as_view(), name="logout"),
]