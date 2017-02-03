CREATE TABLE "users" (
    id            SERIAL,
    username      varchar(30),
    pw            varchar(250),
    email         varchar(100),
    date_created  timestamp default current_timestamp,
    last_modified timestamp,
    primary key(username)
);

CREATE TABLE "playlists" (
    id            SERIAL,
    name          varchar(50),
    url           varchar(250),
    source        varchar(20),
    primary key(url)
);

CREATE TABLE "songs" (
    id            SERIAL,
    songname      varchar(250),
    youtube_id    varchar(15),
    primary key(youtube_id)
);

CREATE TABLE "songs_in_user_playlist" (
    idSong      int,
    uuid        varchar(36),
    primary key(idSong, uuid)
);

CREATE TABLE "user_downloaded" (
    idUser       int,
    idPlaylist   int,
    idSong       int,
    primary key(idUser, idPlaylist, idSong)
);

CREATE TABLE "playlist_users" (
    idUser       int,
    idPlaylist   int,
    uuid         varchar(36),
    primary key(idUser, idPlaylist)
);

CREATE TABLE "errors" (
    idSong       int,
    idUser       int,
    playlist     varchar(50),
    songname     varchar(100),
    description  varchar(250),    
    fecha        timestamp default current_timestamp
)

create or replace function insertpl (plurl varchar, plname varchar, plsource varchar) RETURNS Table(id integer) AS $$
DECLARE
    tempvar integer;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM playlists where url = plurl) THEN
        INSERT INTO "playlists" (name, url, source) values (plname, plurl, plsource);
    END IF;
    RETURN QUERY SELECT playlists.id FROM playlists where url = plurl;
END;
$$ LANGUAGE plpgsql;

