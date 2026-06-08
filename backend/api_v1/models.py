from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import os

FORCE_SQLITE = os.environ.get('FORCE_SQLITE') == 'True'


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('gender', '不願透漏')
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, name, password, **extra_fields)

class User(AbstractBaseUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    id = models.AutoField(primary_key=True, db_column='user_id')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    birthday = models.DateField(db_column='birth_date', null=True, blank=True)
    credit_point = models.IntegerField(default=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    gender = models.CharField(max_length=10, null=True, blank=True)
    avatar_url = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    line_id = models.CharField(max_length=50, null=True, blank=True)
    instagram = models.CharField(max_length=50, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    @property
    def is_active(self):
        return True

    @is_active.setter
    def is_active(self, value):
        pass

    @property
    def is_staff(self):
        return self.role == 'admin'

    @is_staff.setter
    def is_staff(self, value):
        if value:
            self.role = 'admin'

    @property
    def last_login(self):
        return None

    @last_login.setter
    def last_login(self, value):
        pass

    @property
    def is_superuser(self):
        return self.role == 'admin'

    @is_superuser.setter
    def is_superuser(self, value):
        if value:
            self.role = 'admin'

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser




    @property
    def age(self):
        if not self.birthday:
            return 0
        today = timezone.now().date()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))

    def __str__(self):
        return f"{self.name} ({self.email})"

    class Meta:
        db_table = 'users'
        managed = FORCE_SQLITE

class Sport(models.Model):
    id = models.AutoField(primary_key=True, db_column='sport_id')
    name = models.CharField(db_column='sport_name', max_length=100, unique=True)

    @property
    def chinese_name(self):
        translation = {
            'basketball': '籃球',
            'badminton': '羽球',
            'volleyball': '排球',
            'mahjohn': '麻將',
            'table tennis': '桌球'
        }
        return translation.get(self.name.lower(), self.name)

    def __str__(self):
        return self.chinese_name

    class Meta:
        db_table = 'sports'
        managed = FORCE_SQLITE

class UserSportLevel(models.Model):
    LEVEL_CHOICES = (
        ('C', 'C'),
        ('B', 'B'),
        ('A', 'A'),
        ('S', 'S'),
    )
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id', related_name='sport_levels')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, db_column='sport_id')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_sport_levels'
        unique_together = ('user', 'sport')
        managed = FORCE_SQLITE

class Address(models.Model):
    id = models.AutoField(primary_key=True, db_column='address_id')
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    street_line = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.city}{self.district}{self.street_line}"

    class Meta:
        db_table = 'address'
        managed = FORCE_SQLITE

class Facility(models.Model):
    id = models.AutoField(primary_key=True, db_column='facility_id')
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'facilities'
        managed = FORCE_SQLITE

class Venue(models.Model):
    VENUE_TYPES = (
        ('indoor', 'Indoor'),
        ('outdoor', 'Outdoor'),
        ('semi-outdoor', 'Semi-Outdoor'),
    )
    id = models.AutoField(primary_key=True, db_column='venue_id')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, db_column='address_id', related_name='venues')
    name = models.CharField(max_length=100)
    opening_hours = models.JSONField(null=True, blank=True)
    types = models.CharField(max_length=20, choices=VENUE_TYPES, null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True, db_column='latitude')
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True, db_column='longitude')
    facilities = models.ManyToManyField(Facility, db_table='venue_facilities', related_name='venues')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'venues'
        managed = FORCE_SQLITE

class Court(models.Model):
    id = models.AutoField(primary_key=True, db_column='court_id')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, db_column='venue_id', related_name='courts')
    occupied = models.BooleanField(default=False)
    base_price = models.IntegerField(db_column='base_price', default=0)
    sports = models.ManyToManyField(Sport, db_table='court_sports', related_name='courts')

    @property
    def name(self):
        return f"Court {self.id}"

    def __str__(self):
        return f"{self.venue.name} - Court {self.id}"

    class Meta:
        db_table = 'court'
        managed = FORCE_SQLITE

