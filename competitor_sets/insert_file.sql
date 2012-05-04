SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";



CREATE TABLE IF NOT EXISTS `competitor_sets2` (
  `req_id` int(11) NOT NULL,
  `set_id` int(11) DEFAULT NULL,
  `host_id` int(11) DEFAULT NULL,
  `surfer_id` int(11) DEFAULT NULL,
  `winner` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`req_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

INSERT INTO `competitor_sets2` (`req_id`, `set_id`, `host_id`, `surfer_id`, `winner`) VALUES
