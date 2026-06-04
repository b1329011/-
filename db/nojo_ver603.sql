-- phpMyAdmin SQL Dump
-- version 4.6.6
-- https://www.phpmyadmin.net/
--
-- 主機: localhost
-- 產生時間： 2026-06-03 09:17:57
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
(1, '桃園市', '龜山區', '桃園市龜山區中興路100巷20號'),
(2, '桃園市', '龜山區', '桃園市龜山區南美村南上路99號'),
(3, '桃園市', '龜山區', '桃園市龜山區文化一路259號'),
(4, '桃園市', '龜山區', '桃園市龜山區萬壽路一段168號'),
(5, '桃園市', '龜山區', '桃園市龜山區大同路23號'),
(6, '桃園市', '龜山區', '桃園市龜山區文化一路250號'),
(7, '桃園市', '龜山區', '桃園市龜山區自由街40號'),
(8, '桃園市', '龜山區', '桃園市龜山區自強東路269號'),
(9, '桃園市', '龜山區', '桃園市龜山區萬壽路一段300號'),
(10, '桃園市', '龜山區', '桃園市龜山區萬壽路二段933巷14號'),
(11, '桃園市', '龜山區', '桃園市龜山區新路村永和街12號'),
(12, '桃園市', '龜山區', '桃園市龜山區大同村德明路5號'),
(13, '桃園市', '龜山區', '桃園市龜山區大湖村文三二街80號'),
(14, '桃園市', '龜山區', '桃園市龜山區頂興路115巷20號'),
(15, '桃園市', '龜山區', '桃園市龜山區福源街59號'),
(16, '桃園市', '龜山區', '桃園市龜山區龍壽村龍校街30號'),
(17, '桃園市', '龜山區', '桃園市龜山區大坑路一段850號'),
(18, '桃園市', '龜山區', '桃園市龜山區文昌五街95號'),
(19, '桃園市', '龜山區', '桃園市龜山區楓樹村光峰路277號'),
(20, '桃園市', '龜山區', '桃園市龜山區文化里文化二路168號'),
(21, '桃園市', '龜山區', '桃園市龜山區文七二街72號旁'),
(22, '桃園市', '龜山區', '桃園市龜山區自強北路38號'),
(23, '桃園市', '龜山區', '桃園市龜山區同心二路'),
(24, '桃園市', '龜山區', '桃園市龜山區自強南路81巷'),
(25, '桃園市', '龜山區', '桃園市龜山區文化七路116號後方'),
(26, '桃園市', '龜山區', '桃園市龜山區大崗里20鄰大湖一路175號'),
(27, '桃園市', '龜山區', '桃園市龜山區長庚里長庚醫護新村425號'),
(28, '桃園市', '龜山區', '桃園市龜山區大崗村樹人路56號'),
(29, '桃園市', '龜山區', '桃園市龜山區文化一路261號'),
(30, '桃園市', '龜山區', '桃園市龜山區宏德新村2號'),
(31, '桃園市', '龜山區', '桃園市龜山區宏慶街34巷48-1號'),
(32, '桃園市', '龜山區', '復興北路與文昌五街交叉口'),
(33, '桃園市', '龜山區', '桃園市龜山區光峰路及光榮路口'),
(34, '桃園市', '龜山區', '桃園市龜山區文化三路246號'),
(35, '桃園市', '龜山區', '文化七路與興華五街交叉口'),
(36, '桃園市', '龜山區', '桃園市龜山區文安街與文光街交叉口'),
(37, '桃園市', '龜山區', '桃園市龜山區萬壽路一段383號後方'),
(38, '桃園市', '龜山區', '桃園市假日花市'),
(39, '桃園市', '龜山區', '桃園市龜山區自強西路66號');

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
  `occupied` tinyint(1) NOT NULL DEFAULT '0',
  `base_price` int(5) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `court`
--

