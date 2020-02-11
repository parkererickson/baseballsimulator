import pandas as pd
from numpy.random import choice

class Game():
    def __init__(self, lineup1, lineup2, leagueDF, brDF):
        self.lineup1 = lineup1
        self.lineup2 = lineup2
        self.leagueDF = leagueDF
        self.brDF = brDF

    # calculates and returns the list of probabilities of each outcome of a plate 
    # appearance
    def calcOddsRatio(self, batter, pitcher):
        # Tom Tango's Odds Ratio Method
        odds1b = ((batter.p1b / (1-batter.p1b)) * (pitcher.p1b / (1-pitcher.p1b)) 
                / (self.leagueDF.loc[2017, "p1b"] / (1-self.leagueDF.loc[2017, "p1b"])))
        odds2b = ((batter.p2b / (1-batter.p2b)) * (pitcher.p2b / (1-pitcher.p2b)) 
                / (self.leagueDF.loc[2017, "p2b"] / (1-self.leagueDF.loc[2017, "p2b"])))
        odds3b = ((batter.p3b / (1-batter.p3b)) * (pitcher.p3b / (1-pitcher.p3b)) 
                / (self.leagueDF.loc[2017, "p3b"] / (1-self.leagueDF.loc[2017, "p3b"])))
        oddshr = ((batter.phr / (1-batter.phr)) * (pitcher.phr / (1-pitcher.phr)) 
                / (self.leagueDF.loc[2017, "phr"] / (1-self.leagueDF.loc[2017, "phr"])))
        oddstw = ((batter.ptw / (1-batter.ptw)) * (pitcher.ptw / (1-pitcher.ptw)) 
                / (self.leagueDF.loc[2017, "ptw"] / (1-self.leagueDF.loc[2017, "ptw"])))
        oddsso = ((batter.pso / (1-batter.pso)) * (pitcher.pso / (1-pitcher.pso)) 
                / (self.leagueDF.loc[2017, "pso"] / (1-self.leagueDF.loc[2017, "pso"])))
        oddsbo = ((batter.pbo / (1-batter.pbo)) * (pitcher.pbo / (1-pitcher.pbo)) 
                / (self.leagueDF.loc[2017, "pbo"] / (1-self.leagueDF.loc[2017, "pbo"])))
        # turn odds into probabilities
        p1b = odds1b / (odds1b + 1)
        p2b = odds2b / (odds2b + 1)
        p3b = odds3b / (odds3b + 1)
        phr = oddshr / (oddshr + 1)
        ptw = oddstw / (oddstw + 1)
        pso = oddsso / (oddsso + 1)
        pbo = oddsbo / (oddsbo + 1)
        total = p1b + p2b + p3b + phr + ptw + pso + pbo
        # probabilities from the Odds Ratio Method don't exactly add up to 1 used
        # in this way, so they are normalized here
        np1b = p1b / total
        np2b = p2b / total
        np3b = p3b / total
        nphr = phr / total
        nptw = ptw / total
        npso = pso / total
        npbo = pbo / total
        return [np1b, np2b, np3b, nphr, nptw, npso, npbo]

    def playGame(self):
        inning = 0
        out = 0
        bases = "000"
        state = "0,000"
        homeBattingOrder = 1
        awayBattingOrder = 1
        homeScore = 0
        awayScore = 0
        playList = ["1b", "2b", "3b", "hr", "tw", "so", "bo"]

        # play from top 1st to bottom 9th inning, and extra innings are upto 33rd
        for inning in [i / 10 for i in range(10,3305,5)]:
            if inning == 9.5 and awayScore < homeScore:  # home team won; don't play bottom 9th
                break
            elif inning == 10.0 and awayScore != homeScore:  # winner is decided after 9 innings
                break
            elif inning >= 11.0 and (inning % 1.0) == 0.0:  # extra innings (one inning sudden death)
                if awayScore != homeScore:
                    break

            #print("--- inning: " + str(inning) + " ---")
            if (inning % 1.0) == 0.0:  # away team bats
                batter = self.lineup1[awayBattingOrder]
                pitcher = self.lineup2[10]  # no need to do this in this loop since there is only one pitcher now
                score = awayScore
                battingOrder = awayBattingOrder
            else:
                batter = self.lineup2[homeBattingOrder]
                pitcher = self.lineup1[10]
                score = homeScore
                battingOrder = homeBattingOrder
            while out < 3:
                playProbList = self.calcOddsRatio(batter, pitcher)
                play = choice(playList, p=playProbList)
                if play == "1b" or play == "2b" or play == "3b" or play == "bo":
                    brDict = self.brDF.loc[state, play]
                    resultList = list(brDict.keys())[1:]  # keys() and values() methods are not supposed to preserve the order, but they seem to do so
                    countList = list(brDict.values())[1:]
                    totalCount = brDict["total"]
                    probList = [count / totalCount for count in countList]
                    result = choice(resultList, p=probList)
                    out = int(result.split(",")[0])
                    bases = result.split(",")[1]
                    score += int(result.split(",")[2])
                elif play == "hr":
                    score += (int(bases[0]) + int(bases[1]) + int(bases[2]) + 1)
                    bases = "000"
                elif play == "tw":
                    if bases == "000" or bases == "001" or bases == "010":
                        bases = str(int(bases) | 100)
                    elif bases == "100":
                        bases = "110"
                    elif bases == "110" or bases == "011" or bases == "101":
                        bases = "111"
                    else:
                        bases = "111"
                        score += 1
                else:  #play == "so"
                    out += 1

                state = str(out) + "," + bases
                #print("batting team score: " + str(score) + " | batter: " + str(battingOrder) + " | play: " + play + " | new state: " + state)
                if battingOrder < 9:
                    battingOrder += 1
                else:
                    battingOrder = 1

            # update the score and batting order for the correct team
            if (inning % 1.0) == 0.0:
                awayScore = score
                awayBattingOrder = battingOrder
            else:
                homeScore = score
                homeBattingOrder = battingOrder
            out =  0
            bases = "000"
            state = "0,000"
        #print("awayScore: " + str(awayScore) + " | homeScore: " + str(homeScore))
        if awayScore > homeScore:
            return 0
        else:
            return 1
