import math
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, permissions, mixins, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .models import (
    Sport, UserSportLevel, Address, Venue, Court, CourtConflict,
    GameMatch, MatchParticipant, FavoriteGame,
    PenaltyRule, Report, Blacklist,
    Notification, GameBulletin, Feedback, Announcement, Facility
)
from .serializers import (
    UserSerializer, UserProfileSerializer, SportSerializer, UserSportLevelSerializer,
    AddressSerializer, VenueSerializer, CourtSerializer, GameMatchSerializer,
    GameMatchListSerializer, MatchParticipantUserSerializer,
    MatchParticipantSerializer, FavoriteGameSerializer,
    PenaltyRuleSerializer, ReportSerializer,
    BlacklistSerializer, NotificationSerializer, GameBulletinSerializer,
    FeedbackSerializer, AnnouncementSerializer
)

User = get_user_model()

# Helper function for distance calculation
def haversine_distance(lat1, lon1, lat2, lon2):
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return None
    degrees_to_radians = math.pi / 180.0
    phi1 = float(lat1) * degrees_to_radians
    phi2 = float(lat2) * degrees_to_radians
    theta1 = float(lon1) * degrees_to_radians
    theta2 = float(lon2) * degrees_to_radians
    
    dphi = phi2 - phi1
    dtheta = theta2 - theta1
    
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dtheta / 2.0) ** 2
    c = 2.0 * math.asin(math.sqrt(a))
    return 6371.0 * c

def get_sport_by_name_or_alias(sport_name, create=True):
    for sport in Sport.objects.all():
        if sport.name.strip().lower() == sport_name.strip().lower():
            return sport
            
    if create:
        sport, _ = Sport.objects.get_or_create(name=sport_name)
        return sport
    return None

