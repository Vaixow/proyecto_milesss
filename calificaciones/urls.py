# calificaciones/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard y Listado
    path('', views.dashboard_view, name='dashboard'), 

    # Crear (C de CRUD)
    path('nueva-calificacion/', views.crear_calificacion, name='crear_calificacion'),

    path('carga-masiva/', views.carga_masiva_view, name='carga_masiva'),

    # Rutas que necesitan la ID (R, U, D de CRUD)
    path('<int:pk>/', views.ver_calificacion, name='ver_calificacion'),        # URL: /12/
    path('<int:pk>/editar/', views.editar_calificacion, name='editar_calificacion'),  # URL: /12/editar/
    path('<int:pk>/eliminar/', views.eliminar_calificacion, name='eliminar_calificacion'),# URL: /12/eliminar/
]