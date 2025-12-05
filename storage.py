import sqlite3
import uuid
import hashlib
from datetime import datetime

# function to generate UUID
def create_uuid() -> str:
    return str(uuid.uuid4())

class Database:
    # MARK: - Initialisation
    # setting up connection
    def __init__(self):
        self.connection = sqlite3.connect("tournament.db")
        self.connection.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.connection.cursor()

    # creating all the tables if they don't exist
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

        # getting number of circuits
        self.cursor.execute("SELECT COUNT(*) FROM Circuit")
        circuit_count = self.cursor.fetchone()[0]

        # if no circuits exist then add them
        if circuit_count == 0:
            paper_circuits = ['Mario Kart Stadium', 'Water Park', 'Sweet Sweet Canyon', 'Thwomp Ruins', 'Mario Circuit', 'Toad Harbor', 'Twisted Mansion', 'Shy Guy Falls', 'Sunshine Airport', 'Dolphin Shoals', 'Electrodrome', 'Mount Wario', 'Cloudtop Cruise', 'Bone-Dry Dunes', 'Bowser’s Castle', 'Rainbow Road', 'Moo Moo Meadows', 'GBA Mario Circuit', 'Cheep Cheep Beach', 'Toad’s Turnpike', 'Dry Dry Desert', 'Donut Plains 3', 'Royal Raceway', 'DK Jungle', 'Wario Stadium', 'Sherbet Land', 'Music Park', 'Yoshi Valley', 'Tick-Tock Clock', 'Piranha Plant Slide', 'Grumble Volcano', 'N64 Rainbow Road', 'Yoshi Circuit', 'Excitebike Arena', 'Dragon Driftway', 'Mute City', "Wario's Goldmine", 'SNES Rainbow Road', 'Ice Ice Outpost', 'Hyrule Circuit', 'Baby Park', 'Cheese Land', 'Wild Woods', 'Animal Crossing', 'Neo Bowser City', 'Ribbon Road', 'Super Bell Subway', 'Big Blue']
            print("adding)")
            self.cursor.executemany("INSERT INTO Circuit (circuit_id, circuit_name) VALUES (?, ?)", [(create_uuid(), name) for name in paper_circuits])

        self.connection.commit()

    # MARK: - Tournaments

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
        def sort_by_date(o: str, lb: int, ub: int):
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
            # empty arrays for list of tournaments with winners and without winners (incomplete tournaments)
            with_winners = []
            without_winners = []

            for tournament in t:
                # for each tournament, trying to find the winner
                try:
                    winner = self.read_tournament_winner(tournament[0])
                    if winner:
                        # if there is a winner then added the tournament to with winners array
                        with_winners.append(tournament)
                    else:
                        # if no winner then add to without winners array
                        without_winners.append(tournament)
                except:
                    # if fails then add to without winners array
                    without_winners.append(tournament)

            # merge the 2 arrays together, so the tournaments with no winners are at the end
            t = with_winners + without_winners
            counter = len(without_winners)

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
    #* FIXME: update for different tournament types
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
        self.cursor.execute("SELECT tournament_type_id FROM Tournament WHERE tournament_id = ?;", (t_id,))
        return self.cursor.fetchone()[0]

    # creating a new tournament type
    def create_tournament_type(self, def_continuers: int, num_grandprix: int, longer_style: bool):
        self.cursor.execute("INSERT INTO TournamentType (tournament_type_id, def_continuers, num_grandprix, longer_style) VALUES (?, ?, ?, ?)", (create_uuid(), def_continuers, num_grandprix, longer_style))
        self.connection.commit()

    # reading all the accounts in a tournament
    def read_tournament_accounts(self, t_id: str) -> list[tuple]:
        self.cursor.execute("SELECT * FROM Account WHERE tournament_id = ?;", (t_id,))
        return self.cursor.fetchall()
    
    # adding an account to a tournament
    def create_account(self, t_id: str, username: str, password: str) -> bool:
        # creating the password hash
        hashed = hashlib.sha256(password.encode()).hexdigest()
        try:
            # trying to add the account
            self.cursor.execute("INSERT INTO Account (account_id, tournament_id, username, password_hash) VALUES (?, ?, ?, ?)", (create_uuid(), t_id, username, hashed))
            self.connection.commit()
            # worked to returning true
            return True
        except sqlite3.IntegrityError:
            # if didn't work becase userame isn't unique to tournament, return false
            return False
    
    # deleting an account from a tournament
    def delete_account(self, account_id: str):
        self.cursor.execute("DELETE FROM Account WHERE account_id = ?", (account_id,))
        self.connection.commit()

    # trying to login
    def attempt_login(self, t_id: str, username: str, password: str) -> bool:
        self.cursor.execute("SELECT password_hash FROM Account WHERE tournament_id = ? AND username = ?", (t_id, username))
        hash = self.cursor.fetchone()
        # fetching the saved password hash for the tournament with that account name
        # if no hash then account doesn't exist so return false
        if not hash: return False
        # hashing the password user entered
        hashed = hashlib.sha256(password.encode()).hexdigest()
        # if password hashes match then return true, if not then false
        return True if hashed == hash[0] else False
        
    # reading all the players in a tournament
    def read_tournament_players(self, t_id: str) -> list[tuple]:
        self.cursor.execute("""
            SELECT p.player_id, p.forename, p.surname, p.age
            FROM TournamentParticipation tp
            JOIN Player p ON tp.player_id = p.player_id
            WHERE tp.tournament_id = ?;
        """, (t_id,))
        return self.cursor.fetchall()

    # reading a specific tournament
    def read_tournament(self, t_id: str) -> tuple:
        self.cursor.execute("SELECT * FROM Tournament WHERE tournament_id = ?;", (t_id,))
        return self.cursor.fetchone()
    
    # adding a player to a tournament
    def add_player_to_tournament(self, t_id: str, p_id: str):
        self.cursor.execute("INSERT INTO TournamentParticipation (tournament_id, player_id, tournament_result) VALUES (?, ?, ?)", (t_id, p_id, None))
        self.connection.commit()

    # removing a player from a tournament
    def remove_player_from_tournament(self, t_id: str, p_id: str):
        self.cursor.execute("DELETE FROM TournamentParticipation WHERE tournament_id = ? AND player_id = ?;", (t_id, p_id))
        self.connection.commit()

    # reading all grand prixs in a specific tournament
    def read_grand_prix(self, t_id: str) -> list[tuple]:
        self.cursor.execute("""
            SELECT grandprix_id, round, inverse, bracket, continuers
            FROM GrandPrix
            WHERE tournament_id = ?
            ORDER BY round, bracket
        """, (t_id,))
        return self.cursor.fetchall()
    
    # reading all players in a grand prix
    def read_grand_prix_players(self, gp_id: str) -> list[tuple]:
        self.cursor.execute("SELECT * FROM Player WHERE player_id IN (SELECT player_id FROM GrandPrixParticipation WHERE grandprix_id = ?)", (gp_id,))
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
    
    # getting the number of players in a tournament
    def get_player_count_in_tournament(self, t_id: str) -> int:
        self.cursor.execute("SELECT player_count FROM Tournament WHERE tournament_id = ?", (t_id,))
        return self.cursor.fetchone()[0]
    
    # getting the current round in a tournament
    def get_current_round(self, t_id: str) -> int:
        # first fetching all gp id and round in a tournament
        self.cursor.execute("""
            SELECT grandprix_id, round
            FROM GrandPrix
            WHERE tournament_id = ?
            AND round IS NOT NULL
        """, (t_id,))
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
            return -1
    
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
    def find_winners_for_gp(self, gp_id: str, internal=None) -> list[tuple]:
        # selects the continuers property for grand prix
        self.cursor.execute("""
            SELECT continuers
            FROM GrandPrix
            WHERE grandprix_id = ?
        """, (gp_id,))
        limit = self.cursor.fetchone()[0]
        # if this is none then this is final gp, calculate winner if this is not called internally eg so from tournaments file
        if limit is None and not internal:
            return self.calculate_tournament_winner(gp_id)
        else: limit = 2
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
    def find_losers_for_gp(self, gp_id: str, internal=None) -> list[tuple]:
        # fetching all player ids in a grand prix
        # fetching all winners in a grand prix
        self.cursor.execute("""
            SELECT player_id
            FROM GrandPrixParticipation
            WHERE grandprix_id = ?
        """, (gp_id,))
        player = self.cursor.fetchall()
        players = set([x[0] for x in player])
        winner = self.find_winners_for_gp(gp_id, internal)
        if type(winner) == tuple:
            winner = [winner]
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
        """, (gp_id,))
        round = self.cursor.fetchall()
        rounds = [r[0] for r in round if r[0] != None]
        # finding the maximum round
        maxround = max(rounds)

        # fetching the round for current grand prix
        self.cursor.execute("""
            SELECT round
            FROM GrandPrix
            WHERE grandprix_id = ? AND tournament_id = (SELECT tournament_id FROM GrandPrix WHERE grandprix_id = ?)
        """, (gp_id, gp_id))
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
    
    # inserting the grand prix results for players after grand prix finished
    def insert_gp_results(self, gp_id: str, results: list[tuple]):
        for p_id, var in results:
            self.cursor.execute("UPDATE GrandPrixParticipation SET grandprix_result = ? WHERE grandprix_id = ? AND player_id = ?", (int(var.get()), gp_id, p_id))
        self.connection.commit()
        
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
        self.cursor.execute("SELECT * FROM Player WHERE player_id = (SELECT player_id from TournamentParticipation WHERE tournament_id = ? AND tournament_result = 1);", (t_id,))
        return self.cursor.fetchone()
    
    # reading the tournament result for a player
    def get_tournament_result(self, t_id: str, p_id: str) -> int:
        self.cursor.execute("SELECT tournament_result FROM TournamentParticipation WHERE tournament_id = ? AND player_id = ?", (t_id, p_id))
        return self.cursor.fetchone()[0]

    # function to calculate what position eveyone came and then update it in TournamentParticipation
    def set_tournament_results(self, t_id: str):
        # inner function to update results for a specific round number so can gather all players eliminated in that round and rank for results
        def update_for_round(round: int, base: int):
            # selecting all the grand prix ids for that round
            self.cursor.execute("SELECT grandprix_id FROM GrandPrix WHERE tournament_id = ? AND round is ?", (t_id, round))
            round_ids = self.cursor.fetchall()
            round_results = []

            for id in round_ids:
                # if this is final grand prix then adding all players to round_results
                if round == None:
                    self.cursor.execute("SELECT * FROM GrandPrixParticipation WHERE grandprix_id = ?", (id[0],))
                    round_results = self.cursor.fetchall()
                else:
                    # otherwise adding the players which were eliminated to round_results
                    bottom2 = self.find_losers_for_gp(id[0], True)
                    for p in bottom2:
                        self.cursor.execute("SELECT * FROM GrandPrixParticipation WHERE player_id = ? AND grandprix_id = ?", (p, id[0]))
                        full_player = self.cursor.fetchone()
                        round_results.append(full_player)

            # sorting the results by result
            # creating results dictionary with empty arrays for each results number
            sorted_round_results = sorted(round_results, key=lambda x: x[2])
            results = {k: [] for k in range(base, base + len(sorted_round_results))}

            # recursive function to add the result to the dictionary
            def add_data(position: int, offset: int) -> tuple[int, int]:
                # adding the result
                # if the next result has same position then apply recursion
                results[base+offset].append(sorted_round_results[position])
                if position+1 < len(sorted_round_results) and sorted_round_results[position+1][2] == sorted_round_results[position][2]:
                    pos, off = add_data(position+1, offset)
                    return pos, off+1
                return position+1, offset+1

            # setting start variables to 0
            # upperbound is calculated by the number of unique results
            position = 0
            offset = 0
            upperbound = len(set([c[2] for c in sorted_round_results]))
            # calling the recursive function to add results to the dictionary for each position
            for _ in range(0, upperbound):
                pos, off = add_data(position, offset)
                position = pos
                offset = off

            # updating the tournament result for each player into TournamentParticipation
            for pos in results.items():
                for player in pos[1]:
                    self.cursor.execute("UPDATE TournamentParticipation SET tournament_result = ? WHERE tournament_id = ? AND player_id = ?", (pos[0], t_id, player[1]))
        
        # calling the function for each round number with the starting position
        update_for_round(1, 9)
        update_for_round(2, 5)
        update_for_round(None, 1)

        # saving changes
        self.connection.commit()

    # MARK: - Players

    # reading all player data
    def read_player_data(self) -> list[tuple]:
        self.cursor.execute("SELECT * FROM Player;")
        return self.cursor.fetchall()

    # searching players with a query
    def search_players(self, search_term: str) -> list[tuple]:
        # splitting the query into words
        terms = search_term.split()
        if not terms: return []
        
        # making the query with checks for each word in query
        column_check = "(forename LIKE ? OR surname LIKE ? OR CAST(age AS TEXT) LIKE ?)"
        where_clause = " AND ".join([column_check] * len(terms))
        query = f"SELECT * FROM Player WHERE {where_clause}"

        # creating the input parameters for each search term
        params = []
        for term in terms:
            like_term = f"%{term}%"
            params.extend([like_term, like_term, like_term])

        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    # creating a player with details
    def create_player(self, forename: str, surname: str, age: int):
        self.cursor.execute("INSERT INTO Player (player_id, forename, surname, age) VALUES (?, ?, ?, ?)", (create_uuid(), forename, surname, age))
        self.connection.commit()

    # updating a player
    def update_player(self, player_id: str, forename: str, surname: str, age: int):
        self.cursor.execute("UPDATE Player SET forename=?, surname=?, age=? WHERE player_id=?", (forename, surname, age, player_id))
        self.connection.commit()

    # deleting a player
    def delete_player(self, player_id: str) -> bool:
        try:
            self.cursor.execute("DELETE FROM Player WHERE player_id = ?", (player_id,))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    # getting the number of players in database
    def get_player_count(self) -> int:
        self.cursor.execute("SELECT COUNT(*) FROM Player;")
        return self.cursor.fetchone()[0]

    # MARK: - Circuits

    # reading all circuits
    def read_circuit_data(self) -> list[tuple]:
        self.cursor.execute("SELECT * FROM Circuit;")
        return self.cursor.fetchall()

    # searching circuits with a query
    def search_circuits(self, search_term: str) -> list[tuple]:
        # splitting the query into words
        terms = search_term.split()
        if not terms: return []
        
        # making the query with checks for each word in query
        column_check = "(circuit_name LIKE ?)"
        where_clause = " AND ".join([column_check] * len(terms))
        query = f"SELECT * FROM Circuit WHERE {where_clause}"

        # creating the input parameters for each search term
        params = []
        for term in terms:
            like_term = f"%{term}%"
            params.extend([like_term])

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    #* temporary linear search on circuits
    # def search_circuits(self, query: str) -> list[tuple]:
    #     c = self.read_circuit_data()
    #     res = []
    #     for i in c:
    #         if query in i[1].lower():
    #             res.append(i)
    #     return res

    # MARK: - Statistics

    # getting top winners stats
    def get_top_winners_stats(self) -> list[tuple]:
        # fetches the first name and surname in a single string, and the number of tournament wins
        query = """
        SELECT p.forename || ' ' || p.surname, COUNT(tp.tournament_result) as wins
        FROM TournamentParticipation tp
        JOIN Player p ON tp.player_id = p.player_id
        WHERE tp.tournament_result = 1
        GROUP BY p.player_id
        ORDER BY wins DESC
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    # getting rivalry stats
    def get_rivalry_stats(self) -> dict[str: list[tuple]]:
        # fetches the first name and surname in a single string, and the sum and number of tournament resultes
        query = """
        SELECT p.forename || ' ' || p.surname, SUM(tp.tournament_result) as sum, COUNT(tp.tournament_result) as count
        FROM TournamentParticipation tp
        JOIN Player p ON tp.player_id = p.player_id
        GROUP BY p.player_id
        ORDER BY sum ASC
        """
        self.cursor.execute(query)
        res = self.cursor.fetchall()
        # removing people with no results
        for a in res:
            if a[2] == 0 or a[1] == None:
                res.remove(a)
        # finding the average tournament result for each player and sorting the list
        avg_res = [(x[0], x[1]/x[2]) for x in res]
        sorted_res = sorted(avg_res, key=lambda x: x[1])
        # taking the top 5 players with the best average result
        top_players = [p[0] for p in sorted_res[:5]]
        data = {}
        
        # for each player, fetches their tournament history
        for name in top_players:
            # fetching the date and tournament result for the player
            # only if tournament result is recorded and so not null
            query = """
            SELECT t.date, tp.tournament_result
            FROM TournamentParticipation tp
            JOIN Tournament t ON tp.tournament_id = t.tournament_id
            JOIN Player p ON tp.player_id = p.player_id
            WHERE (p.forename || ' ' || p.surname) = ? AND t.date IS NOT NULL AND tp.tournament_result NOT NULL
            """
            self.cursor.execute(query, (name,))
            # adding the data to the dictionary of players
            data[name] = self.cursor.fetchall() 
        return data

    # getting circuit usage stats
    def get_circuit_usage_stats(self) -> list[tuple]:
        # getting the name of circuit and number of races that use that circuit
        query = """
        SELECT c.circuit_name, COUNT(r.race_id)
        FROM Race r
        JOIN Circuit c ON r.circuit_id = c.circuit_id
        GROUP BY c.circuit_id
        ORDER BY COUNT(r.race_id) DESC
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    # getting circuit winners stats
    def get_circuit_winners(self, circuit_id: str) -> list[tuple]:
        # getting the first and surname as a single string, and the number of wins the player has on that circuit
        query = """
        SELECT p.forename || ' ' || p.surname, COUNT(rp.race_result)
        FROM RaceParticipation rp
        JOIN Race r ON rp.race_id = r.race_id
        JOIN Player p ON rp.player_id = p.player_id
        WHERE r.circuit_id = ? AND rp.race_result = 1
        GROUP BY p.player_id
        ORDER BY COUNT(rp.race_result) DESC
        """
        self.cursor.execute(query, (circuit_id,))
        return self.cursor.fetchall()

    # getting player circuit results
    def get_player_circuit_results(self, circuit_id: str, player_id: str) -> list[tuple]:
        # getting the race result and the number of times the player has achieved that result on that circuit
        query = """
        SELECT rp.race_result, COUNT(rp.race_result)
        FROM RaceParticipation rp
        JOIN Race r ON rp.race_id = r.race_id
        WHERE r.circuit_id = ? AND rp.player_id = ?
        GROUP BY rp.race_result
        ORDER BY rp.race_result ASC
        """
        self.cursor.execute(query, (circuit_id, player_id))
        return self.cursor.fetchall()
    
    # getting player history
    def get_player_history(self, player_id: str) -> list[tuple]:
        # getting the date and tournament result for the player
        query = """
        SELECT t.date, tp.tournament_result
        FROM TournamentParticipation tp
        JOIN Tournament t ON tp.tournament_id = t.tournament_id
        WHERE tp.player_id = ? AND tp.tournament_result IS NOT NULL
        """
        self.cursor.execute(query, (player_id,))
        return self.cursor.fetchall()
    
    # getting race results for a player
    def get_race_results(self, p_id: str) -> list[int]:
        # getting the race results for the player
        self.cursor.execute("SELECT race_result FROM RaceParticipation WHERE player_id = ?", (p_id,))
        return [row[0] for row in self.cursor.fetchall()]
    
    # closing the database
    def close(self):
        self.connection.close()

#* temporary manual database operations
# db = Database()
# db.connect()
# db.close()