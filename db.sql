-- phpMyAdmin SQL Dump
-- version 4.5.4.1deb2ubuntu2.1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jan 13, 2021 at 10:25 AM
-- Server version: 5.7.29-0ubuntu0.16.04.1
-- PHP Version: 7.2.29-1+ubuntu16.04.1+deb.sury.org+1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cvdnou`
--
CREATE DATABASE IF NOT EXISTS `cvdnou` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `cvdnou`;

-- --------------------------------------------------------

--
-- Table structure for table `hashImage`
--

CREATE TABLE `hashImage` (
  `id` int(11) NOT NULL,
  `file_id` text NOT NULL,
  `filename` text CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `subs`
--

CREATE TABLE `subs` (
  `user_id` bigint(20) NOT NULL,
  `region` text CHARACTER SET utf8 COLLATE utf8_spanish2_ci NOT NULL,
  `scope` varchar(255) NOT NULL DEFAULT 'void'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `updates`
--

CREATE TABLE `updates` (
  `scope` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `notified` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `tg_id` bigint(20) NOT NULL,
  `lang` text NOT NULL,
  `notifications` set('none','world','spain','italy','france','austria','argentina','australia','brazil','canada','chile','china','colombia','germany','india','mexico','portugal','us','unitedkingdom','balears','mallorca','menorca','eivissa','catalunya') DEFAULT 'none',
  `n_world` tinyint(1) NOT NULL DEFAULT '0',
  `n_spain` tinyint(1) NOT NULL DEFAULT '0',
  `n_italy` tinyint(1) NOT NULL DEFAULT '0',
  `n_france` tinyint(1) NOT NULL DEFAULT '0',
  `n_austria` int(11) NOT NULL DEFAULT '0',
  `botons` set('gl','es','it','fr','at','ar','au','br','ca','cl','cn','co','de','in','mx','pt','us','gb','ib','ma','me','ei','ct') NOT NULL DEFAULT 'gl,es,it'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `hashImage`
--
ALTER TABLE `hashImage`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `subs`
--
ALTER TABLE `subs`
  ADD KEY `s_key` (`user_id`,`region`(255));

--
-- Indexes for table `updates`
--
ALTER TABLE `updates`
  ADD UNIQUE KEY `scope` (`scope`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD UNIQUE KEY `id` (`tg_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `hashImage`
--
ALTER TABLE `hashImage`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=51289;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
