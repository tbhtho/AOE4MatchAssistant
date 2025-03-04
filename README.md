###  🔴🚨*WARNING*🚨🔴:  This project was made for me to learn. Plenty of bugs likely weren't found, tested, or fixed. Your experience could vary!



## Project Status
This project is currently **unfinished** and may not be completed in the near future. It is shared as-is for reference, experimentation, or potential contributions. Features may be incomplete, and there could be bugs or missing functionality. Use at your own risk! This project was made for me to learn how to use requests in python.

## Known Issues/Limitations
- The project is incomplete, and some features may not work as expected.
- API rate limits or connection issues with aoe4world.com could cause errors.
- Hotkeys in `Assistant_LITE` require administrative privileges and may not work on all systems.
- No error recovery for missing or malformed `matchup_strategies.csv`.
- GUI layout and stability may need refinement.

  
## Future Plans 
While this project is on hold, potential future enhancements could include:
- Real-time match tracking with more detailed stats.
- A web-based interface.
- Integration with more game APIs or custom strategy databases.

  
## Installation
### Prerequisites
- **Python 3.8 or higher** (recommended: 3.12.x for the latest stability)
- Internet connection (required for API calls to aoe4world.com)
- Administrative privileges on Windows (for global hotkeys in the LITE version)

### Steps
1. Clone or download this repository to your local machine.
2. Ensure `matchup_strategies.csv` is in the `src` folder (or root, depending on your file structure).
3. Run `src/prereqs.bat` as an administrator to automatically install Python (if needed) and required libraries (`requests` and `keyboard`).
4. After setup, launch either `src/Assistant_FULL.py` or `src/Assistant_LITE.py` based on your needs.

### Troubleshooting
- If `prereqs.bat` fails, manually install Python from [python.org](https://www.python.org/downloads/) and run `pip install requests keyboard` in a command prompt.
- Ensure `profile_id.txt` is not deleted, as it stores your player ID after setup.
  
# AOE4 Match Assistant FULL & LITE
fetches recent match data from AOE4World

Ensure you have Python 3.8+ installed.

__Bat file__:  with libs needed to run either python files,

__matchup_strategies.csv__: Contains the strategy dumb'd down for each civ matchup

__profile_id.txt__: File will be made after providing either your steam or xbox username

------------------------------
Assistant_FULL vs Assistant_LITE:
------------------------------
FULL: Shows more detail Not ables to be toggled like LITE, Full will require you to Rerun it each time you get in a new game, tedious. (Better If You Have Duel Monitors) 

LITE: Only Shows Strategy, Doesnt show teammates, Able to be toggled with f10 & or insert

