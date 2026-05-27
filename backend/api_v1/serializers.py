from rest_framework import serializers
from .models import (
    User, Sport, UserSportLevel, Address, Venue, Court, GameMatch, 
    MatchParticipant, MatchWaitlist, FavoriteGame, FavoriteVenue, 
    PenaltyRule, Report, Blacklist, UserAvailability, Notification, WeatherData
)

class UserSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'phone', 'name', 'birthday', 'age', 'credit_point', 'role')
        read_only_fields = ('credit_point', 'role')

class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='id', read_only=True)
    age = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('user_id', 'name', 'phone', 'birthday', 'age', 'credit_point', 'role')

class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = '__all__'

class UserSportLevelSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source='sport.name', read_only=True)

    class Meta:
        model = UserSportLevel
        fields = ('id', 'sport', 'sport_name', 'level', 'updated_at')

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class VenueSerializer(serializers.ModelSerializer):
    address_detail = AddressSerializer(source='address', read_only=True)
    facilities = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = Venue
        fields = ('id', 'name', 'address', 'address_detail', 'base_price', 'opening_hours', 'types', 'facilities')

class CourtSerializer(serializers.ModelSerializer):
    venue_detail = VenueSerializer(source='venue', read_only=True)
    sports = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = Court
        fields = ('id', 'venue', 'venue_detail', 'name', 'occupied', 'sports')

class MatchParticipantUserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='user.id')
    phone = serializers.ReadOnlyField(source='user.phone')
    name = serializers.ReadOnlyField(source='user.name')

    class Meta:
        model = MatchParticipant
        fields = ('id', 'phone', 'name')

class GameMatchSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    venue_name = serializers.CharField(source='court.venue.name', read_only=True)
    split_price = serializers.ReadOnlyField()
    current_players = serializers.IntegerField(source='current_players_count', read_only=True)
    participants = MatchParticipantUserSerializer(many=True, read_only=True)
    distance_km = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True, required=False)

    class Meta:
        model = GameMatch
        fields = [
            'id', 'sport_id', 'sport_name', 'court_id', 'venue_name', 'least_players', 'most_players',
            'current_players', 'target_level', 'booking_date', 'time_slot',
            'total_price', 'split_price', 'deposit_required', 'cancel_deadline',
            'weather_index', 'air_index', 'is_confirmed', 'booking_status',
            'match_status', 'participants', 'distance_km'
        ]
        read_only_fields = ('match_status', 'weather_index', 'air_index', 'is_confirmed')

class MatchParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchParticipant
        fields = '__all__'

class MatchWaitlistSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = MatchWaitlist
        fields = ('id', 'match', 'user', 'user_name', 'queue_position', 'status', 'joined_at')

class FavoriteGameSerializer(serializers.ModelSerializer):
    match_detail = GameMatchSerializer(source='match', read_only=True)

    class Meta:
        model = FavoriteGame
        fields = ('id', 'user', 'match', 'match_detail', 'created_at')

class FavoriteVenueSerializer(serializers.ModelSerializer):
    venue_detail = VenueSerializer(source='venue', read_only=True)

    class Meta:
        model = FavoriteVenue
        fields = ('id', 'user', 'venue', 'venue_detail', 'created_at')

class PenaltyRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PenaltyRule
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source='reporter.name', read_only=True)
    offender_name = serializers.CharField(source='offender.name', read_only=True)
    rule_detail = PenaltyRuleSerializer(source='rule', read_only=True)

    class Meta:
        model = Report
        fields = (
            'id', 'reporter', 'reporter_name', 'offender', 'offender_name',
            'match', 'reason', 'rule', 'rule_detail', 'admin_note',
            'reviewed_at', 'reviewed_by', 'status', 'created_at'
        )
        read_only_fields = ('reporter', 'reviewed_at', 'reviewed_by', 'status')

class BlacklistSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Blacklist
        fields = ('id', 'user', 'user_phone', 'user_name', 'reason', 'added_at', 'removed_at')

class UserAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAvailability
        fields = (
            'id', 'available_dates', 'time_slots', 'preferred_city',
            'preferred_district', 'latitude', 'longitude', 'search_radius_km'
        )

class NotificationSerializer(serializers.ModelSerializer):
    notification_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Notification
        fields = ('notification_id', 'title', 'content', 'is_read', 'created_at')

class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        fields = '__all__'
