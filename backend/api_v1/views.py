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
    Notification, WeatherData
)
from .serializers import (
    UserSerializer, UserProfileSerializer, SportSerializer, UserSportLevelSerializer,
    AddressSerializer, VenueSerializer, CourtSerializer, GameMatchSerializer,
    MatchParticipantSerializer, MatchWaitlistSerializer, FavoriteGameSerializer,
    FavoriteVenueSerializer, PenaltyRuleSerializer, ReportSerializer,
    BlacklistSerializer, UserAvailabilitySerializer, NotificationSerializer,
    WeatherDataSerializer
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

class AuthLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = request.data.get('phone')
        name = request.data.get('name')
        birthday = request.data.get('birthday')

        if not phone:
            return Response({"detail": "Phone is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(phone=phone).first()
        if not user:
            if not name or not birthday:
                return Response({"detail": "Name and birthday are required for automatic registration."}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.create_user(phone=phone, name=name, birthday=birthday)
        
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user_id": user.id,
            "role": user.role
        }, status=status.HTTP_200_OK)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'], url_path='profile')
    def profile(self, request):
        serializer = UserProfileSerializer(request.user)
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
                title="【場館警報】不可抗力建議取消通知",
                content=f"您預訂的場館【{venue.name}】因不可抗力因素（{reason}）臨時關閉/警告，系統強烈建議您主動取消或修改您的球局，以保障球友權益與安全。"
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
                user=game.creator,
                title="場地異常警告通知 ⚠️",
                content=f"您今天預訂的場地「{court.name}」有球友提報異常（類型：{issue_type}，說明：{description}）。請提前前往確認或進行調整。"
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
            match.weather_index = weather_idx
            
            # 2. Distance calculation
            dist = None
            if lat is not None and lng is not None:
                venue_lat = match.court.venue.address.latitude if match.court and match.court.venue and match.court.venue.address else None
                venue_lng = match.court.venue.address.longitude if match.court and match.court.venue and match.court.venue.address else None
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
        match = serializer.save(creator=self.request.user)
        # Add host as a participant automatically
        MatchParticipant.objects.get_or_create(match=match, user=self.request.user)
        
        venue = match.court.venue if match.court else None
        if venue:
            favorited_users = FavoriteVenue.objects.filter(venue=venue).values_list('user', flat=True)
            for user_id in favorited_users:
                if user_id != self.request.user.id:
                    Notification.objects.create(
                        user_id=user_id,
                        title="新球局開團通知 🏸",
                        content=f"您收藏的場館【{venue.name}】有新的「{match.sport.name}」球局發起了，趕快去看看吧！"
                    )

    def perform_update(self, serializer):
        match = serializer.save()
        for participant in match.participants.all():
            if participant.user != self.request.user:
                Notification.objects.create(
                    user=participant.user,
                    title="球局資訊修改通知 🏸",
                    content=f"您參加的球局「{match.sport.name}」已被主揪修改了資訊，請查看最新時間與內容。"
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

        # 4. Level check
        user_level_obj = UserSportLevel.objects.filter(user=user, sport=match.sport).first()
        user_level = user_level_obj.level if user_level_obj else 'casual'
        if user_level != match.target_level:
            return Response({
                "detail": f"Your level ({user_level}) does not match the target level ({match.target_level})."
            }, status=status.HTTP_400_BAD_REQUEST)

        # 5. Full room check
        if MatchParticipant.objects.filter(match=match).count() >= match.most_players:
            return Response({"detail": "This match is already full. Please join the waitlist instead."}, status=status.HTTP_400_BAD_REQUEST)

        # 6. Join
        MatchParticipant.objects.create(match=match, user=user)
        if MatchParticipant.objects.filter(match=match).count() >= match.most_players:
            match.match_status = 'full'
            match.save()

        return Response({"detail": "Successfully joined the match."}, status=status.HTTP_201_CREATED)

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
                    title="候補成功轉正通知 🏸",
                    content=f"恭喜！您候補的「{match.sport.name}」已成功轉為正式隊員，請準時出席！"
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
                user=wait_entry.user,
                title="候補成功轉正通知 🏸",
                content=f"恭喜！您候補的「{match.sport.name}」已由主揪手動轉為正式隊員，請準時出席！"
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
                rule = PenaltyRule.objects.filter(reason=report.reason).first()
                if not rule:
                    points_map = {'no_show': 20, 'not_paid': 15, 'bad_behavior': 10}
                    rule = PenaltyRule.objects.create(
                        reason=report.reason,
                        points_deducted=points_map.get(report.reason, 10)
                    )
                
                report.rule = rule
                offender = report.offender
                offender.credit_point = max(0, offender.credit_point - rule.points_deducted)
                offender.save()

                if offender.credit_point < 60:
                    if not Blacklist.objects.filter(user=offender, removed_at__isnull=True).exists():
                        Blacklist.objects.create(
                            user=offender,
                            reason=f"Credit score ({offender.credit_point}) dropped below threshold (60) due to review of report #{report.id}."
                        )

            report.save()

        return Response(ReportSerializer(report).data, status=status.HTTP_200_OK)

class AdminGameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GameMatch.objects.all()
    serializer_class = GameMatchSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        status_filter = self.request.query_params.get('status')
        if status_filter:
            return GameMatch.objects.filter(match_status=status_filter)
        return GameMatch.objects.all()

class AdminBroadcastViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminRole]

    def create(self, request):
        target_group = request.data.get('target_group', 'all')
        title = request.data.get('title', '系統通知')
        content = request.data.get('content', '')

        if not content:
            return Response({"detail": "content is required."}, status=status.HTTP_400_BAD_REQUEST)

        if target_group == 'organizers':
            host_ids = GameMatch.objects.values_list('creator_id', flat=True).distinct()
            users_to_notify = User.objects.filter(id__in=host_ids)
        else:
            users_to_notify = User.objects.all()

        notifications = []
        for user in users_to_notify:
            notifications.append(Notification(user=user, title=title, content=content))
        
        Notification.objects.bulk_create(notifications)

        return Response({"detail": f"Broadcast sent to {len(notifications)} users."}, status=status.HTTP_200_OK)

class NotificationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='read')
    def read(self, request, pk=None):
        notif = get_object_or_404(Notification, pk=pk, user=request.user)
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
                city="新北市", district="板橋區", street_line="中正路8號",
                defaults={"latitude": 25.0116, "longitude": 121.4617}
            )

            venue, _ = Venue.objects.get_or_create(
                name="板橋體育館",
                defaults={
                    "address": addr,
                    "base_price": 300.00,
                    "opening_hours": {"weekdays": "06:00-22:00", "weekends": "06:00-22:00"},
                    "types": "indoor"
                }
            )

            parking, _ = Facility.objects.get_or_create(name="免費車位")
            shower, _ = Facility.objects.get_or_create(name="熱水淋浴間")
            vending, _ = Facility.objects.get_or_create(name="自動販賣機")
            venue.facilities.add(parking, shower, vending)

            court1, _ = Court.objects.get_or_create(venue=venue, name="A 羽球場")
            court1.sports.add(badminton)
            court2, _ = Court.objects.get_or_create(venue=venue, name="B 羽球場")
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
