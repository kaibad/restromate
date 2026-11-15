from django.urls import path
from . import views


urlpatterns = [

    path("tables/",views.tables_view,name="tables_view_url"),
    path("menu/<table_id>/",views.menu_view,name="menu_view_url"),
    path("tables/live/",views.tables_status_live,name="tables_status_live_url"),
    path("kitchen/dashboard",views.kitchen_dashboard_view,name="kitchen_dashboard_view_url"),
    path("kitchen/items/<int:pk>/", views.kicthen_item_view, name="kitchen_item_url"),

    path("menu/<table_id>/ready/", views.ready_items_partial, name="ready_items_url"),
    path("items/serve/", views.serve_item_view, name="serve_item_url"),
]
