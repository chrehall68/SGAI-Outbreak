class DataCollection():
    def __init__(self, starting_zombies, starting_humans):
        self.dataList = []
        self.numStartingZombies = starting_zombies
        self.numStartingHumans = starting_humans
        self.numType1Cured = 0 # these are attempts
        self.numType2Cured = 0
        self.numType3Cured = 0
        self.numType1Killed = 0
        self.numType2Killed = 0
        self.numType3Killed = 0
        self.numPeopleTurnedToZombies = 0
        self.didWin = False
        self.totalMoves = 0
        self.totalScore = 0

    def addMove(self, step_num, zombies, humans, move, zombieType="N/A"):
        obj = {
            "step": step_num,
            "# Zombies": zombies,
            "# Humans": humans,
            "Move": move,
            "Enemy Cured/Killed": zombieType
        }
        self.dataList.append(obj)
    def print_attributes (self):
        print(f"Data List: {self.dataList}")
        print(f"Win: {self.didWin}")
        print(f"Starting Zombies: {self.numStartingZombies}")
        print(f"Starting Humans: {self.numStartingHumans}")
        print(f"Score: {self.totalScore}")
        print(f"Total Moves: {self.totalMoves}")
        print(f"Num People Turned to Zombies: {self.numPeopleTurnedToZombies}")
        print(f"Type 1 Cured Attempts: {self.numType1Cured}")
        print(f"Type 2 Cured Attempts: {self.numType2Cured}")
        print(f"Type 3 Cured Attempts: {self.numType3Cured}")
        print(f"Type 1 Killed: {self.numType1Killed}")
        print(f"Type 2 Killed: {self.numType2Killed}")
        print(f"Type 3 Killed: {self.numType3Killed}")
