import requests
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import Error


class JobParser:
    def __init__(self):
        self.URL = "https://realpython.github.io/fake-jobs/"

    def connect(self):
        try:
            response = requests.get(self.URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            positions = soup.find_all('h2', class_='title')
            companies = soup.find_all('h3', class_='company')
            locations = soup.find_all('p', class_='location')
            times = soup.find_all('time')

            info = []
            for company, position, location, time in zip(companies, positions, locations, times):
                info.append({
                    "company": company.text.strip(),
                    "position": position.text.strip(),
                    "location": location.text.strip(),
                    "time": time.text.strip()
                })

            print(f"Знайдено вакансій: {len(info)}")
            return info

        except Exception as error:
            print(f"Помилка при парсингу: {error}")
            return []


class MySQLHandler:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self, create_db_if_missing=True):

        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = self.connection.cursor()
            if create_db_if_missing:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            cursor.execute(f"USE {self.database}")
            print("MySQL підключення успішне")
        except Error as e:
            print(f"Помилка підключення до MySQL: {e}")
            exit(1)

    def create_table(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS jobs
                           (
                               id
                               INT
                               AUTO_INCREMENT
                               PRIMARY
                               KEY,
                               company
                               VARCHAR
                           (
                               255
                           ),
                               position VARCHAR
                           (
                               255
                           ),
                               location VARCHAR
                           (
                               255
                           ),
                               time_posted VARCHAR
                           (
                               100
                           )
                               )
                           """)
            self.connection.commit()
            print("Таблиця jobs створена або вже існує")
        except Error as e:
            print(f"Помилка створення таблиці: {e}")


class JobToDatabase:
    def __init__(self, mysql_handler):
        self.mysql_handler = mysql_handler

    def insert_jobs(self, jobs):
        if not jobs:
            print("Немає вакансій для додавання")
            return
        try:
            cursor = self.mysql_handler.connection.cursor()
            for job in jobs:
                cursor.execute("""
                               INSERT INTO jobs (company, position, location, time_posted)
                               VALUES (%s, %s, %s, %s)
                               """, (job['company'], job['position'], job['location'], job['time']))
            self.mysql_handler.connection.commit()
            print(f"Додано {len(jobs)} вакансій у базу")
        except Error as e:
            print(f"Помилка запису у базу: {e}")


if __name__ == "__main__":
    parser = JobParser()
    jobs_data = parser.connect()

    db = MySQLHandler(host="localhost", user="root", password="Ruslan@2009", database="jobs_db")
    db.connect()
    db.create_table()

    inserter = JobToDatabase(db)
    inserter.insert_jobs(jobs_data)
