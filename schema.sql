CREATE TABLE IF NOT EXISTS `data` (
  `token` char(32) COLLATE utf8_unicode_ci NOT NULL,
  `secret` mediumtext COLLATE utf8_unicode_ci NOT NULL,
  `password` varchar(3358) COLLATE utf8_unicode_ci NOT NULL,
  `creationtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `timetolive` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS `tokens` (
  `token` char(32) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

ALTER TABLE `data`
 ADD PRIMARY KEY (`token`);

ALTER TABLE `tokens`
 ADD PRIMARY KEY (`token`);