SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;


CREATE TABLE `hashImage` (
  `id` int(11) NOT NULL,
  `file_id` text NOT NULL,
  `filename` text CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `subs` (
  `user_id` bigint(20) NOT NULL,
  `region` text CHARACTER SET utf8mb4 NOT NULL,
  `scope` varchar(255) NOT NULL DEFAULT 'void'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `users` (
  `tg_id` bigint(20) NOT NULL,
  `lang` text NOT NULL,
  `notifications` set('none','world','spain','italy','france','austria','argentina','australia','brazil','canada','chile','china','colombia','germany','india','mexico','portugal','us','unitedkingdom') DEFAULT 'none',
  `n_world` tinyint(1) NOT NULL DEFAULT '0',
  `n_spain` tinyint(1) NOT NULL DEFAULT '0',
  `n_italy` tinyint(1) NOT NULL DEFAULT '0',
  `n_france` tinyint(1) NOT NULL DEFAULT '0',
  `n_austria` int(11) NOT NULL DEFAULT '0',
  `botons` set('gl','es','it','fr','at','ar','au','br','ca','cl','cn','co','de','in','mx','pt','us','gb') NOT NULL DEFAULT 'gl,es,it'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


ALTER TABLE `hashImage`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `subs`
  ADD KEY `s_key` (`user_id`,`region`(255));

ALTER TABLE `users`
  ADD UNIQUE KEY `id` (`tg_id`);


ALTER TABLE `hashImage`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3174;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
