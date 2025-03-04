import requests
from os import path
import csv
from tkinter import Tk, Label, Frame, Toplevel, messagebox
from datetime import datetime, timedelta, timezone
import re
import platform
from time import sleep
from os import system
import keyboard

profile_id = None
your_player_name = None 
current_window = None
last_game_id = None  

def debug():
    print('this script runs off of AOE4WORLDs Api')
    print('DEBUGGING\n-------------------------------------')
    api = "https://aoe4world.com/api"
    api2 = 'https://aoe4world.com/api/v0/players/4635035/games'
    response = requests.get(api)
    response2 = requests.get(api2)

    if response.status_code == 200:
        print("DEBUG: API IS LIVE")
    elif response.status_code == 520 or 522:
        print(f"Unable to connect to {api} {response.status_code} [ratelimited]")
    else:
        print(f'error {response.status_code}')
    if response2.status_code == 200:
        print("DEBUG: PlayerID API IS LIVE")
    elif response2.status_code == 520 or 522 :
        print(f"Unable to connect to {api2} {response2.status_code}  [ratelimited")
    else:
        print(f'error {response2.status_code}')
    sleep(2)
    system('cls')

def get_player_id(player_name):
    global profile_id
    if not player_name or player_name.strip() == "":
        return None
    url = f"https://aoe4world.com/api/v0/players/search?query={player_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'players' in data and data['players']:
            profile_id = str(data['players'][0]['profile_id'])
            return profile_id
    return None

