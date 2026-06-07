import math
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .models import (
    Sport, UserSportLevel, Address, Venue, Court, CourtConflict,
    GameMatch, MatchParticipant, FavoriteGame,
    PenaltyRule, Report, Blacklist,
    Notification, GameBulletin
)
from .serializers import (
    UserSerializer, UserProfileSerializer, SportSerializer, UserSportLevelSerializer,
    AddressSerializer, VenueSerializer, CourtSerializer, GameMatchSerializer,
    MatchParticipantSerializer, FavoriteGameSerializer,
    PenaltyRuleSerializer, ReportSerializer,
    BlacklistSerializer, NotificationSerializer, GameBulletinSerializer
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
    name_clean = sport_name.strip().lower()
    alias_map = {
        '籃球': ['basketball', '籃球'],
        '羽毛球': ['badminton', '羽毛球', '羽球'],
        '排球': ['volleyball', '排球'],
        '麻將': ['mahjohn', '麻將'],
        '桌球': ['table tennis', '桌球']
    }
    
    standard_name = None
    for std_name, aliases in alias_map.items():
        if name_clean in aliases:
            standard_name = std_name
            break
            
    if not standard_name:
        standard_name = sport_name
        
    aliases_to_check = alias_map.get(standard_name, [standard_name])
    aliases_to_check = list(set([a.lower() for a in aliases_to_check] + [standard_name.lower(), name_clean]))
    
    for sport in Sport.objects.all():
        if sport.name.lower() in aliases_to_check:
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

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user_id": user.id,
            "role": user.role
        }, status=status.HTTP_200_OK)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

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
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminRole()]

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
    queryset = Court.objects.all()
    serializer_class = CourtSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminRole()]

    @action(detail=True, methods=['post'], url_path='report-status')
    def report_status(self, request, pk=None, venue_id=None):
        court = get_object_or_404(Court, pk=pk, venue_id=venue_id)
        issue_type = request.data.get('issue_type')
        description = request.data.get('description', '')

        if not issue_type:
            return Response({"detail": "issue_type is required."}, status=status.HTTP_400_BAD_REQUEST)

        court.occupied = True
        court.save()

        today = timezone.now().date()
        affected_games = GameMatch.objects.filter(court=court, booking_date=today)
        
        for game in affected_games:
            Notification.objects.create(
                match=game,
                message=f"場地異常警告通知 ⚠️：您今天預訂的場地「{court.name}」有球友提報異常（類型：{issue_type}，說明：{description}）。請提前前往確認或進行調整。"
            )

        return Response({
            "status": "success",
            "message": "感謝您的回報！系統已建立場地修繕案並通知管理員，同時將警告推播給今日預計使用此場地的球友房主。"
        }, status=status.HTTP_200_OK)

