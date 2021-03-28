from django.urls import path, include

from .views import (
    ReservationList,
   reserve_update_view,
    reserve_delete_view,
)
from holes.views import (
    hole_wish_view,
    hole_wish_cancel_view,
    host_hole_confirm_view
    )

app_name="hole_reservations"

urlpatterns = [
    path('reservation_list/', ReservationList.as_view(), name="reservation"),
    # path('create/<int:hole_id>/', reserve_create_view, name="create"),
    path('update/<int:hole_id>/', reserve_update_view, name="update"),
    path('delete/<int:hole_id>/', reserve_delete_view, name="delete"),
    path('hole/<int:pk>/wish', hole_wish_view, name="wish"),
    path('hole/<int:pk>/wishcancel', hole_wish_cancel_view, name="wish_cancel"),
    path('hole/<int:pk>/hostconfirm', host_hole_confirm_view, name="host_confirm"),
]