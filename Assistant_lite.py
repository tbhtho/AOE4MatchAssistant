import requests
from os import path
import csv
from tkinter import Tk, Label, Frame, Button, Toplevel, messagebox
from datetime import datetime, timedelta, timezone
import re

profile_id = None
your_player_name = None 

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

def get_player_name(pid):
    url = f"https://aoe4world.com/api/v0/players/{pid}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'name' in data:
            return data['name'].lower()
    return None

def recent_match():
    global profile_id
    url = f"https://aoe4world.com/api/v0/players/{profile_id}/games/last"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
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
    with open('matchup_strategies.csv', 'r') as c:
        read = csv.DictReader(c)
        strategies = {}
        for row in read:
            strategies[row['Matchup']] = row
        return strategies

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

def show_match_info(match_data):
    root = Toplevel()
    root.overrideredirect(True)
    root.configure(bg='#263d53')

    title_bar = Frame(root, bg='#2a6cac', relief='raised', borderwidth=2, height=25)
    title_bar.pack(fill='x')
    Label(title_bar, text="Age of Empires IV - Match Overview", fg='#f2f2f2', bg='#2a6cac', font=('Arial', 10, 'bold')).pack(side='left', padx=8)
    close_button = Button(title_bar, text="✕", command=root.destroy, bg='#2a6cac', fg='#f2f2f2', 
                          font=('Arial', 8, 'bold'), relief='flat', padx=6, pady=2)
    close_button.pack(side='right', padx=6)

    def start_drag(event):
        root.x = event.x
        root.y = event.y

    def drag(event):
        x = root.winfo_x() + (event.x - root.x)
        y = root.winfo_y() + (event.y - root.y)
        root.geometry(f"+{x}+{y}")

    title_bar.bind("<Button-1>", start_drag)
    title_bar.bind("<B1-Motion>", drag)

    team_size = determine_team_size(match_data)
    if team_size == "1v1":
        height, width = 500, 600
    elif team_size == "2v2":
        height, width = 700, 600
    elif team_size == "3v3":
        height, width = 900, 600
    elif team_size == "4v4":
        height, width = 1100, 600
    else:
        height, width = 700, 600
    root.geometry(f"{width}x{height}")
    root.resizable(False, False)

    main_frame = Frame(root, bg='#263d53', padx=8, pady=8)
    main_frame.pack(fill='both', expand=True)

    match_time = match_data.get('started_at', '')
    parsed_time = parse_time_ago(match_time)
    team_size = determine_team_size(match_data)

    header_frame = Frame(main_frame, bg='#263d53', pady=2)
    header_frame.pack(fill='x')
    Label(header_frame, text=f"Match Started: {parsed_time.strftime('%Y-%m-%d %H:%M:%S') if parsed_time else 'Unknown'}", 
          fg='#f2f2f2', bg='#263d53', font=('Arial', 11, 'bold')).pack(pady=1, anchor='center')
    Label(header_frame, text=f"Match Type: {team_size}", fg='#f2f2f2', bg='#263d53', font=('Arial', 11)).pack(pady=1, anchor='center')

    team1_frame = Frame(main_frame, bg='#3c5f7a', relief='raised', borderwidth=2, padx=10, pady=6)
    team1_frame.pack(fill='x', padx=6, pady=6)
    Label(team1_frame, text="Team 1", fg='#f2f2f2', bg='#3c5f7a', font=('Arial', 12, 'bold')).pack(pady=4, anchor='center')
    for i, player in enumerate(match_data['teams'][0], 1):
        player_frame = create_player_frame(team1_frame, player, 1, i)
        player_frame.pack(fill='x', pady=2)

    team2_frame = Frame(main_frame, bg='#3c5f7a', relief='raised', borderwidth=2, padx=10, pady=6)
    team2_frame.pack(fill='x', padx=6, pady=6)
    Label(team2_frame, text="Team 2", fg='#f2f2f2', bg='#3c5f7a', font=('Arial', 12, 'bold')).pack(pady=4, anchor='center')
    for i, player in enumerate(match_data['teams'][1], 1):
        player_frame = create_player_frame(team2_frame, player, 2, i)
        player_frame.pack(fill='x', pady=2)

    your_player, your_team_idx, your_player_idx = find_your_player(match_data['teams'])
    if your_player:
        my_civ = your_player['civilization']
        my_name = your_player['name']
        
        opponent = find_opponent(match_data['teams'], your_team_idx)
        if opponent:
            enemy_civ = opponent['civilization']
            enemy_name = opponent['name']
            
            strategies = load_strategies()
            matchup = f'{my_civ} vs {enemy_civ}'
            
            strategy_frame = Frame(main_frame, bg='#263d53', pady=2)
            strategy_frame.pack(fill='x', pady=2)
            Label(strategy_frame, text=f"YOU ({my_name}): {my_civ.replace('_', ' ').title()} | Opponent ({enemy_name}): {enemy_civ.replace('_', ' ').title()}", 
                  fg='#2ecc71', bg='#263d53', font=('Arial', 11, 'bold')).pack(pady=2, anchor='center')
            Label(strategy_frame, text="Strategy:", fg='#f2f2f2', bg='#263d53', font=('Arial', 10, 'bold')).pack(pady=2, anchor='center')
            if matchup in strategies:
                strategy_method = f'Best Strategy for {my_civ}'
                strategy = strategies[matchup][strategy_method]
                Label(strategy_frame, text=strategy, fg='#f2f2f2', bg='#263d53', font=('Arial', 10), wraplength=450, justify='left').pack(pady=2, anchor='center')
            else:
                Label(strategy_frame, text=f"No strategy found for matchup: {matchup.replace('_', ' ').title()}", 
                      fg='#e74c3c', bg='#263d53', font=('Arial', 10)).pack(pady=2, anchor='center')
        else:
            strategy_frame = Frame(main_frame, bg='#263d53', pady=2)
            strategy_frame.pack(fill='x', pady=2)
            Label(strategy_frame, text="Could not determine opponent information.", 
                  fg='#e74c3c', bg='#263d53', font=('Arial', 10)).pack(pady=2, anchor='center')
    else:
        strategy_frame = Frame(main_frame, bg='#263d53', pady=2)
        strategy_frame.pack(fill='x', pady=2)
        Label(strategy_frame, text=f"Could not find your player (profile ID: {profile_id}) in the match.", 
              fg='#e74c3c', bg='#263d53', font=('Arial', 10)).pack(pady=2, anchor='center')

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
                your_player_name = get_player_name(profile_id)
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
    root = Tk()
    root.withdraw()
    set_player_id()
    root.mainloop()