INSERT INTO `court` (`court_id`, `venue_id`, `occupied`, `base_price`) VALUES
(1, 1, 0, NULL),
(2, 2, 0, NULL),
(3, 3, 0, NULL),
(4, 3, 0, NULL),
(5, 3, 0, NULL),
(6, 4, 0, NULL),
(7, 4, 0, NULL),
(8, 5, 0, NULL),
(9, 6, 0, NULL),
(10, 7, 0, NULL),
(11, 8, 0, NULL),
(12, 8, 0, NULL),
(13, 8, 0, NULL),
(14, 9, 0, NULL),
(15, 10, 0, NULL),
(16, 10, 0, NULL),
(17, 10, 0, NULL),
(18, 11, 0, NULL),
(19, 12, 0, NULL),
(20, 12, 0, NULL),
(21, 13, 0, NULL),
(22, 14, 0, NULL),
(23, 15, 0, NULL),
(24, 16, 0, NULL),
(25, 16, 0, NULL),
(26, 17, 0, NULL),
(27, 17, 0, NULL),
(28, 17, 0, NULL),
(29, 18, 0, NULL),
(30, 18, 0, NULL),
(31, 19, 0, NULL),
(32, 20, 0, NULL),
(33, 21, 0, NULL),
(34, 22, 0, NULL),
(35, 23, 0, NULL),
(36, 24, 0, NULL),
(37, 25, 0, NULL),
(38, 26, 0, NULL),
(39, 27, 0, NULL),
(40, 28, 0, NULL),
(41, 29, 0, NULL),
(42, 30, 0, NULL),
(43, 31, 0, NULL),
(44, 32, 0, NULL),
(45, 33, 0, NULL),
(46, 34, 0, NULL),
(47, 35, 0, NULL),
(48, 36, 0, NULL),
(49, 37, 0, NULL),
(50, 38, 0, NULL),
(51, 39, 0, NULL),
(52, 40, 0, NULL),
(53, 41, 0, NULL),
(54, 41, 0, NULL),
(55, 42, 0, NULL),
(56, 43, 0, NULL),
(57, 44, 0, NULL),
(58, 45, 0, NULL),
(59, 46, 0, NULL),
(60, 47, 0, NULL),
(61, 48, 0, NULL),
(62, 49, 0, NULL),
(63, 50, 0, NULL),
(64, 51, 0, NULL);

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

--
-- 資料表的匯出資料 `court_sports`
--

INSERT INTO `court_sports` (`court_id`, `sport_id`) VALUES
(1, 1),
(2, 1),
(5, 1),
(7, 1),
(10, 1),
(11, 1),
(14, 1),
(16, 1),
(17, 1),
(19, 1),
(21, 1),
(22, 1),
(23, 1),
(24, 1),
(26, 1),
(30, 1),
(31, 1),
(32, 1),
(33, 1),
(34, 1),
(35, 1),
(36, 1),
(38, 1),
(39, 1),
(40, 1),
(41, 1),
(43, 1),
(44, 1),
(45, 1),
(46, 1),
(47, 1),
(49, 1),
(50, 1),
(52, 1),
(55, 1),
(56, 1),
(57, 1),
(58, 1),
(59, 1),
(60, 1),
(61, 1),
(62, 1),
(64, 1),
(3, 2),
(6, 2),
(8, 2),
(9, 2),
(12, 2),
(15, 2),
(27, 2),
(37, 2),
(42, 2),
(48, 2),
(51, 2),
(53, 2),
(63, 2),
(4, 3),
(10, 3),
(13, 3),
(18, 3),
(20, 3),
(25, 3),
(28, 3),
(29, 3),
(54, 3);

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
(3, '廁所'),
(4, '無障礙停車場');

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
  `target_level` enum('C(初學者)','B(熟練)','A(高手)','S(菁英)') DEFAULT NULL,
  `weather` json DEFAULT NULL,
  `air_index` int(11) DEFAULT NULL,
  `match_status` enum('recruiting','full','closed') NOT NULL DEFAULT 'recruiting',
  `booking_date` date NOT NULL COMMENT '紀錄球局預約的日期',
  `time_slot` varchar(50) NOT NULL COMMENT '紀錄球局進行的時間區間，例如 18:00-20:00',
  `duration` varchar(50) NOT NULL DEFAULT '2 小時',
  `total_price` decimal(10,2) DEFAULT NULL,
  `deposit_required` tinyint(1) NOT NULL DEFAULT '0',
  `cancel_deadline` timestamp NULL DEFAULT NULL,
  `booking_status` enum('已佔到/已預約','未佔到/未預約','未確認') NOT NULL DEFAULT '未佔到/未預約',
  `gender_limit` enum('不限','限男','限女') NOT NULL DEFAULT '不限',
  `game_note` text COMMENT '佔場位置或衣服說明備註',
  `布告欄` text,
  `game_name` varchar(100) NOT NULL COMMENT '比賽名稱'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- 資料表結構 `keep`
--

