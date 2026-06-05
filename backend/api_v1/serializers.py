from rest_framework import serializers
from .models import (
    User, Sport, UserSportLevel, Address, Venue, Court, GameMatch, 
    MatchParticipant, MatchWaitlist, FavoriteGame, FavoriteVenue, 
    PenaltyRule, Report, Blacklist, UserAvailability, Notification, WeatherData,
    Feedback, Announcement
)

class UserSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'name', 'birthday', 'age', 'credit_point', 'role')
        read_only_fields = ('credit_point', 'role')

class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='id', read_only=True)
    age = serializers.ReadOnlyField()
    levels = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('user_id', 'email', 'name', 'phone', 'birthday', 'gender', 'avatar_url', 'bio', 'age', 'credit_point', 'role', 'levels')

    def get_levels(self, obj):
        res = {}
        for usl in obj.sport_levels.all():
            sport_name = usl.sport.name
            level_char = usl.level[0] if usl.level else 'C'
            res[sport_name] = level_char
            if sport_name == "羽毛球":
                res["羽球"] = level_char
            elif sport_name == "羽球":
                res["羽毛球"] = level_char
        return res

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
        fields = ('id', 'name', 'address', 'address_detail', 'opening_hours', 'types', 'facilities', 'latitude', 'longitude')


class CourtSerializer(serializers.ModelSerializer):
    venue_detail = VenueSerializer(source='venue', read_only=True)
    sports = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = Court
        fields = ('id', 'venue', 'venue_detail', 'name', 'occupied', 'base_price', 'sports')

class MatchParticipantUserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='user.id')
    phone = serializers.ReadOnlyField(source='user.phone')
    name = serializers.ReadOnlyField(source='user.name')

    class Meta:
        model = MatchParticipant
        fields = ('id', 'phone', 'name')