class CourtConflict(models.Model):
    id = models.AutoField(primary_key=True, db_column='conflict_id')
    court1 = models.ForeignKey(Court, on_delete=models.CASCADE, db_column='court_id_1', related_name='conflicts_1')
    court2 = models.ForeignKey(Court, on_delete=models.CASCADE, db_column='court_id_2', related_name='conflicts_2')

    class Meta:
        db_table = 'court_conflicts'
        unique_together = ('court1', 'court2')
        managed = FORCE_SQLITE

class GameMatch(models.Model):
    STATUS_CHOICES = (
        ('recruiting', 'Recruiting'),
        ('full', 'Full'),
        ('closed', 'Closed'),
        ('started', 'Started'),
        ('failed_to_start', 'Failed to Start'),
    )
    LEVEL_CHOICES = (
        ('休閒', '休閒'),
        ('業餘', '業餘'),
        ('高手', '高手'),
    )
    BOOKING_STATUS_CHOICES = (
        ('已確認/已預約', '已確認/已預約'),
        ('未借到場地', '未借到場地'),
        ('未確認', '未確認'),
    )
    id = models.AutoField(primary_key=True, db_column='game_id')
    game_name = models.CharField(max_length=100, db_column='game_name', default='未命名球局')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id', related_name='created_matches')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, db_column='sport_id')
    court = models.ForeignKey(Court, on_delete=models.CASCADE, db_column='court_id', default=1)
    least_players = models.IntegerField(default=1)
    most_players = models.IntegerField()
    target_level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    booking_date = models.DateField()
    time_slot = models.CharField(max_length=100) # e.g., "14:00-16:00"
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_required = models.BooleanField(default=False)
    cancel_deadline = models.DateTimeField()
    match_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recruiting')
    weather = models.JSONField(db_column='weather', null=True, blank=True)
    air_index = models.IntegerField(null=True, blank=True)
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='未確認')
    game_note = models.TextField(null=True, blank=True, db_column='game_note')
    gender_limit = models.CharField(max_length=20, default='不限')

    @property
    def split_price(self):
        import math
        if self.total_price is not None and self.total_price > 0 and self.most_players > 0:
            return math.ceil(float(self.total_price) / self.most_players)
        return 0

    @property
    def current_players_count(self):
        return self.participants.count()

    def __str__(self):
        return f"{self.game_name} - {self.sport.chinese_name} at {self.court.venue.name if self.court else 'Unknown Court'} ({self.booking_date} {self.time_slot})"

    class Meta:
        db_table = 'gamesmatches'
        managed = FORCE_SQLITE

