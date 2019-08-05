CREATE TABLE IF NOT EXISTS `users`(
	`email`	TEXT NOT NULL UNIQUE,
	`firstname`	TEXT NOT NULL,
	`familyname`	TEXT NOT NULL,
	`gender`	TEXT NOT NULL,
	`city`	TEXT NOT NULL,
	`country`	TEXT NOT NULL,
	`password`	TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS `activeusers`(
	`email`	TEXT NOT NULL UNIQUE,
	`token`	TEXT NOT NULL UNIQUE
);
