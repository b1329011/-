from rest_framework import serializers
from .models import (
    User, Sport, UserSportLevel, Address, Venue, Court, GameMatch,
    MatchParticipant, FavoriteGame,
    PenaltyRule, Report, Blacklist, Notification, GameBulletin,
    Feedback, FeedbackType, Announcement
)

class UserSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'name', 'birthday', 'age', 'credit_point', 'role', 'line_id', 'instagram')
        read_only_fields = ('credit_point', 'role')

class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='id', read_only=True)
    age = serializers.ReadOnlyField()
    levels = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('user_id', 'email', 'name', 'phone', 'birthday', 'gender', 'avatar_url', 'bio', 'age', 'credit_point', 'role', 'levels', 'line_id', 'instagram')

    def get_levels(self, obj):
        res = {}
        for usl in obj.sport_levels.all():
            sport_name = usl.sport.chinese_name
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
    sport_name = serializers.CharField(source='sport.chinese_name', read_only=True)

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
    age = serializers.ReadOnlyField(source='user.age')
    level = serializers.SerializerMethodField()

    class Meta:
        model = MatchParticipant
        fields = ('id', 'phone', 'name', 'age', 'level')

    def get_level(self, obj):
        user = obj.user
        match = obj.match
        
        # 確保球局和運動分類存在
        if not match or not match.sport:
            return 'C'
            
        # 尋找該使用者對應此球局運動的等級紀錄
        sport_level = user.sport_levels.filter(sport=match.sport).first()
        
        if sport_level and sport_level.level:
            # 回傳等級的第一個字 (例如 'C(beginner)' -> 'C')
            return sport_level.level[0]
            
        return 'C' # 預設回傳 C

class GameMatchListSerializer(serializers.ModelSerializer):
    sport_id = serializers.PrimaryKeyRelatedField(queryset=Sport.objects.all(), source='sport')
    sport_name = serializers.CharField(source='sport.chinese_name', read_only=True)
    venue_name = serializers.CharField(source='court.venue.name', read_only=True)
    split_price = serializers.ReadOnlyField()
    current_players = serializers.SerializerMethodField()
    creator_id = serializers.ReadOnlyField(source='creator.id')
    participant_ids = serializers.SerializerMethodField()
    waitlist_ids = serializers.SerializerMethodField()

    class Meta:
        model = GameMatch
        fields = [
            'id', 'game_name', 'sport_id', 'sport_name', 'venue_name', 'least_players', 'most_players',
            'current_players', 'target_level', 'booking_date', 'time_slot', 
            'split_price', 'booking_status', 'match_status', 'creator_id',
            'gender_limit', 'participant_ids', 'waitlist_ids'
        ]

    def get_current_players(self, obj):
        cnt = obj.participants.count()
        return min(cnt, obj.most_players)

    def get_participant_ids(self, obj):
        all_parts = obj.participants.all().order_by('joined_at')
        regular_parts = all_parts[:obj.most_players]
        return [p.user.id for p in regular_parts]

    def get_waitlist_ids(self, obj):
        all_parts = obj.participants.all().order_by('joined_at')
        waitlisted_parts = all_parts[obj.most_players:]
        return [p.user.id for p in waitlisted_parts]

