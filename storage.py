import os
import sqlite3
import uuid
import hashlib
from datetime import datetime
# os needed to check if db file exists
# sqlite3 for database
# uuid to generate unique identifiers
# hashlib to encode password as a hash
# datetime to convert string dates when sorting dates
import tkinter # used for type hint in insert_gp_results

# function to generate a UUID
def create_uuid() -> str:
    return str(uuid.uuid4())

# Prefilled data: standard circuits, tournament type, demo players, tournaments

# array of all the standard circuits
PAPER_CIRCUITS = ["Mario Kart Stadium", "Water Park", "Sweet Sweet Canyon", "Thwomp Ruins", "Mario Circuit", "Toad Harbor", "Twisted Mansion", "Shy Guy Falls", "Sunshine Airport", "Dolphin Shoals", "Electrodrome", "Mount Wario", "Cloudtop Cruise", "Bone-Dry Dunes", "Bowser's Castle", "Rainbow Road", "Moo Moo Meadows", "GBA Mario Circuit", "Cheep Cheep Beach", "Toad's Turnpike", "Dry Dry Desert", "Donut Plains 3", "Royal Raceway", "DK Jungle", "Wario Stadium", "Sherbet Land", "Music Park", "Yoshi Valley", "Tick-Tock Clock", "Piranha Plant Slide", "Grumble Volcano", "N64 Rainbow Road", "Yoshi Circuit", "Excitebike Arena", "Dragon Driftway", "Mute City", "Wario's Goldmine", "SNES Rainbow Road", "Ice Ice Outpost", "Hyrule Circuit", "Baby Park", "Cheese Land", "Wild Woods", "Animal Crossing", "Neo Bowser City", "Ribbon Road", "Super Bell Subway", "Big Blue"]

# array of all demo names
PAPER_PLAYERS = ["James Smith 24", "Olivia Johnson 19", "Liam Williams 28", "Emma Jones 22", "Ali Gheldi 12", "Ava Davis 17", "Robert Oakling 30", "Sophie Wlid 21", "Mason Moore 26", "Pete Strauss 58", "Ryan Parker 23", "Mia Thomas 29", "Lucas Jackson 16", "Charlotte White 27", "Ethan Harris 20", "Amelia Martin 24", "Jacob Thompson 22", "Tegan Jade 23", "Michael Martinez 30", "Evelyn Robinson 25"]

