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
            round INTEGER,
            inverse BOOLEAN,
            bracket INTEGER,
            continuers INTEGER,
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
            grandprix_result INTEGER,
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

    def create_tournament(self, t_id: str, date: str, p_count: int, ttype_id: str):
        self.cursor.execute("INSERT INTO Tournament (tournament_id, date, player_count, tournament_type_id) VALUES (?, ?, ?, ?)", (t_id, date, p_count, ttype_id))
        self.connection.commit()
    
    def create_gps_for_tournament(self, t_id: str, players: list[tuple]):
        starter_ids = [create_uuid(), create_uuid(), create_uuid(), create_uuid()]
        self.cursor.execute("INSERT INTO GrandPrix (grandprix_id, tournament_id, round, inverse, bracket, continuers) VALUES (?, ?, ?, ?, ?, ?)", (starter_ids[0], t_id, 1, False, 1, 2))
        self.cursor.execute("INSERT INTO GrandPrix (grandprix_id, tournament_id, round, inverse, bracket, continuers) VALUES (?, ?, ?, ?, ?, ?)", (starter_ids[1], t_id, 1, False, 2, 2))
        self.cursor.execute("INSERT INTO GrandPrix (grandprix_id, tournament_id, round, inverse, bracket, continuers) VALUES (?, ?, ?, ?, ?, ?)", (starter_ids[2], t_id, 1, True, 1, 2))
        self.cursor.execute("INSERT INTO GrandPrix (grandprix_id, tournament_id, round, inverse, bracket, continuers) VALUES (?, ?, ?, ?, ?, ?)", (starter_ids[3], t_id, 1, True, 2, 2))
        self.cursor.execute("INSERT INTO GrandPrix (grandprix_id, tournament_id, round, inverse, bracket, continuers) VALUES (?, ?, ?, ?, ?, ?)", (create_uuid(), t_id, 2, False, 1, 2))
        self.cursor.execute("INSERT INTO GrandPrix (grandprix_id, tournament_id, round, inverse, bracket, continuers) VALUES (?, ?, ?, ?, ?, ?)", (create_uuid(), t_id, 2, True, 1, 2))
        self.cursor.execute("INSERT INTO GrandPrix (grandprix_id, tournament_id, round, inverse, bracket, continuers) VALUES (?, ?, ?, ?, ?, ?)", (create_uuid(), t_id, None, None, None, None))
        self.connection.commit()

        for p in players[0:4]:
            self.cursor.execute("INSERT INTO GrandPrixParticipation (grandprix_id, player_id, grandprix_result) VALUES (?, ?, ?)", (starter_ids[0], p[0], None))

        for p in players[4:8]:
            self.cursor.execute("INSERT INTO GrandPrixParticipation (grandprix_id, player_id, grandprix_result) VALUES (?, ?, ?)", (starter_ids[1], p[0], None))

        for p in players[8:12]:
            self.cursor.execute("INSERT INTO GrandPrixParticipation (grandprix_id, player_id, grandprix_result) VALUES (?, ?, ?)", (starter_ids[2], p[0], None))

        for p in players[12:16]:
            self.cursor.execute("INSERT INTO GrandPrixParticipation (grandprix_id, player_id, grandprix_result) VALUES (?, ?, ?)", (starter_ids[3], p[0], None))

        self.connection.commit()

    def update_tournament(self, t_id, date: str, p_count: int, ttype_id: str):
        self.cursor.execute("UPDATE Tournament SET date = ?, player_count = ?, tournament_type_id = ? WHERE tournament_id = ?", (date, p_count, ttype_id, t_id))
        self.connection.commit()

    def read_tournament_types(self) -> list[tuple]:
        self.cursor.execute("SELECT * FROM TournamentType;")
        return self.cursor.fetchall()
    
    def read_tournament_type(self, t_id: str) -> str:
        self.cursor.execute("SELECT tournament_type_id FROM Tournament WHERE tournament_id = ?;", [t_id])
        return self.cursor.fetchone()[0]

    def add_tournament_type(self, def_continuers: int, num_grandprix: int, longer_style: bool):
        self.cursor.execute(
            "INSERT INTO TournamentType (tournament_type_id, def_continuers, num_grandprix, longer_style) VALUES (?, ?, ?, ?)",
            (create_uuid(), def_continuers, num_grandprix, longer_style)
        )
        self.connection.commit()

    def read_tournament_players(self, t_id: str) -> list[tuple]:
        self.cursor.execute("""
            SELECT p.player_id, p.forename, p.surname, p.age
            FROM TournamentParticipation tp
            JOIN Player p ON tp.player_id = p.player_id
            WHERE tp.tournament_id = ?;
        """, [t_id])
        return self.cursor.fetchall()
    
    def read_tournament(self, t_id: str) -> tuple:
        self.cursor.execute("SELECT * FROM Tournament WHERE tournament_id = ?;", [t_id])
        return self.cursor.fetchone()
    
    def add_player_to_tournament(self, t_id: str, p_id: str):
        self.cursor.execute("INSERT INTO TournamentParticipation (tournament_id, player_id, tournament_result) VALUES (?, ?, ?)", (t_id, p_id, None))
        self.connection.commit()

    def remove_player_from_tournament(self, t_id: str, p_id: str):
        self.cursor.execute("DELETE FROM TournamentParticipation WHERE tournament_id = ? AND player_id = ?;", [t_id, p_id])
        self.connection.commit()
    
    def read_grand_prix(self, t_id: str) -> list[tuple]:
        self.cursor.execute("""
            SELECT grandprix_id, round, inverse, bracket, continuers
            FROM GrandPrix
            WHERE tournament_id = ?
            ORDER BY round, bracket
        """, [t_id])
        return self.cursor.fetchall()
    
    def read_grand_prix_players(self, gp_id: str) -> list[tuple]:
        self.cursor.execute("SELECT * FROM Player WHERE player_id IN (SELECT player_id FROM GrandPrixParticipation WHERE grandprix_id = ?)", [gp_id])
        return self.cursor.fetchall()
    
    def create_race(self, gp_id: str, c_id: str, players: list[tuple]):
        r_id = create_uuid()
        self.cursor.execute("INSERT INTO Race (race_id, grandprix_id, circuit_id) VALUES (?, ?, ?)", (r_id, gp_id, c_id))
        for p in players:
            self.cursor.execute("INSERT INTO RaceParticipation (race_id, player_id, race_result) VALUES (?, ?, ?)", (r_id, p[0], p[1]))
        self.connection.commit()

    def get_race_count_in_gp(self, gp_id: str) -> int:
        self.cursor.execute("SELECT COUNT(*) FROM Race WHERE grandprix_id = ?", (gp_id,))
        return self.cursor.fetchone()[0]
    
    def get_player_count_in_gp(self, gp_id: str) -> int:
        self.cursor.execute("SELECT COUNT(*) FROM GrandPrixParticipation WHERE grandprix_id = ?", (gp_id,))
        return self.cursor.fetchone()[0]
    
    def get_current_round(self, t_id: str):
        self.cursor.execute("""
            SELECT grandprix_id, round
            FROM GrandPrix
            WHERE tournament_id = ?
            AND round IS NOT NULL
        """, [t_id])
        gps = self.cursor.fetchall()

        current_rounds = []
        for gp_id, round_num in gps:
            self.cursor.execute("SELECT COUNT(*) FROM Race WHERE grandprix_id = ?", (gp_id,))
            race_count = self.cursor.fetchone()[0]

            if race_count < 4:
                current_rounds.append(round_num)
                continue

            self.cursor.execute("""
                SELECT COUNT(*) 
                FROM GrandPrixParticipation
                WHERE grandprix_id = ? AND grandprix_result IS NULL
            """, (gp_id,))
            unfilled = self.cursor.fetchone()[0]

            if unfilled > 0:
                current_rounds.append(round_num)

        if current_rounds:
            return min(current_rounds)
        else:
            return "Final"
    
    def t_from_gp(self, gp_id: str) -> str:
        self.cursor.execute("SELECT tournament_id FROM GrandPrix WHERE grandprix_id = ?", (gp_id,))
        return self.cursor.fetchone()[0]
    
    def find_winners_for_gp(self, gp_id: str) -> list[tuple]:
        self.cursor.execute("""
                SELECT continuers
                FROM GrandPrix
                WHERE grandprix_id = ?
            """, (gp_id,))
        limit = self.cursor.fetchone()[0]
        if limit is None: return self.calculate_tournament_winner(gp_id)

        self.cursor.execute("""
            SELECT player_id, grandprix_result
            FROM GrandPrixParticipation
            WHERE grandprix_id = ?
            ORDER BY grandprix_result ASC
            LIMIT ?
        """, (gp_id, limit))

        return self.cursor.fetchall()
    
    def find_next_gp_id(self, gp_id: str) -> str:
        self.cursor.execute("SELECT bracket FROM GrandPrix WHERE grandprix_id = ?", (gp_id,))
        bracket = self.cursor.fetchone()[0]
        if bracket is None: return "Tournament finished"
        newbracket = (bracket + 1) // 2

        self.cursor.execute("""
            SELECT round
            FROM GrandPrix
            WHERE tournament_id = (SELECT tournament_id FROM GrandPrix WHERE grandprix_id = ?)
        """, [gp_id])
        rounds = self.cursor.fetchall()
        rounds2 = [r[0] for r in rounds if r[0] != None]
        maxround = max(rounds2)

        self.cursor.execute("""
            SELECT round
            FROM GrandPrix
            WHERE grandprix_id = ? AND tournament_id = (SELECT tournament_id FROM GrandPrix WHERE grandprix_id = ?)
        """, [gp_id, gp_id])
        current_round = self.cursor.fetchone()[0]

        if current_round == maxround:
            self.cursor.execute("""
                SELECT grandprix_id
                FROM GrandPrix
                WHERE tournament_id = (SELECT tournament_id FROM GrandPrix WHERE grandprix_id = ?)
                AND (round IS NULL AND bracket IS NULL AND inverse IS NULL)
            """, (gp_id,))
            return self.cursor.fetchone()[0]
        else:
            self.cursor.execute("""
                SELECT grandprix_id
                FROM GrandPrix
                WHERE tournament_id = (SELECT tournament_id FROM GrandPrix WHERE grandprix_id = ?)
                AND round = (SELECT round FROM GrandPrix WHERE grandprix_id = ?) + 1
                AND inverse = (SELECT inverse FROM GrandPrix WHERE grandprix_id = ?)
                AND bracket = ?
            """, (gp_id, gp_id, gp_id, newbracket))
            return self.cursor.fetchone()[0]
    
    def add_winners_to_gp(self, players: list[tuple], gp_id: str):
        for p in players:
            self.cursor.execute("INSERT INTO GrandPrixParticipation (grandprix_id, player_id, grandprix_result) VALUES (?, ?, ?)", (gp_id, p[0], None))
        self.connection.commit()

    def calculate_tournament_winner(self, gp_id: str) -> tuple:
        self.cursor.execute("""
            SELECT player_id, grandprix_result
            FROM GrandPrixParticipation
            WHERE grandprix_id = ?
            ORDER BY grandprix_result ASC
            LIMIT 1
        """, (gp_id,))
        w_id = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT * FROM Player WHERE player_id = ?", (w_id,))
        return self.cursor.fetchone()
    
    def read_tournament_winner(self, t_id: str) -> tuple:
        self.cursor.execute("SELECT * FROM Player WHERE player_id = (SELECT player_id from TournamentParticipation WHERE tournament_id = ? AND tournament_result = 1);", [t_id])
        return self.cursor.fetchone()
    
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
    
    # def _insert_circuit(self, circuit_name: str):
    #     self.cursor.execute("INSERT INTO Circuit (circuit_id, circuit_name) VALUES (?, ?)", (create_uuid(), circuit_name))
    #     self.connection.commit()

    # def _insert_circuits(self, circuit_names: list[str]):
    #     values = [(create_uuid(), name) for name in circuit_names]
    #     self.cursor.executemany("INSERT INTO Circuit (circuit_id, circuit_name) VALUES (?, ?)", values)
    #     self.connection.commit()
    
    # def _remove_circuits(self, circuit_id: str):
    #     self.cursor.execute("DELETE FROM Circuit WHERE circuit_id = ?", (circuit_id,))
    #     self.connection.commit()

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


db = Database()
db.connect()

# print(db.find_winners_for_next_gp("id1"))
# print(1, db.find_next_gp_id("id1"))
# print(2, db.find_next_gp_id("id2"))
# print(3, db.find_next_gp_id("id3"))
# print(4, db.find_next_gp_id("id4"))
# print(5, db.find_next_gp_id("id5"))
# print(6, db.find_next_gp_id("id6"))
# print(7, db.find_next_gp_id("id7"))

# top_players = db.find_winners_for_next_gp("id1")
# new_gp_id = db.find_next_gp_id("id1")
# db.add_winners_to_gp(top_players, new_gp_id)
db.calculate_tournament_winner("id1")

db.close()