class GameMatchSerializer(serializers.ModelSerializer):
    sport_id = serializers.PrimaryKeyRelatedField(queryset=Sport.objects.all(), source='sport')
    court_id = serializers.PrimaryKeyRelatedField(queryset=Court.objects.all(), source='court', required=False, allow_null=True)
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    venue_name = serializers.CharField(source='court.venue.name', read_only=True)
    split_price = serializers.ReadOnlyField()
    current_players = serializers.IntegerField(source='current_players_count', read_only=True)
    participants = MatchParticipantUserSerializer(many=True, read_only=True)
    distance_km = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True, required=False)
    facilities = serializers.SerializerMethodField()
    cancel_deadline = serializers.DateTimeField(required=False, allow_null=True)
    start_time = serializers.CharField(write_only=True, required=True)
    target_level = serializers.CharField(required=True)

    def validate_target_level(self, value):
        lv_map = {
            'S': '高手',
            'A': '業餘',
            'B': '業餘',
            'C': '休閒',
            'Elite': '高手',
            'Veteran': '業餘',
            'Advanced': '業餘',
            'Beginner': '休閒',
            'S(Elite)': '高手',
            'A(Veteran)': '業餘',
            'B(advanced)': '業餘',
            'C(beginner)': '休閒',
            'S(菁英)': '高手',
            'A(高手)': '業餘',
            'B(熟練)': '業餘',
            'C(初學者)': '休閒',
            '新手(CB可參加)': '休閒',
            '高手(BA可參加)': '業餘',
            '菁英(AS可參加)': '高手',
            '休閒': '休閒',
            '業餘': '業餘',
            '高手': '高手',
        }
        if value in lv_map:
            return lv_map[value]
        valid_values = [choice[0] for choice in GameMatch.LEVEL_CHOICES]
        if value in valid_values:
            return value
        raise serializers.ValidationError("無效的等級名稱。")

    class Meta:
        model = GameMatch
        fields = [
            'id', 'game_name', 'sport_id', 'sport_name', 'court_id', 'venue_name', 'least_players', 'most_players',
            'current_players', 'target_level', 'booking_date', 'start_time', 'time_slot', 'duration', 'game_note',
            'total_price', 'split_price', 'deposit_required', 'cancel_deadline',
            'weather', 'air_index', 'is_confirmed', 'booking_status',
            'match_status', 'participants', 'distance_km', 'facilities',
            'gender_limit', 'venue_status', 'venue_note'
        ]
        read_only_fields = ('match_status', 'weather', 'air_index', 'is_confirmed', 'facilities', 'time_slot')

    def get_facilities(self, obj):
        if obj.court and obj.court.venue:
            return [f.name for f in obj.court.venue.facilities.all()]
        return []

    def validate_total_price(self, value):
        if value is not None and (value < 0 or value > 10000):
            raise serializers.ValidationError("價格必須介於 0 至 10,000 元之間。")
        return value

    def validate_gender_limit(self, value):
        if value not in ['不限', '限男', '限女']:
            raise serializers.ValidationError("性別限制必須為 '不限'、'限男' 或 '限女'。")
        return value

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.time_slot and '-' in instance.time_slot:
            ret['start_time'] = instance.time_slot.split('-')[0].strip()
        else:
            ret['start_time'] = ""
        return ret

    def validate(self, attrs):
        booking_date = attrs.get('booking_date')
        start_time_str = attrs.get('start_time')
        duration_str = attrs.get('duration')
        cancel_deadline = attrs.get('cancel_deadline')
        least_players = attrs.get('least_players')
        most_players = attrs.get('most_players')

        if self.instance:
            if not booking_date:
                booking_date = self.instance.booking_date
            if not start_time_str and self.instance.time_slot and '-' in self.instance.time_slot:
                start_time_str = self.instance.time_slot.split('-')[0].strip()
            if not duration_str:
                duration_str = self.instance.duration
            if least_players is None:
                least_players = self.instance.least_players
            if most_players is None:
                most_players = self.instance.most_players
        else:
            if not duration_str:
                duration_str = '2 小時'
            if least_players is None:
                least_players = 1

        # 1. 預約日期不能為過去
        import datetime
        if booking_date and booking_date < datetime.date.today():
            raise serializers.ValidationError({"booking_date": "球局預約日期不能為過去的日期。"})

        # 2. 人數限制校驗
        if most_players is not None:
            if most_players <= 0:
                raise serializers.ValidationError({"most_players": "最多人數必須大於 0。"})
            if most_players < least_players:
                raise serializers.ValidationError({"most_players": "最多人數不能少於最少人數。"})

        if start_time_str and booking_date:
            import re
            hours = 2.0
            if duration_str:
                # 驗證持續時間格式與數值
                match = re.search(r'(\d+(\.\d+)?)', duration_str)
                if not match:
                    raise serializers.ValidationError({"duration": "持續時間格式不正確，必須包含有效小時數，例如：2 小時。"})
                hours = float(match.group(1))
                if hours <= 0 or hours > 24:
                    raise serializers.ValidationError({"duration": "持續時間必須介於 0.5 到 24 小時之間。"})
            
            from django.utils.dateparse import parse_time
            st = parse_time(start_time_str)
            if st:
                total_minutes = int(hours * 60)
                dt = datetime.datetime.combine(booking_date, st)
                dt_end = dt + datetime.timedelta(minutes=total_minutes)
                end_time_str = dt_end.strftime("%H:%M")
                attrs['time_slot'] = f"{start_time_str}-{end_time_str}"
                
                # 計算 cancel_deadline
                if not cancel_deadline:
                    from django.utils import timezone
                    start_datetime = timezone.make_aware(dt, timezone.get_current_timezone())
                    computed_deadline = start_datetime - timezone.timedelta(days=1)
                    now = timezone.now()
                    if computed_deadline < now:
                        computed_deadline = start_datetime - timezone.timedelta(hours=1)
                        if computed_deadline < now:
                            computed_deadline = now
                    attrs['cancel_deadline'] = computed_deadline
            else:
                raise serializers.ValidationError({"start_time": "起始時間格式不正確，例如：14:00。"})

        if not attrs.get('cancel_deadline'):
            if self.instance:
                attrs['cancel_deadline'] = self.instance.cancel_deadline
            else:
                from django.utils import timezone
                attrs['cancel_deadline'] = timezone.now()

        attrs.pop('start_time', None)
        return attrs

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
        fields = ('id', 'user', 'match', 'match_detail')

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
    game_id = serializers.IntegerField(source='match_id', required=False)
    reported_user_id = serializers.IntegerField(source='offender_id', required=False)
    reporter_name = serializers.CharField(source='reporter.name', read_only=True)
    offender_name = serializers.CharField(source='offender.name', read_only=True)
    rule_detail = PenaltyRuleSerializer(source='rule', read_only=True)

    class Meta:
        model = Report
        fields = (
            'id', 'reporter', 'reporter_name', 'offender', 'offender_name',
            'match', 'rule', 'rule_detail', 'admin_note',
            'reviewed_at', 'reviewed_by', 'status',
            'game_id', 'reported_user_id', 'reason', 'detail'
        )
        read_only_fields = ('reporter', 'reviewed_at', 'reviewed_by', 'status')
        extra_kwargs = {
            'match': {'required': False, 'allow_null': True},
            'offender': {'required': False, 'allow_null': True},
        }

class BlacklistSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Blacklist
        fields = ('id', 'user', 'user_phone', 'user_name', 'added_at', 'removed_at')

class UserAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAvailability
        fields = (
            'id', 'available_dates', 'time_slots', 'preferred_city',
            'preferred_district', 'latitude', 'longitude', 'search_radius_km'
        )

class NotificationSerializer(serializers.ModelSerializer):
    notification_id = serializers.IntegerField(source='id', read_only=True)
    game_id = serializers.IntegerField(source='match.id', read_only=True)

    class Meta:
        model = Notification
        fields = ('notification_id', 'game_id', 'message', 'is_read', 'created_at')

class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Feedback
        fields = ('id', 'user', 'user_name', 'type', 'content', 'is_handled', 'created_at')
        read_only_fields = ('user',)

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ('id', 'title', 'content', 'created_at')
