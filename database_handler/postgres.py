import logging

import psycopg2

from config import DATABASE
from config import HOST
from config import PASSWORD
from config import USER


class DatabaseHandler(object):
    @classmethod
    def sql_query(cls, query, *args, one=True):
        conn = psycopg2.connect(
            f"dbname={DATABASE} user={USER} password={PASSWORD} host={HOST}"
        )
        conn.cursor.execute(query, args)
        if one:
            data = conn.cursor().fetchone()
        else:
            data = conn.cursor().fetchall()
        conn.cursor.close()
        return data

    @classmethod
    def sql_exec(cls, query, *args):
        conn = psycopg2.connect(
            f"dbname={DATABASE} user={USER} password={PASSWORD} host={HOST}"
        )
        conn.cursor().execute(query, args)
        conn.cursor().close()
        conn.commit()

    @classmethod
    def setup_tables(cls) -> None:
        """Creates initial tables"""
        commands = (
            """
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'punishment_types') THEN
                        CREATE TYPE punishment_types AS ENUM ('mute', 'warn', 'kick', 'ban');
                    END IF;
                END$$;
                """,
            """
                CREATE TABLE IF NOT EXISTS punishments (
                    punishment_id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    moderator_id BIGINT NOT NULL,
                    guild_id BIGINT NOT NULL,
                    punishment_type punishment_types NOT NULL,
                    reason TEXT NOT NULL,
                    punished_at TIMESTAMP NOT NULL,
                    duration BIGINT NULL,
                    permanent BOOL DEFAULT TRUE,
                    expired BOOL DEFAULT FALSE
                )
            """,
            """
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT NOT NULL,
                    username TEXT NOT NULL,
                    raw_messages INT NOT NULL DEFAULT 0,
                    messages INT NOT NULL DEFAULT 0,
                    experience INT NOT NULL DEFAULT 0,
                    past_snipes VARCHAR(16)[],
                    snipes_auth_code VARCHAR(64)
                )
            """,
            """
                CREATE TABLE IF NOT EXISTS captcha_users (
                    user_id BIGINT NOT NULL,
                    captcha VARCHAR(5) NOT NULL,
                    attempts INT NOT NULL DEFAULT 0
                )
            """,
        )
        for command in commands:
            cls.sql_exec(command)
        logging.info("Postgres has generated tables...")
