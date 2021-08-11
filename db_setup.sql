CREATE TABLE afk (
   last_seen TIMESTAMP,
   user_id BIGINT NOT NULL,
   reason TEXT,
   PRIMARY KEY (user_id)
);

CREATE TABLE blocks (
   user_id BIGINT NOT NULL,
   PRIMARY KEY (user_id)
);

CREATE TABLE economy (
   user_id BIGINT NOT NULL,
   inventory TEXT,
   wallet INTEGER,
   bank INTEGER,
   PRIMARY KEY (user_id)
);

CREATE TABLE guilds (
   id BIGINT NOT NULL,
   prefix TEXT,
   PRIMARY KEY (id)
);

CREATE TABLE invitetracker (
   guild_id BIGINT NOT NULL,
   channel_id BIGINT,
   PRIMARY KEY (guild_id)
);

CREATE TABLE status (
   last_seen TIMESTAMP,
   user_id BIGINT NOT NULL,
   PRIMARY KEY (user_id)
);

CREATE TABLE timezones (
   timezone TEXT,
   user_id BIGINT NOT NULL,
   PRIMARY KEY (user_id)
);

CREATE TABLE usages (
   usage INTEGER,
   name TEXT NOT NULL,
   PRIMARY KEY (name)
);

CREATE TABLE users (
   usage INTEGER,
   user_id BIGINT NOT NULL,
   PRIMARY KEY (user_id)
);
CREATE TABLE telephones (
   phone_number BIGINT NOT NULL,
   user_id BIGINT NOT NULL,
   PRIMARY KEY (user_id)
);
CREATE TABLE tags (
   last_used TIMESTAMP,
   created_at TIMESTAMP,
   edited_at TIMESTAMP,
   tag_id SMALLSERIAL NOT NULL ,
   author_id BIGINT,
   name VARCHAR(32) NOT NULL,
   content TEXT NOT NULL,
   PRIMARY KEY (tag_id)
);