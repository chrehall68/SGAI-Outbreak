class DataCollection():
    def __init__(self, starting_zombies, starting_humans):
        self.dataList = []
        self.numStartingZombies = starting_zombies
        self.numStartingHumans = starting_humans
        self.numType1Cured = 0
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