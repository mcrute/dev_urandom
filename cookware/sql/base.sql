--
-- Schema Definition for Cookware Recipe Managment System
-- Written July 21, 2007 by Mike Crute (mcrute@gmail.com)
-- 
-- $Id$
--

-- Default database is `cookware`, you can change this if you like.
USE cookware;

--
-- Recipe Table
--
CREATE TABLE IF NOT EXISTS recipe 
(
	-- Record ID
	id           BIGINT    UNISGNED ZEROFILL NOT NULL AUTO_INCREMENT,
	
	-- Core Recipe Data
	name         TEXT      NOT NULL UNIQUE,
	description  LONGTEXT  NOT NULL,
	rating       TINYINT   NOT NULL DEFAULT 0,
	picture      BLOB      NULL,
	ethnicity    BIGINT    UNSIGNED DEFAULT 0,

	-- Creator/Revisor Information
	addedby      BIGINT    UNSIGNED NOT NULL,
	updatedby    BIGINT    UNSIGNED NULL,
	dateadded    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	dateupdated  TIMESTAMP DEFAULT NULL,
	
	-- Yield Information
	yield        TEXT      NOT NULL,
	servings     INT       UNSIGNED NOT NULL,
	
	-- Time Information
	preptime     INT       UNSIGNED NOT NULL,
	prepunits    BIGINT    UNSIGNED NOT NULL,
	cooktime     INT       UNSIGNED NOT NULL,
	cookunits    BIGINT    UNSIGNED NOT NULL,
	preheattemp  INT       UNSIGNED NOT NULL,
	preheatunits BIGINT    UNSIGNED NOT NULL,
	
	-- Keys
	PRIMARY KEY (id)
) 
ENGINE=InnoDB;

--
-- Units Table
--
CREATE TABLE IF NOT EXISTS units
(
	-- Core Unit Data
	id           BIGINT    UNISGNED ZEROFILL NOT NULL AUTO_INCREMENT,
	name         TEXT      NOT NULL,
	
	-- Unit Types and Systems
	--
	-- These are critical for unit conversion but don't actually hold any
	-- conversion data themselves. See the next SQL section and the 
	-- application logic for more information about this process.
	unittype     ENUM(
						'solid',
						'liquid',
						'noconvert'
					)      DEFAULT 'noconvert',
	unitsystem   ENUM(
						'american',
						'si'
					)      DEFAULT 'american',

	-- Unit Conversion Data
	--
	-- The application converts units to and from each other based on an SI
	-- base unit. You should probably be looking at the application logic
	-- and not the schema if you want to know how this really works.
	tosibase     INT,
	fromsibase   INT,

	-- Keys
	PRIMARY KEY (id)
)
ENGINE=InnoDB;

--
-- System Users Table
--
CREATE TABLE IF NOT EXISTS users
(
	-- Core User Data
	id           BIGINT    UNISGNED ZEROFILL NOT NULL AUTO_INCREMENT,
	username     TEXT      NOT NULL UNIQUE,
	name         TEXT      NOT NULL,
	password     TEXT      NOT NULL,
	
	-- Keys
	PRIMARY KEY (id)
)
ENGINE=InnoDB;

--
-- Ethnicity Table
--
CREATE TABLE IF NOT EXISTS ethnicities 
(
	-- Core Ethnicity Data
	id           BIGINT    UNISGNED ZEROFILL NOT NULL AUTO_INCREMENT,
	name         TEXT      NOT NULL UNIQUE,

	-- Keys
	PRIMARY KEY(id)
)
ENGINE=InnoDB;

--
-- Ingredients Table
--
CREATE TABLE IF NOT EXISTS ingredients
(
	-- Core Ingredient Data
	id           BIGINT    UNISGNED ZEROFILL NOT NULL AUTO_INCREMENT,
	name         TEXT      NOT NULL UNIQUE,
	
	-- Keys
	PRIMARY KEY(id)
)
ENGINE=InnoDB;

-- 
-- Ingredient -> Recipe Mapping Table
--
CREATE TABLE IF NOT EXISTS recipe_ingredients
(
	-- Relationship Data
	ingredient   BIGINT    UNSIGNED ZEROFILL NOT NULL,
	recipe       BIGINT    UNSIGNED ZEROFILL NOT NULL,
	
	-- Ingredient Information
	amount       INT       UNSIGNED NOT NULL,
	units        BIGINT    UNSIGNED NOT NULL,
	optional     BIT       DEFAULT 0,
	`order`      INT       UNSIGNED NOT NULL DEFAULT 0  
)
ENGINE=InnoDB;

--
-- Related Recipe Table
--
CREATE TABLE IF NOT EXISTS related_recipes
(
	main_recipe     BIGINT    UNSIGNED ZEROFILL NOT NULL,
	related_recipe  BIGINT    UNSIGNED ZEROFILL NOT NULL
)
ENGINE=InnoDB;

--
-- Instructions Table
--
CREATE TABLE IF NOT EXISTS instructions
(
	-- Core Instructions Data
	id           BIGINT    UNISGNED ZEROFILL NOT NULL AUTO_INCREMENT,
	recipe       BIGINT    UNSIGNED ZEROFILL NOT NULL,
	directions   LONGTEXT  NOT NULL UNIQUE,
	`order`      INT       UNSIGNED NOT NULL DEFAULT 0,

	-- Keys
	PRIMARY KEY(id)
)
ENGINE=InnoDB;