class Database:
    # MARK: - Initialisation
    # setting up connection
    def __init__(self, filename:str="database.db"):
        try:
            if os.path.isfile(filename):
                self.connection = sqlite3.connect(filename)
                self.connection.execute("PRAGMA foreign_keys = ON;")
                self.cursor = self.connection.cursor()
            else:
                raise FileNotFoundError
        except Exception as e:
            print("Database not found: ", e, type(e))

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

        # inserting demo data if new database
        self.insert_standard_circuits()
        self.insert_demo_players()
        self.insert_standard_tournament_type()

        # saving changes
        self.connection.commit()
    
    # function to insert all standard circuits
    def insert_standard_circuits(self):
        # getting number of circuits
        self.cursor.execute("SELECT COUNT(*) FROM Circuit")
        circuit_count = self.cursor.fetchone()[0]

        # if no circuits exist then add them
        if circuit_count == 0:
            print("adding standard circuits")
            self.cursor.executemany("INSERT INTO Circuit (circuit_id, circuit_name) VALUES (?, ?)", [(create_uuid(), name) for name in PAPER_CIRCUITS])

    # function to insert the standard tournament type
    def insert_standard_tournament_type(self):
        # getting number of tournament types
        self.cursor.execute("SELECT COUNT(*) FROM TournamentType")
        ttype_count = self.cursor.fetchone()[0]

        # if no tournament types exist then add one
        if ttype_count == 0:
            print("adding standard tournament type")
            self.cursor.execute("INSERT INTO TournamentType (tournament_type_id, def_continuers, num_grandprix, longer_style) VALUES (?, ?, ?, ?)", (create_uuid(), 2, 4, False))

    # function to insert all demo players
    def insert_demo_players(self):
        # getting number of players
        self.cursor.execute("SELECT COUNT(*) FROM Player")
        player_count = self.cursor.fetchone()[0]

        # if no players exist then add them
        if player_count == 0:
            print("adding demo players")
            self.cursor.executemany("INSERT INTO Player (player_id, forename, surname, age) VALUES (?, ?, ?, ?)", [(create_uuid(), p.split(" ")[0], p.split(" ")[1], int(p.split(" ")[2])) for p in PAPER_PLAYERS])

    # closing the database
    def close(self):
        self.connection.close()

    # MARK: - Tournaments

    # reads all tournament data
    def read_tournament_data(self) -> list[tuple[str, str, int, str]]:
        self.cursor.execute("SELECT * FROM Tournament;")
        return self.cursor.fetchall()
    
    # bubble sort on tournaments
    def sort_tournaments(self, options: tuple[str, str]) -> list[tuple[str, str, int, str]]:
        # reading all tournaments, the list to sort
        t = self.read_tournament_data()

        # internal function to compare 2 string dates
        def compare_dates(lhs: str, rhs: str, sign: str) -> bool:
            # trying converting the string to datetime objects
            try:
                lhs_date = datetime.strptime(lhs, "%d/%m/%y")
                rhs_date = datetime.strptime(rhs, "%d/%m/%y")
            except (ValueError, TypeError):
                # if the date is invalid for some reason then just quickly exit by returning false
                return False
            # comparing the dates based on function input
            if sign == ">": return lhs_date > rhs_date
            elif sign == "<": return lhs_date < rhs_date
            return False
        
        # recursive quicksort function
        # data: the list of tuples to sort
        # key_func: a function that extracts the value to compare (e.g., date or winner name)
        def quick_sort(data: list[tuple[str, str, int, str]], key_func) -> list[tuple[str, str, int, str]]:
            # base case: A list of 0 or 1 elements is already sorted
            if len(data) <= 1:
                return data
            
            # defining the pivot to be the middle element (where the element is a tournament object)
            # pivot_val is the tournament winner name if order by name otherwise the tournament date if no winner or order by date
            pivot = data[len(data) // 2]
            pivot_val = key_func(pivot)

            # empty arrays for the splits
            left = []
            middle = []
            right = []

            # partitioning loop
            # for each item in the data
            for item in data:
                # getting the item to be sorted
                val = key_func(item)
                
                # if sort option is date
                if options[0] == "Date":
                    # date comparison
                    is_less = compare_dates(val, pivot_val, "<")
                    is_greater = compare_dates(val, pivot_val, ">")
                else:
                    # winner name comparison
                    is_less = val < pivot_val
                    is_greater = val > pivot_val

                # append to appropriate sub-list
                if is_less:
                    left.append(item)
                elif is_greater:
                    right.append(item)
                else:
                    middle.append(item) # equal to pivot

            # recursive step: sort left and right, then combine
            return quick_sort(left, key_func) + middle + quick_sort(right, key_func)

        # if the field to sort is date
        if options[0] == "Date":
            # sorting the list
            sorted_list = quick_sort(t, lambda x: x[1])
            
            # quick_sort naturally sorts ascending so reverse if DESC is required
            if options[1] == "DESC":
                sorted_list.reverse()

            return sorted_list
        
        else:
            # empty arrays for list of tournaments with winners and without winners (incomplete tournaments)
            with_winners = []
            without_winners = []
            # partitioning with winners v no winners
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

            # sorting the winners by name
            # the closure takes a tournament object and gets the id and then finds the player name, and so sorting by winner name
            sorted_winners = quick_sort(with_winners, lambda x: self.read_tournament_winner(x[0])[1])

            # Sort the incomplete tournaments by Date (always ASC by default convention)
            sorted_losers = quick_sort(without_winners, lambda x: x[1])

            # reverse winners if DESC required
            if options[1] == "DESC":
                sorted_winners.reverse()

            # combine arrays: with winners first, then incomplete tournaments
            return sorted_winners + sorted_losers
    
    # creates a new tournament with the specified data
    def create_tournament(self, t_id: str, date: str, p_count: int, ttype_id: str):
        self.cursor.execute("INSERT INTO Tournament (tournament_id, date, player_count, tournament_type_id) VALUES (?, ?, ?, ?)", (t_id, date, p_count, ttype_id))
        self.connection.commit()
    
    # creating the grand prixs for a new tournament and adding the respective players to them
    def create_gps_for_tournament(self, t_id: str, players: list[tuple[str, str, str, int]]):
        starter_ids = [create_uuid(), create_uuid(), create_uuid(), create_uuid()]
        # creating the new grand prixs for all the different brackets
        self.cursor.execute("INSERT INTO GrandPrix (grandprix_id, tournament_id, round, inverse, bracket, continuers) VALUES (?, ?, ?, ?, ?, ?)", (starter_ids[0], t_id, 1, False, 1, 2))
        self.cursor.execute("INSERT INTO GrandPrix (grandprix_id, tournament_id, round, inverse, bracket, continuers) VALUES (?, ?, ?, ?, ?, ?)", (starter_ids[1], t_id, 1, False, 2, 2))
        self.cursor.execute("INSERT INTO GrandPrix (grandprix_id, tournament_id, round, inverse, bracket, continuers) VALUES (?, ?, ?, ?, ?, ?)", (starter_ids[2], t_id, 1, True, 1, 2))
        self.cursor.execute("INSERT INTO GrandPrix (grandprix_id, tournament_id, round, inverse, bracket, continuers) VALUES (?, ?, ?, ?, ?, ?)", (starter_ids[3], t_id, 1, True, 2, 2))
        self.cursor.execute("INSERT INTO GrandPrix (grandprix_id, tournament_id, round, inverse, bracket, continuers) VALUES (?, ?, ?, ?, ?, ?)", (create_uuid(), t_id, 2, False, 1, 2))
        self.cursor.execute("INSERT INTO GrandPrix (grandprix_id, tournament_id, round, inverse, bracket, continuers) VALUES (?, ?, ?, ?, ?, ?)", (create_uuid(), t_id, 2, True, 1, 2))
        self.cursor.execute("INSERT INTO GrandPrix (grandprix_id, tournament_id, round, inverse, bracket, continuers) VALUES (?, ?, ?, ?, ?, ?)", (create_uuid(), t_id, None, None, None, None))
        self.connection.commit()

        # adding the respective players to their respective grand prix (new code using 2D array)

        # 2D array of players, each array has 4 players, and 4 arrays
        # each array of 4 players for each Grand Prix
        # creates an array for each 4 players [[player1, player2, player3, player4], [player5, player6, player7, player8]...]
        player_groups = [players[i:i + 4] for i in range(0, len(players), 4)]
        # for each index, array in player_groups
        for i, group in enumerate(player_groups):
            # for each player in the small array
            for p in group:
                # add the player to the grand prix using the starter_ids subscript i which is the group index (0-3)
                self.add_player_to_gp(starter_ids[i], p[0], None)

    # adds a player to a grand prix
    def add_player_to_gp(self, gp_id: str, p_id: str, res: int | None):
        self.cursor.execute("INSERT INTO GrandPrixParticipation (grandprix_id, player_id, grandprix_result) VALUES (?, ?, ?)", (gp_id, p_id, res))
        self.connection.commit()

    # updates a tournament with the changes
    def update_tournament(self, t_id: str, date: str, p_count: int, ttype_id: str):
        self.cursor.execute("UPDATE Tournament SET date = ?, player_count = ?, tournament_type_id = ? WHERE tournament_id = ?", (date, p_count, ttype_id, t_id))
        self.connection.commit()

    # reading all the tournament types
    def read_tournament_types(self) -> list[tuple[str, int, int, bool]]:
        self.cursor.execute("SELECT * FROM TournamentType;")
        return self.cursor.fetchall()
    
    # reading the tournament type id for a specific tournament
    def read_tournament_type(self, t_id: str) -> str:
        self.cursor.execute("SELECT tournament_type_id FROM Tournament WHERE tournament_id = ?;", (t_id,))
        # trying to find it
        try:
            return self.cursor.fetchone()[0]
        except (TypeError, AttributeError):
            # if no value then can't subscript
            print(f"Error: Tournament ID {t_id} not found.")
            return ""

    # creating a new tournament type
    def create_tournament_type(self, def_continuers: int, num_grandprix: int, longer_style: bool):
        self.cursor.execute("INSERT INTO TournamentType (tournament_type_id, def_continuers, num_grandprix, longer_style) VALUES (?, ?, ?, ?)", (create_uuid(), def_continuers, num_grandprix, longer_style))
        self.connection.commit()

    # reading all the accounts in a tournament
    def read_tournament_accounts(self, t_id: str) -> list[tuple[str, str, str, str]]:
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
            # no errors so returning true
            return True
        except sqlite3.IntegrityError:
            # if didn't work because username isn't unique to tournament, return false
            return False
    
    # deleting an account from a tournament
    def delete_account(self, account_id: str) -> bool:
        # try except to check if account can be safely deleted
        try:
            self.cursor.execute("DELETE FROM Account WHERE account_id = ?", (account_id,))
            self.connection.commit()
            # if account deleted with no errors then return true
            return True
        except sqlite3.IntegrityError:
            # else return false
            return False

    # trying to login to a tournament
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
    def read_tournament_players(self, t_id: str) -> list[tuple[str, str, str, int]]:
        self.cursor.execute("""
            SELECT p.player_id, p.forename, p.surname, p.age
            FROM TournamentParticipation tp
            JOIN Player p ON tp.player_id = p.player_id
            WHERE tp.tournament_id = ?;
        """, (t_id,))
        return self.cursor.fetchall()

    # reading a specific tournament
    def read_tournament(self, t_id: str) -> tuple[str, str, int, str]:
        self.cursor.execute("SELECT * FROM Tournament WHERE tournament_id = ?;", (t_id,))
        return self.cursor.fetchone()
    
    # adding a player to a tournament
    def add_player_to_tournament(self, t_id: str, p_id: str):
        self.cursor.execute("INSERT INTO TournamentParticipation (tournament_id, player_id, tournament_result) VALUES (?, ?, ?)", (t_id, p_id, None))
        self.connection.commit()

    # removing a player from a tournament
    def remove_player_from_tournament(self, t_id: str, p_id: str) -> bool:
        # try except to check if player can be safely deleted from tournament participation
        try:
            self.cursor.execute("DELETE FROM TournamentParticipation WHERE tournament_id = ? AND player_id = ?;", (t_id, p_id))
            self.connection.commit()
            # if entry deleted with no errors then return true
            return True
        except sqlite3.IntegrityError:
            # else return false
            return False

    # reading all grand prixs in a specific tournament
    def read_grand_prix(self, t_id: str) -> list[tuple[str, int, bool, int, int]]:
        self.cursor.execute("""
            SELECT grandprix_id, round, inverse, bracket, continuers
            FROM GrandPrix
            WHERE tournament_id = ?
            ORDER BY round, bracket
        """, (t_id,))
        return self.cursor.fetchall()
    
    # reading all players in a grand prix
    def read_grand_prix_players(self, gp_id: str) -> list[tuple[str, str, str, int]]:
        self.cursor.execute("SELECT * FROM Player WHERE player_id IN (SELECT player_id FROM GrandPrixParticipation WHERE grandprix_id = ?)", (gp_id,))
        return self.cursor.fetchall()
    
    # creating a race and adding all the players to it
    def create_race(self, gp_id: str, c_id: str, player_results: list[tuple[str, int]]):
        # creating new id
        r_id = create_uuid()
        # creating the Race entry
        self.cursor.execute("INSERT INTO Race (race_id, grandprix_id, circuit_id) VALUES (?, ?, ?)", (r_id, gp_id, c_id))
        for p in player_results:
            # adding the players to the race via RaceParticipation
            self.cursor.execute("INSERT INTO RaceParticipation (race_id, player_id, race_result) VALUES (?, ?, ?)", (r_id, p[0], p[1]))
        self.connection.commit()

    # getting the number of races currently in a grand prix
    def get_race_count_in_gp(self, gp_id: str) -> int:
        self.cursor.execute("SELECT COUNT(*) FROM Race WHERE grandprix_id = ?", (gp_id,))
        return self.cursor.fetchone()[0]
    
    # getting the number of players currently in a grand prix
    def get_player_count_in_gp(self, gp_id: str) -> int:
        self.cursor.execute("SELECT COUNT(*) FROM GrandPrixParticipation WHERE grandprix_id = ?", (gp_id,))
        return self.cursor.fetchone()[0]
    
    # getting the number of players currently in a tournament
    def get_player_count_in_tournament(self, t_id: str) -> int:
        self.cursor.execute("SELECT player_count FROM Tournament WHERE tournament_id = ?", (t_id,))
        # trying to find it
        try:
            return self.cursor.fetchone()[0]
        except (TypeError, AttributeError):
            # if no value then can't subscript 
            print(f"Error: Tournament ID {t_id} not found.")
            return -1
    
    # getting the current round in a tournament
    def get_current_round(self, t_id: str) -> int:
        # first fetching all gp_id and round in a tournament
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
                # if grand prix is not finished then add the round of the grand prix to the array
                current_rounds.append(round_num)
                continue
            
            # fetching the number of players added to the grand prix
            self.cursor.execute("""
                SELECT COUNT(*) 
                FROM GrandPrixParticipation
                WHERE grandprix_id = ? AND grandprix_result IS NULL
            """, (gp_id,))
            unfilled = self.cursor.fetchone()[0]

            if unfilled > 0:
                # if grand prix has more than 0 players then add the round of the grand prix to the array
                current_rounds.append(round_num)

        # if there is at elast 1 grand prix not finished
        if current_rounds:
            # returning the smallest round number of grand prix that isn't finished
            return min(current_rounds)
        else:
            # othewise returning the final round
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

        # players as an empty set
        players: set[str] = set()

        # for each grand prix in the tournament
        for gp in gp_ids:
            # if the grand prix is finished
            if self.get_player_count_in_gp(gp[0]) == 4 and self.get_race_count_in_gp(gp[0]) == 4:
                # add the losers to the set
                losers = self.find_losers_for_gp(gp[0], False)
                players.update(losers)

        # players now contains a list of all players that have been eliminated from each bracket
        # but as it is a set, it removes duplicates and so is a list of all people who have been eliminated
        # return the eliminated count
        return len(players)
    
    # finds the winners for a grand prix
    def find_winners_for_gp(self, gp_id: str, internal: bool) -> list[tuple[str, int]] | tuple[str, str, str, int]:
        # selects the continuers property for grand prix
        self.cursor.execute("""
            SELECT continuers
            FROM GrandPrix
            WHERE grandprix_id = ?
        """, (gp_id,))
        # trying to find it
        try:
            limit = self.cursor.fetchone()[0]
        except (TypeError, AttributeError):
            # if no value then can't subscript 
            print(f"Error: Grandprix ID {gp_id} not found.")
            return []
        
        # if this is none then this is final gp, calculate winner if this is not called internally eg so from tournaments file
        if limit is None and not internal:
            w = self.calculate_tournament_winner(gp_id)
            if w: return w
            else: return []
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
    def find_losers_for_gp(self, gp_id: str, internal: bool) -> list[str]:
        # fetching all player ids in a grand prix
        self.cursor.execute("""
            SELECT player_id
            FROM GrandPrixParticipation
            WHERE grandprix_id = ?
        """, (gp_id,))
        player = self.cursor.fetchall()
        # set of all player ids in a grand prix
        players = set([x[0] for x in player])

        # fetching all winners in a grand prix
        winner = self.find_winners_for_gp(gp_id, internal)
        # if only 1 winner because final gp, it returns a tuple, so convert this to an array of tuples to match other data
        if type(winner) == tuple: winner2 = [winner]
        elif type(winner) == list: winner2 = winner
        # set of all player ids for winners
        winners = set([x[0] for x in winner2])

        # finding losers by the player ids that are not winners
        losers = players - winners
        return list(losers)
    
    # finding the grand prix id for next round
    def find_next_gp_id(self, gp_id: str, t_id: str) -> str:
        # selecting the current bracket and finding the next one
        self.cursor.execute("SELECT bracket FROM GrandPrix WHERE grandprix_id = ?", (gp_id,))
        # trying to find it
        try:
            bracket = self.cursor.fetchone()[0]
        except (TypeError, AttributeError):
            # if no value then can't subscript 
            print(f"Error: Grandprix ID {gp_id} not found.")
            return ""
        
        # if the current bracket is None then this is the final grand prix so return tournament finished
        if bracket is None: return "Tournament finished"
        # calculate the new bracket
        newbracket = (bracket + 1) // 2

        # fetching the round of all grand prix in a tournament
        self.cursor.execute("SELECT round FROM GrandPrix WHERE tournament_id = ?", (t_id,))
        round = self.cursor.fetchall()
        # removing the final round
        rounds = [r[0] for r in round if r[0] != None]
        # finding the maximum round in the tournament
        maxround = max(rounds)

        # fetching the round for current grand prix
        self.cursor.execute("SELECT round FROM GrandPrix WHERE grandprix_id = ? AND tournament_id = ?", (gp_id, t_id))
        # trying to find it
        try:
            current_round = self.cursor.fetchone()[0]
        except (TypeError, AttributeError):
            # if no value then can't subscript 
            print(f"Error: Tournament ID {t_id} or Grandprix ID {gp_id} not found.")
            return ""

        # if this is the last round
        if current_round == maxround:
            # return the grand prix id of the final
            self.cursor.execute("""
                SELECT grandprix_id
                FROM GrandPrix
                WHERE tournament_id = ?
                AND (round IS NULL AND bracket IS NULL AND inverse IS NULL)
            """, (t_id,))
            # trying to find it
            try:
                return self.cursor.fetchone()[0]
            except (TypeError, AttributeError):
                # if no value then can't subscript 
                print(f"Error: Grandprix ID {gp_id} not found.")
                return ""
        else:
            # return the grand prix id of the next grand prix by increasing the round
            self.cursor.execute("""
                SELECT grandprix_id
                FROM GrandPrix
                WHERE tournament_id = ?
                AND round = (SELECT round FROM GrandPrix WHERE grandprix_id = ?) + 1
                AND inverse = (SELECT inverse FROM GrandPrix WHERE grandprix_id = ?)
                AND bracket = ?
            """, (t_id, gp_id, gp_id, newbracket))
            # trying to find it
            try:
                return self.cursor.fetchone()[0]
            except (TypeError, AttributeError):
                # if no value then can't subscript 
                print(f"Error: Tournament ID {t_id} or Grandprix ID {gp_id} not found.")
                return ""
    
    # inserting the grand prix results for players after grand prix finished
    def insert_gp_results(self, gp_id: str, results: list[tuple[str, tkinter.StringVar]]):
        for p_id, var in results:
            self.cursor.execute("UPDATE GrandPrixParticipation SET grandprix_result = ? WHERE grandprix_id = ? AND player_id = ?", (int(var.get()), gp_id, p_id))
        self.connection.commit()
        
    # adding the winners to the next grand prix
    def add_winners_to_gp(self, players: list[tuple[str, str, str, int]], gp_id: str):
        for p in players: self.add_player_to_gp(gp_id, p[0], None)

    # finding the tournament winner from the final grand prix id
    def calculate_tournament_winner(self, gp_id: str) -> tuple[str, str, str, int] | None:
        # finding the player with highest grand prix result in the final grand prix
        self.cursor.execute("""
            SELECT player_id, grandprix_result
            FROM GrandPrixParticipation
            WHERE grandprix_id = ?
            ORDER BY grandprix_result ASC
            LIMIT 1
        """, (gp_id,))
        # trying to find it
        try:
            p_id = self.cursor.fetchone()[0]
        except (TypeError, AttributeError):
            # if no value then can't subscript 
            print(f"Error: Grandprix ID {gp_id} not found.")
            return None

        # returing the whole player object with the player_id found above
        self.cursor.execute("SELECT * FROM Player WHERE player_id = ?", (p_id,))
        return self.cursor.fetchone()
    
    # finding the tournament winner from a tournament id
    def read_tournament_winner(self, t_id: str) -> tuple[str, str, str, int]:
        self.cursor.execute("SELECT * FROM Player WHERE player_id = (SELECT player_id from TournamentParticipation WHERE tournament_id = ? AND tournament_result = 1);", (t_id,))
        return self.cursor.fetchone()
    
    # reading the tournament result for a player
    def get_tournament_result(self, t_id: str, p_id: str) -> int:
        self.cursor.execute("SELECT tournament_result FROM TournamentParticipation WHERE tournament_id = ? AND player_id = ?", (t_id, p_id))
        # trying to find it
        try:
            return self.cursor.fetchone()[0]
        except (TypeError, AttributeError):
            # if no value then can't subscript 
            print(f"Error: Tournament ID {t_id} or Player ID {p_id} not found.")
            return -1

    # function to calculate what position eveyone came and then update it in TournamentParticipation
    def set_tournament_results(self, t_id: str):
        # inner function to update results for a specific round number so can gather all players eliminated in that round and rank for results
        def update_for_round(round: int | None, base: int):
            # selecting all the grand prix ids for that round
            self.cursor.execute("SELECT grandprix_id FROM GrandPrix WHERE tournament_id = ? AND round is ?", (t_id, round))
            round_ids = self.cursor.fetchall()
            # turning list of tuples into array of gp_ids
            gp_ids = [x[0] for x in round_ids]
            round_results = []

            # for each grand prix in this round
            for gp_id in gp_ids:
                # if this is final grand prix then adding all players to round_results
                if round == None:
                    self.cursor.execute("SELECT * FROM GrandPrixParticipation WHERE grandprix_id = ?", (gp_id,))
                    round_results = self.cursor.fetchall()
                else:
                    # otherwise adding the players which were eliminated to round_results
                    # fetching the players eliminated for this grand prix
                    bottom2 = self.find_losers_for_gp(gp_id, True)
                    for p in bottom2:
                        # fetching the GrandPrixParticipation object and adding to round_results
                        self.cursor.execute("SELECT * FROM GrandPrixParticipation WHERE player_id = ? AND grandprix_id = ?", (p, gp_id))
                        full_player = self.cursor.fetchone()
                        round_results.append(full_player)

            # sorting the round_results by result
            # sorted_round_results is a list of all GrandPrixParticipation sorted by grandprix_result
            # so it is a sorted array of players results who were eliminated in this round
            sorted_round_results = sorted(round_results, key=lambda x: x[2])
            # creating results dictionary with key result and value empty array
            results: dict[int, list[tuple[str, str, int]]] = {x: [] for x in range(base, base + len(sorted_round_results))}

            # recursive function to add the player to the to the dictionary for key result
            def add_data(position: int, offset: int) -> tuple[int, int]:
                # adding the result
                results[base+offset].append(sorted_round_results[position])
                # if the next result has same position then apply recursion
                if position+1 < len(sorted_round_results) and sorted_round_results[position+1][2] == sorted_round_results[position][2]:
                    pos, off = add_data(position+1, offset)
                    return pos, off+1
                return position+1, offset+1

            # setting start variables to 0
            position = 0
            offset = 0
            # upperbound is calculated by the number of unique results
            # first make array of all results, then encase in a set to remove duplicate result numbers, then apply len to get number of unique result numbers
            upperbound = len(set([x[2] for x in sorted_round_results]))
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
    def read_player_data(self) -> list[tuple[str, str, str, int]]:
        self.cursor.execute("SELECT * FROM Player;")
        return self.cursor.fetchall()
    
    # linear search on players with a query
    def search_players(self, search_term: str) -> list[tuple[str, str, str, int]]:
        # fetching all players into a 2d array
        all_players = self.read_player_data()
        
        # if no query, return everyone
        if not search_term.strip():
            return all_players

        # prepare search terms, split into lowercase words
        terms = search_term.lower().split()
        results: list[tuple[str, str, str, int]] = []

        # iterate through each player
        for player in all_players:
            # player structure: (id, forename, surname, age)
            # creating a searchable string for this row
            searchable_text = (player[1] + " " + player[2] + " " + str(player[3])).lower()
            
            # initially set match to true
            match = True
            # for each term
            # we want all terms to be in the searchable_text
            for term in terms:
                # if the term is not in the searchable_text then break loop and so this player will not be in the results
                if term not in searchable_text:
                    # no match so set match to false
                    match = False
                    break
            
            # if match hasn't been set to false, means that all terms were in the searchable_text (so related to the player) therefore add player to results
            if match:
                results.append(player)
                
        return results
    
    # creating a player with details
    def create_player(self, forename: str, surname: str, age: int):
        self.cursor.execute("INSERT INTO Player (player_id, forename, surname, age) VALUES (?, ?, ?, ?)", (create_uuid(), forename, surname, age))
        self.connection.commit()

    # updating a player
    def update_player(self, player_id: str, forename: str, surname: str, age: int):
        self.cursor.execute("UPDATE Player SET forename = ?, surname = ?, age = ? WHERE player_id = ?", (forename, surname, age, player_id))
        self.connection.commit()

    # deleting a player
    def delete_player(self, player_id: str) -> bool:
        # try except to handle sql errors
        try:
            self.cursor.execute("DELETE FROM Player WHERE player_id = ?", (player_id,))
            self.connection.commit()
            # if player deleted without any errors then return true
            return True
        except sqlite3.IntegrityError:
            # else return false
            return False
    
    # getting the number of players in database
    def get_player_count(self) -> int:
        self.cursor.execute("SELECT COUNT(*) FROM Player;")
        return self.cursor.fetchone()[0]

    # MARK: - Circuits

    # reading all circuits
    def read_circuit_data(self) -> list[tuple[str, str]]:
        self.cursor.execute("SELECT * FROM Circuit;")
        return self.cursor.fetchall()

    # linear search on circuits with a query
    def search_circuits(self, search_term: str) -> list[tuple[str, str]]:
        # fetching all circuits into a 2d array
        all_circuits = self.read_circuit_data()
        
        # if no query, return everyone
        if not search_term.strip():
            return all_circuits

        # prepare search terms, split into lowercase words
        terms = search_term.lower().split()
        results: list[tuple[str, str]] = []

        # iterate through each player
        for circuit in all_circuits:
            # circuit structure: (id, name)
            # creating a searchable string for this row
            searchable_text = circuit[1].lower()
            
            # initially set match to true
            match = True
            # for each term
            # we want all terms to be in the searchable_text
            for term in terms:
                # if the term is not in the searchable_text then break loop and so this circuit will not be in the results
                if term not in searchable_text:
                    # no match so set match to false
                    match = False
                    break
            
            # if match hasn't been set to false, means that all terms were in the searchable_text (so related to the circuit) therefore add circuit to results
            if match:
                results.append(circuit)
                
        return results

    # MARK: - Statistics

    # getting top winners stats
    def get_top_winners_stats(self) -> list[tuple[str, int]]:
        # fetching the full name concatenated along with the number of tournaments come first in
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
    def get_rivalry_stats(self) -> dict[str, list[tuple[str, int]]]:
        # fetches the first name and surname in a single string, the sum and number of tournament results
        query = """
        SELECT p.forename || ' ' || p.surname, SUM(tp.tournament_result) as sum, COUNT(tp.tournament_result) as count
        FROM TournamentParticipation tp
        JOIN Player p ON tp.player_id = p.player_id
        GROUP BY p.player_id
        ORDER BY sum ASC
        """
        self.cursor.execute(query)
        res = self.cursor.fetchall()

        # calculating the average result for each player
        avg_res: list[tuple[str, float]] = []
        for row in res:
            # trying to divide the sum of results by the number of results (number of individual data so the number of tournaments with results)
            try:
                average = row[1] / row[2]
                avg_res.append((row[0], average))
            except (ZeroDivisionError, TypeError):
                # if either is 0 or Null/None then continue
                # this will be if the player hasn't finished tournament yet
                continue
        # sorting the list by average result highest to lowest
        sorted_res = sorted(avg_res, key=lambda x: x[1])
        # taking the top 5 players with the best average result
        top_players = [p[0] for p in sorted_res[:5]]
        data: dict[str, list[tuple[str, int]]] = {}
        
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
    def get_circuit_usage_stats(self) -> list[tuple[str, int]]:
        # getting the name of circuit and number of races that use that circuit
        # ordering from highest to lowest (DESC)
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
    def get_circuit_winners(self, circuit_id: str) -> list[tuple[str, int]]:
        # getting the first and surname as a single string, and the number of wins the player has on that circuit
        # ordering by number of wins highest to lowest
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
    def get_player_circuit_results(self, circuit_id: str, player_id: str) -> list[tuple[int, int]]:
        # getting the race result and the number of times the player has achieved that result on that circuit
        # ordering by result ascending (1st place to 12th place)
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
    def get_player_history(self, player_id: str) -> list[tuple[str, int]]:
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
        # returning as an array of raw results [2,4,6,3,7,3] instead of list of tuples
        self.cursor.execute("SELECT race_result FROM RaceParticipation WHERE player_id = ?", (p_id,))
        return [row[0] for row in self.cursor.fetchall()]

#* temporary manual database operations
def temp_operations():
    print("database opened")
    db = Database()
    db.connect()
    
    # tempoary function to create an account for all tournaments with username "username" and password "password"
    # def reset_all_accounts():
    #     db.cursor.execute("DELETE FROM Account")
    #     db.connection.commit()

    #     db.cursor.execute("SELECT tournament_id FROM Tournament;")
    #     tournament_ids = db.cursor.fetchall()
    #     for t_id in tournament_ids:
    #         hashed = hashlib.sha256("password".encode()).hexdigest()
    #         db.cursor.execute("INSERT INTO Account (account_id, tournament_id, username, password_hash) VALUES (?, ?, ?, ?)", (create_uuid(), t_id[0], "username", hashed))
    #     db.connection.commit()

    db.close()
    print("database closed")

# if this file is run directly then run temp_operations function
if __name__ == "__main__":
    temp_operations()