CREATE TABLE `keep` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `game_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

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
-- 資料表結構 `notification`
--

CREATE TABLE `notification` (
  `notification_id` int(11) NOT NULL,
  `game_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_read` tinyint(1) DEFAULT '0',
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 資料表結構 `penalty_rules`
--

CREATE TABLE `penalty_rules` (
  `rule_id` int(11) NOT NULL,
  `reason` varchar(50) NOT NULL,
  `points_deducted` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `penalty_rules`
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
  `status` enum('pending','deducted','rejected') NOT NULL DEFAULT 'pending',
  `detail` text COMMENT '檢舉詳細內容說明'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
(2, '羽毛球'),
(1, '籃球'),
(4, '麻將'),
(3, '排球');

-- --------------------------------------------------------

--
-- 資料表結構 `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `role` enum('user','admin') NOT NULL DEFAULT 'user',
  `email` varchar(255) NOT NULL,
  `name` varchar(100) NOT NULL,
  `credit_point` int(11) NOT NULL DEFAULT '100',
  `phone` varchar(20) DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `gender` enum('男','女','其他','不願透漏') NOT NULL,
  `avatar_url` varchar(255) DEFAULT NULL COMMENT '頭貼網址',
  `bio` text COMMENT '個人簡介',
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `users`
--

INSERT INTO `users` (`user_id`, `role`, `email`, `name`, `credit_point`, `phone`, `birth_date`, `gender`, `avatar_url`, `bio`, `password`) VALUES
(1, 'admin', 'yangxin@example.com', '楊鑫', 999, '0912345678', '2006-04-17', '男', NULL, '韓德利克森', '12345678'),
(2, 'admin', 'linminghe@example.com', '林明和', 999, '0923456789', '2026-07-11', '男', NULL, '阿葛力搏依', '12345678'),
(3, 'admin', 'chenhanlin@example.com', '陳涵林', 999, '0934567890', '2026-06-25', '女', NULL, NULL, '12345678'),
(4, 'admin', 'jianlu@example.com', '簡律', 999, '0945678901', '2025-10-11', '女', NULL, NULL, ''),
(5, 'admin', 'lisiyu@example.com', '李偲伃', 999, '0956789012', '2026-03-05', '女', NULL, 'SB', '');

-- --------------------------------------------------------

--
-- 資料表結構 `user_sport_levels`
--

CREATE TABLE `user_sport_levels` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `sport_id` int(11) NOT NULL,
  `level` enum('C(初學者)','B(熟練)','A(高手)','S(菁英)') NOT NULL,
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
  `opening_hours` json DEFAULT NULL,
  `types` enum('indoor','outdoor','semi-outdoor') DEFAULT NULL,
  `latitude` decimal(10,8) DEFAULT NULL COMMENT '場館緯度',
  `longitude` decimal(11,8) DEFAULT NULL COMMENT '場館經度'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 資料表的匯出資料 `venues`
--