class GameMatchViewSet(viewsets.ModelViewSet):
    queryset = GameMatch.objects.all()
    serializer_class = GameMatchSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'quick_match']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = GameMatch.objects.select_related(
            'sport', 'court__venue__address', 'creator'
        ).prefetch_related(
            'participants__user'
        ).all()

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
        if announcement_text:
            latest = match.bulletins.order_by('-created_at').first()
            if not latest or latest.content != announcement_text:
                GameBulletin.objects.create(
                    match=match,
                    title="公告",
                    content=announcement_text
                )

        Notification.objects.create(
            user=match.creator,
            match=match,
            message=f"球局資訊修改通知 🏸：您發起的球局「{match.sport.chinese_name}」資訊已成功修改。"
        )
        for p in match.participants.all():
            if p.user != match.creator:
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
            
        return super().destroy(request, *args, **kwargs)

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
        user_level_raw = user_level_obj.level
        
        # 正規化使用者等級為 C, B, A, S
        norm_map = {
            'C': 'C', 'C(初學者)': 'C', 'C(beginner)': 'C', 'beginner': 'C',
            'B': 'B', 'B(熟練)': 'B', 'B(advanced)': 'B', 'casual': 'B',
            'A': 'A', 'A(高手)': 'A', 'A(Veteran)': 'A',
            'S': 'S', 'S(菁英)': 'S', 'S(Elite)': 'S', 'advanced': 'A',
        }
        user_lv = norm_map.get(user_level_raw, 'B')

        # 正規化球局的 target_level 為 休閒、業餘、高手
        target_lv_raw = match.target_level
        target_norm = {
            '休閒': '休閒',
            '業餘': '業餘',
            '高手': '高手',
            # 舊版相容
            '新手(CB可參加)': '休閒',
            '高手(BA可參加)': '業餘',
            '菁英(AS可參加)': '高手',
            'C(初學者)': '休閒', 'C(beginner)': '休閒', 'C': '休閒', 'beginner': '休閒',
            'B(熟練)': '業餘', 'B(advanced)': '業餘', 'B': '業餘', 'casual': '業餘',
            'A(高手)': '業餘', 'A(Veteran)': '業餘', 'A': '業餘',
            'S(菁英)': '高手', 'S(Elite)': '高手', 'S': '高手', 'advanced': '業餘',
        }
        target_lv = target_norm.get(target_lv_raw, '休閒')

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
            start_time = timezone.datetime.min.time()
            if match.time_slot and '-' in match.time_slot:
                start_str = match.time_slot.split('-')[0].strip()
                for fmt in ("%H:%M", "%H:%M:%S"):
                    try:
                        start_time = timezone.datetime.strptime(start_str, fmt).time()
                        break
                    except ValueError:
                        pass
            
            match_time = timezone.make_aware(timezone.datetime.combine(match.booking_date, start_time))
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
        status_val = request.data.get('status')
        note_val = request.data.get('note', '')

        if not status_val:
            return Response({"detail": "status is required."}, status=status.HTTP_400_BAD_REQUEST)

        match.booking_status = status_val
        match.game_note = note_val
        match.save()

        participants = match.participants.all()
        for p in participants:
            Notification.objects.create(
                user=p.user,
                match=match,
                message=f"【場地狀態回報通知】您報名的球局「{match.sport.chinese_name}」場地狀態已更新！\n狀態：{status_val}\n說明：{note_val or '無'}"
            )

        return Response({
            "status": "success",
            "venue_status": match.booking_status,
            "venue_note": match.game_note,
            "message": "場地狀態更新成功，已同步發送通知給所有參賽球友。"
        }, status=status.HTTP_200_OK)

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
    permission_classes = [permissions.IsAuthenticated]

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

    def create(self, request, *args, **kwargs):
        game_id = request.data.get('game_id')
        reported_user_id = request.data.get('reported_user_id')
        
        if not game_id or not reported_user_id:
            return Response({"detail": "game_id and reported_user_id are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        existing_report = Report.objects.filter(
            match_id=game_id,
            reporter=request.user,
            offender_id=reported_user_id
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
        if reason:
            detail = f"[{reason}] {detail}"
        serializer.save(reporter=self.request.user, detail=detail)

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
        if status_val:
            match.match_status = status_val
            match.save()
        return Response({"detail": f"Status updated to {match.match_status}"})

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
            match_id__in=match_ids
        ).filter(
            Q(user=request.user) | Q(user__isnull=True)
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
            badminton, _ = Sport.objects.get_or_create(name="羽毛球")
            basketball, _ = Sport.objects.get_or_create(name="籃球")
            volleyball, _ = Sport.objects.get_or_create(name="排球")
            mahjong, _ = Sport.objects.get_or_create(name="麻將")

            addr, _ = Address.objects.get_or_create(
                city="新北市", district="板橋區", street_line="中正路8號"
            )

            venue, _ = Venue.objects.get_or_create(
                name="板橋體育館",
                defaults={
                    "address": addr,
                    "opening_hours": {"weekdays": "06:00-22:00", "weekends": "06:00-22:00"},
                    "types": "indoor",
                    "latitude": 25.0116,
                    "longitude": 121.4617
                }
            )

            venue.facilities.clear()
            for facility_name in ["免費車位", "熱水淋浴間", "自動販賣機"]:
                facility, _ = Facility.objects.get_or_create(name=facility_name)
                venue.facilities.add(facility)
            venue.save()

            # Clean and create courts with base_price
            Court.objects.filter(venue=venue).delete()
            court1 = Court.objects.create(venue=venue, base_price=300)
            court1.sports.add(badminton)
            court2 = Court.objects.create(venue=venue, base_price=300)
            court2.sports.add(badminton)

            # WeatherData is commented out
            pass

        return Response({
            "status": "success",
            "message": "OpenData venues successfully synchronized and cached."
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
        city = request.query_params.get('city', '桃園市')
        district = request.query_params.get('district', '桃園區')

        return Response({
            "location": city,
            "temperature": 26,
            "condition": "多雲時晴",
            "aqi": 45
        }, status=status.HTTP_200_OK)

# 
# class AnnouncementViewSet(viewsets.ModelViewSet):
#     queryset = Announcement.objects.all().order_by('-created_at')
#     serializer_class = AnnouncementSerializer
# 
#     def get_permissions(self):
#         if self.action in ['list', 'retrieve']:
#             return [permissions.AllowAny()]
#         return [IsAdminRole()]

class AdminAnalyticsView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        today = timezone.now().date()
        # is_active is a virtual property, count all users
        active_users = User.objects.count()
        ongoing_games = GameMatch.objects.filter(booking_date=today).count()
        
        sports_ratio = {}
        for s in Sport.objects.all():
            sports_ratio[s.name] = GameMatch.objects.filter(sport=s).count()
        
        activity_trend = [
            {"date": str(today - timezone.timedelta(days=i)), 
             "count": GameMatch.objects.filter(booking_date=today - timezone.timedelta(days=i)).count()}
            for i in range(7)
        ]
        
        return Response({
            "active_users_today": active_users,
            "ongoing_games_count": ongoing_games,
            "sports_ratio": sports_ratio,
            "activity_trend": activity_trend
        }, status=status.HTTP_200_OK)

class DemoWeatherView(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request):
        value = request.data.get('value', 50)
        # WeatherData is commented out
        return Response({"detail": f"Demo weather suitability updated to {value}% (Mocked)"}, status=status.HTTP_200_OK)
