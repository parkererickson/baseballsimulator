import csv
import sys
import pandas as pd
from numpy.random import choice
from batter import Batter
from pitcher import Pitcher
from lineup import Lineup
from game import Game
import data

# simulates multiple games between two teams and prints out the result
def simulate(lineup1, lineup2, leagueDF, brDF, numGames, verbose):
	awayWin = 0
	homeWin = 0
	for i in range(0, numGames):
		game = Game(lineup1, lineup2, leagueDF, brDF)
		result = game.playGame(verbose)
		if result == 0:
			awayWin += 1
		else:
			homeWin += 1
	print("awayWin: " + str(awayWin) + " | homeWin: " + str(homeWin))

def main(argv):
	batterDF, pitcherDF, leagueDF = data.read_data("2017FanGraphsBatting.csv", "2017FanGraphsPitching.csv", "2017FanGraphsLeague.csv")
	lineup1 = Lineup(argv[1], batterDF, pitcherDF) 
	lineup2 = Lineup(argv[2], batterDF, pitcherDF)
	print(lineup1)
	print(lineup2)
	leagueDF = data.fill_statline(leagueDF)
	brDF = data.fill_baserunning()
	simulate(lineup1, lineup2, leagueDF, brDF, 1000, verbose=False)

if __name__ == "__main__": 
	main(sys.argv)