INSERT INTO `venues` (`venue_id`, `address_id`, `name`, `opening_hours`, `types`, `latitude`, `longitude`) VALUES
(1, 1, '幸福國中籃球場', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五\", \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '24.98786195', '121.33263230'),
(2, 2, '南美國小田徑場', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.04861101', '121.29699110'),
(3, 3, '長庚大學體育館', '{\"opening\": [{\"days\": \"星期六、星期日\", \"time\": \"平日8：30～21：30為學生體育課程及運動訓練時間，不對外開放，假日可申請租用。\", \"category\": \"羽球場\", \"court_ref\": \"羽球場\"}, {\"days\": \"星期六、星期日\", \"time\": \"平日8：30～21：30為學生體育課程及運動訓練使用時間，不對外開放，假日可申請租用。\", \"category\": \"排球場\", \"court_ref\": \"排球場\"}, {\"days\": \"星期六、星期日\", \"time\": \"平日8：30～21：30為學生體育課程及運動訓練使用時間，不對外開放，假日可申請租用。\", \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.03260190', '121.39029120'),
(4, 4, '迴龍國中小體育館', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期日\", \"time\": null, \"category\": \"羽球場(館)\", \"court_ref\": \"羽球場(館)\"}, {\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.01933398', '121.40470060'),
(5, 3, '長庚大學羽球室', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五\", \"time\": \"平日8：30～21：30為體育教學及課餘活動使用時段，故不對外開放。\", \"category\": \"羽球室\", \"court_ref\": \"羽球室\"}]}', NULL, '25.03261162', '121.39042000'),
(6, 5, '壽山高中活動中心', '{\"opening\": [{\"days\": null, \"time\": null, \"category\": \"羽球場(館)\", \"court_ref\": \"羽球場(館)\"}]}', NULL, '24.99538368', '121.34144600'),
(7, 6, '體育大學綜合體育館', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"週一至週五為全日及週六上午為教學使用，故不對外開放， 辦理大型活動除外，春節及休館時間配合活動調整。\", \"category\": \"籃排球場\", \"court_ref\": \"籃排球場\"}]}', NULL, '25.03456513', '121.38351920'),
(8, 7, '光啟高中田徑場', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"平日07:30-1700.18:30-22:30為學生上課時間，故不對外開放。\", \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}, {\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"平日07:30-17:00.18:30-22:30為學生上課時間，故不對外開放。\", \"category\": \"羽球場\", \"court_ref\": \"羽球場\"}, {\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"平日07:30-17:00.18:30-22:30為學生上課時間，故不對外開放。\", \"category\": \"排球場\", \"court_ref\": \"排球場\"}]}', NULL, '25.02016278', '121.40298660'),
(9, 8, '籃球場館', '{\"opening\": [{\"days\": null, \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '24.99727985', '121.34530310'),
(10, 9, '龍華科技大學學生活動中心', '{\"opening\": [{\"days\": null, \"time\": null, \"category\": \"羽球場(館)\", \"court_ref\": \"羽球場(館)\"}, {\"days\": null, \"time\": null, \"category\": \"室內籃球場\", \"court_ref\": \"室內籃球場\"}, {\"days\": null, \"time\": null, \"category\": \"室外籃球場\", \"court_ref\": \"室外籃球場\"}]}', NULL, '25.01967182', '121.40094280'),
(11, 3, '長庚大學排球場', '{\"opening\": [{\"days\": \"星期六、星期日\", \"time\": \"平日為體育教學及學生活動時段，不對外開放，假日可申請租借。\", \"category\": \"室外排球場\", \"court_ref\": \"室外排球場\"}]}', NULL, '25.03510407', '121.39067210'),
(12, 3, '長庚大學薄膜球場', '{\"opening\": [{\"days\": \"星期一、星期二、星期四、星期五\", \"time\": \"平日8：30～21：30為體育教學及活動時段，本校師生免費使用，假日則申請租借用。\", \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}, {\"days\": \"星期一、星期二、星期四、星期五\", \"time\": \"平日8：30～21：30為體育教學及活動時段，本校師生免費使用，假日則申請租借。\", \"category\": \"排球場\", \"court_ref\": \"排球場\"}]}', NULL, '25.03245065', '121.39004660'),
(13, 3, '長庚大學籃球場', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五\", \"time\": \"平日為本校師生體育教學及課餘活動時間，不對外開放，假日得申請租借。\", \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.03308754', '121.39214190'),
(14, 10, '龜山國小中正堂', '{\"opening\": [{\"days\": null, \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '24.99416332', '121.33979920'),
(15, 11, '新路國小籃球場', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"開放時間說明： 平日16:00~18:30 假日06:30~18:30\", \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '24.99544203', '121.33510530'),
(16, 12, '銘傳大學體育二館', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"除寒暑假外，休假日及國定假日開放，平日上課期間，不對外開放。 \", \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}, {\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"除寒暑假外，休假日及國定假日開放，平日上課期間，不對外開放。\", \"category\": \"排球場(館)\", \"court_ref\": \"排球場(館)\"}]}', NULL, '24.98803293', '121.34169280'),
(17, 12, '銘傳大學體育一館', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"除寒暑假外，休假日及國定假日開放，平日上課期間，不對外開放。 \", \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}, {\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"除寒暑假外，休假日及國定假日開放，平日上課期間，不對外開放。\", \"category\": \"羽球場(館)\", \"court_ref\": \"羽球場(館)\"}, {\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"除寒暑假外，休假日及國定假日開放，平日上課期間，不對外開放。\", \"category\": \"排球場(館)\", \"court_ref\": \"排球場(館)\"}]}', NULL, '24.98413081', '121.34231510'),
(18, 12, '銘傳大學室外籃球場', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"除寒暑假外，休假日及國定假日開放，平日上課期間，不對外開放。\", \"category\": \"排球場(館)\", \"court_ref\": \"排球場(館)\"}, {\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"除寒暑假外，休假日及國定假日開放，平日上課期間，不對外開放。\", \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '24.98369951', '121.34292390'),
(19, 13, '大湖國小籃球場(新)', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"例假日開放時間:8:00~19:00\", \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.05799995', '121.35893400'),
(20, 14, '幸福國小學生活動中心', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"以學校活動為優先\", \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '24.98922338', '121.33029880'),
(21, 15, '福源國小籃球場', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"開放時間週一到週五16:00-18:00，週六週日8:00-18:00。\", \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '24.98818996', '121.35750170'),
(22, 14, '幸福國小操場', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"上課無法開放\", \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '24.98879064', '121.33070110'),
(23, 16, '龍壽國小田徑場', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"除寒暑假外，平日08:30~17:30為學生上課時間，故不對外開放。\", \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.01079768', '121.38767930'),
(24, 17, '大坑國小田徑場', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"除寒暑假外，平日07:30~16:30為學生上課時間，故不對外開放。\", \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.04453478', '121.31490390'),
(25, 17, '大坑國小活動中心', '{\"opening\": [{\"days\": \"星期六、星期日\", \"time\": \"除寒暑假外，平日07:30~17:30為學生上課時間，故不對外開放。\", \"category\": \"羽球場(館)\", \"court_ref\": \"羽球場(館)\"}]}', NULL, '25.04450056', '121.31474780'),
(26, 18, '文欣國小田徑場附設籃球場', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"無\", \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.05765990', '121.37202340'),
(27, 19, '楓樹國小籃球場', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"無\", \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.00599696', '121.34314050'),
(28, 20, '大崗國中田徑場、籃球場', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"如遇整修或天然災害時不對外開放\", \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.05128392', '121.37063380'),
(29, 13, '大湖國小籃球場', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五\", \"time\": \"例假日為8:00~19:00，平日則放學後才開放。\", \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.05733906', '121.35879990'),
(30, 16, '龍壽國小活動中心', '{\"opening\": [{\"days\": null, \"time\": null, \"category\": \"羽球場(館)\", \"court_ref\": \"羽球場(館)\"}]}', NULL, '25.01096053', '121.38805750'),
(31, 21, '華美公園', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.05247456', '121.36032880'),
(32, 22, '中正公園籃球場 ', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '24.99939477', '121.34353280'),
(33, 23, '南崁溪河濱公園籃球場 ', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '24.99526213', '121.32973020'),
(34, 24, '第三運動公園', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '24.99148430', '121.34006740'),
(35, 25, '第二運動公園', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.04982597', '121.36486710'),
(36, 26, '大崗國小活動中心', '{\"opening\": [{\"days\": \"星期六、星期日\", \"time\": null, \"category\": \"羽球場(館)\", \"court_ref\": \"羽球場(館)\"}]}', NULL, '25.05185014', '121.35856430'),
(37, 10, '籃球場(半場)', '{\"opening\": [{\"days\": null, \"time\": null, \"category\": \"半場籃球場\", \"court_ref\": \"半場籃球場\"}]}', NULL, '24.99407580', '121.34095520'),
(38, 27, '長庚國小活動中心', '{\"opening\": [{\"days\": null, \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.06166397', '121.38710260'),
(39, 6, '體育大學羽球場(館)', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五\", \"time\": \"週一至週五平日時段為校內專長及教學使用，故不對外開放，夜間18:00至21:00，辦理活動除外。\", \"category\": \"羽球場(館)\", \"court_ref\": \"羽球場(館)\"}]}', NULL, '25.03047256', '121.38761760'),
(40, 28, '中央警察大學體育館', '{\"opening\": [{\"days\": null, \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.04716275', '121.35351060'),
(41, 29, '長庚科技大學體育館', '{\"opening\": [{\"days\": null, \"time\": null, \"category\": \"羽球場(館)\", \"court_ref\": \"羽球場(館)\"}, {\"days\": null, \"time\": null, \"category\": \"排球場(館)\", \"court_ref\": \"排球場(館)\"}]}', NULL, '25.03065727', '121.38989210'),
(42, 30, '宏德高商進修學校籃球場', '{\"opening\": [{\"days\": null, \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '24.97991670', '121.33137170'),
(43, 31, '迴龍活動中心前籃球場', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.01898641', '121.41026080'),
(44, 32, '文化公園', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.05681417', '121.37156760'),
(45, 33, '楓樹籃球場', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.00638588', '121.34135490'),
(46, 34, '大坪頂公園', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.05458321', '121.36710950'),
(47, 35, '廣六公園', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.05142085', '121.36558060'),
(48, 36, '樂善公園', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.05523486', '121.38071360'),
(49, 37, '迴龍加油站後', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '25.01638657', '121.40242880'),
(50, 38, '桃園市成功橋下運動暨休憩空間', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六、星期日\", \"time\": \"無\", \"category\": \"羽球場(館)\", \"court_ref\": \"羽球場(館)\"}]}', NULL, '24.99606922', '121.32514360'),
(51, 39, '龜山國中籃球場', '{\"opening\": [{\"days\": \"星期一、星期二、星期三、星期四、星期五、星期六\", \"time\": null, \"category\": \"籃球場\", \"court_ref\": \"籃球場\"}]}', NULL, '24.99733819', '121.33889260');

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
(2, 1),
(3, 1),
(4, 1),
(5, 1),
(6, 1),
(7, 1),
(8, 1),
(9, 1),
(10, 1),
(11, 1),
(12, 1),
(13, 1),
(14, 1),
(15, 1),
(16, 1),
(17, 1),
(18, 1),
(19, 1),
(20, 1),
(21, 1),
(23, 1),
(26, 1),
(27, 1),
(28, 1),
(29, 1),
(30, 1),
(36, 1),
(39, 1),
(41, 1),
(50, 1),
(51, 1),
(3, 4),
(5, 4),
(11, 4),
(12, 4),
(13, 4),
(15, 4),
(17, 4),
(21, 4),
(26, 4),
(27, 4),
(28, 4),
(36, 4),
(41, 4),
(51, 4);

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
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `keep_user_id_game_id_uniq` (`user_id`,`game_id`),
  ADD KEY `game_id` (`game_id`);

--
-- 資料表索引 `match_participants`
--
ALTER TABLE `match_participants`
  ADD PRIMARY KEY (`list_id`),
  ADD UNIQUE KEY `game_id` (`game_id`,`user_id`),
  ADD KEY `user_id` (`user_id`);

--
-- 資料表索引 `notification`
--
ALTER TABLE `notification`
  ADD PRIMARY KEY (`notification_id`),
  ADD KEY `fk_notification_game` (`game_id`),
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
  ADD UNIQUE KEY `phone` (`phone`),
  ADD UNIQUE KEY `email` (`email`);

--
-- 資料表索引 `user_sport_levels`
--
ALTER TABLE `user_sport_levels`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_sport_levels_user_id_sport_id_uniq` (`user_id`,`sport_id`),
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
  MODIFY `address_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=40;
--
-- 使用資料表 AUTO_INCREMENT `blacklist`
--
ALTER TABLE `blacklist`
  MODIFY `blacklist_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- 使用資料表 AUTO_INCREMENT `court`
--
ALTER TABLE `court`
  MODIFY `court_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=65;
--
-- 使用資料表 AUTO_INCREMENT `court_conflicts`
--
ALTER TABLE `court_conflicts`
  MODIFY `conflict_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- 使用資料表 AUTO_INCREMENT `facilities`
--
ALTER TABLE `facilities`
  MODIFY `facility_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
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
-- 使用資料表 AUTO_INCREMENT `keep`
--
ALTER TABLE `keep`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- 使用資料表 AUTO_INCREMENT `notification`
--
ALTER TABLE `notification`
  MODIFY `notification_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- 使用資料表 AUTO_INCREMENT `penalty_rules`
--
ALTER TABLE `penalty_rules`
  MODIFY `rule_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;
--
-- 使用資料表 AUTO_INCREMENT `reports`
--
ALTER TABLE `reports`
  MODIFY `report_id` int(11) NOT NULL AUTO_INCREMENT;
--
-- 使用資料表 AUTO_INCREMENT `sports`
--
ALTER TABLE `sports`
  MODIFY `sport_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
--
-- 使用資料表 AUTO_INCREMENT `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
--
-- 使用資料表 AUTO_INCREMENT `venues`
--
ALTER TABLE `venues`
  MODIFY `venue_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=52;
--
-- 使用資料表 AUTO_INCREMENT `user_sport_levels`
--
ALTER TABLE `user_sport_levels`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
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
-- 資料表的 Constraints `notification`
--
ALTER TABLE `notification`
  ADD CONSTRAINT `fk_notification_game` FOREIGN KEY (`game_id`) REFERENCES `gamesmatches` (`game_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `notification_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

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
