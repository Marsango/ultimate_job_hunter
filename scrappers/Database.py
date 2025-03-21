from typing import Any
import psycopg2
import psycopg2.extras


class Database:
    def __init__(self) -> None:
        self.__con: psycopg2.connect = psycopg2.connect(host="localhost", dbname="job_hunter", user="postgres",
                                                        password="123", port=5432)
        self.__cur: psycopg2.cursor = self.__con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.setup_database()

    def setup_database(self) -> None:
        self.__cur.execute(
            "CREATE TABLE IF NOT EXISTS available_job(id SERIAL PRIMARY KEY, name varchar(255), description text,"
            "company varchar(255), type varchar(255), published_date timestamp, dead_line_date timestamp, is_remote boolean,"
            "url text, website varchar(255), job_id varchar(255))")
        self.__cur.execute(
            "CREATE TABLE IF NOT EXISTS past_available_job(id SERIAL PRIMARY KEY, name varchar(255), description text,"
            "company varchar(255), type varchar(255), published_date timestamp, dead_line_date timestamp, is_remote boolean,"
            "url text, website varchar(255), job_id varchar(255))")
        self.__con.commit()

    def insert_new_jobs(self, job_list: list[dict[str, Any]]) -> list[dict[str, str]]:
        new_jobs: list[dict[str, str]] = []
        for job_info in job_list:
            self.__cur.execute("""
                INSERT INTO available_job(name, description, company, type, published_date, dead_line_date, is_remote, url, website, job_id)
                SELECT %(name)s, %(description)s, %(careerPageName)s, %(type)s, %(publishedDate)s, %(applicationDeadline)s, %(isRemoteWork)s, %(jobUrl)s, %(website)s, %(id)s
                WHERE NOT EXISTS (
                    SELECT 1 FROM available_job 
                    WHERE url = %(jobUrl)s
                )
                AND NOT EXISTS (                   
                    SELECT 1 FROM available_job 
                    WHERE company = %(careerPageName)s 
                    AND name = %(name)s
                    AND DATE_TRUNC('week', published_date) = DATE_TRUNC('week', %(publishedDate)s::DATE)                  
                ) 
                RETURNING name, is_remote, published_date, company, url, website, job_id;
            """, job_info)
            current_result: dict[str, str] = self.__cur.fetchone()
            if current_result:
                new_jobs.append(current_result)
                self.__con.commit()
        return new_jobs

    def is_job_in_database(self, job_id: str) -> bool:
        self.__cur.execute("""SELECT * from available_job 
                            WHERE job_id = %s""", (job_id, ))
        find: None | dict[str, str] = self.__cur.fetchone()
        if find:
            return True
        return False

    def close(self):
        self.__cur.close()
        self.__con.close()


