-- CREATE TABLE `computer_users` (
-- 	`full_name` varchar(50) NOT NULL,
-- 	`user_name` varchar(50) NOT NULL UNIQUE,
-- 	`password` varchar(255) NOT NULL,
-- 	`comouter` BINARY NOT NULL UNIQUE,
-- 	`salt` int NOT NULL,
-- 	PRIMARY KEY (`user_name`)
-- );

CREATE TABLE `Computers` (
	`MAC` BINARY PRIMARY KEY NOT NULL,
	`ip` varchar(15) NOT NULL,
	`size` bigint NOT NULL,
	`online` TINYINT(1) NOT NULL DEFAULT 0,
	`geo_location` enum NOT NULL,
	PRIMARY KEY (`MAC`)
);

-- -- CREATE TABLE `Data` (
-- -- 	`hash` varchar(250) NOT NULL,
-- -- 	`id` INT NOT NULL AUTO_INCREMENT UNIQUE,
-- -- 	`size` BINARY NOT NULL,
-- -- 	`path` varchar(255) NOT NULL,
-- -- 	`relation` varchar(50) NOT NULL,
-- -- 	`location` BINARY NOT NULL,
-- -- 	`parity` bool NOT NULL DEFAULT 'False',
-- -- 	`Segment` INT NOT NULL,
-- -- 	PRIMARY KEY (`id`)
-- -- );

-- -- CREATE TABLE `data_users` (
-- -- 	`user_id` varchar(50) NOT NULL UNIQUE,
-- -- 	`name` varchar(50) NOT NULL,
-- -- 	`password` INT NOT NULL,
-- -- 	`AES_Key` BINARY NOT NULL UNIQUE,
-- -- 	PRIMARY KEY (`user_id`)
-- -- );

-- -- CREATE TABLE `drives` (
-- -- 	`MAC` BINARY NOT NULL AUTO_INCREMENT,
-- -- 	`drive_type` enum NOT NULL,
-- -- 	`drive_name` varchar(50) NOT NULL,
-- -- 	`left_space` bigint NOT NULL
-- -- );

-- -- ALTER TABLE `computer_users` ADD CONSTRAINT `computer_users_fk0` FOREIGN KEY (`comouter`) REFERENCES `Computers`(`MAC`);

-- -- ALTER TABLE `Data` ADD CONSTRAINT `Data_fk0` FOREIGN KEY (`relation`) REFERENCES `data_users`(`user_id`);

-- -- ALTER TABLE `Data` ADD CONSTRAINT `Data_fk1` FOREIGN KEY (`location`) REFERENCES `Computers`(`MAC`);

-- -- ALTER TABLE `Data` ADD CONSTRAINT `Data_fk2` FOREIGN KEY (`Segment`) REFERENCES `Data`(`id`);

-- -- ALTER TABLE `drives` ADD CONSTRAINT `drives_fk0` FOREIGN KEY (`MAC`) REFERENCES `Computers`(`MAC`);