def validate_venue_hours(venue, booking_date, time_slot):
    import re
    if not venue or not venue.opening_hours:
        return True, ""

    parts = time_slot.split('-')
    if len(parts) < 2:
        return True, ""
        
    start_time_str, end_time_str = parts[0].strip(), parts[1].strip()
    
    def parse_time_to_min(t_str):
        t_str = t_str.replace('：', ':').strip()
        t_parts = re.split(r'[:]', t_str)
        if len(t_parts) >= 2:
            return int(t_parts[0]) * 60 + int(t_parts[1])
        elif len(t_parts) == 1 and len(t_parts[0]) == 4:
            return int(t_parts[0][:2]) * 60 + int(t_parts[0][2:])
        return 0

    t_min = parse_time_to_min(start_time_str)
    end_min = parse_time_to_min(end_time_str)
    if end_min <= t_min:
        end_min += 1440
        
    is_weekend = booking_date.weekday() >= 5
    day_name = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][booking_date.weekday()]
    
    opening_hours = venue.opening_hours

    # Format 1: weekdays/weekends
    if 'weekdays' in opening_hours or 'weekends' in opening_hours:
        range_str = opening_hours.get('weekends') if is_weekend else opening_hours.get('weekdays')
        if not range_str:
            return True, ""
        
        m = re.findall(r'(\d{1,2}[:：]\d{2})', range_str)
        if len(m) >= 2:
            r_start = parse_time_to_min(m[0])
            r_end = parse_time_to_min(m[1])
            if r_end <= r_start:
                r_end += 1440
            if r_end - r_start >= 1440:
                return True, ""
            if r_start <= t_min and end_min <= r_end:
                return True, ""
            else:
                return False, f"超出該場地當天營業時間 ({range_str})"
        return True, ""

    # Format 2: opening list
    opening = opening_hours.get('opening')
    if not opening or not isinstance(opening, list):
        return True, ""
        
    day_specific_entries = [e for e in opening if e.get('days') and e.get('days') != '全年24小時']
    if day_specific_entries:
        matching_entries = [e for e in day_specific_entries if day_name in e.get('days')]
        if not matching_entries:
            return False, f"該場地於 {day_name} 不開放營業"
    else:
        matching_entries = opening

    for entry in matching_entries:
        time_text = entry.get('time')
        if not time_text or time_text in ['無', '全年24小時']:
            continue
            
        if '不對外開放' in time_text or '不開放' in time_text or '無法開放' in time_text:
            m = re.findall(r'(\d{1,2}[:：]?\d{2}?)\s*[-~～至]\s*(\d{1,2}[:：]\d{2})', time_text)
            closed_ranges = []
            for r in m:
                closed_ranges.append((parse_time_to_min(r[0]), parse_time_to_min(r[1])))
                
            if not closed_ranges and not is_weekend:
                closed_ranges.append((8 * 60, 17 * 60))
            
            if closed_ranges:
                for r_start, r_end in closed_ranges:
                    if r_end <= r_start:
                        r_end += 1440
                    if t_min < r_end and r_start < end_min:
                        return False, f"此時段為該場地非開放時間：{time_text}"
                        
        elif '開放時間' in time_text or '開放' in time_text or '時段' in time_text:
            weekday_part = ""
            weekend_part = ""
            if '週六週日' in time_text or '假日' in time_text or '例假日' in time_text:
                parts = re.split(r'[，,；;。]', time_text)
                for p in parts:
                    if any(k in p for k in ['週六週日', '假日', '例假日', '週六', '週日']):
                        weekend_part += " " + p
                    else:
                        weekday_part += " " + p
            else:
                weekday_part = time_text
                
            active_part = weekend_part if is_weekend else weekday_part
            if not active_part.strip():
                active_part = time_text
                
            m = re.findall(r'(\d{1,2}[:：]?\d{2}?)\s*[-~～至]\s*(\d{1,2}[:：]\d{2})', active_part)
            open_ranges = []
            for r in m:
                open_ranges.append((parse_time_to_min(r[0]), parse_time_to_min(r[1])))
                
            if open_ranges:
                matched = False
                for r_start, r_end in open_ranges:
                    if r_end <= r_start:
                        r_end += 1440
                    if r_end - r_start >= 1440:
                        matched = True
                        break
                    if r_start <= t_min and end_min <= r_end:
                        matched = True
                        break
                if not matched:
                    return False, f"此時段超出該場地開放時間：{time_text}"
            
    return True, ""

