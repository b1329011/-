-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2026-06-06 16:52:12
-- 伺服器版本： 10.4.32-MariaDB
-- PHP 版本： 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `nojo`
--

--
-- 傾印資料表的資料 `facilities`
--

INSERT INTO `facilities` (`facility_id`, `name`) VALUES
(1, '停車場'),
(2, '冷氣機'),
(3, '廁所'),
(4, '無障礙停車場');

--
-- 傾印資料表的資料 `penalty_rules`
--

INSERT INTO `penalty_rules` (`rule_id`, `reason`, `points_deducted`) VALUES
(1, 'no_show', 20),
(2, 'not_paid', 15),
(3, 'bad_behavior', 10),
(4, 'verbal_abuse', 10),
(5, 'poor_attitude', 10),
(6, 'rank_mismatch', 10),
(7, 'harassment', 30),
(8, 'physical_violence', 60),
(9, 'MLM', 15),
(10, 'without_report', 10),
(11, 'price_gouging', 30),
(12, 'without_reservation', 20);

--
-- 傾印資料表的資料 `sports`
--

INSERT INTO `sports` (`sport_id`, `sport_name`) VALUES
(2, 'Badminton'),
(1, 'Basketball'),
(4, 'Mahjohn'),
(3, 'Volleyball'),
(5, '桌球');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
