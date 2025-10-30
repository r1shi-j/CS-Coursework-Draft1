import sqlite3
import uuid
from datetime import datetime

# function to generate UUID
def create_uuid() -> str:
    return str(uuid.uuid4())

class Database:
    # setting up connection
    def __init__(self, path="tournament.db"):
        self.connection = sqlite3.connect(path)
        self.connection.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.connection.cursor()

    # creating all the tables if they dont exist
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

    # reads all tournament data
    def read_tournament_data(self) -> list[tuple]:
        self.cursor.execute("SELECT * FROM Tournament;")
        return self.cursor.fetchall()

    # bubble sort on tournaments
    def sort_tournaments(self, options: tuple[str, str]) -> list[tuple]:
        # internal function to convert string dates to date objects so can compare them
        def compare_dates(lhs, rhs, sign) -> bool:
            lhs_date = datetime.strptime(lhs, "%d/%m/%y")
            rhs_date = datetime.strptime(rhs, "%d/%m/%y")

            if sign == ">":
                return lhs_date > rhs_date
            elif sign == "<":
                return lhs_date < rhs_date
        
        # function to sort a list by date
        # takes the order, and the lower and upper bounds of the indexes in the list to sort
        def sort_by_date(o, lb, ub):
            # classic bubble sort to sort the dates
            swapped = True
            while swapped == True:
                swapped = False
                for i in range(lb, ub):
                    curr = t[i][1]
                    next = t[i+1][1]
                    # storings the dates for the current and next tournaments in curr and next
            
                    if o == "ASC":
                        # comparing the dates to see if the current is larger then next
                        # if so then swaps
                        if compare_dates(curr, next, ">"):
                            temp = t[i]
                            t[i] = t[i+1]
                            t[i+1] = temp
                            swapped = True
                    elif o == "DESC":
                        if compare_dates(curr, next, "<"):
                            temp = t[i]
                            t[i] = t[i+1]
                            t[i+1] = temp
                            swapped = True

        # reading all tournaments, the list to sort
        t = self.read_tournament_data()

        # if the field to sort is winner
        if options[0] == "Winner":
            # counting all the times there is no winner, and for each time moving the tournament to the end of the list
            counter = 0
            for i in range(len(t)-1):
                try:
                    curr = self.read_tournament_winner(t[i][0])[1]
                except:
                    temp = t[i]
                    t.remove(t[i])
                    t.append(temp)
                    counter += 1

            # classic bubble sort to sort the tournaments by tournament name
            swapped = True
            while swapped == True:
                swapped = False
                # range is only for the tournaments with winners
                for i in range(len(t)-1-counter):
                    curr = self.read_tournament_winner(t[i][0])[1]
                    next = self.read_tournament_winner(t[i+1][0])[1]
            
                    if options[1] == "ASC":
                        if curr > next:
                            temp = t[i]
                            t[i] = t[i+1]
                            t[i+1] = temp
                            swapped = True
                    elif options[1] == "DESC":
                        if curr < next:
                            temp = t[i]
                            t[i] = t[i+1]
                            t[i+1] = temp
                            swapped = True
            
            # sort by date for the rest of the tournaments with no winner
            sort_by_date("ASC", len(t)-counter, len(t)-1)

        # else if the field to sort is date, sort by date
        elif options[0] == "Date":
            sort_by_date(options[1], 0, len(t)-1)
        
        return t
    
    # creates a new tournament with the specified data
    def create_tournament(self, t_id: str, date: str, p_count: int, ttype_id: str):
        self.cursor.execute("INSERT INTO Tournament (tournament_id, date, player_count, tournament_type_id) VALUES (?, ?, ?, ?)", (t_id, date, p_count, ttype_id))
        self.connection.commit()
    
    # creating the grand prixs for a new tournament and adding the respective players to them
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

        for p in players[0:4]: self.add_player_to_gp(starter_ids[0], p[0], None)
        for p in players[4:8]: self.add_player_to_gp(starter_ids[1], p[0], None)
        for p in players[8:12]: self.add_player_to_gp(starter_ids[2], p[0], None)
        for p in players[12:16]: self.add_player_to_gp(starter_ids[3], p[0], None)

    # adds a player to a grand prix
    def add_player_to_gp(self, gp_id: str, p_id: str, res: int):
        self.cursor.execute("INSERT INTO GrandPrixParticipation (grandprix_id, player_id, grandprix_result) VALUES (?, ?, ?)", (gp_id, p_id, res))
        self.connection.commit()

    # updates a tournament with the changes
    def update_tournament(self, t_id, date: str, p_count: int, ttype_id: str):
        self.cursor.execute("UPDATE Tournament SET date = ?, player_count = ?, tournament_type_id = ? WHERE tournament_id = ?", (date, p_count, ttype_id, t_id))
        self.connection.commit()

    # reading all the tournament types
    def read_tournament_types(self) -> list[tuple]:
        self.cursor.execute("SELECT * FROM TournamentType;")
        return self.cursor.fetchall()
    
    # reading the tournament type id for a specific tournament
    def read_tournament_type(self, t_id: str) -> str:
        self.cursor.execute("SELECT tournament_type_id FROM Tournament WHERE tournament_id = ?;", [t_id])
        return self.cursor.fetchone()[0]

    # creating a new tournament type
    def add_tournament_type(self, def_continuers: int, num_grandprix: int, longer_style: bool):
        self.cursor.execute(
            "INSERT INTO TournamentType (tournament_type_id, def_continuers, num_grandprix, longer_style) VALUES (?, ?, ?, ?)",
            (create_uuid(), def_continuers, num_grandprix, longer_style)
        )
        self.connection.commit()

    # reading all the players in a tournament
    def read_tournament_players(self, t_id: str) -> list[tuple]:
        self.cursor.execute("""
            SELECT p.player_id, p.forename, p.surname, p.age
            FROM TournamentParticipation tp
            JOIN Player p ON tp.player_id = p.player_id
            WHERE tp.tournament_id = ?;
        """, [t_id])
        return self.cursor.fetchall()

    # reading a specific tournament
    def read_tournament(self, t_id: str) -> tuple:
        self.cursor.execute("SELECT * FROM Tournament WHERE tournament_id = ?;", [t_id])
        return self.cursor.fetchone()
    
    # adding a player to a tournament
    def add_player_to_tournament(self, t_id: str, p_id: str):
        self.cursor.execute("INSERT INTO TournamentParticipation (tournament_id, player_id, tournament_result) VALUES (?, ?, ?)", (t_id, p_id, None))
        self.connection.commit()

    # removing a player from a tournament
    def remove_player_from_tournament(self, t_id: str, p_id: str):
        self.cursor.execute("DELETE FROM TournamentParticipation WHERE tournament_id = ? AND player_id = ?;", [t_id, p_id])
        self.connection.commit()

    # reading all grand prixs in a specific tournament
    def read_grand_prix(self, t_id: str) -> list[tuple]:
        self.cursor.execute("""
            SELECT grandprix_id, round, inverse, bracket, continuers
            FROM GrandPrix
            WHERE tournament_id = ?
            ORDER BY round, bracket
        """, [t_id])
        return self.cursor.fetchall()
    
    # reading all players in a grand prix
    def read_grand_prix_players(self, gp_id: str) -> list[tuple]:
        self.cursor.execute("SELECT * FROM Player WHERE player_id IN (SELECT player_id FROM GrandPrixParticipation WHERE grandprix_id = ?)", [gp_id])
        return self.cursor.fetchall()
    
    # creating a race and adding all the players to it
    def create_race(self, gp_id: str, c_id: str, players: list[tuple]):
        r_id = create_uuid()
        self.cursor.execute("INSERT INTO Race (race_id, grandprix_id, circuit_id) VALUES (?, ?, ?)", (r_id, gp_id, c_id))
        for p in players:
            self.cursor.execute("INSERT INTO RaceParticipation (race_id, player_id, race_result) VALUES (?, ?, ?)", (r_id, p[0], p[1]))
        self.connection.commit()

    # getting the number of races in a grand prix
    def get_race_count_in_gp(self, gp_id: str) -> int:
        self.cursor.execute("SELECT COUNT(*) FROM Race WHERE grandprix_id = ?", (gp_id,))
        return self.cursor.fetchone()[0]
    
    # getting the number of players in a grand prix
    def get_player_count_in_gp(self, gp_id: str) -> int:
        self.cursor.execute("SELECT COUNT(*) FROM GrandPrixParticipation WHERE grandprix_id = ?", (gp_id,))
        return self.cursor.fetchone()[0]
    
    # getting the current round in a tournament
    def get_current_round(self, t_id: str):
        # first fetching all gp id and round in a tournament
        self.cursor.execute("""
            SELECT grandprix_id, round
            FROM GrandPrix
            WHERE tournament_id = ?
            AND round IS NOT NULL
        """, [t_id])
        gps = self.cursor.fetchall()

        # if any grand prix not finished, then adding the round number to list
        current_rounds = []
        for gp_id, round_num in gps:
            race_count = self.get_race_count_in_gp(gp_id)

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

        # if at least one grand prix not finished, then return the smallest round number for this grand prix
        # otherwise return final
        if current_rounds:
            return min(current_rounds)
        else:
            return "Final"
    
    # gets the number of players that are eliminated
    def get_players_count_eliminated(self, t_id: str) -> int:
        # fetching all grand prix ids for specific tournament
        self.cursor.execute("""
            SELECT grandprix_id
            FROM GrandPrix
            WHERE tournament_id = ?
        """, (t_id,))
        
        gp_ids = self.cursor.fetchall()
        players = set()

        # for each grand prix in the tournament
        for gp in gp_ids:
            # if the grand prix is finished
            if self.get_player_count_in_gp(gp[0]) == 4 and self.get_race_count_in_gp(gp[0]) == 4:
                # add the losers to the set
                losers = self.find_losers_for_gp(gp[0])
                players.update([x for x in losers])

        # return the number of people in the set
        return len(players)
    
    # finds the winners for a grand prix
    def find_winners_for_gp(self, gp_id: str) -> list[tuple]:
        # selects the continuers property for grand prix
        self.cursor.execute("""
            SELECT continuers
            FROM GrandPrix
            WHERE grandprix_id = ?
        """, (gp_id,))
        limit = self.cursor.fetchone()[0]
        # if this is None then this is the final grand prix so only one winner, therefore calculate the winner
        if limit is None: return self.calculate_tournament_winner(gp_id)

        # return the top n people in the grand prix where n is found above
        self.cursor.execute("""
            SELECT player_id, grandprix_result
            FROM GrandPrixParticipation
            WHERE grandprix_id = ?
            ORDER BY grandprix_result ASC
            LIMIT ?
        """, (gp_id, limit))

        return self.cursor.fetchall()
    
    # finds the losers for a grand prix
    def find_losers_for_gp(self, gp_id: str) -> list[tuple]:
        # fetching all player ids in a grand prix
        # fetching all winners in a grand prix
        self.cursor.execute("""
            SELECT player_id
            FROM GrandPrixParticipation
            WHERE grandprix_id = ?
        """, (gp_id,))
        player = self.cursor.fetchall()
        players = set([x[0] for x in player])
        winner = self.find_winners_for_gp(gp_id)
        winners = set([x[0] for x in winner])

        # finding the players that didn't win so are the losers
        losers = players - winners
        return losers
    
    # finding the grand prix id for next round
    def find_next_gp_id(self, gp_id: str) -> str:
        # selecting the current bracket and finding the next one
        self.cursor.execute("SELECT bracket FROM GrandPrix WHERE grandprix_id = ?", (gp_id,))
        bracket = self.cursor.fetchone()[0]
        if bracket is None: return "Tournament finished"
        newbracket = (bracket + 1) // 2

        # fetching the round of all grand prix in a tournament
        self.cursor.execute("""
            SELECT round
            FROM GrandPrix
            WHERE tournament_id = (SELECT tournament_id FROM GrandPrix WHERE grandprix_id = ?)
        """, [gp_id])
        round = self.cursor.fetchall()
        rounds = [r[0] for r in round if r[0] != None]
        # finding the maximum round
        maxround = max(rounds)

        # fetching the round for current grand prix
        self.cursor.execute("""
            SELECT round
            FROM GrandPrix
            WHERE grandprix_id = ? AND tournament_id = (SELECT tournament_id FROM GrandPrix WHERE grandprix_id = ?)
        """, [gp_id, gp_id])
        current_round = self.cursor.fetchone()[0]

        # if this is the last round
        if current_round == maxround:
            # return the grand prix id of the final
            self.cursor.execute("""
                SELECT grandprix_id
                FROM GrandPrix
                WHERE tournament_id = (SELECT tournament_id FROM GrandPrix WHERE grandprix_id = ?)
                AND (round IS NULL AND bracket IS NULL AND inverse IS NULL)
            """, (gp_id,))
            return self.cursor.fetchone()[0]
        else:
            # return the grand prix id of the next grand prix by increasing the round
            self.cursor.execute("""
                SELECT grandprix_id
                FROM GrandPrix
                WHERE tournament_id = (SELECT tournament_id FROM GrandPrix WHERE grandprix_id = ?)
                AND round = (SELECT round FROM GrandPrix WHERE grandprix_id = ?) + 1
                AND inverse = (SELECT inverse FROM GrandPrix WHERE grandprix_id = ?)
                AND bracket = ?
            """, (gp_id, gp_id, gp_id, newbracket))
            return self.cursor.fetchone()[0]
    
    # adding the winners to the next gp
    def add_winners_to_gp(self, players: list[tuple], gp_id: str):
        for p in players: self.add_player_to_gp(gp_id, p[0], None)

    # finding the tournament winner from the final grand prix id
    def calculate_tournament_winner(self, gp_id: str) -> tuple:
        # finding the player with highest grand prix result in the final grand prix
        self.cursor.execute("""
            SELECT player_id, grandprix_result
            FROM GrandPrixParticipation
            WHERE grandprix_id = ?
            ORDER BY grandprix_result ASC
            LIMIT 1
        """, (gp_id,))
        w_id = self.cursor.fetchone()[0]

        # returing the player with that id
        self.cursor.execute("SELECT * FROM Player WHERE player_id = ?", (w_id,))
        return self.cursor.fetchone()
    
    # finding the tournament winner from a tournament id
    def read_tournament_winner(self, t_id: str) -> tuple:
        self.cursor.execute("SELECT * FROM Player WHERE player_id = (SELECT player_id from TournamentParticipation WHERE tournament_id = ? AND tournament_result = 1);", [t_id])
        return self.cursor.fetchone()
    
    # reading all player data
    def read_player_data(self) -> list[tuple]:
        self.cursor.execute("SELECT * FROM Player;")
        return self.cursor.fetchall()

    # searching players with a query
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
    
    # creating a player with details
    def add_player(self, forename: str, surname: str, age: int):
        self.cursor.execute("INSERT INTO Player (player_id, forename, surname, age) VALUES (?, ?, ?, ?)", (create_uuid(), forename, surname, age))
        self.connection.commit()

    # updating a player
    def update_player(self, player_id: str, forename: str, surname: str, age: int):
        self.cursor.execute("UPDATE Player SET forename=?, surname=?, age=? WHERE player_id=?", (forename, surname, age, player_id))
        self.connection.commit()

    # deleting a player
    def delete_player(self, player_id: str):
        self.cursor.execute("DELETE FROM Player WHERE player_id = ?", (player_id,))
        self.connection.commit()

    # reading all circuits
    def read_circuit_data(self) -> list[tuple]:
        self.cursor.execute("SELECT * FROM Circuit;")
        return self.cursor.fetchall()

    # searching circuits with a query
    # def search_circuits(self, search_term: str) -> list[tuple]:
    #     query = """
    #         SELECT * FROM Circuit
    #         WHERE circuit_name LIKE ?
    #     """
    #     like_term = f"%{search_term}%"
    #     params = [like_term]

    #     self.cursor.execute(query, params)
    #     return self.cursor.fetchall()

    # linear search on circuits
    def search_circuits(self, query: str) -> list[tuple]:
        c = self.read_circuit_data()
        res = []
        for i in c:
            if query in i[1].lower():
                res.append(i)
        return res
    
    # closing the database
    def close(self):
        self.connection.close()

# db = Database()
# db.connect()
# db.close()