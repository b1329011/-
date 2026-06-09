from django.contrib import admin
from .models import (
    User, Sport, UserSportLevel, Address, Facility, Venue, Court, 
    CourtConflict, GameMatch, MatchParticipant,
    FavoriteGame, PenaltyRule, Report, Blacklist,
    Notification, Feedback, Announcement
)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'type', 'is_handled', 'created_at')
    list_filter = ('type', 'is_handled', 'created_at')
    search_fields = ('content',)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'content')

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
    list_display = ('id', 'sport', 'court', 'match_status', 'booking_date', 'time_slot', 'most_players')
    list_filter = ('match_status', 'sport', 'booking_date')
    search_fields = ('sport__name', 'court__venue__name')

@admin.register(MatchParticipant)
class MatchParticipantAdmin(admin.ModelAdmin):
    list_display = ('match', 'user', 'joined_at')
    list_filter = ('joined_at',)

@admin.register(FavoriteGame)
class FavoriteGameAdmin(admin.ModelAdmin):
    list_display = ('user', 'match')

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

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('match', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
