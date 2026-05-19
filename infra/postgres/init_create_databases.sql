-- Creates the two databases used by the compose setup: redsage and redmine_agent
-- Place this file in a volume mounted to /docker-entrypoint-initdb.d/ so Postgres creates DBs at container init

CREATE DATABASE redsage;
CREATE DATABASE redmine_agent;
