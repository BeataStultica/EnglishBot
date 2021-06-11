CREATE TABLE Sessions(
	UserId     integer       NOT NULL,
	Command    varchar

);
CREATE TABLE Dictionaries(
	UserId     integer       NOT NULL,
	word       varchar(255)  NOT NULL,
	translates varchar(255)
);

CREATE OR REPLACE PROCEDURE CurrCommand(users integer, commands varchar)
AS $$
BEGIN
	IF EXISTS (SELECT FROM Sessions WHERE Sessions.UserId=users) THEN
		UPDATE Sessions
			SET command = commands
		WHERE Sessions.UserId=users;
	ELSE
		INSERT INTO Sessions(UserId, Command) VALUES(users, commands);
	END IF;
END
$$ LANGUAGE plpgsql;
