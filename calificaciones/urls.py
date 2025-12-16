# calificaciones/urls.py
from django.urls import path, include
from . import views
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"groups", views.GroupViewSet)
router.register(r"Calificacion", views.CalificacionViewSet)
router.register(r"ArchivoMasivo", views.ArchivoMasivoViewSet)
router.register(r"Auditoria", views.AuditoriaViewSet)
router.register(r"ChatMessage", views.ChatMessageViewSet)



urlpatterns = [
        # Rutas JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # Dashboard y Listado
    path('', views.dashboard_view, name='dashboard'), 

    # Crear (C de CRUD)
    path('nueva-calificacion/', views.crear_calificacion, name='crear_calificacion'),

    path('carga-masiva/', views.carga_masiva_view, name='carga_masiva'),

    # Rutas que necesitan la ID (R, U, D de CRUD)
    path('<int:pk>/', views.ver_calificacion, name='ver_calificacion'),        # URL: /12/
    path('<int:pk>/editar/', views.editar_calificacion, name='editar_calificacion'),  # URL: /12/editar/
    path('<int:pk>/eliminar/', views.eliminar_calificacion, name='eliminar_calificacion'),# URL: /12/eliminar/
    path('exportar/csv/', views.exportar_calificaciones_csv, name='exportar_calificaciones_csv'),
    path('exportar/excel/', views.exportar_calificaciones_excel, name='exportar_calificaciones_excel'),
    path('exportar/pdf/', views.exportar_calificaciones_pdf, name='exportar_calificaciones_pdf'),
    path("chat/mensajes/", views.cargar_mensajes, name="cargar_mensajes"),


]