class IsAdminRole(permissions.BasePermission):
    """
    Custom Admin permission class based on User.role
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

def check_and_update_credit(user):
    if user.credit_point <= 40:
        return
    if user.credit_point >= 100:
        return
    now = timezone.now()
    if not user.last_credit_update:
        user.last_credit_update = now
        user.save()
        return

    elapsed_seconds = (now - user.last_credit_update).total_seconds()
    seconds_per_point = 2 * 86400  # 1 point per 2 days
    
    points_to_recover = int(elapsed_seconds / seconds_per_point)
    if points_to_recover > 0:
        user.credit_point = min(100, user.credit_point + points_to_recover)
        user.last_credit_update = user.last_credit_update + timedelta(seconds=points_to_recover * seconds_per_point)
        user.save()

class IsNotBanned(permissions.BasePermission):
    message = "您的信譽分數已低於或等於 40 分，帳號已被永久停權。"
    
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            check_and_update_credit(request.user)
            if request.user.credit_point <= 40:
                return False
        return True

class AuthRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password')

        if not name or not email or not password:
            return Response({"detail": "name, email and password are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        import re
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            return Response({"detail": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"detail": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(email=email, name=name, password=password)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user_id": user.id,
                "role": user.role
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AuthLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"detail": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import authenticate
        user = authenticate(email=email, password=password)
        if not user:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)

        # 執行信用分每日恢復檢查
        check_and_update_credit(user)

        # 檢查是否被永久停權
        if user.credit_point <= 40:
            return Response({"detail": "您的信譽分數已低於或等於 40 分，帳號已被永久停權。"}, status=status.HTTP_403_FORBIDDEN)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user_id": user.id,
            "role": user.role
        }, status=status.HTTP_200_OK)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]

    @action(detail=False, methods=['get', 'put', 'patch', 'delete'], url_path='profile')
    def profile(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)
        
        if request.method == 'DELETE':
            user.delete()
            return Response({"detail": "帳號已成功註銷與刪除。"}, status=status.HTTP_200_OK)
        
        # PUT / PATCH
        name = request.data.get('name')
        phone = request.data.get('phone')
        bio = request.data.get('bio')
        gender = request.data.get('gender')
        avatar = request.data.get('avatar')
        birthday = request.data.get('birthday')
        levels = request.data.get('levels')
        instagram = request.data.get('instagram') or request.data.get('ig')
        line_id = request.data.get('line_id') or request.data.get('line')

        # Robust string/JSON parsing for levels and ISO date formatting for birthday
        if levels and isinstance(levels, str):
            import json
            try:
                levels = json.loads(levels)
            except Exception:
                pass

        if birthday and isinstance(birthday, str):
            if 'T' in birthday:
                birthday = birthday.split('T')[0]

        # 首次建立檔案校驗：phone 與 levels 為必填
        is_first_setup = not user.phone
        if is_first_setup:
            if not phone:
                return Response({"detail": "Phone is required for initial profile setup."}, status=status.HTTP_400_BAD_REQUEST)
            if not birthday:
                return Response({"detail": "Birthday is required for initial profile setup."}, status=status.HTTP_400_BAD_REQUEST)
            if not gender:
                return Response({"detail": "Gender is required for initial profile setup."}, status=status.HTTP_400_BAD_REQUEST)
            if not levels:
                return Response({"detail": "Sport levels are required for initial profile setup."}, status=status.HTTP_400_BAD_REQUEST)

            # 首次修改時檢查手機、IG、LINE是否重複
            duplicates = {}
            if phone and User.objects.exclude(id=user.id).filter(phone=phone).exists():
                duplicates['phone'] = "手機號碼已被使用。"
            if instagram and User.objects.exclude(id=user.id).filter(instagram=instagram).exists():
                duplicates['instagram'] = "Instagram 帳號已被使用。"
            if line_id and User.objects.exclude(id=user.id).filter(line_id=line_id).exists():
                duplicates['line_id'] = "LINE ID 已被使用。"

            if duplicates:
                return Response({
                    "detail": "手機、IG 或 LINE 帳號重複。",
                    "duplicates": duplicates
                }, status=status.HTTP_400_BAD_REQUEST)

        # 手機號碼格式驗證
        if phone:
            import re
            if not re.match(r"^09\d{8}$", phone):
                return Response({"detail": "手機號碼格式不正確，必須是 09 開頭且為 10 碼數字。"}, status=status.HTTP_400_BAD_REQUEST)

        if name:
            user.name = name
        if phone:
            user.phone = phone
        if bio is not None:
            user.bio = bio
        if avatar:
            user.avatar_url = avatar
        if instagram is not None:
            user.instagram = instagram
        if line_id is not None:
            user.line_id = line_id

        # birthday 與 gender 僅能在首次建立檔案時填寫，後續不可修改
        if birthday:
            if not user.birthday:
                user.birthday = birthday
            elif str(user.birthday) != str(birthday):
                # 忽略修改
                pass
        
        if gender:
            if not user.gender or user.gender == '不願透漏':
                if gender not in ['男', '女']:
                    return Response({"detail": "性別必須為 '男' 或 '女'。"}, status=status.HTTP_400_BAD_REQUEST)
                user.gender = gender
            elif user.gender != gender:
                # 忽略修改
                pass

        user.save()

        if levels and isinstance(levels, dict):
            for sport_name, short_lv in levels.items():
                first_char = short_lv.strip().upper()[0] if short_lv else 'C'
                if first_char not in ['S', 'A', 'B', 'C']:
                    first_char = 'C'
                sport = get_sport_by_name_or_alias(sport_name)
                UserSportLevel.objects.update_or_create(
                    user=user, sport=sport,
                    defaults={'level': first_char}
                )

        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['get', 'put'], url_path='sport-levels')
    def sport_levels(self, request):
        if request.method == 'GET':
            levels = UserSportLevel.objects.filter(user=request.user)
            serializer = UserSportLevelSerializer(levels, many=True)
            return Response(serializer.data)
        elif request.method == 'PUT':
            sport_id = request.data.get('sport_id')
            level = request.data.get('level')
            if not sport_id or not level:
                return Response({"detail": "sport_id and level are required."}, status=status.HTTP_400_BAD_REQUEST)
            
            first_char = level.strip().upper()[0] if level else 'C'
            if first_char not in ['S', 'A', 'B', 'C']:
                first_char = 'C'
            
            sport = get_object_or_404(Sport, pk=sport_id)
            level_obj, created = UserSportLevel.objects.update_or_create(
                user=request.user, sport=sport,
                defaults={'level': first_char}
            )
            serializer = UserSportLevelSerializer(level_obj)
            return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='reputation', permission_classes=[IsAdminRole])
    def update_reputation(self, request, pk=None):
        user = self.get_object()
        score = request.data.get('credit_point')
        if score is not None:
            try:
                user.credit_point = int(score)
                user.save()
                return Response({"detail": f"User credit points updated to {user.credit_point}."})
            except ValueError:
                return Response({"detail": "Invalid credit point value."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "credit_point is required."}, status=status.HTTP_400_BAD_REQUEST)

    # @action(detail=False, methods=['get', 'post'], url_path='availability')
    # def availability(self, request):
    #     availability_obj = UserAvailability.objects.filter(user=request.user).first()
    #     if request.method == 'GET':
    #         if not availability_obj:
    #             return Response({"detail": "Availability not set yet."}, status=status.HTTP_404_NOT_FOUND)
    #         serializer = UserAvailabilitySerializer(availability_obj)
    #         return Response(serializer.data)
    #     elif request.method == 'POST':
    #         if availability_obj:
    #             serializer = UserAvailabilitySerializer(availability_obj, data=request.data, partial=True)
    #         else:
    #             serializer = UserAvailabilitySerializer(data=request.data)
    #         
    #         if serializer.is_valid():
    #             serializer.save(user=request.user)
    #             return Response({
    #                 "status": "success",
    #                 "message": "月曆可用時間與地點更新成功。"
    #             }, status=status.HTTP_200_OK)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SportViewSet(viewsets.ModelViewSet):
    queryset = Sport.objects.all()
    serializer_class = SportSerializer
    permission_classes = [permissions.AllowAny]

class VenueViewSet(viewsets.ModelViewSet):
    serializer_class = VenueSerializer

    def get_queryset(self):
        queryset = Venue.objects.select_related('address').prefetch_related('facilities').all()
        city = self.request.query_params.get('city')
        district = self.request.query_params.get('district')
        if city:
            queryset = queryset.filter(address__city__icontains=city)
        if district:
            queryset = queryset.filter(address__district__icontains=district)
        return queryset

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'regions']:
            return [permissions.AllowAny()]
        return [IsAdminRole()]

    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        city = request.data.get('city')
        district = request.data.get('district')
        street_line = request.data.get('street_line', '未指定路段')
        facilities_list = request.data.get('facilities', [])
        
        # 1. Create or get Address
        address, _ = Address.objects.get_or_create(
            city=city,
            district=district,
            street_line=street_line
        )
        
        # 2. Create Venue
        venue = Venue.objects.create(
            name=name,
            address=address,
            types='indoor'
        )
        
        # 3. Handle Facilities
        if isinstance(facilities_list, str):
            facilities_list = [f.strip() for f in facilities_list.split(',') if f.strip()]
        
        for f_name in facilities_list:
            facility, _ = Facility.objects.get_or_create(name=f_name)
            venue.facilities.add(facility)
            
        serializer = self.get_serializer(venue)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='regions')
    def regions(self, request):
        """
        Returns venues grouped by City and District, matching the frontend's expected structure.
        """
        venues = self.get_queryset()
        regions_data = {}
        
        for v in venues:
            if not v.address:
                continue
            city = v.address.city
            district = v.address.district
            
            if city not in regions_data:
                regions_data[city] = {}
            if district not in regions_data[city]:
                regions_data[city][district] = []
            
            regions_data[city][district].append({
                "id": v.id,
                "name": v.name,
                "facilities": [f.name for f in v.facilities.all()]
            })
            
        return Response(regions_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        venue = self.get_object()
        active_matches = GameMatch.objects.filter(
            court__venue=venue,
            match_status__in=['recruiting', 'full']
        )
        if active_matches.exists():
            return Response(
                {"detail": "無法刪除此場地：仍有招募中或進行中的球局正在使用該場地。"},
                status=status.HTTP_409_CONFLICT
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['patch'], url_path='approve')
    def approve(self, request, pk=None):
        remarks = request.data.get('remarks', '')
        return Response({
            "is_approved": 1,
            "remarks": remarks or "場地安全設施與地板規格審核通過"
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='emergency-close')
    def emergency_close(self, request, pk=None):
        venue = self.get_object()
        close_date = request.data.get('close_date')
        time_slots = request.data.get('time_slots', [])
        reason = request.data.get('reason', '緊急關閉')

        if not close_date:
            return Response({"detail": "close_date is required."}, status=status.HTTP_400_BAD_REQUEST)

        affected_matches = GameMatch.objects.filter(
            court__venue=venue,
            booking_date=close_date,
            time_slot__in=time_slots
        )

        for match in affected_matches:
            Notification.objects.create(
                user=match.creator,
                match=match,
                message=f"【場館警報】不可抗力建議取消通知：您預訂的場館【{venue.name}】因不可抗力因素（{reason}）臨時關閉/警告，系統強烈建議您主動取消或修改您的球局，以保障球友權益與安全。"
            )
            for p in match.participants.all():
                if p.user != match.creator:
                    Notification.objects.create(
                        user=p.user,
                        match=match,
                        message=f"【場館警報】不可抗力建議取消通知：您參加的「{match.sport.chinese_name}」球局場館【{venue.name}】因臨時關閉（{reason}）受到影響，請留意主揪後續通知。"
                    )

        return Response({
            "status": "success",
            "detail": f"Venue emergency closure registered. Notifications sent to {affected_matches.count()} hosts."
        }, status=status.HTTP_200_OK)

class CourtViewSet(viewsets.ModelViewSet):
    serializer_class = CourtSerializer

    def get_queryset(self):
        return Court.objects.select_related(
            'venue__address'
        ).prefetch_related(
            'venue__facilities',
            'sports'
        ).all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminRole()]

def get_match_start_datetime(match):
    """
    Given a GameMatch, return its timezone-aware start datetime.
    """
    start_time = timezone.datetime.min.time()
    if match.time_slot and '-' in match.time_slot:
        start_str = match.time_slot.split('-')[0].strip()
        for fmt in ("%H:%M", "%H:%M:%S"):
            try:
                start_time = timezone.datetime.strptime(start_str, fmt).time()
                break
            except ValueError:
                pass
    return timezone.make_aware(timezone.datetime.combine(match.booking_date, start_time))

def get_match_end_datetime(match):
    """
    Given a GameMatch, return its timezone-aware end datetime.
    Handles midnight crossing by checking if end_time < start_time.
    """
    start_dt = get_match_start_datetime(match)
    end_time = timezone.datetime.max.time()
    if match.time_slot and '-' in match.time_slot:
        parts = match.time_slot.split('-')
        if len(parts) > 1:
            end_str = parts[1].strip()
            for fmt in ("%H:%M", "%H:%M:%S"):
                try:
                    end_time = timezone.datetime.strptime(end_str, fmt).time()
                    break
                except ValueError:
                    pass
    
    end_dt = timezone.make_aware(timezone.datetime.combine(match.booking_date, end_time))
    
    # If end time is numerically before start time, it means it ends the next day
    if end_dt <= start_dt:
        end_dt += timezone.timedelta(days=1)
        
    return end_dt

def update_all_match_statuses():
    """
    Updates statuses and sends notifications for all active matches based on their time status.
    """
    now = timezone.now()
    # Fetch recruiting, full, and started matches
    active_matches = GameMatch.objects.filter(match_status__in=['recruiting', 'full', 'started'])
    
    for match in active_matches:
        start_time = get_match_start_datetime(match)
        end_time = get_match_end_datetime(match)
        
        # 1. Check if 24 hours before start (Notify participants)
        if match.match_status in ['recruiting', 'full']:
            if 0 < (start_time - now).total_seconds() <= 86400:
                for p in match.participants.all():
                    msg_contains = "將在 24 小時內開始"
                    if not Notification.objects.filter(user=p.user, match=match, message__contains=msg_contains).exists():
                        Notification.objects.create(
                            user=p.user,
                            match=match,
                            message=f"【活動提醒】您參與的球局「{match.game_name}」將在 24 小時內開始！請準時抵達。"
                        )
        
        # 2. Check time transitions
        if now >= start_time:
            if now < end_time:
                # Started but not finished yet
                if match.match_status in ['recruiting', 'full']:
                    if match.current_players_count >= match.least_players:
                        # Successfully started
                        match.match_status = 'started'
                        match.save()
                        msg_contains = "已經開始"
                        for p in match.participants.all():
                            if not Notification.objects.filter(user=p.user, match=match, message__contains=msg_contains).exists():
                                Notification.objects.create(
                                    user=p.user,
                                    match=match,
                                    message=f"【活動開始】您參與的球局「{match.game_name}」已經開始！祝您運動愉快。"
                                )
                    else:
                        # Failed to start (cancel/流局 -> physical delete)
                        for p in match.participants.all():
                            Notification.objects.create(
                                user=p.user,
                                match=match,
                                message=f"【活動取消】您參與的球局「{match.game_name}」因人數未達下限（{match.least_players}人）已取消。"
                            )
                        match.delete()
            else:
                # Past end time
                if match.current_players_count >= match.least_players:
                    match.match_status = 'closed'
                    match.save()
                    # Also make sure they got start notification (in case it ended without started trigger)
                    msg_contains_start = "已經開始"
                    for p in match.participants.all():
                        if not Notification.objects.filter(user=p.user, match=match, message__contains=msg_contains_start).exists():
                            Notification.objects.create(
                                user=p.user,
                                match=match,
                                message=f"【活動開始】您參與的球局「{match.game_name}」已經開始！祝您運動愉快。"
                            )
                        
                        Notification.objects.create(
                            user=p.user,
                            match=match,
                            message=f"【活動結束】您參與的球局「{match.game_name}」已順利結束，球局已自動關閉。"
                        )
                else:
                    # Past end time and failed (physical delete)
                    for p in match.participants.all():
                        Notification.objects.create(
                            user=p.user,
                            match=match,
                            message=f"【活動取消】您參與的球局「{match.game_name}」因人數未達下限已取消。"
                        )
                    match.delete()

class GameMatchViewSet(viewsets.ModelViewSet):
    queryset = GameMatch.objects.all()
    serializer_class = GameMatchSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return GameMatchListSerializer
        return GameMatchSerializer

    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        match = self.get_object()
        all_parts = match.participants.all().order_by('joined_at')
        regular_parts = all_parts[:match.most_players]
        waitlisted_parts = all_parts[match.most_players:]
        
        return Response({
            'participants': MatchParticipantUserSerializer(regular_parts, many=True).data,
            'waitlist': MatchParticipantUserSerializer(waitlisted_parts, many=True).data
        })

    @action(detail=False, methods=['get'], url_path='history')
    def history(self, request):
        # 確保狀態機是最新的
        update_all_match_statuses()
        
        user = request.user
        now = timezone.now()
        
        # 篩選已參加且標記為 closed 的球局
        queryset = GameMatch.objects.filter(
            participants__user=user,
            match_status='closed'
        ).select_related(
            'sport', 'court__venue__address', 'creator'
        ).prefetch_related(
            'participants__user'
        ).distinct().order_by('-booking_date', '-time_slot')
        
        valid_matches = []
        for match in queryset:
            # 額外校驗：確保人數達標且時間確實已結束
            if match.current_players_count >= match.least_players:
                if get_match_end_datetime(match) <= now:
                    valid_matches.append(match)
                
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = request.query_params.get('radius') # in km

        matches_list = []
        for match in valid_matches:
            # 1. Weather calculation
            city = match.court.venue.address.city if match.court and match.court.venue and match.court.venue.address else None
            district = match.court.venue.address.district if match.court and match.court.venue and match.court.venue.address else None
            
            rain_prob = 0.2
            aqi = 50
            weather_idx = (5 * float(rain_prob)) + (float(aqi) / 50.0)
            match.weather = round(weather_idx, 1)
            
            # 2. Distance calculation
            dist = None
            if lat is not None and lng is not None:
                venue_lat = match.court.venue.latitude if match.court and match.court.venue else None
                venue_lng = match.court.venue.longitude if match.court and match.court.venue else None
                if venue_lat is not None and venue_lng is not None:
                    dist = haversine_distance(float(lat), float(lng), float(venue_lat), float(venue_lng))
            
            match.distance_km = dist
            
            # Apply radius filter
            if radius is not None and dist is not None:
                if dist > float(radius):
                    continue
            
            matches_list.append(match)

        serializer = GameMatchListSerializer(matches_list, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'quick_match']:
            return [permissions.AllowAny(), IsNotBanned()]
        return [permissions.IsAuthenticated(), IsNotBanned()]

    def create(self, request, *args, **kwargs):
        if request.user.credit_point < 60:
            return Response(
                {"detail": "您的信譽分數低於 60 分，限制發起（創建）新球局。"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        # Dynamically trigger state machine updates
        update_all_match_statuses()

        queryset = GameMatch.objects.select_related(
            'sport', 'court__venue__address', 'creator'
        ).prefetch_related(
            'participants__user'
        ).all().order_by('-id')

        sport_id = self.request.query_params.get('sport_id')
        target_level = self.request.query_params.get('target_level')
        city = self.request.query_params.get('city')
        date = self.request.query_params.get('date')
        time_slot = self.request.query_params.get('time_slot')
        
        region = self.request.query_params.get('region')
        sport_type = self.request.query_params.get('sport_type')
        level = self.request.query_params.get('level')

        if sport_id:
            queryset = queryset.filter(sport_id=sport_id)
        if target_level:
            queryset = queryset.filter(target_level=target_level)
        if city:
            queryset = queryset.filter(court__venue__address__city__contains=city)
        if date:
            queryset = queryset.filter(booking_date=date)
        if time_slot:
            queryset = queryset.filter(time_slot=time_slot)
            
        if region:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(court__venue__address__city__icontains=region) |
                Q(court__venue__address__district__icontains=region) |
                Q(court__venue__address__street_line__icontains=region)
            )
        if sport_type:
            sport_obj = get_sport_by_name_or_alias(sport_type, create=False)
            if sport_obj:
                queryset = queryset.filter(sport=sport_obj)
            else:
                queryset = queryset.filter(sport__name__icontains=sport_type)
        if level:
            queryset = queryset.filter(target_level__icontains=level)

        # Filter by start time / participation if action is list
        if getattr(self, 'action', None) == 'list':
            now = timezone.now()
            user = self.request.user
            valid_ids = []
            
            for match in queryset:
                start_time = get_match_start_datetime(match)
                end_time = get_match_end_datetime(match)
                
                # Exclude ended or closed matches completely
                if now >= end_time or match.match_status in ['closed', 'failed_to_start']:
                    continue
                
                has_started = now >= start_time
                is_participant = False
                if user and user.is_authenticated:
                    is_participant = (
                        match.creator_id == user.id or
                        any(p.user_id == user.id for p in match.participants.all())
                    )
                
                # Logic: 
                # 1. Creators always see their own matches
                # 2. Participants always see their matches
                # 3. Non-participants see matches that haven't ended AND (haven't started OR are still recruiting/full)
                # This ensures "just started" matches don't disappear if they are still open.
                if is_participant:
                    valid_ids.append(match.id)
                elif not has_started or match.match_status in ['recruiting', 'full']:
                    valid_ids.append(match.id)
            
            queryset = queryset.filter(id__in=valid_ids)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = request.query_params.get('radius') # in km

        matches_list = []
        for match in queryset:
            # 1. Weather calculation
            city = match.court.venue.address.city if match.court and match.court.venue and match.court.venue.address else None
            district = match.court.venue.address.district if match.court and match.court.venue and match.court.venue.address else None
            
            # WeatherData model is commented out, fallback to mock values
            rain_prob = 0.2
            aqi = 50
            
            # playability index formula: (5 * rain_probability) + (aqi / 50.0)
            weather_idx = (5 * float(rain_prob)) + (float(aqi) / 50.0)
            match.weather = round(weather_idx, 1)
            
            # 2. Distance calculation
            dist = None
            if lat is not None and lng is not None:
                venue_lat = match.court.venue.latitude if match.court and match.court.venue else None
                venue_lng = match.court.venue.longitude if match.court and match.court.venue else None
                if venue_lat is not None and venue_lng is not None:
                    dist = haversine_distance(float(lat), float(lng), float(venue_lat), float(venue_lng))
            
            match.distance_km = dist
            
            # Apply radius filter
            if radius is not None and dist is not None:
                if dist > float(radius):
                    continue
            
            matches_list.append(match)

        serializer = self.get_serializer(matches_list, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        venue_id = self.request.data.get('venue_id')
        sport_id = self.request.data.get('sport_id')
        court_id = self.request.data.get('court_id')
        
        assigned_court = None
        if court_id:
            assigned_court = Court.objects.filter(id=court_id).first()
        elif venue_id:
            courts = Court.objects.filter(venue_id=venue_id)
            if sport_id:
                courts = courts.filter(sports__id=sport_id)
            assigned_court = courts.first()
            if not assigned_court:
                assigned_court = Court.objects.filter(venue_id=venue_id).first()
            if not assigned_court:
                venue = Venue.objects.filter(id=venue_id).first()
                if venue:
                    assigned_court = Court.objects.create(venue=venue, base_price=300)
                    if sport_id:
                        sport = Sport.objects.filter(id=sport_id).first()
                        if sport:
                            assigned_court.sports.add(sport)
        
        if not assigned_court:
            from rest_framework import serializers
            raise serializers.ValidationError({"court_id": "本場館無可用或符合該運動項目的球場，球局一定要有場地才能建立。"})
            
        match = serializer.save(creator=self.request.user, court=assigned_court)

        MatchParticipant.objects.get_or_create(match=match, user=self.request.user)

        announcement_text = self.request.data.get('announcements')
        if announcement_text:
            GameBulletin.objects.create(
                match=match,
                title="公告",
                content=announcement_text
            )
        
        # venue = match.court.venue
        # if venue:
        #     favs = FavoriteVenue.objects.filter(venue=venue)
        #     for f in favs:
        #         Notification.objects.create(
        #             user=f.user,
        #             match=match,
        #             message=f"新球局開團通知 🏸：您收藏的場館【{venue.name}】有新的「{match.sport.chinese_name}」球局發起了，趕快去看看吧！"
        #         )

    def perform_update(self, serializer):
        match = serializer.save()
        
        announcement_text = self.request.data.get('announcements')
        new_bulletin_created = False
        if announcement_text:
            latest = match.bulletins.order_by('-created_at').first()
            if not latest or latest.content != announcement_text:
                GameBulletin.objects.create(
                    match=match,
                    title="公告",
                    content=announcement_text
                )
                new_bulletin_created = True

        Notification.objects.create(
            user=match.creator,
            match=match,
            message=f"球局資訊修改通知 🏸：您發起的球局「{match.sport.chinese_name}」資訊已成功修改。"
        )
        for p in match.participants.all():
            if p.user != match.creator:
                if new_bulletin_created:
                    Notification.objects.create(
                        user=p.user,
                        match=match,
                        message=f"球局公告通知 📢：您參與的球局「{match.sport.chinese_name}」有新公告：「{announcement_text}」"
                    )
                else:
                    Notification.objects.create(
                        user=p.user,
                        match=match,
                        message=f"球局資訊修改通知 🏸：您參加的球局「{match.sport.chinese_name}」已被主揪修改了資訊，請查看最新時間與內容。"
                    )

    def destroy(self, request, *args, **kwargs):
        match = self.get_object()
        
        # 檢查發送請求的使用者是否為球局的主揪，或是否為管理員
        if match.creator != request.user and request.user.role != 'admin':
            return Response(
                {"detail": "只有主揪或管理員才能刪除此球局。"}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        # 發送取消通知給所有參與者（除了主揪自己）
        participants = match.participants.all()
        for p in participants:
            if p.user != match.creator:
                Notification.objects.create(
                    user=p.user,
                    match=match,
                    message=f"【活動取消】您參與的球局「{match.game_name}」已被主揪取消。"
                )
                
        # 物理刪除球局，以符合新機制 (通知已設為 SET_NULL 會保留)
        match.delete()
        
        return Response({"detail": "球局已成功取消。"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='quick-match')
    def quick_match(self, request):
        sport_id = request.data.get('sport_id')
        target_level = request.data.get('target_level')
        age_preference = request.data.get('age_preference') # 'same_generation', 'any'

        if not sport_id or not target_level:
            return Response({"detail": "sport_id and target_level are required."}, status=status.HTTP_400_BAD_REQUEST)

        matches = GameMatch.objects.filter(sport_id=sport_id, match_status='recruiting')
        results = []

        user_age = request.user.age if request.user.is_authenticated else 25

        for m in matches:
            score = 100
            reasons = []

            # Level match
            if m.target_level == target_level:
                score += 10
                reasons.append("能力要求完全符合")
            else:
                score -= 20
                reasons.append("能力要求稍有不同")

            # Age match
            creator_age = m.creator.age
            age_diff = abs(creator_age - user_age)
            if age_preference == 'same_generation':
                if age_diff <= 5:
                    score += 15
                    reasons.append("同年代球友，等級與您高度吻合")
                else:
                    score -= 15
                    reasons.append("主揪年齡段與您不同")
            
            results.append({
                "game_id": m.id,
                "sport_name": m.sport.chinese_name,
                "venue_name": m.court.venue.name if m.court else "Unknown",
                "match_score": max(0, min(100, score)),
                "reason": ", ".join(reasons) or "時間與地點基本吻合"
            })

        results.sort(key=lambda x: x['match_score'], reverse=True)

        exact_matches = [r for r in results if r['match_score'] >= 90][:3]
        alternative_matches = [r for r in results if r['match_score'] < 90][:3]

        if exact_matches:
            return Response({
                "matched_type": "exact",
                "matches": exact_matches
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "matched_type": "alternative",
                "matches": alternative_matches
            }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='join')
    def join_match(self, request, pk=None):
        match = self.get_object()
        user = request.user
        
        # 0. Check if the match has already started
        now = timezone.now()
        match_time = get_match_start_datetime(match)
        if now >= match_time:
            return Response({"detail": "此球局已經開始，無法加入。"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 讀取強制加入參數，支援布林值與字串
        force_param = request.data.get('force', False) if isinstance(request.data, dict) else False
        force = force_param in [True, 'true', 'True', 1, '1']

        # 1. Blacklist check
        if Blacklist.objects.filter(user=user, removed_at__isnull=True).exists():
            return Response({"detail": "You are blacklisted from joining matches."}, status=status.HTTP_403_FORBIDDEN)

        # 2. Credit check
        if user.credit_point < 60:
            return Response({"detail": "Your credit rating is below 60. Joining matches is disabled."}, status=status.HTTP_403_FORBIDDEN)

        # 3. Double booking check
        if match.participants.filter(user=user).exists():
            return Response({"detail": "You are already a participant in this match."}, status=status.HTTP_400_BAD_REQUEST)

        # 3.5 Gender limit check
        if match.gender_limit == '限男' and user.gender != '男':
            return Response({"detail": "此球局限男性參加。"}, status=status.HTTP_400_BAD_REQUEST)
        if match.gender_limit == '限女' and user.gender != '女':
            return Response({"detail": "此球局限女性參加。"}, status=status.HTTP_400_BAD_REQUEST)

        # 3.8 Profile completeness check
        if not user.phone:
            return Response({"detail": "請先完善個人檔案後再加入球局。"}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Level check
        user_level_obj = UserSportLevel.objects.filter(user=user, sport=match.sport).first()
        if not user_level_obj:
            return Response({"detail": f"請先至個人檔案設定您的 {match.sport.chinese_name} 等級。"}, status=status.HTTP_400_BAD_REQUEST)
        user_lv = user_level_obj.level
        target_lv = match.target_level

        warning_msg = None
        if not force:
            if target_lv == '休閒':
                if user_lv not in ['C', 'B']:
                    warning_msg = "您的球技等級高於此球局的目標程度，請多加留意。"
            elif target_lv == '業餘':
                if user_lv not in ['B', 'A']:
                    warning_msg = "您的球技等級不符此球局的目標程度，請多加留意。"
            elif target_lv == '高手':
                if user_lv not in ['A', 'S']:
                    warning_msg = "您的球技等級低於此球局的目標程度，請多加留意。"

            if warning_msg:
                return Response({
                    "error_code": "LEVEL_MISMATCH",
                    "detail": f"{warning_msg}是否確定要加入？"
                }, status=status.HTTP_400_BAD_REQUEST)

        # 5. Queue capacity check
        current_count = MatchParticipant.objects.filter(match=match).count()
        max_allowed = math.ceil(match.most_players * 1.3)

        if current_count >= max_allowed:
            return Response({"detail": "球局與候補名額已滿。"}, status=status.HTTP_400_BAD_REQUEST)

        # Create MatchParticipant
        MatchParticipant.objects.create(match=match, user=user)
        
        response_data = {}
        if current_count >= match.most_players:
            pos = current_count - match.most_players + 1
            response_data = {
                "status": "waitlist",
                "position": pos,
                "message": f"球局已滿，已自動為您排入候補名單，目前順位為第 {pos} 位。"
            }
        else:
            if current_count + 1 >= match.most_players:
                match.match_status = 'full'
                match.save()
            response_data = {
                "status": "joined",
                "message": "成功加入球局。"
            }

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='leave')
    def leave_match(self, request, pk=None):
        match = self.get_object()
        user = request.user

        participant = match.participants.filter(user=user).first()
        if not participant:
            return Response({"detail": "You are not a participant in this match."}, status=status.HTTP_400_BAD_REQUEST)

        warning_msg = None
        now = timezone.now()
        if now > match.cancel_deadline and match.deposit_required:
            warning_msg = "已過取消截止時間，且本球局需要預收訂金，將扣除您的訂金。"

        with transaction.atomic():
            # Get list of current participants ordered by joined_at to determine who was waitlisted
            participants = list(match.participants.all().order_by('joined_at'))
            deleted_idx = -1
            for i, p in enumerate(participants):
                if p.id == participant.id:
                    deleted_idx = i
                    break

            promoted_user = None
            if 0 <= deleted_idx < match.most_players and len(participants) > match.most_players:
                # The first waitlisted player is at index match.most_players
                promoted_user = participants[match.most_players].user

            participant.delete()

            if promoted_user:
                Notification.objects.create(
                    user=promoted_user,
                    match=match,
                    message=f"候補成功轉正通知 🏸：恭喜！{promoted_user.name} 候補的「{match.sport.chinese_name}」已成功轉為正式隊員，請準時出席！"
                )

            remaining_count = match.participants.count()
            if remaining_count >= match.most_players:
                match.match_status = 'full'
            else:
                match.match_status = 'recruiting'
            match.save()

        response_data = {"detail": "Successfully left the match."}
        if warning_msg:
            response_data["warning"] = warning_msg
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='cancel')
    def cancel_match(self, request, pk=None):
        match = self.get_object()
        user = request.user

        participant = match.participants.filter(user=user).first()
        if not participant:
            return Response({"detail": "您未報名或候補此球局。"}, status=status.HTTP_400_BAD_REQUEST)

        deducted = False
        warning_msg = None
        now = timezone.now()
        
        is_late_cancel = False
        if match.cancel_deadline and now > match.cancel_deadline:
            is_late_cancel = True
        else:
            match_time = get_match_start_datetime(match)
            if (match_time - now).total_seconds() < 86400:
                is_late_cancel = True

        if is_late_cancel:
            with transaction.atomic():
                user.credit_point = max(0, user.credit_point - 10)
                user.save()
                deducted = True
                warning_msg = "已超過免費取消期限（活動前 24 小時），已扣除信譽分數 10 分！"
                if user.credit_point < 60:
                    Blacklist.objects.get_or_create(user=user)
                    warning_msg += " 您的信譽分數已低於 60 分，已列入黑名單。"

        with transaction.atomic():
            # Get list of current participants ordered by joined_at to determine who was waitlisted
            participants = list(match.participants.all().order_by('joined_at'))
            deleted_idx = -1
            for i, p in enumerate(participants):
                if p.id == participant.id:
                    deleted_idx = i
                    break

            promoted_user = None
            if 0 <= deleted_idx < match.most_players and len(participants) > match.most_players:
                # The first waitlisted player is at index match.most_players
                promoted_user = participants[match.most_players].user

            participant.delete()

            if promoted_user:
                Notification.objects.create(
                    user=promoted_user,
                    match=match,
                    message=f"候補成功轉正通知 🏸：恭喜！{promoted_user.name} 候補的「{match.sport.chinese_name}」已成功轉為正式隊員，請準時出席！"
                )

            remaining_count = match.participants.count()
            if remaining_count >= match.most_players:
                match.match_status = 'full'
            else:
                match.match_status = 'recruiting'
            match.save()

        response_data = {"detail": "成功取消報名並退出球局。"}
        if deducted:
            response_data["warning"] = warning_msg
            response_data["credit_point"] = user.credit_point
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'post'], url_path='announcements')
    def announcements(self, request, pk=None):
        match = self.get_object()
        if request.method == 'GET':
            bulletins = match.bulletins.all().order_by('created_at')
            data = []
            for b in bulletins:
                local_dt = timezone.localtime(b.created_at)
                formatted_time = local_dt.strftime("%I:%M %p")
                formatted_date = local_dt.strftime("%Y-%m-%d")
                data.append({
                    "id": b.id,
                    "title": b.title,
                    "content": b.content,
                    "text": b.content,  # for backwards compatibility with tests
                    "date": formatted_date,
                    "time": formatted_time,
                    "created_at": b.created_at
                })
            return Response(data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            if match.creator != request.user:
                return Response({"detail": "Only the host can post announcements."}, status=status.HTTP_403_FORBIDDEN)
            
            content = request.data.get('content') or request.data.get('text')
            title = request.data.get('title', '公告')
            
            if not content:
                return Response({"detail": "text is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            bulletin = GameBulletin.objects.create(
                match=match,
                title=title,
                content=content
            )
            
            for p in match.participants.all():
                if p.user != match.creator:
                    Notification.objects.create(
                        user=p.user,
                        match=match,
                        message=f"球局公告通知 📢：您參與的球局「{match.sport.chinese_name}」有新公告：「{content}」"
                    )
            
            local_dt = timezone.localtime(bulletin.created_at)
            formatted_time = local_dt.strftime("%I:%M %p")
            formatted_date = local_dt.strftime("%Y-%m-%d")
            return Response({
                "id": bulletin.id,
                "title": bulletin.title,
                "content": bulletin.content,
                "text": bulletin.content,  # for backwards compatibility with tests
                "date": formatted_date,
                "time": formatted_time,
                "created_at": bulletin.created_at
            }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='venue-status')
    def venue_status(self, request, pk=None):
        match = self.get_object()
        # 權限檢查：只有主揪才能回報場地狀態
        if match.creator != request.user and request.user.role != 'admin':
            return Response({"detail": "只有主揪才能回報場地狀態。"}, status=status.HTTP_403_FORBIDDEN)

        status_val = request.data.get('status')

        if not status_val:
            return Response({"detail": "status is required."}, status=status.HTTP_400_BAD_REQUEST)

        # 支援前端傳入的英文或中文狀態，並映射為資料庫的中文真實值
        status_map = {
            'confirmed': '已佔到/已預約',
            'failed': '未佔到/未預約',
            '已佔到/已預約': '已佔到/已預約',
            '未佔到/未預約': '未佔到/未預約',
            '未確認': '未確認'
        }
        
        mapped_status = status_map.get(status_val)
        if not mapped_status:
            return Response({"detail": f"無效的狀態值：{status_val}"}, status=status.HTTP_400_BAD_REQUEST)
            
        match.booking_status = mapped_status
        
        is_failed = mapped_status == '未佔到/未預約'
        
        if not is_failed:
            match.save()

        # 發送通知給所有參與者
        participants = match.participants.all()
        for p in participants:
            if is_failed:
                msg = f"【活動取消】您報名的球局「{match.game_name}」因【場地未借到】已取消。"
            else:
                msg = f"【場地狀態回報通知】您報名的球局「{match.game_name}」場地狀態已更新！\n狀態：{match.booking_status}"
            Notification.objects.create(
                user=p.user,
                match=match,
                message=msg
            )

        if is_failed:
            match.delete()
            return Response({"detail": "球局因場地預約失敗已取消並刪除。"}, status=status.HTTP_200_OK)

        # 回傳完整的球局資料，方便前端同步
        serializer = self.get_serializer(match)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='confirm-presence')
    def confirm_presence(self, request, pk=None):
        return Response({"status": "success", "message": "Host presence confirmed."}, status=status.HTTP_200_OK)

    # @action(detail=True, methods=['post', 'delete'], url_path='waitlist')
    # def waitlist_action(self, request, pk=None):
    #     pass
    # 
    # @action(detail=True, methods=['post'], url_path='waitlist/promote')
    # def manual_promote(self, request, pk=None):
    #     pass

class FavoriteGameViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]

    def list(self, request):
        favs = FavoriteGame.objects.filter(user=request.user)
        serializer = FavoriteGameSerializer(favs, many=True)
        return Response(serializer.data)

    def create(self, request):
        game_id = request.data.get('game_id')
        if not game_id:
            return Response({"detail": "game_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        match = get_object_or_404(GameMatch, pk=game_id)
        fav, created = FavoriteGame.objects.get_or_create(user=request.user, match=match)
        serializer = FavoriteGameSerializer(fav)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        fav = FavoriteGame.objects.filter(user=request.user, match_id=pk).first()
        if not fav:
            return Response({"detail": "Favorite not found."}, status=status.HTTP_404_NOT_FOUND)
        fav.delete()
        return Response({"detail": "Successfully removed from favorites."}, status=status.HTTP_200_OK)

# class FavoriteVenueViewSet(viewsets.ViewSet):
#     permission_classes = [permissions.IsAuthenticated]
# 
#     def list(self, request):
#         favs = FavoriteVenue.objects.filter(user=request.user)
#         serializer = FavoriteVenueSerializer(favs, many=True)
#         return Response(serializer.data)
# 
#     def create(self, request):
#         venue_id = request.data.get('venue_id')
#         if not venue_id:
#             return Response({"detail": "venue_id is required."}, status=status.HTTP_400_BAD_REQUEST)
#         
#         venue = get_object_or_404(Venue, pk=venue_id)
#         fav, created = FavoriteVenue.objects.get_or_create(user=request.user, venue=venue)
#         serializer = FavoriteVenueSerializer(fav)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
# 
#     def destroy(self, request, pk=None):
#         fav = FavoriteVenue.objects.filter(user=request.user, venue_id=pk).first()
#         if not fav:
#             return Response({"detail": "Favorite not found."}, status=status.HTTP_404_NOT_FOUND)
#         fav.delete()
#         return Response({"detail": "Successfully removed from favorites."}, status=status.HTTP_200_OK)

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]

    def create(self, request, *args, **kwargs):
        game_id = request.data.get('game_id')
        reported_user_id = request.data.get('reported_user_id')

        if not game_id or not reported_user_id:
            return Response({"detail": "game_id and reported_user_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        # 確保 ID 是數字，避免 ValueError: Field 'id' expected a number but got 'xxx'
        try:
            game_id_int = int(game_id)
            reported_user_id_int = int(reported_user_id)
        except (ValueError, TypeError):
            return Response({"detail": "game_id 與 reported_user_id 必須為數字。"}, status=status.HTTP_400_BAD_REQUEST)

        existing_report = Report.objects.filter(
            match_id=game_id_int,
            reporter=request.user,
            offender_id=reported_user_id_int
        )
        if existing_report.exists():
            return Response(
                {"detail": "您已經針對此球局檢舉過該名使用者，無法重複檢舉。"},
                status=status.HTTP_409_CONFLICT
            )

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        reason = self.request.data.get('reason')
        detail = self.request.data.get('detail') or ""

        # 使用 validated_data 確保型別正確
        offender = serializer.validated_data.get('offender')
        if not offender:
            offender_id = serializer.validated_data.get('offender_id')
            offender = get_object_or_404(User, id=offender_id)

        match = serializer.validated_data.get('match')
        if not match:
            game_id = self.request.data.get('game_id')
            if game_id:
                match = get_object_or_404(GameMatch, id=game_id)

        is_host = False
        if match and match.creator == offender:
            is_host = True

        # 1. 執行被檢舉人的信譽分數恢復更新
        check_and_update_credit(offender)

        # 2. 定義檢舉原因與扣分對照表
        DEDUCTION_MAP = {
            '未出現': 30 if is_host else 20,
            '沒交錢': 15,
            '球品不好': 10,
            '不當言語': 10,
            '言語攻擊': 10,
            '態度不佳': 10,
            '等級不符': 10,
            '等級不符（有菜雞，炸魚的）': 10,
            '騷擾與人身攻擊': 30,
            '肢體暴力': 60,
            '直銷': 15,
            # 主揪專屬原因
            '未回報場地': 15,
            '惡意抬價': 25,
            '沒預約場地': 30,
            '回報與實際場地不符': 20,
        }
        
        points_to_deduct = DEDUCTION_MAP.get(reason, 10) # 預設扣 10 分

        # 3. 系統自動扣分
        offender.credit_point = max(0, offender.credit_point - points_to_deduct)
        offender.save()

        # 4. 立即發送扣分訊息給被檢舉人
        Notification.objects.create(
            user=offender,
            message=f"【信譽扣分通知】您因為「{reason}」被其他使用者檢舉，信譽分數已扣除 {points_to_deduct} 分。目前分數：{offender.credit_point} 分。"
        )

        # 4.2 立即發送通知給檢舉人
        Notification.objects.create(
            user=self.request.user,
            message=f"【檢舉處理通知】您對「{offender.name}」的檢舉（原因：{reason}）已成功提交，系統已自動對其扣除 {points_to_deduct} 分。"
        )

        # 5. 60給警告與限制創房
        if offender.credit_point < 60:
            Notification.objects.create(
                user=offender,
                message="【信譽警告】您的信譽分數已低於 60 分。系統已限制您發起（創建）新球局的功能，請遵守規範以恢復分數。"
            )

        # 6. 40永久停權 (ban forever) 並加入黑名單
        if offender.credit_point <= 40:
            Blacklist.objects.get_or_create(user=offender)
            Notification.objects.create(
                user=offender,
                message="【永久停權通知】您的信譽分數已低於或等於 40 分，帳號已被系統永久停權。"
            )

        # 7. 儲存檢舉紀錄，狀態直接設為 'deducted' (自動處罰完成)
        if reason:
            detail = f"[{reason}] {detail}"
        serializer.save(
            reporter=self.request.user,
            offender=offender,
            status='deducted',
            detail=detail,
            reviewed_at=timezone.now(),
            admin_note="系統自動審查扣分"
        )

    @action(detail=True, methods=['patch'], url_path='review', permission_classes=[IsAdminRole])
    def review(self, request, pk=None):
        report = self.get_object()
        status_val = request.data.get('status') # 'deducted', 'rejected'
        admin_note = request.data.get('admin_note', '')

        if status_val not in ['deducted', 'rejected']:
            return Response({"detail": "Invalid status value. Choose 'deducted' or 'rejected'."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            report.status = status_val
            report.admin_note = admin_note
            report.reviewed_at = timezone.now()
            report.reviewed_by = request.user

            if status_val == 'deducted':
                rule = report.rule
                if not rule:
                    rule = PenaltyRule.objects.first()
                
                if rule:
                    offender = report.offender
                    offender.credit_point = max(0, offender.credit_point - rule.points_deducted)
                    offender.save()

                    if offender.credit_point < 60:
                        if not Blacklist.objects.filter(user=offender, removed_at__isnull=True).exists():
                            Blacklist.objects.create(
                                user=offender
                            )

            report.save()

        return Response(ReportSerializer(report).data, status=status.HTTP_200_OK)

class AdminGameViewSet(viewsets.ModelViewSet):
    queryset = GameMatch.objects.all()
    serializer_class = GameMatchSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        status_filter = self.request.query_params.get('status')
        if status_filter:
            return GameMatch.objects.filter(match_status=status_filter)
        return GameMatch.objects.all()

    @action(detail=True, methods=['patch'], url_path='status')
    def change_status(self, request, pk=None):
        match = self.get_object()
        status_val = request.data.get('status')
        booking_date = request.data.get('booking_date')
        time_slot = request.data.get('time_slot')

        updated_fields = []
        if status_val:
            match.match_status = status_val
            updated_fields.append("status")
        if booking_date:
            match.booking_date = booking_date
            updated_fields.append("booking_date")
        if time_slot:
            match.time_slot = time_slot
            updated_fields.append("time_slot")

        if updated_fields:
            match.save()
            return Response({"detail": f"Game match {', '.join(updated_fields)} updated successfully."})
        return Response({"detail": "No fields to update."}, status=status.HTTP_400_BAD_REQUEST)

class AdminBroadcastViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminRole]

    def create(self, request):
        target_group = request.data.get('target_group', 'all')
        content = request.data.get('content', '')

        if not content:
            return Response({"detail": "content is required."}, status=status.HTTP_400_BAD_REQUEST)

        matches = GameMatch.objects.all()
        if target_group == 'organizers':
            matches = matches.filter(match_status='recruiting')

        notifications = []
        for match in matches:
            notifications.append(Notification(match=match, message=content))
        
        Notification.objects.bulk_create(notifications)

        return Response({"detail": f"Broadcast sent to {len(notifications)} matches."}, status=status.HTTP_200_OK)

class NotificationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        from django.db.models import Q
        user_matches = GameMatch.objects.filter(
            Q(creator=request.user) | Q(participants__user=request.user)
        ).values_list('id', flat=True)
        
        # fav_venues = FavoriteVenue.objects.filter(user=request.user).values_list('venue', flat=True)
        # fav_venue_matches = GameMatch.objects.filter(court__venue__in=fav_venues).values_list('id', flat=True)
        fav_venue_matches = []
        
        match_ids = set(list(user_matches) + list(fav_venue_matches))
        
        notifs = Notification.objects.filter(
            Q(match_id__in=match_ids) | Q(match__isnull=True)
        ).filter(
            Q(user=request.user) | (Q(user__isnull=True) & Q(match_id__in=match_ids))
        ).order_by('-created_at')
        serializer = NotificationSerializer(notifs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='read')
    def read(self, request, pk=None):
        notif = get_object_or_404(Notification, pk=pk)
        notif.is_read = True
        notif.save()
        return Response({"status": "success", "message": "Notification marked as read."}, status=status.HTTP_200_OK)

class OpenDataViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'], url_path='sync-venues')
    def sync_venues(self, request):
        if request.user.is_authenticated and request.user.role != 'admin':
            return Response({"detail": "Only admin can sync opendata."}, status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            # Ensure basic sports exist
            sports_data = ["羽毛球", "籃球", "排球", "麻將", "桌球"]
            sport_objs = {}
            for s_name in sports_data:
                s, _ = Sport.objects.get_or_create(name=s_name)
                sport_objs[s_name] = s

            # Data from frontend's taiwanRegions
            venues_to_seed = [
                {"city": "桃園市", "district": "桃園區", "name": "桃園國民運動中心", "lat": 24.9934, "lng": 121.3124, "facilities": ["冷氣", "飲水機", "廁所", "淋浴間"]},
                {"city": "桃園市", "district": "桃園區", "name": "桃園巨蛋室外籃球場", "lat": 24.9961, "lng": 121.3204, "facilities": ["飲水機", "廁所"]},
                {"city": "桃園市", "district": "中壢區", "name": "中壢國民運動中心", "lat": 24.9602, "lng": 121.2144, "facilities": ["冷氣", "飲水機", "廁所", "淋浴間"]},
                {"city": "台北市", "district": "大安區", "name": "台大體育館", "lat": 25.0219, "lng": 121.5353, "facilities": ["冷氣", "飲水機", "廁所"]},
                {"city": "台北市", "district": "大安區", "name": "大安運動中心", "lat": 25.0224, "lng": 121.5404, "facilities": ["冷氣", "飲水機", "廁所", "淋浴間"]},
                {"city": "新北市", "district": "板橋區", "name": "板橋體育館", "lat": 25.0116, "lng": 121.4617, "facilities": ["免費車位", "熱水淋浴間", "自動販賣機"]},
            ]

            for v_data in venues_to_seed:
                addr, _ = Address.objects.get_or_create(
                    city=v_data["city"], 
                    district=v_data["district"], 
                    street_line=v_data.get("street_line", "測試路 1 號")
                )

                venue, _ = Venue.objects.get_or_create(
                    name=v_data["name"],
                    defaults={
                        "address": addr,
                        "opening_hours": {"weekdays": "06:00-22:00", "weekends": "06:00-22:00"},
                        "types": "indoor" if "冷氣" in v_data["facilities"] else "outdoor",
                        "latitude": v_data["lat"],
                        "longitude": v_data["lng"]
                    }
                )

                # Update facilities
                venue.facilities.clear()
                for f_name in v_data["facilities"]:
                    facility, _ = Facility.objects.get_or_create(name=f_name)
                    venue.facilities.add(facility)
                venue.save()

                # Create at least 2 courts per venue if none exist
                if not venue.courts.exists():
                    c1 = Court.objects.create(venue=venue, base_price=300)
                    c2 = Court.objects.create(venue=venue, base_price=300)
                    # Randomly assign sports for demo
                    c1.sports.add(sport_objs["籃球"], sport_objs["羽毛球"])
                    c2.sports.add(sport_objs["籃球"], sport_objs["羽毛球"])

        return Response({
            "status": "success",
            "message": f"Successfully synchronized {len(venues_to_seed)} venues from OpenData."
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='weather')
    def weather(self, request):
        city = request.query_params.get('city', '新北市')
        district = request.query_params.get('district', '板橋區')

        # Static mock weather data
        weather_idx = 0.8 * 5 + 45 / 50.0  # 4.9
        warning = "午後雷陣雨機率高，不建議進行戶外球局。"

        return Response({
            "city": city,
            "district": district,
            "temperature": 28.5,
            "rain_probability": 80.0,
            "aqi": 45,
            "weather_index": round(weather_idx, 1),
            "warning_message": warning
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='weather-aqi')
    def weather_aqi(self, request):
        import urllib.request, urllib.parse, json, ssl
        city = request.query_params.get('city', '桃園市')
        district = request.query_params.get('district', '龜山區')

        ssl_context = ssl._create_unverified_context()

        # 1. Fetch Weather (CWA District Level)
        cwa_key = 'CWA-3B417C47-F5EB-406C-A733-DFA20CE8E8C6'
        encoded_dist = urllib.parse.quote(district.replace("台", "臺"))
        # F-D0047-005 is Taoyuan City 2-day forecast
        weather_url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-005?Authorization={cwa_key}&format=JSON&locationName={encoded_dist}"
        temperature = 26
        condition = "多雲時晴"
        try:
            req = urllib.request.Request(weather_url)
            with urllib.request.urlopen(req, timeout=5, context=ssl_context) as response:
                data = json.loads(response.read().decode('utf-8'))
                locs = data.get('records', {}).get('Locations', [{}])[0].get('Location', [])
                if locs:
                    weather_elements = locs[0].get('WeatherElement', [])
                    for el in weather_elements:
                        if el['ElementName'] == '溫度':
                            temperature = int(el['Time'][0]['ElementValue'][0]['Temperature'])
                        elif el['ElementName'] == '天氣現象':
                            condition = el['Time'][0]['ElementValue'][0]['Weather']
        except Exception as e:
            print(f"Weather API Error: {e}")

        # 2. Fetch AQI (MOENV)
        moenv_key = '741bb4e0-4089-4ef3-9189-d021e4753b3f'
        aqi_url = f"https://data.moenv.gov.tw/api/v2/aqx_p_432?language=zh&api_key={moenv_key}"
        aqi = 45
        try:
            req = urllib.request.Request(aqi_url)
            with urllib.request.urlopen(req, timeout=5, context=ssl_context) as response:
                data = json.loads(response.read().decode('utf-8'))
                records = data if isinstance(data, list) else data.get('records', [])
                for r in records:
                    if r.get('county') == city or r.get('county') == city.replace("台", "臺"):
                        val = r.get('aqi')
                        if val and val.isdigit():
                            aqi = int(val)
                            break
        except Exception as e:
            print(f"AQI API Error: {e}")

        return Response({
            "location": f"{city}{district}",
            "temperature": temperature,
            "condition": condition,
            "aqi": aqi
        }, status=status.HTTP_200_OK)

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all().order_by('-created_at')
    serializer_class = AnnouncementSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminRole()]

    def perform_create(self, serializer):
        announcement = serializer.save()
        # 當發布系統公告時，自動為所有使用者建立一則通知
        users = User.objects.all()
        notifications = [
            Notification(
                user=user, 
                message=f"【系統公告】{announcement.title}\n{announcement.content}"
            )
            for user in users
        ]
        Notification.objects.bulk_create(notifications)

class AdminAnalyticsView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        today = timezone.now().date()
        
        # Today's active users: users who are participants in a match today or created a match today
        active_users = User.objects.filter(
            models.Q(created_matches__booking_date=today) | 
            models.Q(matchparticipant__match__booking_date=today)
        ).distinct().count()
        
        # If no one is active today, show total users as a fallback or just show 0
        # The user might prefer seeing total users if "active" is too strict
        total_users = User.objects.count()
        
        ongoing_games = GameMatch.objects.filter(booking_date=today).count()
        
        sports_ratio = {}
        for s in Sport.objects.all():
            # Calculate popularity based on number of participants in matches of this sport
            count = MatchParticipant.objects.filter(match__sport=s).count()
            # If no participants, maybe count matches instead
            if count == 0:
                count = GameMatch.objects.filter(sport=s).count()
            
            sports_ratio[s.chinese_name] = count
        
        activity_trend = [
            {"date": str(today - timezone.timedelta(days=i)), 
             "count": GameMatch.objects.filter(booking_date=today - timezone.timedelta(days=i)).count()}
            for i in range(7)
        ]
        
        # Count system notifications
        system_messages_count = Notification.objects.count()
        
        return Response({
            "active_users_today": total_users, # Keep as total_users for now as per original intent but could be active_users
            "active_users_real": active_users,
            "ongoing_games_count": ongoing_games,
            "sports_ratio": sports_ratio,
            "activity_trend": activity_trend,
            "system_messages_count": system_messages_count
        }, status=status.HTTP_200_OK)

class DemoWeatherView(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request):
        value = request.data.get('value', 50)
        # WeatherData is commented out
        return Response({"detail": f"Demo weather suitability updated to {value}% (Mocked)"}, status=status.HTTP_200_OK)

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all().order_by('-created_at')
    serializer_class = FeedbackSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'handle', 'destroy']:
            return [IsAdminRole()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = Feedback.objects.all().order_by('-created_at')
        is_handled = self.request.query_params.get('is_handled')
        if is_handled is not None:
            val = is_handled.lower() == 'true'
            queryset = queryset.filter(is_handled=val)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['put'], url_path='handle')
    def handle(self, request, pk=None):
        feedback = self.get_object()
        admin_reply = request.data.get('admin_reply', '')
        
        feedback.is_handled = True
        if admin_reply:
            feedback.admin_reply = admin_reply
        feedback.save()

        # Send notification to user
        if feedback.user:
            # Format message so frontend can parse it
            msg_reply = admin_reply or "您的建議已收到，感謝您的支持！"
            message_content = f"【回饋處理通知】\n[Feedback]\n{feedback.content}\n[Reply]\n{msg_reply}"
            Notification.objects.create(
                user=feedback.user,
                message=message_content
            )

        return Response(FeedbackSerializer(feedback).data, status=status.HTTP_200_OK)


import os
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_image(request):
    if 'file' not in request.FILES:
        return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
    
    uploaded_file = request.FILES['file']
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
        return Response({"error": "Invalid file type. Only PNG, JPG, JPEG, GIF, and WEBP are allowed."}, status=status.HTTP_400_BAD_REQUEST)
        
    filename = f"uploads/{uuid.uuid4()}{ext}"
    path = default_storage.save(filename, ContentFile(uploaded_file.read()))
    file_url = request.build_absolute_uri(settings.MEDIA_URL + path)
    
    return Response({"url": file_url}, status=status.HTTP_201_CREATED)
