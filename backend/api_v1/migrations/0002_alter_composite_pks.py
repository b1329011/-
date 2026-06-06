from django.db import migrations

def alter_mysql_tables(apps, schema_editor):
    if schema_editor.connection.vendor == 'mysql':
        with schema_editor.connection.cursor() as cursor:
            # 暫時停用外鍵檢查以進行結構修改
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            try:
                # 1. user_sport_levels
                cursor.execute("ALTER TABLE `user_sport_levels` DROP PRIMARY KEY")
                cursor.execute("ALTER TABLE `user_sport_levels` ADD COLUMN `id` INT AUTO_INCREMENT PRIMARY KEY FIRST")
                cursor.execute("ALTER TABLE `user_sport_levels` ADD UNIQUE KEY `user_id_sport_id` (`user_id`, `sport_id`)")

                # 2. keep
                cursor.execute("ALTER TABLE `keep` DROP PRIMARY KEY")
                cursor.execute("ALTER TABLE `keep` ADD COLUMN `id` INT AUTO_INCREMENT PRIMARY KEY FIRST")
                cursor.execute("ALTER TABLE `keep` ADD UNIQUE KEY `user_id_game_id` (`user_id`, `game_id`)")

                # 3. court_sports
                cursor.execute("ALTER TABLE `court_sports` DROP PRIMARY KEY")
                cursor.execute("ALTER TABLE `court_sports` ADD COLUMN `id` INT AUTO_INCREMENT PRIMARY KEY FIRST")
                cursor.execute("ALTER TABLE `court_sports` ADD UNIQUE KEY `court_id_sport_id` (`court_id`, `sport_id`)")

                # 4. venue_facilities
                cursor.execute("ALTER TABLE `venue_facilities` DROP PRIMARY KEY")
                cursor.execute("ALTER TABLE `venue_facilities` ADD COLUMN `id` INT AUTO_INCREMENT PRIMARY KEY FIRST")
                cursor.execute("ALTER TABLE `venue_facilities` ADD UNIQUE KEY `venue_id_facility_id` (`venue_id`, `facility_id`)")
            finally:
                # 恢復外鍵檢查
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

def reverse_alter_mysql_tables(apps, schema_editor):
    if schema_editor.connection.vendor == 'mysql':
        with schema_editor.connection.cursor() as cursor:
            # 暫時停用外鍵檢查以進行結構修改
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            try:
                # 還原 user_sport_levels
                cursor.execute("ALTER TABLE `user_sport_levels` DROP INDEX `user_id_sport_id`")
                cursor.execute("ALTER TABLE `user_sport_levels` DROP COLUMN `id`")
                cursor.execute("ALTER TABLE `user_sport_levels` ADD PRIMARY KEY (`user_id`, `sport_id`)")

                # 還原 keep
                cursor.execute("ALTER TABLE `keep` DROP INDEX `user_id_game_id`")
                cursor.execute("ALTER TABLE `keep` DROP COLUMN `id`")
                cursor.execute("ALTER TABLE `keep` ADD PRIMARY KEY (`user_id`, `game_id`)")

                # 還原 court_sports
                cursor.execute("ALTER TABLE `court_sports` DROP INDEX `court_id_sport_id`")
                cursor.execute("ALTER TABLE `court_sports` DROP COLUMN `id`")
                cursor.execute("ALTER TABLE `court_sports` ADD PRIMARY KEY (`court_id`, `sport_id`)")

                # 還原 venue_facilities
                cursor.execute("ALTER TABLE `venue_facilities` DROP INDEX `venue_id_facility_id`")
                cursor.execute("ALTER TABLE `venue_facilities` DROP COLUMN `id`")
                cursor.execute("ALTER TABLE `venue_facilities` ADD PRIMARY KEY (`venue_id`, `facility_id`)")
            finally:
                # 恢復外鍵檢查
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

class Migration(migrations.Migration):
    dependencies = [
        ('api_v1', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(alter_mysql_tables, reverse_alter_mysql_tables),
    ]
