PRAGMA foreign_keys = ON;

create table anime(
    animeID integer primary key,
    animeName text,
    animeDescription text,
    imgUrl text
);

create table tags(
    tagID integer primary key,
    content text
);

create table animeTag(
    tagID integer,
    animeID integer,
    foreign key (tagID) references anime(animeID)
    on delete cascade,
    foreign key (animeID) references tags(tagID)
    on delete cascade,
    primary key(tagID, animeID)
);

create table stuffs(
    stuffID integer primary key,
    stuffName text,
    title text
);

create table produce(
    stuffID integer,
    animeID integer,
    foreign key (stuffID) references stuffs(stuffID)
    on delete cascade,
    foreign key (animeID) references anime(animeID)
    on delete cascade,
    primary key(stuffID, animeID)
);

create table mangas(
    mangaID integer primary key,
    mangaName text,
    imgUrl text
);

create table relatedManga(
    mangaID integer,
    animeID integer,
    foreign key (mangaID) references mangas(mangaID)
    on delete cascade,
    foreign key (animeID) references anime(animeID)
    on delete cascade,
    primary key(mangaID, animeID)
);

create table relatedAnime(
    animeID1 integer,
    animeID2 integer,
    foreign key (animeID1) references anime(animeID)
    on delete cascade,
    foreign key (animeID2) references anime(animeID)
    on delete cascade,
    primary key(animeID1, animeID2),
    check (animeID1 < animeID2)
);