def recent_match():
    global profile_id
    if not profile_id:
        return None
    url = f"https://aoe4world.com/api/v0/players/{profile_id}/games/last"
    try:
        response = requests.get(url, timeout=5)  # Add timeout to prevent hanging
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API Error: Status code {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Network error fetching recent match: {e}")
        return None

def parse_time_ago(time_str):
    if not time_str:
        return None
    try:
        return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        pass
    now = datetime.now()
    match = re.match(r"about (\d+) (\w+) ago", time_str.lower())
    if match:
        num, unit = match.groups()
        num = int(num)
        if "hour" in unit:
            return now - timedelta(hours=num)
        elif "day" in unit:
            return now - timedelta(days=num)
        elif "minute" in unit:
            return now - timedelta(minutes=num)
    return None

def determine_team_size(match_data):
    if not match_data or 'teams' not in match_data:
        return "Unknown"
    team_sizes = [len(team) for team in match_data['teams']]
    if len(team_sizes) != 2:
        return "Unknown"
    if all(size == 1 for size in team_sizes):
        return "1v1"
    elif all(size == 2 for size in team_sizes):
        return "2v2"
    elif all(size == 3 for size in team_sizes):
        return "3v3"
    elif all(size == 4 for size in team_sizes):
        return "4v4"
    return "Custom or Unknown"

def load_strategies():
    try:
        with open('matchup_strategies.csv', 'r') as c:
            read = csv.DictReader(c)
            strategies = {}
            for row in read:
                strategies[row['Matchup']] = row
            return strategies
    except FileNotFoundError:
        messagebox.showerror("Error", "matchup_strategies.csv not found. Please ensure it’s in the same directory.")
        return {}
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load strategies: {e}")
        return {}

def create_player_frame(parent, player, team_number, player_number):
    frame = Frame(parent, bg='#3c5f7a', relief='raised', borderwidth=2, padx=8, pady=4)
    
    name = player.get('name', 'Unknown')
    civ = player.get('civilization', 'Unknown').replace('_', ' ').title()
    rating = player.get('rating', 'N/A')

    Label(frame, text=f"Player {player_number} - {name}", fg='#f2f2f2', bg='#3c5f7a', font=('Arial', 10, 'bold')).pack(anchor='w', pady=1)
    Label(frame, text=f"Civilization: {civ}", fg='#f4c430', bg='#3c5f7a', font=('Arial', 8)).pack(anchor='w', pady=1)
    Label(frame, text=f"Rating: {rating}", fg='#4d9de0', bg='#3c5f7a', font=('Arial', 8)).pack(anchor='w', pady=1)
    
    return frame

def find_your_player(teams):
    global profile_id
    for team_idx, team in enumerate(teams):
        for player_idx, player in enumerate(team):
            if str(player.get('profile_id', '')) == str(profile_id):
                return player, team_idx, player_idx
    return None, None, None

def find_opponent(teams, your_team_idx):
    opponent_team_idx = 1 if your_team_idx == 0 else 0
    if teams and len(teams) > opponent_team_idx and teams[opponent_team_idx]:
        return teams[opponent_team_idx][0]
    return None

def toggle_window_visibility():
    global current_window
    if current_window and current_window.winfo_exists():
        if current_window.winfo_viewable():
            current_window.withdraw()
        else:
            current_window.deiconify()

def show_match_info(match_data, window=None):
    global current_window, last_game_id
    if window and window.winfo_exists():
        window.destroy()
    
    root = Toplevel()
    root.overrideredirect(True)
    root.attributes('-topmost', True)

    if platform.system() == 'Windows':
        root.attributes('-alpha', 0.85)
        root.configure(bg='#1f261f')
    else:
        root.configure(bg='systemTransparent')
        root.attributes('-transparentcolor', '#1f261f')

    root.geometry("465x85")
    root.resizable(False, False)

    frame = Frame(root, bg='#1f261f', padx=10, pady=10)
    frame.pack(fill='both', expand=True)

    your_player, your_team_idx, your_player_idx = find_your_player(match_data['teams'])
    if your_player:
        my_civ = your_player['civilization']
        opponent = find_opponent(match_data['teams'], your_team_idx)
        if opponent:
            enemy_civ = opponent['civilization']
            strategies = load_strategies()
            matchup = f'{my_civ} vs {enemy_civ}'
            if matchup in strategies:
                strategy_method = f'Best Strategy for {my_civ}'
                strategy = strategies[matchup][strategy_method]
                Label(frame, text=f"{matchup} : {strategy}", fg='#f2f2f2', bg='#1f261f', font=('Arial', 10), wraplength=450, justify='center').pack(pady=10)
                print(f"Debug: {matchup}: {strategy}") 
            else:
                Label(frame, text=f"No strategy found for matchup: {matchup.replace('_', ' ').title()}", 
                      fg='#e74c3c', bg='#1f261f', font=('Arial', 10)).pack(pady=10)
                print(f"Debug: {matchup}: No strategy found") 
        else:
            Label(frame, text="Could not determine opponent information.", 
                  fg='#e74c3c', bg='#1f261f', font=('Arial', 10)).pack(pady=10)
            print("Debug: Could not determine opponent information") 
    else:
        Label(frame, text=f"Could not find your player (profile ID: {profile_id}) in the match.", 
              fg='#e74c3c', bg='#1f261f', font=('Arial', 10)).pack(pady=10)
        print(f"Debug: Could not find your player (profile ID: {profile_id})")

    current_window = root
    last_game_id = match_data.get('game_id')
    root.after(10000, check_for_new_game) 

def check_for_new_game(window=None):
    global last_game_id, current_window
    match_data = recent_match()
    if match_data:
        current_game_id = match_data.get('game_id')
        your_player, your_team_idx, _ = find_your_player(match_data['teams'])
        if your_player:
            my_civ = your_player['civilization']
            opponent = find_opponent(match_data['teams'], your_team_idx)
            enemy_civ = opponent['civilization'] if opponent else 'Unknown'
            strategies = load_strategies()
            matchup = f'{my_civ} vs {enemy_civ}'
            if matchup in strategies and enemy_civ != 'Unknown':
                strategy_method = f'Best Strategy for {my_civ}'
                strategy = strategies[matchup][strategy_method]
                print(f"Debug: {matchup}: {strategy}")  
            else:
                print(f"Debug: {matchup}: No strategy found or opponent unknown")  
        else:
            print("Debug: Could not find your player in the match") 
        
        if current_game_id and current_game_id != last_game_id:
            show_match_info(match_data, current_window)
    if current_window and current_window.winfo_exists():
        current_window.after(10000, check_for_new_game)

def grabbing_match_info():
    global profile_id
    match_data = recent_match()
    if not match_data:
        messagebox.showerror("Error", f"No recent match data found for profile ID {profile_id}.")
        return
    show_match_info(match_data)

def set_player_id():
    global profile_id, your_player_name
    if path.exists('profile_id.txt'):
        with open('profile_id.txt', 'r') as f:
            pid = f.read().strip()
            profile_id = pid
            if profile_id:
                your_player_name = get_player_id(profile_id)
                grabbing_match_info()
    else:
        player_name = input('Enter your Age of Empires IV player name: ').strip()
        if player_name:
            profile_id = get_player_id(player_name)
            if profile_id:
                your_player_name = player_name.lower()
                print(f"Profile ID: {profile_id}")
                with open('profile_id.txt', 'w') as f:
                    f.write(str(profile_id))
                grabbing_match_info()
            else:
                messagebox.showerror("Error", f"Could not find profile for {player_name}.")
        else:
            messagebox.showerror("Error", "Player name cannot be empty.")

if __name__ == "__main__":
    debug()
    root = Tk()
    root.withdraw()
    keyboard.on_press_key("insert", lambda _: toggle_window_visibility())
    keyboard.on_press_key("f10", lambda _: toggle_window_visibility())
    set_player_id()
    root.mainloop()