class GameMatchSerializer(serializers.ModelSerializer):
    sport_id = serializers.PrimaryKeyRelatedField(queryset=Sport.objects.all(), source='sport')
    court_id = serializers.PrimaryKeyRelatedField(queryset=Court.objects.all(), source='court', required=False, allow_null=True)
    sport_name = serializers.CharField(source='sport.chinese_name', read_only=True)
    venue_name = serializers.CharField(source='court.venue.name', read_only=True)
    split_price = serializers.ReadOnlyField()
    current_players = serializers.SerializerMethodField()
    current_waitlist = serializers.SerializerMethodField()
    max_waitlist = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()
    waitlist = serializers.SerializerMethodField()
    participant_ids = serializers.SerializerMethodField()
    waitlist_ids = serializers.SerializerMethodField()
    creator_id = serializers.ReadOnlyField(source='creator.id')
    distance_km = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True, required=False)
    facilities = serializers.SerializerMethodField()
    cancel_deadline = serializers.DateTimeField(required=False, allow_null=True)
    start_time = serializers.CharField(write_only=True, required=True)
    target_level = serializers.CharField(required=True)
    duration = serializers.CharField(write_only=True, required=False, default='2 小時')
    announcements = serializers.SerializerMethodField()

    def validate_target_level(self, value):
        valid_values = [choice[0] for choice in GameMatch.LEVEL_CHOICES]
        if value in valid_values:
            return value
        raise serializers.ValidationError("無效的等級名稱，必須為 '休閒'、'業餘' 或 '高手'。")

    class Meta:
        model = GameMatch
        fields = [
            'id', 'game_name', 'sport_id', 'sport_name', 'court_id', 'venue_name', 'least_players', 'most_players',
            'current_players', 'target_level', 'booking_date', 'start_time', 'time_slot', 'duration', 'game_note',
            'total_price', 'split_price', 'deposit_required', 'cancel_deadline',
            'weather', 'air_index', 'booking_status',
            'match_status', 'participants', 'waitlist', 'participant_ids', 'waitlist_ids', 'current_waitlist', 'max_waitlist', 'creator_id', 'distance_km', 'facilities',
            'gender_limit', 'announcements'
        ]
        read_only_fields = ('match_status', 'weather', 'air_index', 'facilities', 'time_slot')

    def get_facilities(self, obj):
        if obj.court and obj.court.venue:
            return [f.name for f in obj.court.venue.facilities.all()]
        return []

    def get_announcements(self, obj):
        latest = obj.bulletins.order_by('-created_at').first()
        return latest.content if latest else ""

    def get_current_players(self, obj):
        cnt = obj.participants.count()
        return min(cnt, obj.most_players)

    def get_current_waitlist(self, obj):
        cnt = obj.participants.count()
        return max(0, cnt - obj.most_players)

    def get_max_waitlist(self, obj):
        import math
        max_allowed = math.ceil(obj.most_players * 1.3)
        return max_allowed - obj.most_players

    def get_participant_ids(self, obj):
        all_parts = obj.participants.all().order_by('joined_at')
        regular_parts = all_parts[:obj.most_players]
        return [p.user.id for p in regular_parts]

    def get_waitlist_ids(self, obj):
        all_parts = obj.participants.all().order_by('joined_at')
        waitlisted_parts = all_parts[obj.most_players:]
        return [p.user.id for p in waitlisted_parts]

    def get_participants(self, obj):
        all_parts = obj.participants.all().order_by('joined_at')
        regular_parts = all_parts[:obj.most_players]
        return MatchParticipantUserSerializer(regular_parts, many=True).data

    def get_waitlist(self, obj):
        all_parts = obj.participants.all().order_by('joined_at')
        waitlisted_parts = all_parts[obj.most_players:]
        return MatchParticipantUserSerializer(waitlisted_parts, many=True).data

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

        # 人數達標時將招募中狀態轉換為已成團，優化前端顯示效果
        if instance.match_status == 'recruiting' and instance.current_players_count >= instance.least_players: 
            ret['match_status'] = 'established'

        return ret


    def validate(self, attrs):
        import datetime
        booking_date = attrs.get('booking_date')
        start_time_str = attrs.get('start_time')
        duration_str = attrs.get('duration')
        cancel_deadline = attrs.get('cancel_deadline')
        least_players = attrs.get('least_players')
        most_players = attrs.get('most_players')

        # 性別限制校驗：男生不能發起/修改為限女生團，女生不能發起/修改為限男生團
        gender_limit = attrs.get('gender_limit')
        if self.instance and gender_limit is None:
            gender_limit = self.instance.gender_limit
            
        if gender_limit and gender_limit != '不限':
            request = self.context.get('request')
            if request and request.user and request.user.is_authenticated:
                user_gender = request.user.gender
                if gender_limit == '限男' and user_gender != '男':
                    raise serializers.ValidationError({"gender_limit": "男性專屬球局只能由男生發起。"})
                elif gender_limit == '限女' and user_gender != '女':
                    raise serializers.ValidationError({"gender_limit": "女性專屬球局只能由女生發起。"})

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

        # 解決前端跨日或早晨球局 (台北時間 00:00 - 08:00) 因使用 .toISOString() 轉換成 UTC Date 導致日期少一天的問題。
        # 當傳入 booking_date 且其對應的 start_time 小時小於 8 時，自動將日期加一天以修正為正確的台北本地日期。
        if 'booking_date' in attrs and start_time_str:
            from django.utils.dateparse import parse_time
            st = parse_time(start_time_str)
            if st and st.hour < 8:
                booking_date = booking_date + datetime.timedelta(days=1)
                attrs['booking_date'] = booking_date

        # 1. 預約日期不能為過去
        from django.utils import timezone
        if booking_date and booking_date < timezone.localdate():
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

        # 3. 驗證場地營業時間
        val_date = booking_date or (self.instance.booking_date if self.instance else None)
        val_time_slot = attrs.get('time_slot') or (self.instance.time_slot if self.instance else None)
        if val_date and val_time_slot:
            request = self.context.get('request')
            venue = None
            if request:
                venue_id = request.data.get('venue_id')
                court_id = request.data.get('court_id')
                if court_id:
                    court = Court.objects.filter(id=court_id).first()
                    if court:
                        venue = court.venue
                elif venue_id:
                    venue = Venue.objects.filter(id=venue_id).first()
            
            if not venue and self.instance and self.instance.court:
                venue = self.instance.court.venue

            if venue:
                is_open, err_msg = validate_venue_hours(venue, val_date, val_time_slot)
                if not is_open:
                    raise serializers.ValidationError({"time_slot": err_msg})

        attrs.pop('start_time', None)
        attrs.pop('duration', None)
        return attrs


class MatchParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchParticipant
        fields = '__all__'

# class MatchWaitlistSerializer(serializers.ModelSerializer):
#     user_name = serializers.CharField(source='user.name', read_only=True)
# 
#     class Meta:
#         model = MatchWaitlist
#         fields = ('id', 'match', 'user', 'user_name', 'queue_position', 'status', 'joined_at')

class FavoriteGameSerializer(serializers.ModelSerializer):
    match_detail = GameMatchSerializer(source='match', read_only=True)

    class Meta:
        model = FavoriteGame
        fields = ('id', 'user', 'match', 'match_detail')

# class FavoriteVenueSerializer(serializers.ModelSerializer):
#     venue_detail = VenueSerializer(source='venue', read_only=True)
# 
#     class Meta:
#         model = FavoriteVenue
#         fields = ('id', 'user', 'venue', 'venue_detail', 'created_at')

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
            'game_id', 'reported_user_id', 'detail'
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

# class UserAvailabilitySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserAvailability
#         fields = (
#             'id', 'available_dates', 'time_slots', 'preferred_city',
#             'preferred_district', 'latitude', 'longitude', 'search_radius_km'
#         )

class NotificationSerializer(serializers.ModelSerializer):
    notification_id = serializers.IntegerField(source='id', read_only=True)
    game_id = serializers.IntegerField(source='match.id', read_only=True)

    class Meta:
        model = Notification
        fields = ('notification_id', 'game_id', 'message', 'is_read', 'created_at')

# class WeatherDataSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WeatherData
#         fields = '__all__'

class GameBulletinSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameBulletin
        fields = ('id', 'match', 'title', 'content', 'created_at')

class FeedbackTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackType
        fields = ('id', 'name')

class FeedbackSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Feedback
        fields = ('id', 'user', 'user_name', 'type', 'content', 'is_handled', 'admin_reply', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'

    def validate_photo(self, value):
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("公告圖片格式必須為列表（Array）。")
        if len(value) > 3:
            raise serializers.ValidationError("公告圖片數量上限為 3 張。")
        for url in value:
            if not isinstance(url, str):
                raise serializers.ValidationError("公告圖片的 URL 必須是字串（String）。")
        return value