class MatchParticipant(models.Model):
    id = models.AutoField(primary_key=True, db_column='list_id')
    match = models.ForeignKey(GameMatch, on_delete=models.CASCADE, db_column='game_id', related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'match_participants'
        unique_together = ('match', 'user')
        managed = FORCE_SQLITE

# class MatchWaitlist(models.Model):
#     STATUS_CHOICES = (
#         ('waiting', 'Waiting'),
#         ('promoted', 'Promoted'),
#         ('cancelled', 'Cancelled'),
#     )
#     id = models.AutoField(primary_key=True, db_column='waitlist_id')
#     match = models.ForeignKey(GameMatch, on_delete=models.CASCADE, db_column='game_id', related_name='waitlist')
#     user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
#     queue_position = models.IntegerField()
#     joined_at = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
# 
#     class Meta:
#         db_table = 'match_waitlist'
#         unique_together = (('match', 'user'), ('match', 'queue_position'))
#         managed = False

class FavoriteGame(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id', related_name='favorite_games')
    match = models.ForeignKey(GameMatch, on_delete=models.CASCADE, db_column='game_id')

    class Meta:
        db_table = 'keep'
        unique_together = ('user', 'match')
        managed = FORCE_SQLITE

# class FavoriteVenue(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True, db_column='user_id', related_name='favorite_venues')
#     venue = models.ForeignKey(Venue, on_delete=models.CASCADE, db_column='venue_id')
#     created_at = models.DateTimeField(auto_now_add=True)
# 
#     class Meta:
#         db_table = 'favorite_venues'
#         unique_together = ('user', 'venue')
#         managed = False

class PenaltyRule(models.Model):
    id = models.AutoField(primary_key=True, db_column='rule_id')
    reason = models.CharField(max_length=20, choices=(
        ('no_show', 'No Show'),
        ('not_paid', 'Not Paid'),
        ('bad_behavior', 'Bad Behavior'),
    ), unique=True)
    points_deducted = models.IntegerField()

    def __str__(self):
        return f"{self.reason} (-{self.points_deducted} points)"

    class Meta:
        db_table = 'penalty_rules'
        managed = FORCE_SQLITE

class Report(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('deducted', 'Deducted'),
        ('rejected', 'Rejected'),
    )
    REASON_CHOICES = (
        ('no_show', 'No Show'),
        ('not_paid', 'Not Paid'),
        ('bad_behavior', 'Bad Behavior'),
    )
    id = models.AutoField(primary_key=True, db_column='report_id')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, db_column='reporter_id', related_name='reports_made')
    offender = models.ForeignKey(User, on_delete=models.CASCADE, db_column='offender_id', related_name='reports_received')
    match = models.ForeignKey(GameMatch, on_delete=models.SET_NULL, null=True, db_column='game_id')
    rule = models.ForeignKey(PenaltyRule, on_delete=models.SET_NULL, null=True, blank=True, db_column='rule_id')
    detail = models.TextField(null=True, blank=True)
    admin_note = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_column='reviewed_by', related_name='reports_reviewed')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        db_table = 'reports'
        managed = FORCE_SQLITE

class Blacklist(models.Model):
    id = models.AutoField(primary_key=True, db_column='blacklist_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id', related_name='blacklist_entries')
    added_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Blacklisted: {self.user.phone}"

    class Meta:
        db_table = 'blacklist'
        managed = FORCE_SQLITE

# class UserAvailability(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, db_column='user_id', related_name='availability')
#     available_dates = models.JSONField(default=list) # e.g. ["2026-05-25", "2026-05-26"]
#     time_slots = models.JSONField(default=list) # e.g. ["18:00-20:00", "20:00-22:00"]
#     preferred_city = models.CharField(max_length=50)
#     preferred_district = models.CharField(max_length=50)
#     latitude = models.DecimalField(max_digits=9, decimal_places=6)
#     longitude = models.DecimalField(max_digits=9, decimal_places=6)
#     search_radius_km = models.IntegerField(default=5)
# 
#     class Meta:
#         db_table = 'user_availability'

class Notification(models.Model):
    id = models.AutoField(primary_key=True, db_column='notification_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id', related_name='notifications', null=True, blank=True)
    match = models.ForeignKey(GameMatch, on_delete=models.CASCADE, db_column='game_id', related_name='notifications')
    message = models.TextField(db_column='message')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification'
        managed = FORCE_SQLITE

# class WeatherData(models.Model):
#     city = models.CharField(max_length=50)
#     district = models.CharField(max_length=50)
#     temperature = models.DecimalField(max_digits=4, decimal_places=1, default=25.0)
#     rain_probability = models.DecimalField(max_digits=4, decimal_places=2, default=0.0) # 0.00 to 1.00
#     aqi = models.IntegerField(default=50)
#     updated_at = models.DateTimeField(auto_now=True)
# 
#     class Meta:
#         db_table = 'weather_data'
#         unique_together = ('city', 'district')
class GameBulletin(models.Model):
    id = models.AutoField(primary_key=True, db_column='bulletin_id')
    match = models.ForeignKey(GameMatch, on_delete=models.CASCADE, db_column='game_id', related_name='bulletins')
    title = models.CharField(max_length=200, default='公告')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'game_bulletins'
        managed = FORCE_SQLITE
