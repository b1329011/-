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
    GameMatch, MatchParticipant, MatchWaitlist, FavoriteGame,
    FavoriteVenue, PenaltyRule, Report, Blacklist, UserAvailability,
    Notification, WeatherData, Feedback, Announcement
)
from .serializers import (
    UserSerializer, UserProfileSerializer, SportSerializer, UserSportLevelSerializer,
    AddressSerializer, VenueSerializer, CourtSerializer, GameMatchSerializer,
    MatchParticipantSerializer, MatchWaitlistSerializer, FavoriteGameSerializer,
    FavoriteVenueSerializer, PenaltyRuleSerializer, ReportSerializer,
    BlacklistSerializer, UserAvailabilitySerializer, NotificationSerializer,
    WeatherDataSerializer, FeedbackSerializer, AnnouncementSerializer
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

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='profile')
    def profile(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)
        
        # PUT / PATCH
        name = request.data.get('name')
        phone = request.data.get('phone')
        bio = request.data.get('bio')
        gender = request.data.get('gender')
        avatar = request.data.get('avatar')
        birthday = request.data.get('birthday')
        levels = request.data.get('levels')

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

        # birthday 與 gender 僅能在首次建立檔案時填寫，後續不可修改
        if birthday:
            if not user.birthday:
                user.birthday = birthday
            elif str(user.birthday) != str(birthday):
                # 忽略修改
                pass
        
        if gender:
            if not user.gender:
                if gender not in ['男', '女']:
                    return Response({"detail": "性別必須為 '男' 或 '女'。"}, status=status.HTTP_400_BAD_REQUEST)
                user.gender = gender
            elif user.gender != gender:
                # 忽略修改
                pass

        user.save()

        if levels and isinstance(levels, dict):
            for sport_name, short_lv in levels.items():
                db_sport_name = "羽毛球" if sport_name == "羽球" else sport_name
                lv_map = {
                    'S': 'S(菁英)',
                    'A': 'A(高手)',
                    'B': 'B(熟練)',
                    'C': 'C(初學者)'
                }
                full_lv = lv_map.get(short_lv, 'C(初學者)')
                sport, _ = Sport.objects.get_or_create(name=db_sport_name)
                UserSportLevel.objects.update_or_create(
                    user=user, sport=sport,
                    defaults={'level': full_lv}
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
            
            sport = get_object_or_404(Sport, pk=sport_id)
            level_obj, created = UserSportLevel.objects.update_or_create(
                user=request.user, sport=sport,
                defaults={'level': level}
            )
            serializer = UserSportLevelSerializer(level_obj)
            return Response(serializer.data)

    @action(detail=False, methods=['get', 'post'], url_path='availability')
    def availability(self, request):
        availability_obj = UserAvailability.objects.filter(user=request.user).first()
        if request.method == 'GET':
            if not availability_obj:
                return Response({"detail": "Availability not set yet."}, status=status.HTTP_404_NOT_FOUND)
            serializer = UserAvailabilitySerializer(availability_obj)
            return Response(serializer.data)
        elif request.method == 'POST':
            if availability_obj:
                serializer = UserAvailabilitySerializer(availability_obj, data=request.data, partial=True)
            else:
                serializer = UserAvailabilitySerializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response({
                    "status": "success",
                    "message": "月曆可用時間與地點更新成功。"
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
                        message=f"【場館警報】不可抗力建議取消通知：您參加的「{match.sport.name}」球局場館【{venue.name}】因臨時關閉（{reason}）受到影響，請留意主揪後續通知。"
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
            
            weather = WeatherData.objects.filter(city=city, district=district).first() if city else None
            rain_prob = weather.rain_probability if weather else 0.2
            aqi = weather.aqi if weather else 50
            
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
        
        venue = match.court.venue
        if venue:
            favs = FavoriteVenue.objects.filter(venue=venue)
            for f in favs:
                Notification.objects.create(
                    user=f.user,
                    match=match,
                    message=f"新球局開團通知 🏸：您收藏的場館【{venue.name}】有新的「{match.sport.name}」球局發起了，趕快去看看吧！"
                )

    def perform_update(self, serializer):
        match = serializer.save()
        Notification.objects.create(
            user=match.creator,
            match=match,
            message=f"球局資訊修改通知 🏸：您發起的球局「{match.sport.name}」資訊已成功修改。"
        )
        for p in match.participants.all():
            if p.user != match.creator:
                Notification.objects.create(
                    user=p.user,
                    match=match,
                    message=f"球局資訊修改通知 🏸：您參加的球局「{match.sport.name}」已被主揪修改了資訊，請查看最新時間與內容。"
                )

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
                "sport_name": m.sport.name,
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

        # 4. Level check
        user_level_obj = UserSportLevel.objects.filter(user=user, sport=match.sport).first()
        user_level = user_level_obj.level if user_level_obj else 'B(熟練)'
        
        level_map = {
            'C(初學者)': ['beginner', 'casual', 'C', 'C(初學者)'],
            'B(熟練)': ['casual', 'advanced', 'B', 'B(熟練)'],
            'A(高手)': ['advanced', 'A', 'A(高手)'],
            'S(菁英)': ['advanced', 'S', 'S(菁英)'],
            # 也保留對舊資料的相容
            'C(beginner)': ['beginner', 'casual', 'C', 'C(初學者)'],
            'B(advanced)': ['casual', 'advanced', 'B', 'B(熟練)'],
            'A(Veteran)': ['advanced', 'A', 'A(高手)'],
            'S(Elite)': ['advanced', 'S', 'S(菁英)'],
            'beginner': ['beginner', 'C', 'C(初學者)'],
            'casual': ['casual', 'B', 'B(熟練)'],
            'advanced': ['advanced', 'A', 'S', 'A(高手)', 'S(菁英)']
        }
        
        if user_level in level_map:
            allowed_target_levels = level_map.get(user_level, ['casual', 'B', 'B(熟練)'])
        else:
            allowed_target_levels = [user_level, 'casual', 'B', 'B(熟練)']

        if match.target_level not in allowed_target_levels:
            if match.target_level and len(match.target_level) == 1:
                pass
            else:
                return Response({
                    "detail": f"Your level ({user_level}) does not match the target level ({match.target_level})."
                }, status=status.HTTP_400_BAD_REQUEST)

        # 5. Full room check
        if MatchParticipant.objects.filter(match=match).count() >= match.most_players:
            # Automatically join waitlist!
            pos = MatchWaitlist.objects.filter(match=match, status='waiting').count() + 1
            wait_entry = MatchWaitlist.objects.create(match=match, user=user, queue_position=pos, status='waiting')
            return Response({
                "status": "waitlist",
                "position": pos,
                "message": f"球局已滿，已自動為您排入候補名單，目前順位為第 {pos} 位。"
            }, status=status.HTTP_200_OK)

        # 6. Join
        MatchParticipant.objects.create(match=match, user=user)
        if MatchParticipant.objects.filter(match=match).count() >= match.most_players:
            match.match_status = 'full'
            match.save()

        return Response({
            "status": "joined",
            "message": "成功加入球局。"
        }, status=status.HTTP_201_CREATED)

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
            participant.delete()

            # Automatic waitlist promotion
            waiting_waitlist = MatchWaitlist.objects.filter(match=match, status='waiting').order_by('queue_position')
            first_waiting = waiting_waitlist.first()

            if first_waiting:
                MatchParticipant.objects.create(match=match, user=first_waiting.user)
                
                first_waiting.status = 'promoted'
                first_waiting.save()

                # Decrement queue positions of remaining
                remaining_waiting = waiting_waitlist.exclude(id=first_waiting.id)
                for item in remaining_waiting:
                    item.queue_position -= 1
                    item.save()

                Notification.objects.create(
                    user=first_waiting.user,
                    match=match,
                    message=f"候補成功轉正通知 🏸：恭喜！{first_waiting.user.name} 候補的「{match.sport.name}」已成功轉為正式隊員，請準時出席！"
                )

                if MatchParticipant.objects.filter(match=match).count() >= match.most_players:
                    match.match_status = 'full'
                else:
                    match.match_status = 'recruiting'
                match.save()
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
            wait_entry = MatchWaitlist.objects.filter(match=match, user=user, status='waiting').first()
            if wait_entry:
                with transaction.atomic():
                    pos = wait_entry.queue_position
                    wait_entry.status = 'cancelled'
                    wait_entry.save()
                    remaining = MatchWaitlist.objects.filter(match=match, status='waiting', queue_position__gt=pos)
                    for item in remaining:
                        item.queue_position -= 1
                        item.save()
                return Response({"detail": "成功取消候補。"}, status=status.HTTP_200_OK)
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
            participant.delete()

            waiting_waitlist = MatchWaitlist.objects.filter(match=match, status='waiting').order_by('queue_position')
            first_waiting = waiting_waitlist.first()

            if first_waiting:
                MatchParticipant.objects.create(match=match, user=first_waiting.user)
                first_waiting.status = 'promoted'
                first_waiting.save()

                remaining_waiting = waiting_waitlist.exclude(id=first_waiting.id)
                for item in remaining_waiting:
                    item.queue_position -= 1
                    item.save()

                Notification.objects.create(
                    user=first_waiting.user,
                    match=match,
                    message=f"候補成功轉正通知 🏸：恭喜！{first_waiting.user.name} 候補的「{match.sport.name}」已成功轉為正式隊員，請準時出席！"
                )

                if MatchParticipant.objects.filter(match=match).count() >= match.most_players:
                    match.match_status = 'full'
                else:
                    match.match_status = 'recruiting'
                match.save()
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
            announcements = match.announcements.all().order_by('-created_at')
            data = []
            for a in announcements:
                formatted_time = timezone.localtime(a.created_at).strftime("%I:%M %p")
                data.append({
                    "id": a.id,
                    "text": a.content,
                    "time": formatted_time
                })
            return Response(data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            if match.creator != request.user:
                return Response({"detail": "Only the host can post announcements."}, status=status.HTTP_403_FORBIDDEN)
            
            text = request.data.get('text')
            if not text:
                return Response({"detail": "text is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            announcement = Announcement.objects.create(
                game=match,
                content=text,
                title=f"球局【{match.sport.name}】公告"
            )
            
            for p in match.participants.all():
                if p.user != match.creator:
                    Notification.objects.create(
                        user=p.user,
                        match=match,
                        message=f"球局公告通知 📢：您參與的球局「{match.sport.name}」有新公告：「{text}」"
                    )
            
            formatted_time = timezone.localtime(announcement.created_at).strftime("%I:%M %p")
            return Response({
                "id": announcement.id,
                "text": announcement.content,
                "time": formatted_time
            }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='venue-status')
    def venue_status(self, request, pk=None):
        match = self.get_object()
        status_val = request.data.get('status')
        note_val = request.data.get('note', '')

        if not status_val:
            return Response({"detail": "status is required."}, status=status.HTTP_400_BAD_REQUEST)

        match.venue_status = status_val
        match.venue_note = note_val
        match.save()

        participants = match.participants.all()
        for p in participants:
            Notification.objects.create(
                match=match,
                message=f"【場地狀態回報通知】您報名的球局「{match.sport.name}」場地狀態已更新！\n狀態：{status_val}\n說明：{note_val or '無'}"
            )

        return Response({
            "status": "success",
            "venue_status": match.venue_status,
            "venue_note": match.venue_note,
            "message": "場地狀態更新成功，已同步發送通知給所有參賽球友。"
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='confirm-presence')
    def confirm_presence(self, request, pk=None):
        match = self.get_object()
        if match.creator != request.user:
            return Response({"detail": "Only the host can confirm presence."}, status=status.HTTP_403_FORBIDDEN)
        
        match.is_confirmed = True
        match.save()
        return Response({"status": "success", "message": "Host presence confirmed."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'], url_path='waitlist')
    def waitlist_action(self, request, pk=None):
        match = self.get_object()
        user = request.user

        if request.method == 'POST':
            if match.participants.filter(user=user).exists():
                return Response({"detail": "You are already a participant in this match."}, status=status.HTTP_400_BAD_REQUEST)
            if MatchWaitlist.objects.filter(match=match, user=user, status='waiting').exists():
                return Response({"detail": "You are already on the waitlist for this match."}, status=status.HTTP_400_BAD_REQUEST)

            pos = MatchWaitlist.objects.filter(match=match, status='waiting').count() + 1
            wait_entry = MatchWaitlist.objects.create(match=match, user=user, queue_position=pos, status='waiting')

            return Response({
                "waitlist_id": wait_entry.id,
                "position": pos,
                "status": "waiting",
                "message": f"已成功加入候補名單，您目前順位為第 {pos} 位。"
            }, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            wait_entry = MatchWaitlist.objects.filter(match=match, user=user, status='waiting').first()
            if not wait_entry:
                return Response({"detail": "You are not on the waitlist for this match."}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                pos = wait_entry.queue_position
                wait_entry.status = 'cancelled'
                wait_entry.save()

                remaining = MatchWaitlist.objects.filter(match=match, status='waiting', queue_position__gt=pos)
                for item in remaining:
                    item.queue_position -= 1
                    item.save()

            return Response({"detail": "Successfully removed from waitlist."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='waitlist/promote')
    def manual_promote(self, request, pk=None):
        match = self.get_object()
        if match.creator != request.user and request.user.role != 'admin':
            return Response({"detail": "Only the host or admin can manually promote waitlist users."}, status=status.HTTP_403_FORBIDDEN)

        target_user_id = request.data.get('user_id')
        if not target_user_id:
            return Response({"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        wait_entry = MatchWaitlist.objects.filter(match=match, user_id=target_user_id, status='waiting').first()
        if not wait_entry:
            return Response({"detail": "User is not in waitlist."}, status=status.HTTP_400_BAD_REQUEST)

        if MatchParticipant.objects.filter(match=match).count() >= match.most_players:
            return Response({"detail": "Match is full, cannot promote."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            MatchParticipant.objects.create(match=match, user=wait_entry.user)
            
            pos = wait_entry.queue_position
            wait_entry.status = 'promoted'
            wait_entry.save()

            remaining = MatchWaitlist.objects.filter(match=match, status='waiting', queue_position__gt=pos)
            for item in remaining:
                item.queue_position -= 1
                item.save()

            Notification.objects.create(
                match=match,
                message=f"候補成功轉正通知 🏸：恭喜！{wait_entry.user.name} 候補的「{match.sport.name}」已由主揪手動轉為正式隊員，請準時出席！"
            )

            if MatchParticipant.objects.filter(match=match).count() >= match.most_players:
                match.match_status = 'full'
                match.save()

        return Response({"detail": "User successfully promoted from waitlist."}, status=status.HTTP_200_OK)

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

class FavoriteVenueViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        favs = FavoriteVenue.objects.filter(user=request.user)
        serializer = FavoriteVenueSerializer(favs, many=True)
        return Response(serializer.data)

    def create(self, request):
        venue_id = request.data.get('venue_id')
        if not venue_id:
            return Response({"detail": "venue_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        venue = get_object_or_404(Venue, pk=venue_id)
        fav, created = FavoriteVenue.objects.get_or_create(user=request.user, venue=venue)
        serializer = FavoriteVenueSerializer(fav)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        fav = FavoriteVenue.objects.filter(user=request.user, venue_id=pk).first()
        if not fav:
            return Response({"detail": "Favorite not found."}, status=status.HTTP_404_NOT_FOUND)
        fav.delete()
        return Response({"detail": "Successfully removed from favorites."}, status=status.HTTP_200_OK)

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
        serializer.save(reporter=self.request.user)

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
        
        fav_venues = FavoriteVenue.objects.filter(user=request.user).values_list('venue', flat=True)
        fav_venue_matches = GameMatch.objects.filter(court__venue__in=fav_venues).values_list('id', flat=True)
        
        match_ids = set(list(user_matches) + list(fav_venue_matches))
        
        notifs = Notification.objects.filter(match_id__in=match_ids).order_by('-created_at')
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


            WeatherData.objects.update_or_create(
                city="新北市", district="板橋區",
                defaults={
                    "temperature": 28.5,
                    "rain_probability": 0.80,
                    "aqi": 45
                }
            )

        return Response({
            "status": "success",
            "message": "OpenData venues successfully synchronized and cached."
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='weather')
    def weather(self, request):
        city = request.query_params.get('city', '新北市')
        district = request.query_params.get('district', '板橋區')

        weather = WeatherData.objects.filter(city=city, district=district).first()
        if not weather:
            weather = WeatherData.objects.create(
                city=city, district=district,
                temperature=28.5, rain_probability=0.80, aqi=45
            )

        weather_idx = float(weather.rain_probability) * 5 + float(weather.aqi) / 50.0
        warning = ""
        if weather_idx > 4.5:
            warning = "午後雷陣雨機率高，不建議進行戶外球局。"
        else:
            warning = "天氣適宜，適合進行各項運動。"

        return Response({
            "city": weather.city,
            "district": weather.district,
            "temperature": float(weather.temperature),
            "rain_probability": float(weather.rain_probability * 100),
            "aqi": weather.aqi,
            "weather_index": round(weather_idx, 1),
            "warning_message": warning
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='weather-aqi')
    def weather_aqi(self, request):
        city = request.query_params.get('city', '桃園市')
        district = request.query_params.get('district', '桃園區')

        weather = WeatherData.objects.filter(city=city).first()
        if not weather:
            temperature = 26.0
            aqi = 45
            condition = "多雲時晴"
        else:
            temperature = float(weather.temperature)
            aqi = weather.aqi
            condition = "多雲時晴" if aqi < 50 else "普通"

        return Response({
            "location": city,
            "temperature": int(temperature),
            "condition": condition,
            "aqi": aqi
        }, status=status.HTTP_200_OK)

class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [IsAdminRole()]

    def get_queryset(self):
        queryset = Feedback.objects.all()
        is_handled = self.request.query_params.get('is_handled')
        if is_handled is not None:
            val = is_handled.lower() in ['true', '1']
            queryset = queryset.filter(is_handled=val)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['put'], url_path='handle')
    def handle_feedback(self, request, pk=None):
        feedback = self.get_object()
        is_handled_val = request.data.get('is_handled', True)
        feedback.is_handled = is_handled_val
        feedback.save()
        return Response(FeedbackSerializer(feedback).data, status=status.HTTP_200_OK)

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all().order_by('-created_at')
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminRole()]

class AdminAnalyticsView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        today = timezone.now().date()
        active_users = User.objects.filter(is_active=True).count()
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
        WeatherData.objects.all().update(rain_probability=float(value)/100.0)
        return Response({"detail": f"Demo weather suitability updated to {value}%"}, status=status.HTTP_200_OK)
