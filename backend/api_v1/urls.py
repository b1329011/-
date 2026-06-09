from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthLoginView, AuthRegisterView, UserViewSet, SportViewSet, VenueViewSet, CourtViewSet,
    GameMatchViewSet, FavoriteGameViewSet, ReportViewSet,
    AdminGameViewSet, AdminBroadcastViewSet, NotificationViewSet, OpenDataViewSet,
    AdminAnalyticsView, DemoWeatherView, FeedbackViewSet, FeedbackTypeViewSet,
    AnnouncementViewSet, upload_image
)

class OptionalSlashRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Change trailing slash match to optional regex '/?'
        self.trailing_slash = '/?'

router = OptionalSlashRouter()
router.register('users', UserViewSet, basename='user')
router.register('sports', SportViewSet, basename='sport')
router.register('venues', VenueViewSet, basename='venue')
router.register('courts', CourtViewSet, basename='court')
router.register('games', GameMatchViewSet, basename='gamematch')
router.register('favorites/games', FavoriteGameViewSet, basename='favorite-game')
# router.register('favorites/venues', FavoriteVenueViewSet, basename='favorite-venue')
router.register('reports', ReportViewSet, basename='report')
router.register('admin/games', AdminGameViewSet, basename='admin-game')
router.register('notifications', NotificationViewSet, basename='notification')
router.register('announcements', AnnouncementViewSet, basename='announcement')
router.register('feedback', FeedbackViewSet, basename='feedback')
router.register('admin/feedbacks', FeedbackViewSet, basename='admin-feedback')
router.register('feedback-types', FeedbackTypeViewSet, basename='feedback-type')

urlpatterns = [
    path('', include(router.urls)),
    
    # Custom non-viewset endpoints with optional trailing slash support
    re_path(r'^admin/venues/(?P<pk>\d+)/?$', VenueViewSet.as_view({'delete': 'destroy'}), name='admin-venue-delete'),
    re_path(r'^auth/register/?$', AuthRegisterView.as_view(), name='auth-register'),
    re_path(r'^auth/login/?$', AuthLoginView.as_view(), name='auth-login'),
    re_path(r'^admin/broadcast/?$', AdminBroadcastViewSet.as_view({'post': 'create'}), name='admin-broadcast'),
    re_path(r'^admin/opendata/sync-venues/?$', OpenDataViewSet.as_view({'post': 'sync_venues'}), name='admin-sync-venues'),
    re_path(r'^opendata/weather/?$', OpenDataViewSet.as_view({'get': 'weather'}), name='opendata-weather'),
    re_path(r'^weather/aqi/?$', OpenDataViewSet.as_view({'get': 'weather_aqi'}), name='weather-aqi'),
    re_path(r'^admin/announcements/?$', AnnouncementViewSet.as_view({'post': 'create'}), name='admin-announcement-create'),
    re_path(r'^admin/analytics/?$', AdminAnalyticsView.as_view(), name='admin-analytics'),
    re_path(r'^admin/demo/games/(?P<pk>\d+)/status/?$', AdminGameViewSet.as_view({'patch': 'change_status'}), name='admin-demo-game-status'),
    re_path(r'^admin/demo/weather/?$', DemoWeatherView.as_view(), name='admin-demo-weather'),
    re_path(r'^upload/?$', upload_image, name='upload-image'),
]