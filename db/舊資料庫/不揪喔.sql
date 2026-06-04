-- phpMyAdmin SQL Dump
-- version 4.6.6
-- https://www.phpmyadmin.net/
--
-- 主機: localhost
-- 產生時間： 2026-05-11 14:12:58
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
  `street_line` varchar(255) NOT NULL,
  `formatted` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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

-- --------------------------------------------------------

--
-- 資料表結構 `court`
--

CREATE TABLE `court` (
  `court_id` int(11) NOT NULL,
  `venue_id` int(11) NOT NULL,
  `occupied` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- 資料表結構 `court_conflicts`
--

CREATE TABLE `court_conflicts` (
  `conflict_id` int(11) NOT NULL,
  `court_id_1` int(11) NOT NULL,
  `court_id_2` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- 資料表結構 `court_sports`
--

CREATE TABLE `court_sports` (
  `court_id` int(11) NOT NULL,
  `sport_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- 資料表結構 `gamesmatches`
--

CREATE TABLE `gamesmatches` (
  `game_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `court_id` int(11) DEFAULT NULL,
  `sport_id` int(11) NOT NULL,
  `least_players` int(11) NOT NULL,
  `most_players` int(11) NOT NULL,
  `split_price` decimal(10,2) DEFAULT NULL,
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

-- --------------------------------------------------------

--
-- 資料表結構 `penalty_rules`
--

CREATE TABLE `penalty_rules` (
  `rule_id` int(11) NOT NULL,
  `reason` enum('no_show','not_paid','bad_behavior') NOT NULL,
  `points_deducted` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- 資料表結構 `reports`
--

CREATE TABLE `reports` (
  `report_id` int(11) NOT NULL,
  `game_id` int(11) NOT NULL,
  `reporter_id` int(11) NOT NULL,
  `offender_id` int(11) NOT NULL,
  `reason` enum('no_show','not_paid','bad_behavior') NOT NULL,
  `rule_id` int(11) DEFAULT NULL,
  `admin_note` text,
  `reviewed_at` timestamp NULL DEFAULT NULL,
  `reviewed_by` int(11) DEFAULT NULL,
  `status` enum('pending','deducted','rejected') NOT NULL DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- 資料表結構 `sports`
--

CREATE TABLE `sports` (
  `sport_id` int(11) NOT NULL,
  `sport_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- 資料表結構 `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `role` enum('user','admin') NOT NULL DEFAULT 'user',
  `name` varchar(100) NOT NULL,
  `age` int(10) UNSIGNED DEFAULT NULL,
  `credit_point` int(11) NOT NULL DEFAULT '100',
  `phone` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
  `facilities` json DEFAULT NULL,
  `types` enum('indoor','outdoor','semi-outdoor') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
-- 資料表索引 `gamesmatches`
--
ALTER TABLE `gamesmatches`
  ADD PRIMARY KEY (`game_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `court_id` (`court_id`),
  ADD KEY `sport_id` (`sport_id`);

--
-- 資料表索引 `match_participants`
--
ALTER TABLE `match_participants`
  ADD PRIMARY KEY (`list_id`),
  ADD UNIQUE KEY `game_id` (`game_id`,`user_id`),
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
-- 在匯出的資料表使用 AUTO_INCREMENT
--

--
-- 使用資料表 AUTO_INCREMENT `address`
--
ALTER TABLE `address`
  MODIFY `address_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- 使用資料表 AUTO_INCREMENT `blacklist`
--
ALTER TABLE `blacklist`
  MODIFY `blacklist_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- 使用資料表 AUTO_INCREMENT `court`
--
ALTER TABLE `court`
  MODIFY `court_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- 使用資料表 AUTO_INCREMENT `court_conflicts`
--
ALTER TABLE `court_conflicts`
  MODIFY `conflict_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- 使用資料表 AUTO_INCREMENT `gamesmatches`
--
ALTER TABLE `gamesmatches`
  MODIFY `game_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- 使用資料表 AUTO_INCREMENT `match_participants`
--
ALTER TABLE `match_participants`
  MODIFY `list_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- 使用資料表 AUTO_INCREMENT `penalty_rules`
--
ALTER TABLE `penalty_rules`
  MODIFY `rule_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- 使用資料表 AUTO_INCREMENT `reports`
--
ALTER TABLE `reports`
  MODIFY `report_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- 使用資料表 AUTO_INCREMENT `sports`
--
ALTER TABLE `sports`
  MODIFY `sport_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- 使用資料表 AUTO_INCREMENT `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- 使用資料表 AUTO_INCREMENT `venues`
--
ALTER TABLE `venues`
  MODIFY `venue_id` int(11) NOT NULL AUTO_INCREMENT;
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
  ADD CONSTRAINT `gamesmatches_ibfk_2` FOREIGN KEY (`court_id`) REFERENCES `court` (`court_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `gamesmatches_ibfk_3` FOREIGN KEY (`sport_id`) REFERENCES `sports` (`sport_id`) ON UPDATE CASCADE;

--
-- 資料表的 Constraints `match_participants`
--
ALTER TABLE `match_participants`
  ADD CONSTRAINT `match_participants_ibfk_1` FOREIGN KEY (`game_id`) REFERENCES `gamesmatches` (`game_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `match_participants_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

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

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
