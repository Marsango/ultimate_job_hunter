from typing import Any

import psycopg2


class Database:
    def __init__(self) -> None:
        self.__con: psycopg2.connect = psycopg2.connect(host="localhost", dbname="job_hunter", user="postgres",
                                                        password="123", port=5432)
        self.__cur: psycopg2.cursor = self.__con.cursor()
        self.setup_database()

    def setup_database(self) -> None:
        self.__cur.execute(
            "CREATE TABLE IF NOT EXISTS job_available(id SERIAL PRIMARY KEY, name varchar(255), description text,"
            "company varchar(255), type varchar(255), published_date date, dead_line_date date, is_remote boolean,"
            "url varchar(400))")
        self.__cur.execute(
            "CREATE TABLE IF NOT EXISTS past_available_job(id SERIAL PRIMARY KEY, name varchar(255), description text,"
            "company varchar(255), type varchar(255), published_date date, dead_line_date date, is_remote boolean,"
            "url varchar(400))")
        self.__con.commit()

    def insert_new_jobs(self, job_list: list[dict[str, Any]]) -> list[dict[str, str]]:
        new_jobs: list[dict[str, str]] = []
        for job_info in job_list:
            self.__cur.execute("""
                INSERT INTO job_available(name, description, company, type, published_date, dead_line_date, is_remote, url)
                SELECT %(name)s, %(description)s, %(company)s, %(type)s, %(published_date)s, %(dead_line_date)s, %(is_remote)s, %(url)s
                WHERE NOT EXISTS (
                    SELECT 1 FROM job_available 
                    WHERE name = %(name)s AND company = %(company)s AND published_date = %(published_date)s
                )
                RETURNING name, description;
            """, job_info)
            current_result: dict[str, str] = self.__cur.fetchone()
            if current_result:
                new_jobs.append(current_result)
                self.__con.commit()
        return new_jobs
