-- phpMyAdmin SQL Dump
-- version 4.9.1
-- https://www.phpmyadmin.net/
--
-- 主機： localhost
-- 產生時間： 
-- 伺服器版本： 8.0.17
-- PHP 版本： 7.3.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `university2026`
--

-- --------------------------------------------------------

--
-- 資料表結構 `section`
--

CREATE TABLE `section` (
  `course_id` varchar(8) DEFAULT NULL,
  `sec_id` varchar(8) DEFAULT NULL,
  `semester` varchar(6) DEFAULT NULL,
  `year` decimal(4,0) DEFAULT NULL,
  `building` varchar(15) DEFAULT NULL,
  `room_number` varchar(7) DEFAULT NULL,
  `time_slot_id` varchar(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- 傾印資料表的資料 `section`
--

INSERT INTO `section` (`course_id`, `sec_id`, `semester`, `year`, `building`, `room_number`, `time_slot_id`) VALUES
('BIO-301', '1', 'Summer', '2010', 'Painter', '514', 'A'),
('CS-101', '1', 'Fall', '2009', 'Packard', '101', 'H'),
('CS-101', '1', 'Spring', '2010', 'Packard', '101', 'F'),
('CS-190', '1', 'Spring', '2009', 'Taylor', '3128', 'E'),
('CS-190', '2', 'Spring', '2009', 'Taylor', '3128', 'A'),
('BIO-101', '1', 'Summer', '2009', 'Painter', '514', 'B'),
('CS-315', '1', 'Spring', '2010', 'Watson', '120', 'D'),
('CS-319', '1', 'Spring', '2010', 'Watson', '100', 'B'),
('CS-319', '2', 'Spring', '2010', 'Taylor', '3128', 'C'),
('CS-347', '1', 'Fall', '2009', 'Taylor', '3128', 'A'),
('EE-181', '1', 'Spring', '2009', 'Taylor', '3128', 'C'),
('FIN-201', '1', 'Spring', '2010', 'Packard', '101', 'B'),
('HIS-351', '1', 'Spring', '2010', 'Painter', '514', 'C'),
('MU-199', '1', 'Spring', '2010', 'Packard', '101', 'D'),
('PHY-101', '1', 'Fall', '2009', 'Watson', '100', 'A');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION *
