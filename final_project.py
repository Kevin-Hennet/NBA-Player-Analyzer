
import csv
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
"""
Player class, manages the individual player data
(info, stats, normal stats, and score)
It also updates stats, returns set stats, adds new stats
calculates the score for each player for each situation based of the weights 
and its normalized data, and finally it adds all the player information into a dictionary 
"""
class Player: 
    def __init__(self, name: str, team: str, position: str, age: int, games_played: int, min_played: int, stats: dict):
        # all the attributes needed to create the individual player object 
        self.name = name 
        self.team = team 
        self.position = position
        self.age = age 
        self.games_played = games_played
        self.min_played = min_played
        self.stats = stats
        self.norm_stats = {}
        self.score = 0.0
        self.id = f"{name}_{team}"

    def get_stat(self, stat_name):
        # method is used to get the value of a specific stat 
        return self.stats[stat_name]
    
    def set_stat(self, stat_name, value):
        # method is used to set a new stat or update a previous stat 
        self.stats[stat_name] = value

    def calculate_score(self, weights):
        """
        method is used to calculate a score for each player based on the weights in place for each situation.
        This is done by looping through all the stats in the weights and then multiplying the stat weight by the 
        normalized value of the stat.  
        """
        total = 0
        for stat in weights:
            total += self.norm_stats[stat] * weights[stat]
        self.score = total 
        return self.score
    def to_dict(self):
         # This method just makes the dictionary containing all the information of the player
         return {
             "ID": self.id,
             "Player": self.name,
             "Age": self.age, 
             "Team": self.team,
             "Pos": self.position,
             "G": self.games_played,
             "MP": self.min_played,
             "Stats": self.stats,
             "Norm Stats": self.norm_stats,
             "Score": self.score
         }
    """
    def __repr__(self): 
        (used to check if the read_csv_as_dict function worked properly)
        return f"Player({self.name}, {self.team}, {self.position}, Score: {self.score})"
    """
"""
The RankingSystem Class unlike the player class manages the entire dataset instead of just one player 
It takes a list of Player objects from the player class and handles all the ranking aspects of the project. 
The methods add player objects, filters the list, normalizes all the statistics, applies the weights, ranks the players, and 
finally puts the ranked players into a list 
"""
class RankingSystem:
    def __init__(self, min_games_played: int = 20, min_minutes_played: int = 15, weights: dict = None):
        # all the attributes from the ranking class
        self.players = [] # list of player objects
        # thresholds to filter the list of player objects
        self.min_games_played  = min_games_played
        self.min_minutes_played = min_minutes_played
        #normalized data mins and maxes
        self.norm_min = {}
        self.norm_max = {}
        # weights for each situation 
        self.weights = weights
    def add_player(self, player_or_list):
        # method can be used to add individual player objects and full lists of player objects
        if isinstance(player_or_list, list):
            for player in player_or_list:
                self.add_player(player)
        else:
            # filtering aspect of the add_player method to remove the benchwarmers (players with low outliers)
            if player_or_list.games_played >= self.min_games_played and player_or_list.min_played >= self.min_minutes_played: 
                self.players.append(player_or_list)
    def normalize_value(self, value, min_value, max_value):
        # this method runs the normalize formula that can be used for all the stats
        if max_value == min_value: 
            return 0
        return (value - min_value) / (max_value - min_value)
    def calculate_min_max(self):
        """
        This method is used to apply the min max formula to all the values 
        for each stat that is included for each player, This is done by looping through all the keys in stats to 
        find the normal min and normal max for each stat. Then the players list is looped through to apply the normalize
        statistic formula to each stat 

        """
        if not self.players:
            return 
        
        stats_keys = self.players[0].stats.keys()
        for key in stats_keys:
            all_values = [player.stats[key] for player in self.players]
            self.norm_min[key] = min(all_values)
            self.norm_max[key] = max(all_values)
        
        for player in self.players:
            player.norm_stats = {}
            for key in stats_keys:
                min_val = self.norm_min[key]
                max_val = self.norm_max[key]
                if max_val == min_val:
                    player.norm_stats[key] = 0 
                else:
                    player.norm_stats[key] = self.normalize_value(player.stats[key], min_val, max_val)

    def apply_weights(self):
        """
        This method applies the weights to all the players in the players list.
        It first checks if the weights are even valid by makingf sure they are also in the normal stats 
        dictionary. Tt then will calculate the score for each player after the weights are applied
        through the player objects in the player list

        """
        if not self.weights:
            return 
        for player in self.players:
            valid_weights = {k:v for k,v in self.weights.items() if k in player.norm_stats} 
            player.score = player.calculate_score(valid_weights)
    def rank_player(self, top_n = 10):
        # This method actually ranks the players based of the score for each situation 
        # (reverse order)

        ranked_players = sorted(self.players, key=lambda player: player.score, reverse=True)
        
        return ranked_players[:top_n]
    
    def normalize_and_rank(self):
        # this method combines multiple methods to quickly normalize and rank players
        self.calculate_min_max() # normalize stats method
        self.apply_weights() # weights applied to find the score
        return self.rank_player() # finally based of the score the players are ranked
    def rank_by_situation(self, weights, top_n=10):
        """
        This method ranks the players based of the score from different situations instead 
        of just the standard overall ranking weights
        The system updates the active weights that the score was calulcated with based
        of the chosen situation
        """
        self.weights = weights
        self.normalize_and_rank()
        return self.rank_player(top_n)
    def to_dict_list(self, top_n= None):
        """
        This method is used to transfer the players from a dictionary 
        into a list with dictionaries inside of them
        """
        if top_n:
            players_to_export = self.rank_player(top_n)
        else: 
            players_to_export = self.players
        dict_list = [player.to_dict() for player in players_to_export]
        return dict_list

        

def read_csv_as_dicts(filename):
    """
    This function is what get's the data from the orginal player CSV
    It also initalizes a list of player objects in the format
    that the player class attributes were
    it later will be transfered into the ranking_system class for filtering
    and ranking
    """
    players = []
    try: 
        with open(filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try: 
                    name = row.get("Player")
                    team = row.get("Team", "")
                    position = row.get("Pos", "")
                    age = int(row.get("Age", 0))
                    games_played = int(row.get("G", 0))
                    min_played = float(row.get("MP", 0))
                    non_stat_fields = {"Player", "Team", "Pos", "Age", "G", "MP"}    
                    stats = {}
                    for key, value in row.items():
                        if key not in non_stat_fields:
                            try:
                                stats[key] = float(value) if value != "" else 0
                            except ValueError:
                                stats[key] = value
                    player = Player(name, team, position, age, games_played, min_played, stats)
                    players.append(player)
                except Exception as e:
                    print(f"Skipping row due to error: {e}")
    except FileNotFoundError:
        print(f"File {filename} not found")
    except IOError as e: 
        print(f"Error opening file {filename}: {e}")
            
    return players

# these dictionaries below are some of the set stat weights for specific situations
# I decided on the weighted values based on which stats are important for each situation 
overall = {
    "PTS":0.4,
    "AST": 0.2,
    "TRB": 0.1,
    "STL": 0.2,
    "BLK": 0.2,
    "TOV": -0.1
}
best_clutch_player = {
    "PTS": 0.2, 
    "FG%": 0.3,
    "eFG%": 0.3,
    "FT": 0.2,
    "TOV": -0.2

}

best_defensive_player = {
    "DRB": 0.2,
    "STL": 0.4,
    "BLK": 0.4
}

best_playmaker = {
    "AST": 0.5, 
    "TOV": -0.25,
    "ORB": 0.1,
    "PF": -0.05,
    "eFG%": 0.15

}

best_three_point_scorer = {
    "3P": 0.3,
    "3P%": 0.5,
    "3PA": 0.1

}

def create_custom_weights():
    #This function allows the user to create their own unique situation and custom weights
    stats = ["FGA", "FG%", "3P", "3PA", "3P%", "2P", "2PA", "2P%", "eFG%", 
             "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]
    situation_type = input("What type of situation are you measuring? ")
    num_stats = int(input("How many stats do you want to weigh? "))
    weights = {}
    for i in range(num_stats):
        while True: 
            stat = input(f"What is the stat that you want to weigh, make sure that it is in this list: {stats} \n")
            if stat not in stats: 
                print("The stat that you chose was not in the list of stats!")
                continue
            break
        while True:
            try:

                value = float(input("what value do you want to set this stat weight to that is between -1 and 1? "))
                if value > 1 or value < -1:
                    print("The value must be between -1 and 1.")
                    continue
                break
            except ValueError:
                print("Invalid number! Please enter a numeric value.")
        weights[stat] = value
    print(f"Custom weights for {situation_type}: {weights}")
    return weights 


def compare_players(p1, p2, weights, scenario_name="Custom"):
    """
    Compares two players using normalized and weighted stats
    and prints a clear, easy-to-read comparison.
    """

    def calculate_weighted(player):
        results = {}
        total_score = 0

        for stat in weights:
            norm_val = player.norm_stats.get(stat, 0)
            weighted_val = norm_val * weights[stat]

            results[stat] = {
                "Normalized": norm_val,
                "Weighted": weighted_val
            }

            total_score += weighted_val

        player.score = total_score
        return results

    p1_stats = calculate_weighted(p1)
    p2_stats = calculate_weighted(p2)

    print("\n==============================")
    print("Player Comparison")
    print("Scenario:", scenario_name)
    print("==============================")

    for stat in weights:
        p1_norm = p1_stats[stat]["Normalized"]
        p2_norm = p2_stats[stat]["Normalized"]

        p1_weighted = p1_stats[stat]["Weighted"]
        p2_weighted = p2_stats[stat]["Weighted"]

        print("\nStat:", stat)
        print(p1.name, "- Normalized:", round(p1_norm, 3),
              "Weighted:", round(p1_weighted, 3))
        print(p2.name, "- Normalized:", round(p2_norm, 3),
              "Weighted:", round(p2_weighted, 3))
        print("Difference (", p1.name, "-", p2.name, "):",
              round(p1_weighted - p2_weighted, 3))

    print("\nFinal Scores:")
    print(p1.name, "Score:", round(p1.score, 3))
    print(p2.name, "Score:", round(p2.score, 3))

    if p1.score > p2.score:
        print("Better player for this situation:", p1.name)
    elif p2.score > p1.score:
        print("Better player for this situation:", p2.name)
    else:
        print("Both players are equal for this situation.")

    return sorted([p1, p2], key=lambda x: x.score, reverse=True)


def export_rankings_to_csv(players, filename):
    """
    This function exports the sorted players by score into a
    brand new CSV. This will export the full sorted player list
    """
    if not players:
        print("No players to export.")
        return
    stat_keys = list(players[0].stats.keys())
    headers = ["Player", "Team", "Pos", "Age", "G", "MP", "Score"] + stat_keys 
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f: 
            writer = csv.writer(f)
            writer.writerow(headers)

            for p in players:
                row = [
                    p.name,
                    p.team,
                    p.position,
                    p.age, 
                    p.games_played,
                    p.min_played,
                    round(p.score, 4)

                ] + [p.stats[k] for k in stat_keys]

                writer.writerow(row)
    except Exception:
        print(f"Error occurred when opening {filename} to write")
    print(f"Exported full rankings to {filename}") 

def export_top_n_to_csv(players, filename, top_n=20):
    # this function specifically exports the top players into the csv
    sorted_players = sorted(players, key=lambda p: p.score, reverse=True)
    top_players = sorted_players[:top_n]
    export_rankings_to_csv(top_players, filename)


def flatten_player_dicts(player_dicts):
    """
    This function flattens the nested player dictionaries so that plotly
    can use them for plotting. It combines raw stats and normalized stats into 
    one flat dictionary

    """
    flat_list = []
    for p in player_dicts:
        flat = p.copy()
        stats = flat.pop("Stats", {})
        norms = flat.pop("Norm Stats", {})
        flat.update(stats)
        flat.update(norms)
        flat_list.append(flat)
    return flat_list


def plot_top_players(players, title=f"Top Players", scenario_name =""):
    """
    This function is what creates the bar graph showing the top players 
    for each different situation in order. It shows their respective 
    scores after the data was normalized and weighted

    """
    if not players:
        print("No players to plot.")
        return
    dict_players = [p.to_dict() for p in players]
    df = pd.DataFrame(flatten_player_dicts(dict_players))
    if "Player" not in df.columns or "Score" not in df.columns:
        print("Player or Score column missing!")
        return
    if scenario_name:
        title =f"{title} - {scenario_name} Scenario"
    fig = px.bar(
        df,
        x="Player",
        y="Score",
        title=title,
    )
    fig.show()



def plot_player_comparision(p1, p2):
    """
    This function is what creates the radar chart
    to closesly see the differences between two players in
    different areas of basketball skills
    """
    categories = list(p1.norm_stats.keys())

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[p1.norm_stats[c] for c in categories],
        theta=categories,
        fill='toself',
        name=p1.name
    ))
    fig.add_trace(go.Scatterpolar(
        r=[p2.norm_stats[c] for c in categories],
        theta = categories,
        fill='toself',
        name=p2.name
    ))

    fig.update_layout(title="Player Comparision Radar Chart")
    fig.show()

def plot_scatter(players, stat_x, stat_y):
    """
    This function creates the scatterplot that compares players 
    to the relationship between two different stats 

    """
    if not players:
        print("No players to plot.")
        return
    df = pd.DataFrame(flatten_player_dicts([p.to_dict() for p in players]))

    if stat_x not in df.columns or stat_y not in df.columns:
        print(f"Error: {stat_x}  or {stat_y} not in data. Available:", df.columns.tolist())
        return
    fig = px.scatter(
        df,
        x=stat_x,
        y=stat_y,
        hover_name="Player",
        title=f"{stat_x} vs {stat_y}"
    )
    fig.show()


def find_player_by_name(players, query):
    # function loops through the list of players to find the players the players
    # the user could have inputed (case insensitive)
    matches = [p for p in players if query.lower() in p.name.lower()]
    if not matches:
        print(f"No player found matching '{query}'")
        return None
    return matches[0]
def weight_situation():
    # function allows the user to choose the type of situation they want to use to rank players
    print("\nSelect a ranking scenario:")
    print("1. Overall")
    print("2. Clutch")
    print("3. Defensive")
    print("4. Playmaker")
    print("5. Three-point scorer")
    print("6 Custom! Create your own weights and situation")
    try:
        choice = int(input("Enter your choice: "))
    except ValueError:
        print("Invalid input. Defaulting to overall.")
        return overall
    if choice == 1:
        return overall
    elif choice == 2: 
        return best_clutch_player
    elif choice == 3: 
        return best_defensive_player
    elif choice == 4: 
        return best_playmaker
    elif choice == 5: 
        return best_three_point_scorer
    elif choice == 6:
        return create_custom_weights()
    else:
        # default choice is overall weights
        print("Invalid choice. Defaulting to overall weights. ")
        return overall
