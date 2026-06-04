from django.contrib import admin
from .models import (
    User, Sport, UserSportLevel, Address, Facility, Venue, Court, 
    CourtConflict, GameMatch, MatchParticipant, MatchWaitlist,
    FavoriteGame, FavoriteVenue, PenaltyRule, Report, Blacklist,
    UserAvailability, Notification, WeatherData, Feedback, Announcement
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone', 'name', 'birthday', 'credit_point', 'role')
    list_filter = ('role',)
    search_fields = ('phone', 'name')
    ordering = ('phone',)
    fields = ('phone', 'name', 'password', 'birthday', 'role', 'credit_point')

@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(UserSportLevel)
class UserSportLevelAdmin(admin.ModelAdmin):
    list_display = ('user', 'sport', 'level')
    list_filter = ('level', 'sport')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'district', 'street_line')
    list_filter = ('city', 'district')
    search_fields = ('city', 'district', 'street_line')

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'types')
    list_filter = ('types',)
    search_fields = ('name',)

@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'venue', 'occupied', 'base_price')
    list_filter = ('venue', 'occupied')

@admin.register(CourtConflict)
class CourtConflictAdmin(admin.ModelAdmin):
    list_display = ('id', 'court1', 'court2')

@admin.register(GameMatch)
class GameMatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'sport', 'court', 'match_status', 'booking_date', 'time_slot', 'most_players', 'is_confirmed')
    list_filter = ('match_status', 'sport', 'booking_date', 'is_confirmed')
    search_fields = ('sport__name', 'court__venue__name')

@admin.register(MatchParticipant)
class MatchParticipantAdmin(admin.ModelAdmin):
    list_display = ('match', 'user', 'joined_at')
    list_filter = ('joined_at',)

@admin.register(MatchWaitlist)
class MatchWaitlistAdmin(admin.ModelAdmin):
    list_display = ('match', 'user', 'queue_position', 'status', 'joined_at')
    list_filter = ('status', 'joined_at')

@admin.register(FavoriteGame)
class FavoriteGameAdmin(admin.ModelAdmin):
    list_display = ('user', 'match')

@admin.register(FavoriteVenue)
class FavoriteVenueAdmin(admin.ModelAdmin):
    list_display = ('user', 'venue', 'created_at')

@admin.register(PenaltyRule)
class PenaltyRuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'reason', 'points_deducted')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'offender', 'status')
    list_filter = ('status',)
    search_fields = ('reporter__name', 'offender__name')

@admin.register(Blacklist)
class BlacklistAdmin(admin.ModelAdmin):
    list_display = ('user', 'added_at', 'removed_at')
    search_fields = ('user__name', 'user__phone')

@admin.register(UserAvailability)
class UserAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_city', 'preferred_district', 'search_radius_km')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('match', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('city', 'district', 'temperature', 'rain_probability', 'aqi', 'updated_at')
    list_filter = ('city',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'created_at')
    list_filter = ('type', 'created_at')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    list_filter = ('created_at',)
