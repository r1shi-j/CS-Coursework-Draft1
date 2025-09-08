import sqlite3
import uuid
from datetime import datetime
from typing import Optional

def tempdate():
    return datetime.now().strftime("%Y-%m-%d")

def create_uuid() -> str:
    return str(uuid.uuid4())

class Database:
    def __init__(self, path="tournament.db"):
        self.connection = sqlite3.connect(path)
        self.connection.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.connection.cursor()

    def connect(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Player (
            player_id TEXT PRIMARY KEY NOT NULL,
            forename TEXT NOT NULL,
            surname TEXT NOT NULL,
            age INTEGER
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Race (
            race_id TEXT PRIMARY KEY NOT NULL,
            grandprix_id TEXT NOT NULL,
            circuit_id TEXT NOT NULL,
            FOREIGN KEY (grandprix_id) REFERENCES GrandPrix(grandprix_id),
            FOREIGN KEY (circuit_id) REFERENCES Circuit(circuit_id)
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS GrandPrix (
            grandprix_id TEXT PRIMARY KEY NOT NULL,
            tournament_id TEXT NOT NULL,
            round INTEGER NOT NULL,
            inverse BOOLEAN NOT NULL,
            bracket INTEGER NOT NULL,
            continuers INTEGER NOT NULL,
            FOREIGN KEY (tournament_id) REFERENCES Tournament(tournament_id)
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tournament (
            tournament_id TEXT PRIMARY KEY NOT NULL,
            date TEXT,
            player_count INTEGER,
            tournament_type_id TEXT NOT NULL,
            FOREIGN KEY (tournament_type_id) REFERENCES TournamentType(tournament_type_id)
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Account (
            account_id TEXT PRIMARY KEY NOT NULL,
            tournament_id TEXT NOT NULL,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            FOREIGN KEY (tournament_id) REFERENCES Tournament(tournament_id),
            UNIQUE (tournament_id, username)
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Circuit (
            circuit_id TEXT PRIMARY KEY NOT NULL,
            circuit_name TEXT NOT NULL
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS TournamentType (
            tournament_type_id TEXT PRIMARY KEY NOT NULL,
            def_continuers INTEGER,
            num_grandprix INTEGER,
            longer_style BOOLEAN
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS RaceParticipation (
            race_id TEXT NOT NULL,
            player_id TEXT NOT NULL,
            race_result INTEGER NOT NULL,
            PRIMARY KEY (race_id, player_id),
            FOREIGN KEY (race_id) REFERENCES Race(race_id),
            FOREIGN KEY (player_id) REFERENCES Player(player_id)
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS GrandPrixParticipation (
            grandprix_id TEXT NOT NULL,
            player_id TEXT NOT NULL,
            grandprix_result INTEGER NOT NULL,
            PRIMARY KEY (grandprix_id, player_id),
            FOREIGN KEY (grandprix_id) REFERENCES GrandPrix(grandprix_id),
            FOREIGN KEY (player_id) REFERENCES Player(player_id)
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS TournamentParticipation (
            tournament_id TEXT NOT NULL,
            player_id TEXT NOT NULL,
            tournament_result INTEGER NOT NULL,
            PRIMARY KEY (tournament_id, player_id),
            FOREIGN KEY (tournament_id) REFERENCES Tournament(tournament_id),
            FOREIGN KEY (player_id) REFERENCES Player(player_id)
        );
        """)

        self.connection.commit()

    def insert_data(self):
        # self.cursor.execute("INSERT INTO Player (player_id, forename, surname, age) VALUES (?, ?, ?, ?)", (create_uuid(), "Lewis", "Hamilton", 39))
        # self.cursor.execute("INSERT INTO Player (player_id, forename, surname, age) VALUES (?, ?, ?, ?)", (create_uuid(), "Max", "Verstappen", 27))
        # self.cursor.execute("""
        # INSERT INTO TournamentType (tournament_type_id, def_continuers, num_grandprix, longer_style) 
        # VALUES (?, ?, ?, ?)
        # """, (create_uuid(), 2, 1, False))

        self.cursor.execute("INSERT INTO Tournament (tournament_id, date, player_count, tournament_type_id) VALUES (?, ?, ?, ?)", (create_uuid(), tempdate(), 17, "af1b7dbc-a3cd-46d5-aaae-f16aff3eec2a"))

        # players = [
        #     (create_uuid(), "Lewis", "Hamilton", 39),
        #     (create_uuid(), "Max", "Verstappen", 27),
        # ]

        # self.cursor.executemany("INSERT INTO Player (player_id, forename, surname, age) VALUES (?, ?, ?, ?)", players)
        self.connection.commit()

    def read_data(self):# -> list[tuple]:
        self.cursor.execute("SELECT * FROM Player;")
        data = self.cursor.fetchall()
        return data
        # print(type(data))
        # for x in data:
        #     print(x)

    def search_players(self, search_term: str) -> Optional[list[tuple]]:
        # if firstname == "" and surname == "" and age == "":
        #     return None
        
        query = "SELECT * FROM Player WHERE forename LIKE ? OR surname LIKE ? OR age LIKE ?"
        params = [search_term, search_term, search_term]

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def search_data(self):
        self.cursor.execute("SELECT forename, surname FROM Player WHERE age > ?", (30,))
        print(self.cursor.fetchall())

    def delete_data(self):
        # self.cursor.execute("DELETE FROM Player WHERE player_id = ?", (player_id_to_delete,))
        players = [
            ("e1198136-f478-41a1-803e-0ab4009cb4bd",),
            ("691f1187-04be-4f47-aaab-cd6e27f3e0d4",)
        ]
        self.cursor.executemany("DELETE FROM Player WHERE player_id = ?", players)
        self.connection.commit()

    def close(self):
        self.connection.close()


# db = Database()
# db.connect()
# insert_data()
# db.read_data()
# search_data()
# delete_data()
# read_data()