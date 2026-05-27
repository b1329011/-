from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, phone, name, birthday, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone number must be set')
        user = self.model(phone=phone, name=name, birthday=birthday, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, name, birthday, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(phone, name, birthday, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    phone = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    birthday = models.DateField(null=True, blank=True)
    credit_point = models.IntegerField(default=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name', 'birthday']

    @property
    def age(self):
        if not self.birthday:
            return 0
        today = timezone.now().date()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))

    def __str__(self):
        return f"{self.name} ({self.phone})"

class Sport(models.Model):
    name = models.CharField(max_length=100, unique=True) # e.g., Badminton, Basketball

    def __str__(self):
        return self.name

class UserSportLevel(models.Model):
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('casual', 'Casual'),
        ('advanced', 'Advanced'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sport_levels')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'sport')

class Address(models.Model):
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    street_line = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.city}{self.district}{self.street_line}"

class Facility(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Venue(models.Model):
    VENUE_TYPES = (
        ('indoor', 'Indoor'),
        ('outdoor', 'Outdoor'),
        ('semi-outdoor', 'Semi-Outdoor'),
    )
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='venues')
    name = models.CharField(max_length=100)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    opening_hours = models.JSONField(null=True, blank=True)
    types = models.CharField(max_length=20, choices=VENUE_TYPES, null=True, blank=True)
    facilities = models.ManyToManyField(Facility, db_table='venue_facilities', related_name='venues')

    def __str__(self):
        return self.name

class Court(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='courts')
    name = models.CharField(max_length=100) # e.g., Court A, Court B
    occupied = models.BooleanField(default=False)
    sports = models.ManyToManyField(Sport, db_table='court_sports', related_name='courts')

    def __str__(self):
        return f"{self.venue.name} - {self.name}"

class CourtConflict(models.Model):
    court1 = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='conflicts_1')
    court2 = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='conflicts_2')

    class Meta:
        unique_together = ('court1', 'court2')

class GameMatch(models.Model):
    STATUS_CHOICES = (
        ('recruiting', 'Recruiting'),
        ('full', 'Full'),
        ('closed', 'Closed'),
        ('failed_to_start', 'Failed to Start'),
    )
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('casual', 'Casual'),
        ('advanced', 'Advanced'),
    )
    BOOKING_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
    )
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_matches', db_column='user_id')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    court = models.ForeignKey(Court, on_delete=models.SET_NULL, null=True, blank=True)
    least_players = models.IntegerField(default=1)
    most_players = models.IntegerField()
    target_level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    booking_date = models.DateField()
    time_slot = models.CharField(max_length=100) # e.g., "14:00-16:00"
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_required = models.BooleanField(default=False)
    cancel_deadline = models.DateTimeField()
    match_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recruiting')
    weather_index = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    air_index = models.IntegerField(null=True, blank=True)
    is_confirmed = models.BooleanField(default=False)
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def split_price(self):
        if self.most_players > 0:
            return self.total_price / self.most_players
        return 0

    @property
    def current_players_count(self):
        return self.participants.count()

    def __str__(self):
        return f"{self.sport.name} at {self.court.venue.name if self.court else 'Unknown Court'} ({self.booking_date} {self.time_slot})"

class MatchParticipant(models.Model):
    match = models.ForeignKey(GameMatch, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('match', 'user')

class MatchWaitlist(models.Model):
    STATUS_CHOICES = (
        ('waiting', 'Waiting'),
        ('promoted', 'Promoted'),
        ('cancelled', 'Cancelled'),
    )
    match = models.ForeignKey(GameMatch, on_delete=models.CASCADE, related_name='waitlist')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    queue_position = models.IntegerField()
    joined_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')

    class Meta:
        unique_together = (('match', 'user'), ('match', 'queue_position'))

class FavoriteGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_games')
    match = models.ForeignKey(GameMatch, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'keep'
        unique_together = ('user', 'match')

class FavoriteVenue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_venues')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'venue')

class PenaltyRule(models.Model):
    REASON_CHOICES = (
        ('no_show', 'No Show'),
        ('not_paid', 'Not Paid'),
        ('bad_behavior', 'Bad Behavior'),
    )
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, unique=True)
    points_deducted = models.IntegerField()

    def __str__(self):
        return f"{self.reason} (-{self.points_deducted} points)"

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
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    offender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')
    match = models.ForeignKey(GameMatch, on_delete=models.SET_NULL, null=True)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    rule = models.ForeignKey(PenaltyRule, on_delete=models.SET_NULL, null=True, blank=True)
    admin_note = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_reviewed')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class Blacklist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blacklist_entries')
    reason = models.TextField()
    added_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Blacklisted: {self.user.phone}"

class UserAvailability(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='availability')
    available_dates = models.JSONField(default=list) # e.g. ["2026-05-25", "2026-05-26"]
    time_slots = models.JSONField(default=list) # e.g. ["18:00-20:00", "20:00-22:00"]
    preferred_city = models.CharField(max_length=50)
    preferred_district = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    search_radius_km = models.IntegerField(default=5)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class WeatherData(models.Model):
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, default=25.0)
    rain_probability = models.DecimalField(max_digits=4, decimal_places=2, default=0.0) # 0.00 to 1.00
    aqi = models.IntegerField(default=50)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('city', 'district')
