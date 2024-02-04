
CREATE TABLE `Computers` (
	`MAC` BINARY PRIMARY KEY NOT NULL,
	`ip` varchar(15) NOT NULL,
	`size` bigint NOT NULL,
    `geo_location` INT NOT NULL CHECK (`geo_location` >= 1 AND `geo_location` <= 194)
);