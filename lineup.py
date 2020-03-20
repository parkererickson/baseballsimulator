import sys

from batter import Batter
from pitcher import Pitcher

class Lineup():
    def __init__(self, lineup, batterDF, pitcherDF):
        self.lineup = [None] * 11
        self.posInLineup = 1
        self.score = 0
        if(isinstance(lineup, type(""))):
            fileName = lineup
            if not fileName.lower().endswith(".txt"):
                sys.exit("Sorry, lineup file, " + fileName + (" needs to be in a "
                        ".txt file"))
            file = open(fileName, "r")
            tmplineup = [s.strip() for s in file.readline().split(",")]
            file.close()
        elif(isinstance(lineup, type([]))):
            tmplineup = lineup
        else:
            sys.exit("Lineup not valid type")
        

        for i in range(11):
            if i == 0:
                self.lineup[i] = tmplineup[i]
            elif i > 0 and i < 10:
                if not tmplineup[i] in batterDF.index:
                    sys.exit("batter, " + tmplineup[i] + ", "+
                            (" does not exist in the FanGraphs database. "
                            "Please check the spelling of the player's "
                            "name."))
                self.lineup[i] = Batter(tmplineup[i], batterDF)
            else:
                if not tmplineup[i] in pitcherDF.index:
                    sys.exit("pitcher, " + tmplineup[i] + ", " +
                            (" does not exist in the FanGraphs database. "
                            "Please check the spelling of the player's "
                            "name."))
                self.lineup[i] = Pitcher(tmplineup[i], pitcherDF)

    def getLineup(self):
        return(self.lineup)
        
    def getScore(self):
        return(self.score)
    
    def setScore(self, score):
        self.score = score

    def nextBatter(self):
        tmp = self.posInLineup
        self.posInLineup += 1
        if self.posInLineup > 9:
            self.posInLineup = 1
        return(self.lineup[tmp])
    
    def getPitcher(self):
        return(self.lineup[10])

    def addRuns(self, runs):
        self.score = self.score + runs

    def __repr__(self):
        return(str(self.lineup))