def list_all_players(players):
    for p in players:
        print(p.name)
"""
 these next few lines set the player, ranking system, player lists, and normalizes
 and ranks all the data each player has. This will be used for the main menu function 
"""
players_list = read_csv_as_dicts("CS final project starter csv - Sheet1.csv")
ranking_system = RankingSystem(min_games_played=20, min_minutes_played=15, weights=overall)
ranking_system.add_player(players_list)
top_players = ranking_system.normalize_and_rank()


def main_menu():
    """
    Essentially the "game_loop" for the project. 
    Utilizes a while loop to allow the user to do many different things
    with the NBA player analyzer. This combines all the functions from earlier to 
    show top overall players, top players for situations, 
    compare two players, export rankings to CSV, see the top players for each situation 
    bar graph, see the radar chart when comparing two players, and see a relationship between 
    players and two stats via scatterplot. There is also the exit option to ensure the program
    doesn't cause an infinite loop 

    """

    while True:
        print("\n--- NBA Player Analyzer Menu ---")
        print("1. Show top overall players")
        print("2. Show top players by situation")
        print("3. Compare two players")
        print("4. Export current rankings to CSV")
        print("5. Visualize top players per situation (bar chart)")
        print("6. Compare two players visually (radar chart)")
        print("7. Visualize stat relationships (scatter plot)")
        print("8. Exit")
        try:
            choice = int(input("Enter your choice (1-8): "))
        except ValueError:
            print("Invalid input. Enter a number between 1 and 8.")
            continue 

        if choice == 1:
            top_n = int(input("How many top players do you want to see? "))
            top = ranking_system.rank_player(top_n)
            for i, player in enumerate(top, 1):
                print(f"{i}. {player.name} - {player.score:.3f}")
        
        elif choice == 2: 
            scenario = weight_situation()
            top_n = int(input("How many top players do you want to see? "))

            top = ranking_system.rank_by_situation(scenario, top_n)
            for i, player in enumerate(top, 1):
                print(f"{i}. {player.name} - {player.score:.3f}")
        
        elif choice == 3:

            list_all_players(ranking_system.players)
            name1 = input("Enter first player's name: ")
            name2 = input("Enter second player's name: ")

            p1 = find_player_by_name(ranking_system.players, name1)
            p2 = find_player_by_name(ranking_system.players, name2)
            if not p1 or not p2:
                print("One or both players not found.")
                continue
            scenario = weight_situation()
            


            top_two = compare_players(p1, p2, scenario, "Custom" )
            print(f"\nComparision ({scenario} weights):")
            print("\nOverall Scores:")
            for p in top_two:
                print(f"{p.name} - {p.score:.3f}")
        elif choice == 4:
            scenario = weight_situation() 
            top_players = ranking_system.rank_by_situation(scenario, top_n=20)
            filename = input("Enter filename for CSV export (e.g. 'Clutch Rankings'): ")
            export_rankings_to_csv(top_players, f"{filename}_Top20.csv")

            all_players = ranking_system.rank_by_situation(scenario, top_n=len(ranking_system.players))
            export_rankings_to_csv(all_players, f"{filename}_Full.csv")
        elif choice == 5: 
            scenario = weight_situation()
            top_n = int(input("How many players do you want to display? "))
            top_players = ranking_system.rank_by_situation(scenario, top_n)
            scenario_name = input("Enter a name for this scenario (e.g 'Defensive'): ")
            plot_top_players(top_players, f"Top {top_n} Players",  scenario_name)
        elif choice == 6:
            list_all_players(ranking_system.players)
            name1 = input("Enter first player's name: ")
            name2 = input("Enter second player's name: ")

            p1 = find_player_by_name(ranking_system.players, name1)
            p2 = find_player_by_name(ranking_system.players, name2)
            if not p1 or not p2:
                print("One or both players not found.")
                continue
            plot_player_comparision(p1, p2)
        elif choice == 7: 
            scenario = weight_situation()
            top_n = int(input("How many players do you want to include? "))
            players_to_plot = ranking_system.rank_by_situation(scenario, top_n)

            print("Available stats:", list(players_to_plot[0].stats.keys()))
            stat_x = input("Enter the stat for X-axis: ")
            stat_y = input("Enter the stat for y-axis: ")
            plot_scatter(players_to_plot, stat_x, stat_y)

        elif choice == 8: 
            print("Exiting menu.")
            break
        else:
            print("Invalid choice. Enter a number between 1 and 8.")

# testing functions above the main menu()
# Test updating a stat
#test_player = ranking_system.players[0]
#print(f"Original PTS: {test_player.get_stat('PTS')}")
#test_player.set_stat('PTS', test_player.get_stat('PTS') + 5)
#print(f"Updated PTS: {test_player.get_stat('PTS')}")
"""
for rank, p in enumerate(ranking_system.to_dict_list(10), 1):
    print(f"{rank}. {p['Player']} - {p['Score']:.3f}")
"""
#more testing 
#export_top_n_to_csv(ranking_system.players, "Top5_testRankings.CSV", top_n=5)
#export_rankings_to_csv(ranking_system.players, "Full Ranking.CSV")
#top10 = ranking_system.to_dict_list(10)
#plot_top_players(top10, "Top 10 Overall Players")
#plot_scatter(ranking_system.to_dict_list(), "PTS", "MP")

main_menu()

         



