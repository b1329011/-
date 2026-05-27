from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthLoginView, UserViewSet, SportViewSet, VenueViewSet, CourtViewSet,
    GameMatchViewSet, FavoriteGameViewSet, FavoriteVenueViewSet, ReportViewSet,
    AdminGameViewSet, AdminBroadcastViewSet, NotificationViewSet, OpenDataViewSet
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('sports', SportViewSet, basename='sport')
router.register('venues', VenueViewSet, basename='venue')
router.register('courts', CourtViewSet, basename='court')
router.register('games', GameMatchViewSet, basename='gamematch')
router.register('favorites/games', FavoriteGameViewSet, basename='favorite-game')
router.register('favorites/venues', FavoriteVenueViewSet, basename='favorite-venue')
router.register('reports', ReportViewSet, basename='report')
router.register('admin/games', AdminGameViewSet, basename='admin-game')
router.register('notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login', AuthLoginView.as_view(), name='auth-login'),
    path('venues/<int:venue_id>/courts/<int:pk>/report-status', CourtViewSet.as_view({'post': 'report_status'}), name='court-report-status'),
    path('admin/broadcast', AdminBroadcastViewSet.as_view({'post': 'create'}), name='admin-broadcast'),
    path('admin/opendata/sync-venues', OpenDataViewSet.as_view({'post': 'sync_venues'}), name='admin-sync-venues'),
    path('opendata/weather', OpenDataViewSet.as_view({'get': 'weather'}), name='opendata-weather'),
]