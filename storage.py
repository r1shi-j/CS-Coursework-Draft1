import sqlite3
import uuid
from datetime import datetime

# def _tempdate() -> str:
#     return datetime.now().strftime("%d/%m/%y %H:%M:%S")#.strftime("%Y-%m-%d %h:%m:%s")

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
            tournament_result INTEGER,
            PRIMARY KEY (tournament_id, player_id),
            FOREIGN KEY (tournament_id) REFERENCES Tournament(tournament_id),
            FOREIGN KEY (player_id) REFERENCES Player(player_id)
        );
        """)

        self.connection.commit()

    def read_tournament_data(self) -> list[tuple]:
        self.cursor.execute("SELECT * FROM Tournament;")
        return self.cursor.fetchall()
    
    def find_tournament_winner(self, t_id: str):
        self.cursor.execute("""
            SELECT p.*
            FROM TournamentParticipation tp
            JOIN Player p ON tp.player_id = p.player_id
            WHERE tp.tournament_id = ?
            AND tp.tournament_result = 1
        """, (t_id,))
        return self.cursor.fetchall()
    
    # def _insert_filler_tournament_data(self):
    #     self.cursor.execute("INSERT INTO Tournament (tournament_id, date, player_count, tournament_type_id) VALUES (?, ?, ?, ?)", (create_uuid(), _tempdate(), 5, "af1b7dbc-a3cd-46d5-aaae-f16aff3eec2a"))
    #     self.connection.commit()

    def add_player_to_tournament(self, t_id: str, p_id: str):
        self.cursor.execute("INSERT INTO TournamentParticipation (tournament_id, player_id, tournament_result) VALUES (?, ?, ?)", (t_id, p_id, None))
        self.connection.commit()

    def create_tournament(self, t_id: str, date: str, p_count: int, ttype_id: str):
        self.cursor.execute("INSERT INTO Tournament (tournament_id, date, player_count, tournament_type_id) VALUES (?, ?, ?, ?)", (t_id, date, p_count, ttype_id))
        self.connection.commit()

    def read_tournament_types(self) -> list[tuple]:
        self.cursor.execute("SELECT * FROM TournamentType;")
        return self.cursor.fetchall()

    def add_tournament_type(self, def_continuers: int, num_grandprix: int, longer_style: bool):
        self.cursor.execute(
            "INSERT INTO TournamentType (tournament_type_id, def_continuers, num_grandprix, longer_style) VALUES (?, ?, ?, ?)",
            (create_uuid(), def_continuers, num_grandprix, longer_style)
        )
        self.connection.commit()
    
    # def remove_player_to_tournament(self, p_id: str):
    #     return
    
    # def tournament_players(self, t_id: str) -> list[tuple]:
    #     self.cursor.execute("SELECT * FROM TournamentParticipation WHERE player_id;")
    #     return self.cursor.fetchall()
    
    def read_player_data(self) -> list[tuple]:
        self.cursor.execute("SELECT * FROM Player;")
        return self.cursor.fetchall()

    def search_players(self, search_term: str) -> list[tuple]:
        query = """
            SELECT * FROM Player
            WHERE forename LIKE ?
            OR surname LIKE ?
            OR CAST(age AS TEXT) LIKE ?
        """
        like_term = f"%{search_term}%"
        params = [like_term, like_term, like_term]

        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def add_player(self, forename: str, surname: str, age: int):
        self.cursor.execute("INSERT INTO Player (player_id, forename, surname, age) VALUES (?, ?, ?, ?)", (create_uuid(), forename, surname, age))
        self.connection.commit()

    def update_player(self, player_id: str, forename: str, surname: str, age: int):
        self.cursor.execute("UPDATE Player SET forename=?, surname=?, age=? WHERE player_id=?", (forename, surname, age, player_id))
        self.connection.commit()

    def delete_player(self, player_id: str):
        self.cursor.execute("DELETE FROM Player WHERE player_id = ?", (player_id,))
        self.connection.commit()

    def read_circuit_data(self) -> list[tuple]:
        self.cursor.execute("SELECT * FROM Circuit;")
        return self.cursor.fetchall()

    def search_circuits(self, search_term: str) -> list[tuple]:
        query = """
            SELECT * FROM Circuit
            WHERE circuit_name LIKE ?
        """
        like_term = f"%{search_term}%"
        params = [like_term]

        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def _insert_circuit(self, circuit_name: str):
        self.cursor.execute("INSERT INTO Circuit (circuit_id, circuit_name) VALUES (?, ?)", (create_uuid(), circuit_name))
        self.connection.commit()

    def _insert_circuits(self, circuit_names: list[str]):
        values = [(create_uuid(), name) for name in circuit_names]
        self.cursor.executemany("INSERT INTO Circuit (circuit_id, circuit_name) VALUES (?, ?)", values)
        self.connection.commit()
    
    def _remove_circuits(self, circuit_id: str):
        self.cursor.execute("DELETE FROM Circuit WHERE circuit_id = ?", (circuit_id,))
        self.connection.commit()

    # def search_data(self):
    #     self.cursor.execute("SELECT forename, surname FROM Player WHERE age > ?", (30,))
    #     print(self.cursor.fetchall())
    # 
    # def insert_data(self):
    #     # self.cursor.execute("INSERT INTO Player (player_id, forename, surname, age) VALUES (?, ?, ?, ?)", (create_uuid(), "Lewis", "Hamilton", 39))
    #     # self.cursor.execute("INSERT INTO Player (player_id, forename, surname, age) VALUES (?, ?, ?, ?)", (create_uuid(), "Max", "Verstappen", 27))
    #     # self.cursor.execute("""
    #     # INSERT INTO TournamentType (tournament_type_id, def_continuers, num_grandprix, longer_style) 
    #     # VALUES (?, ?, ?, ?)
    #     # """, (create_uuid(), 2, 1, False))
    # 
    #     self.cursor.execute("INSERT INTO Tournament (tournament_id, date, player_count, tournament_type_id) VALUES (?, ?, ?, ?)", (create_uuid(), tempdate(), 17, "af1b7dbc-a3cd-46d5-aaae-f16aff3eec2a"))
    # 
    #     # players = [
    #     #     (create_uuid(), "Lewis", "Hamilton", 39),
    #     #     (create_uuid(), "Max", "Verstappen", 27),
    #     #
    # 
    #     # self.cursor.executemany("INSERT INTO Player (player_id, forename, surname, age) VALUES (?, ?, ?, ?)", players)
    #     self.connection.commit()
    # 
    # def delete_data(self):
    #     # self.cursor.execute("DELETE FROM Player WHERE player_id = ?", (player_id_to_delete,))
    #     players = [
    #         ("e1198136-f478-41a1-803e-0ab4009cb4bd",),
    #         ("691f1187-04be-4f47-aaab-cd6e27f3e0d4",)
    #     ]
    #     self.cursor.executemany("DELETE FROM Player WHERE player_id = ?", players)
    #     self.connection.commit()

    def close(self):
        self.connection.close()


# db = Database()
# db.connect()
# db._insert_filler_tournament_data()
# db.close()