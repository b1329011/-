-- phpMyAdmin SQL Dump
-- version 4.6.6
-- https://www.phpmyadmin.net/
--
-- 主機: localhost
-- 產生時間： 2026-05-25 15:49:45
-- 伺服器版本: 5.7.17-log
-- PHP 版本： 5.6.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `不揪喔`
--

-- --------------------------------------------------------

--
-- 資料表結構 `address`
--

CREATE TABLE `address` (
  `address_id` int(11) NOT NULL,
  `city` varchar(50) NOT NULL,
  `district` varchar(50) NOT NULL,
  `street_line` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `address`
--

INSERT INTO `address` (`address_id`, `city`, `district`, `street_line`) VALUES
(1, '台北市', '大安區', '和平東路一段100號'),
(2, '新北市', '板橋區', '文化路一段88號'),
(3, '台中市', '西屯區', '台灣大道三段200號');

-- --------------------------------------------------------

--
-- 資料表結構 `blacklist`
--

CREATE TABLE `blacklist` (
  `blacklist_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `added_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `removed_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `blacklist`
--

INSERT INTO `blacklist` (`blacklist_id`, `user_id`, `added_at`, `removed_at`) VALUES
(1, 2, '2026-05-20 02:00:00', NULL),
(2, 1, '2026-05-20 03:00:00', '2026-05-25 03:00:00'),
(3, 3, '2026-05-20 04:00:00', NULL);

-- --------------------------------------------------------

--
-- 資料表結構 `court`
--

CREATE TABLE `court` (
  `court_id` int(11) NOT NULL,
  `venue_id` int(11) NOT NULL,
  `occupied` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `court`
--

INSERT INTO `court` (`court_id`, `venue_id`, `occupied`) VALUES
(1, 1, 0),
(2, 2, 1),
(3, 3, 0);

-- --------------------------------------------------------

--
-- 資料表結構 `court_conflicts`
--

CREATE TABLE `court_conflicts` (
  `conflict_id` int(11) NOT NULL,
  `court_id_1` int(11) NOT NULL,
  `court_id_2` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `court_conflicts`
--

INSERT INTO `court_conflicts` (`conflict_id`, `court_id_1`, `court_id_2`) VALUES
(1, 1, 2),
(3, 1, 3),
(2, 2, 3);

-- --------------------------------------------------------

--
-- 資料表結構 `court_sports`
--

CREATE TABLE `court_sports` (
  `court_id` int(11) NOT NULL,
  `sport_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `court_sports`
--

INSERT INTO `court_sports` (`court_id`, `sport_id`) VALUES
(1, 1),
(2, 2),
(3, 3);

-- --------------------------------------------------------

--
-- 資料表結構 `facilities`
--

CREATE TABLE `facilities` (
  `facility_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `facilities`
--

INSERT INTO `facilities` (`facility_id`, `name`) VALUES
(1, '停車場'),
(2, '冷氣機'),
(3, '廁所');

-- --------------------------------------------------------

--
-- 資料表結構 `gamesmatches`
--

CREATE TABLE `gamesmatches` (
  `game_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `court_id` int(20) NOT NULL,
  `sport_id` int(11) NOT NULL,
  `least_players` int(11) NOT NULL,
  `most_players` int(11) NOT NULL,
  `target_level` enum('beginner','casual','advanced') DEFAULT NULL,
  `weather_index` decimal(5,2) DEFAULT NULL,
  `air_index` int(11) DEFAULT NULL,
  `match_status` enum('recruiting','full','closed') NOT NULL DEFAULT 'recruiting',
  `booking_date` date DEFAULT NULL,
  `time_slot` varchar(50) DEFAULT NULL,
  `total_price` decimal(10,2) DEFAULT NULL,
  `deposit_required` tinyint(1) NOT NULL DEFAULT '0',
  `cancel_deadline` timestamp NULL DEFAULT NULL,
  `is_confirmed` tinyint(1) NOT NULL DEFAULT '0',
  `booking_status` enum('pending','booked','cancelled') NOT NULL DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `gamesmatches`
--

INSERT INTO `gamesmatches` (`game_id`, `user_id`, `court_id`, `sport_id`, `least_players`, `most_players`, `target_level`, `weather_index`, `air_index`, `match_status`, `booking_date`, `time_slot`, `total_price`, `deposit_required`, `cancel_deadline`, `is_confirmed`, `booking_status`) VALUES
(1, 1, 1, 1, 6, 10, 'casual', '85.50', 40, 'recruiting', '2026-06-01', '18:00-20:00', '1000.00', 1, '2026-05-31 10:00:00', 1, 'booked'),
(2, 2, 2, 2, 2, 4, 'advanced', '92.00', 25, 'full', '2026-06-03', '19:00-21:00', '600.00', 0, '2026-06-02 11:00:00', 1, 'booked'),
(3, 1, 3, 3, 8, 12, 'beginner', '70.00', 55, 'recruiting', '2026-06-05', '15:00-18:00', '960.00', 0, '2026-06-04 07:00:00', 0, 'pending');

-- --------------------------------------------------------

--
-- 資料表結構 `keep`
--

CREATE TABLE `keep` (
  `user_id` int(11) NOT NULL,
  `game_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 資料表的匯出資料 `keep`
--

INSERT INTO `keep` (`user_id`, `game_id`) VALUES
(2, 1),
(1, 2),
(3, 3);

-- --------------------------------------------------------

--
-- 資料表結構 `match_participants`
--

CREATE TABLE `match_participants` (
  `list_id` int(11) NOT NULL,
  `game_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `joined_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `match_participants`
--

INSERT INTO `match_participants` (`list_id`, `game_id`, `user_id`, `joined_at`) VALUES
(1, 1, 1, '2026-05-21 02:00:00'),
(2, 2, 2, '2026-05-21 03:00:00'),
(3, 3, 3, '2026-05-21 04:00:00');

-- --------------------------------------------------------

--
-- 資料表結構 `match_waitlist`
--

CREATE TABLE `match_waitlist` (
  `wait_id` int(11) NOT NULL,
  `game_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `queue_position` int(11) NOT NULL,
  `joined_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('waiting','promoted','cancelled') NOT NULL DEFAULT 'waiting'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `match_waitlist`
--

INSERT INTO `match_waitlist` (`wait_id`, `game_id`, `user_id`, `queue_position`, `joined_at`, `status`) VALUES
(4, 1, 1, 1, '2026-05-25 15:20:13', 'waiting'),
(5, 1, 2, 2, '2026-05-25 15:20:13', 'waiting'),
(6, 1, 3, 3, '2026-05-25 15:20:13', 'waiting');

-- --------------------------------------------------------

--
-- 資料表結構 `penalty_rules`
--

CREATE TABLE `penalty_rules` (
  `rule_id` int(11) NOT NULL,
  `reason` enum('no_show','not_paid','bad_behavior') NOT NULL,
  `points_deducted` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `penalty_rules`
--

INSERT INTO `penalty_rules` (`rule_id`, `reason`, `points_deducted`) VALUES
(1, 'no_show', 20),
(2, 'not_paid', 15),
(3, 'bad_behavior', 30);

-- --------------------------------------------------------

--
-- 資料表結構 `reports`
--

CREATE TABLE `reports` (
  `report_id` int(11) NOT NULL,
  `game_id` int(11) NOT NULL,
  `reporter_id` int(11) NOT NULL,
  `offender_id` int(11) NOT NULL,
  `rule_id` int(11) DEFAULT NULL,
  `admin_note` text,
  `reviewed_at` timestamp NULL DEFAULT NULL,
  `reviewed_by` int(11) DEFAULT NULL,
  `status` enum('pending','deducted','rejected') NOT NULL DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `reports`
--

INSERT INTO `reports` (`report_id`, `game_id`, `reporter_id`, `offender_id`, `rule_id`, `admin_note`, `reviewed_at`, `reviewed_by`, `status`) VALUES
(1, 1, 1, 2, 1, '未到場', '2026-05-22 02:00:00', 3, 'deducted'),
(2, 2, 2, 1, 2, '未付款', '2026-05-22 03:00:00', 3, 'pending'),
(3, 3, 1, 3, 3, '行為不當', '2026-05-22 04:00:00', 3, 'rejected');

-- --------------------------------------------------------

--
-- 資料表結構 `sports`
--

CREATE TABLE `sports` (
  `sport_id` int(11) NOT NULL,
  `sport_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `sports`
--

INSERT INTO `sports` (`sport_id`, `sport_name`) VALUES
(2, 'Badminton'),
(1, 'Basketball'),
(3, 'Volleyball');

-- --------------------------------------------------------

--
-- 資料表結構 `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `role` enum('user','admin') NOT NULL DEFAULT 'user',
  `name` varchar(100) NOT NULL,
  `credit_point` int(11) NOT NULL DEFAULT '100',
  `phone` varchar(20) DEFAULT NULL,
  `birth_date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `users`
--

INSERT INTO `users` (`user_id`, `role`, `name`, `credit_point`, `phone`, `birth_date`) VALUES
(1, 'user', '小明', 100, '0911111111', '2005-08-17'),
(2, 'user', '小華', 120, '0922222222', '2004-05-20'),
(3, 'admin', '管理員阿杰', 999, '0933333333', '2000-01-01');

-- --------------------------------------------------------

--
-- 資料表結構 `user_sport_levels`
--

CREATE TABLE `user_sport_levels` (
  `user_id` int(11) NOT NULL,
  `sport_id` int(11) NOT NULL,
  `level` enum('beginner','casual','advanced') NOT NULL,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `user_sport_levels`
--

INSERT INTO `user_sport_levels` (`user_id`, `sport_id`, `level`, `updated_at`) VALUES
(1, 1, 'casual', '2026-05-25 07:07:38'),
(2, 2, 'advanced', '2026-05-25 07:07:38'),
(3, 3, 'beginner', '2026-05-25 07:07:38');

-- --------------------------------------------------------

--
-- 資料表結構 `venues`
--

CREATE TABLE `venues` (
  `venue_id` int(11) NOT NULL,
  `address_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `base_price` decimal(10,2) NOT NULL DEFAULT '0.00',
  `opening_hours` json DEFAULT NULL,
  `types` enum('indoor','outdoor','semi-outdoor') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `venues`
--

INSERT INTO `venues` (`venue_id`, `address_id`, `name`, `base_price`, `opening_hours`, `types`) VALUES
(1, 1, '大安運動中心', '500.00', '{\"open\": \"08:00\", \"close\": \"22:00\"}', 'indoor'),
(2, 2, '板橋羽球館', '300.00', '{\"open\": \"09:00\", \"close\": \"23:00\"}', 'indoor'),
(3, 3, '台中陽光球場', '200.00', '{\"open\": \"07:00\", \"close\": \"21:00\"}', 'outdoor');

-- --------------------------------------------------------

--
-- 資料表結構 `venue_facilities`
--

CREATE TABLE `venue_facilities` (
  `venue_id` int(11) NOT NULL,
  `facility_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `venue_facilities`
--

INSERT INTO `venue_facilities` (`venue_id`, `facility_id`) VALUES
(1, 1),
(3, 1),
(1, 2),
(2, 2),
(2, 3),
(3, 3);

--
-- 已匯出資料表的索引
--

--
-- 資料表索引 `address`
--
ALTER TABLE `address`
  ADD PRIMARY KEY (`address_id`);

--
-- 資料表索引 `blacklist`
--
ALTER TABLE `blacklist`
  ADD PRIMARY KEY (`blacklist_id`),
  ADD KEY `user_id` (`user_id`);

--
-- 資料表索引 `court`
--
ALTER TABLE `court`
  ADD PRIMARY KEY (`court_id`),
  ADD KEY `venue_id` (`venue_id`);

--
-- 資料表索引 `court_conflicts`
--
ALTER TABLE `court_conflicts`
  ADD PRIMARY KEY (`conflict_id`),
  ADD UNIQUE KEY `court_id_1` (`court_id_1`,`court_id_2`),
  ADD KEY `court_id_2` (`court_id_2`);

--
-- 資料表索引 `court_sports`
--
ALTER TABLE `court_sports`
  ADD PRIMARY KEY (`court_id`,`sport_id`),
  ADD KEY `sport_id` (`sport_id`);

--
-- 資料表索引 `facilities`
--
ALTER TABLE `facilities`
  ADD PRIMARY KEY (`facility_id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- 資料表索引 `gamesmatches`
--
ALTER TABLE `gamesmatches`
  ADD PRIMARY KEY (`game_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `sport_id` (`sport_id`),
  ADD KEY `court_id` (`court_id`);

--
-- 資料表索引 `keep`
--
ALTER TABLE `keep`
  ADD PRIMARY KEY (`user_id`,`game_id`),
  ADD KEY `game_id` (`game_id`);

--
-- 資料表索引 `match_participants`
--
ALTER TABLE `match_participants`
  ADD PRIMARY KEY (`list_id`),
  ADD UNIQUE KEY `game_id` (`game_id`,`user_id`),
  ADD KEY `user_id` (`user_id`);

--
-- 資料表索引 `match_waitlist`
--
ALTER TABLE `match_waitlist`
  ADD PRIMARY KEY (`wait_id`),
  ADD UNIQUE KEY `game_id` (`game_id`,`user_id`),
  ADD UNIQUE KEY `game_id_2` (`game_id`,`queue_position`),
  ADD KEY `user_id` (`user_id`);

--
-- 資料表索引 `penalty_rules`
--
ALTER TABLE `penalty_rules`
  ADD PRIMARY KEY (`rule_id`),
  ADD UNIQUE KEY `reason` (`reason`);

--
-- 資料表索引 `reports`
--
ALTER TABLE `reports`
  ADD PRIMARY KEY (`report_id`),
  ADD UNIQUE KEY `game_id` (`game_id`,`reporter_id`,`offender_id`),
  ADD KEY `reporter_id` (`reporter_id`),
  ADD KEY `offender_id` (`offender_id`),
  ADD KEY `rule_id` (`rule_id`),
  ADD KEY `reviewed_by` (`reviewed_by`);

--
-- 資料表索引 `sports`
--
ALTER TABLE `sports`
  ADD PRIMARY KEY (`sport_id`),
  ADD UNIQUE KEY `sport_name` (`sport_name`);

--
-- 資料表索引 `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `phone` (`phone`);

--
-- 資料表索引 `user_sport_levels`
--
ALTER TABLE `user_sport_levels`
  ADD PRIMARY KEY (`user_id`,`sport_id`),
  ADD KEY `sport_id` (`sport_id`);

--
-- 資料表索引 `venues`
--
ALTER TABLE `venues`
  ADD PRIMARY KEY (`venue_id`),
  ADD KEY `address_id` (`address_id`);

--
-- 資料表索引 `venue_facilities`
--
ALTER TABLE `venue_facilities`
  ADD PRIMARY KEY (`venue_id`,`facility_id`),
  ADD KEY `facility_id` (`facility_id`);

--
-- 在匯出的資料表使用 AUTO_INCREMENT
--

--
-- 使用資料表 AUTO_INCREMENT `address`
--
ALTER TABLE `address`
  MODIFY `address_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- 使用資料表 AUTO_INCREMENT `blacklist`
--
ALTER TABLE `blacklist`
  MODIFY `blacklist_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- 使用資料表 AUTO_INCREMENT `court`
--
ALTER TABLE `court`
  MODIFY `court_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- 使用資料表 AUTO_INCREMENT `court_conflicts`
--
ALTER TABLE `court_conflicts`
  MODIFY `conflict_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- 使用資料表 AUTO_INCREMENT `facilities`
--
ALTER TABLE `facilities`
  MODIFY `facility_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- 使用資料表 AUTO_INCREMENT `gamesmatches`
--
ALTER TABLE `gamesmatches`
  MODIFY `game_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- 使用資料表 AUTO_INCREMENT `match_participants`
--
ALTER TABLE `match_participants`
  MODIFY `list_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- 使用資料表 AUTO_INCREMENT `match_waitlist`
--
ALTER TABLE `match_waitlist`
  MODIFY `wait_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;
--
-- 使用資料表 AUTO_INCREMENT `penalty_rules`
--
ALTER TABLE `penalty_rules`
  MODIFY `rule_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- 使用資料表 AUTO_INCREMENT `reports`
--
ALTER TABLE `reports`
  MODIFY `report_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- 使用資料表 AUTO_INCREMENT `sports`
--
ALTER TABLE `sports`
  MODIFY `sport_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- 使用資料表 AUTO_INCREMENT `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- 使用資料表 AUTO_INCREMENT `venues`
--
ALTER TABLE `venues`
  MODIFY `venue_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- 已匯出資料表的限制(Constraint)
--

--
-- 資料表的 Constraints `blacklist`
--
ALTER TABLE `blacklist`
  ADD CONSTRAINT `blacklist_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- 資料表的 Constraints `court`
--
ALTER TABLE `court`
  ADD CONSTRAINT `court_ibfk_1` FOREIGN KEY (`venue_id`) REFERENCES `venues` (`venue_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- 資料表的 Constraints `court_conflicts`
--
ALTER TABLE `court_conflicts`
  ADD CONSTRAINT `court_conflicts_ibfk_1` FOREIGN KEY (`court_id_1`) REFERENCES `court` (`court_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `court_conflicts_ibfk_2` FOREIGN KEY (`court_id_2`) REFERENCES `court` (`court_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- 資料表的 Constraints `court_sports`
--
ALTER TABLE `court_sports`
  ADD CONSTRAINT `court_sports_ibfk_1` FOREIGN KEY (`court_id`) REFERENCES `court` (`court_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `court_sports_ibfk_2` FOREIGN KEY (`sport_id`) REFERENCES `sports` (`sport_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- 資料表的 Constraints `gamesmatches`
--
ALTER TABLE `gamesmatches`
  ADD CONSTRAINT `gamesmatches_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `gamesmatches_ibfk_3` FOREIGN KEY (`sport_id`) REFERENCES `sports` (`sport_id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `gamesmatches_ibfk_4` FOREIGN KEY (`court_id`) REFERENCES `court` (`court_id`);

--
-- 資料表的 Constraints `keep`
--
ALTER TABLE `keep`
  ADD CONSTRAINT `keep_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `keep_ibfk_2` FOREIGN KEY (`game_id`) REFERENCES `gamesmatches` (`game_id`);

--
-- 資料表的 Constraints `match_participants`
--
ALTER TABLE `match_participants`
  ADD CONSTRAINT `match_participants_ibfk_1` FOREIGN KEY (`game_id`) REFERENCES `gamesmatches` (`game_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `match_participants_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- 資料表的 Constraints `match_waitlist`
--
ALTER TABLE `match_waitlist`
  ADD CONSTRAINT `match_waitlist_ibfk_1` FOREIGN KEY (`game_id`) REFERENCES `gamesmatches` (`game_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `match_waitlist_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- 資料表的 Constraints `reports`
--
ALTER TABLE `reports`
  ADD CONSTRAINT `reports_ibfk_1` FOREIGN KEY (`game_id`) REFERENCES `gamesmatches` (`game_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `reports_ibfk_2` FOREIGN KEY (`reporter_id`) REFERENCES `users` (`user_id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `reports_ibfk_3` FOREIGN KEY (`offender_id`) REFERENCES `users` (`user_id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `reports_ibfk_4` FOREIGN KEY (`rule_id`) REFERENCES `penalty_rules` (`rule_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `reports_ibfk_5` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- 資料表的 Constraints `user_sport_levels`
--
ALTER TABLE `user_sport_levels`
  ADD CONSTRAINT `user_sport_levels_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `user_sport_levels_ibfk_2` FOREIGN KEY (`sport_id`) REFERENCES `sports` (`sport_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- 資料表的 Constraints `venues`
--
ALTER TABLE `venues`
  ADD CONSTRAINT `venues_ibfk_1` FOREIGN KEY (`address_id`) REFERENCES `address` (`address_id`) ON UPDATE CASCADE;

--
-- 資料表的 Constraints `venue_facilities`
--
ALTER TABLE `venue_facilities`
  ADD CONSTRAINT `venue_facilities_ibfk_1` FOREIGN KEY (`venue_id`) REFERENCES `venues` (`venue_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `venue_facilities_ibfk_2` FOREIGN KEY (`facility_id`) REFERENCES `facilities` (`facility_id`) ON DELETE CASCADE ON UPDATE CASCADE;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
