# SGAI - Outbreak
This is the repository that Beaverworks' SGAI 2022 will be using to understand
serious games and reinforcement learning.

## Team Courtney II
The best team out there.

## Requirements
For windows users use `pip3 install -r requirements.txt` to install all the requirements.
For Macos users use `pip3 install -r macos_requirements.txt` to install all the requirements.

## How to run
### VS Code version
DO NOT run main.py when the current directory is SGAI-Outbreak.
You must open the folder SGAI_MK3 with vscode. Then, you can
run main.py from VS Code.
### cmd line version
First, `cd ./SGAI_MK3`. Then, `python main.py`

## How to play
There are basic moves:
- Move - Click on a person and a square next to them.
If the square isn't occupied, the person will move to that square.
- Cure - Click the cure button and a zombie. This will cure them. You must be adjacent to the zombie for the cure to work!
- Vaccinate - Click the vaccinate button and a person to vaccinate them. Vaccination lasts for 5 turns and gives 100% immunity to being zombified. You must be in the vaccination zone indicated by a different color tile.
- Place Wall - Click the wall and any square that is adjacent to a person. This will place a wall and last for anywhere between 2-4 turns.
- Every Action besides moving requires resources. You accumulate resources based on how well you are doing.
