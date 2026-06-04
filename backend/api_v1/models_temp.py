[Database] MySQL detected! Using MySQL database ('nojo').
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Address(models.Model):
    address_id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    street_line = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'address'


class Blacklist(models.Model):
    blacklist_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    added_at = models.DateTimeField()
    removed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'blacklist'


class Court(models.Model):
    court_id = models.AutoField(primary_key=True)
    venue = models.ForeignKey('Venues', models.DO_NOTHING)
    occupied = models.IntegerField()
    base_price = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'court'


class CourtConflicts(models.Model):
    conflict_id = models.AutoField(primary_key=True)
    court_id_1 = models.ForeignKey(Court, models.DO_NOTHING, db_column='court_id_1')
    court_id_2 = models.ForeignKey(Court, models.DO_NOTHING, db_column='court_id_2', related_name='courtconflicts_court_id_2_set')

    class Meta:
        managed = False
        db_table = 'court_conflicts'
        unique_together = (('court_id_1', 'court_id_2'),)


class CourtSports(models.Model):
    pk = models.CompositePrimaryKey('court_id', 'sport_id')
    court = models.ForeignKey(Court, models.DO_NOTHING)
    sport = models.ForeignKey('Sports', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'court_sports'


class Facilities(models.Model):
    facility_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'facilities'


class Gamesmatches(models.Model):
    game_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    court = models.ForeignKey(Court, models.DO_NOTHING)
    sport = models.ForeignKey('Sports', models.DO_NOTHING)
    least_players = models.IntegerField()
    most_players = models.IntegerField()
    target_level = models.CharField(max_length=11, blank=True, null=True)
    weather = models.JSONField(blank=True, null=True)
    air_index = models.IntegerField(blank=True, null=True)
    match_status = models.CharField(max_length=10)
    booking_date = models.DateField(db_comment='紀錄球局預約的日期')
    time_slot = models.CharField(max_length=50, db_comment='紀錄球局進行的時間區間，例如 18:00-20:00')
    duration = models.CharField(max_length=50)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deposit_required = models.IntegerField()
    cancel_deadline = models.DateTimeField(blank=True, null=True)
    booking_status = models.CharField(max_length=7)
    gender_limit = models.CharField(max_length=2)
    game_note = models.TextField(blank=True, null=True, db_comment='佔場位置或衣服說明備註')
    布告欄 = models.TextField(blank=True, null=True)
    game_name = models.CharField(max_length=100, db_comment='比賽名稱')

    class Meta:
        managed = False
        db_table = 'gamesmatches'


class Keep(models.Model):
    pk = models.CompositePrimaryKey('user_id', 'game_id')
    user = models.ForeignKey('Users', models.DO_NOTHING)
    game = models.ForeignKey(Gamesmatches, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'keep'


class MatchParticipants(models.Model):
    list_id = models.AutoField(primary_key=True)
    game = models.ForeignKey(Gamesmatches, models.DO_NOTHING)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    joined_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'match_participants'
        unique_together = (('game', 'user'),)


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    game = models.ForeignKey(Gamesmatches, models.DO_NOTHING)
    message = models.TextField()
    created_at = models.DateTimeField()
    is_read = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'notification'


class PenaltyRules(models.Model):
    rule_id = models.AutoField(primary_key=True)
    reason = models.CharField(unique=True, max_length=50)
    points_deducted = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'penalty_rules'


class Reports(models.Model):
    report_id = models.AutoField(primary_key=True)
    game = models.ForeignKey(Gamesmatches, models.DO_NOTHING)
    reporter = models.ForeignKey('Users', models.DO_NOTHING)
    offender = models.ForeignKey('Users', models.DO_NOTHING, related_name='reports_offender_set')
    rule = models.ForeignKey(PenaltyRules, models.DO_NOTHING, blank=True, null=True)
    admin_note = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey('Users', models.DO_NOTHING, db_column='reviewed_by', related_name='reports_reviewed_by_set', blank=True, null=True)
    status = models.CharField(max_length=8)
    detail = models.TextField(blank=True, null=True, db_comment='檢舉詳細內容說明')

    class Meta:
        managed = False
        db_table = 'reports'
        unique_together = (('game', 'reporter', 'offender'),)


class Sports(models.Model):
    sport_id = models.AutoField(primary_key=True)
    sport_name = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'sports'


class UserSportLevels(models.Model):
    user = models.ForeignKey('Users', models.DO_NOTHING)
    sport = models.ForeignKey(Sports, models.DO_NOTHING)
    level = models.CharField(max_length=11)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'user_sport_levels'
        unique_together = (('user', 'sport'),)


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=5)
    email = models.CharField(unique=True, max_length=255)
    name = models.CharField(max_length=100)
    credit_point = models.IntegerField()
    phone = models.CharField(unique=True, max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=4)
    avatar_url = models.CharField(max_length=255, blank=True, null=True, db_comment='頭貼網址')
    bio = models.TextField(blank=True, null=True, db_comment='個人簡介')
    password = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'users'


class VenueFacilities(models.Model):
    pk = models.CompositePrimaryKey('venue_id', 'facility_id')
    venue = models.ForeignKey('Venues', models.DO_NOTHING)
    facility = models.ForeignKey(Facilities, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'venue_facilities'


class Venues(models.Model):
    venue_id = models.AutoField(primary_key=True)
    address = models.ForeignKey(Address, models.DO_NOTHING)
    name = models.CharField(max_length=100)
    opening_hours = models.JSONField(blank=True, null=True)
    types = models.CharField(max_length=12, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True, db_comment='場館緯度')
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True, db_comment='場館經度')

    class Meta:
        managed = False
        db_table = 'venues'
