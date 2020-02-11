import csv
import sys
import pandas as pd
from numpy.random import choice
from batter import Batter
from pitcher import Pitcher
from game import Game
# reads csv files and store the data into the pandas dataframes
# returns the 3 data frames
def read_data():
	batterDF = pd.read_csv("2017FanGraphsBatting.csv")
	batterDF = batterDF.set_index("Name")
	# TODO:
	# There are duplicate Chris Young and Matt Duffy
	# batterDF = batterDF.set_index("Name", verify_integrity=True)
	batterCols = ["PA", "1B", "2B", "3B", "HR", "BB", "IBB", "HBP", "SO"]
	batterDF[batterCols] = batterDF[batterCols].apply(pd.to_numeric,
													  errors="ignore")
	
	pitcherDF = pd.read_csv("2017FanGraphsPitching.csv")
	pitcherDF = pitcherDF.set_index("Name")
	pitcherCols = ["TBF", "H", "2B", "3B", "HR", "BB", "IBB", "HBP", "SO"]
	pitcherDF[pitcherCols] = pitcherDF[pitcherCols].apply(pd.to_numeric,
													      errors="ignore")
	singleCol = pitcherDF["H"] - (pitcherDF["2B"] + pitcherDF["3B"] 
				+ pitcherDF["HR"])
	pitcherDF["1B"] = singleCol

	leagueDF = pd.read_csv("2017FanGraphsLeague.csv")
	leagueDF = leagueDF.set_index("Season")
	leagueDF[batterCols] = leagueDF[batterCols].apply(pd.to_numeric,
													  errors="ignore")
	return (batterDF, pitcherDF, leagueDF)

# checks the input files containing team names and lineups and then creates and
# returns lineups - a list of a string, 9 batter objects, and a pitcher object
def create_lineups(fileName1, fileName2, batterDF, pitcherDF):
	lineup1, lineup2 = [None] * 11, [None] * 11
	lineupList = [lineup1, lineup2]
	fileList = [fileName1, fileName2]

	for lineup, fileName in zip(lineupList, fileList):
		if not fileName.lower().endswith(".txt"):
			sys.exit("Sorry, lineup file, " + fileName + (" needs to be in a "
				     ".txt file"))
		file = open(fileName, "r")
		tmplineup = [s.strip() for s in file.readline().split(",")]

		for i in range(11):
			if i == 0:
				lineup[i] = tmplineup[i]
			elif i > 0 and i < 10:
				if not tmplineup[i] in batterDF.index:
					sys.exit("batter, " + tmplineup[i] + ", in " + fileName + 
						     (" does not exist in the FanGraphs database. "
						      "Please check the spelling of the player's "
						      "name."))
				lineup[i] = Batter()
				lineup[i].name = tmplineup[i]
			else:
				if not tmplineup[i] in pitcherDF.index:
					sys.exit("pitcher, " + tmplineup[i] + ", in " + fileName + 
						     (" does not exist in the FanGraphs database. "
						      "Please check the spelling of the player's "
						      "name."))
				lineup[i] = Pitcher()
				lineup[i].name = tmplineup[i]
		file.close()
	return (lineup1, lineup2)

# fills and returns attributes for the batter and pitcher objects in the lineup
def fill_statline(batterDF, pitcherDF, leagueDF, lineup1, lineup2):
	lineupList = [lineup1, lineup2]
	for lineup in lineupList:
		for i in range(1,11):
			player = lineup[i]
			# I'm using chain indexing here, which is different from other lines
			if i < 10:
				row = batterDF.loc[player.name]
				PA = row["PA"]
			else:
				row = pitcherDF.loc[player.name]
				PA = row["TBF"]
			player.p1b = row["1B"] / PA
			player.p2b = row["2B"] / PA
			player.p3b = row["3B"] / PA
			player.phr = row["HR"] / PA
			player.ptw = (row["BB"] + row["IBB"] + row["HBP"]) / PA
			player.pso = row["SO"] / PA
			player.pbo = ((PA - row["1B"] - row["2B"] - row["3B"] - row["HR"] 
				              - row["BB"] - row["IBB"] - row["HBP"] - row["SO"]) 
						  / PA)
	# duplicate code, but couldn't find a way to fit this in the above for loop
	PA = leagueDF.loc[2017, "PA"]
	leagueDF.loc[2017, "p1b"] = leagueDF.loc[2017, "1B"] / PA
	leagueDF.loc[2017, "p2b"] = leagueDF.loc[2017, "2B"] / PA
	leagueDF.loc[2017, "p3b"] = leagueDF.loc[2017, "3B"] / PA
	leagueDF.loc[2017, "phr"] = leagueDF.loc[2017, "HR"] / PA
	leagueDF.loc[2017, "ptw"] = (leagueDF.loc[2017, "BB"] 
								 + leagueDF.loc[2017, "IBB"] 
								 + leagueDF.loc[2017, "HBP"]) / PA
	leagueDF.loc[2017, "pso"] = leagueDF.loc[2017]["SO"] / PA
	leagueDF.loc[2017, "pbo"] = (PA - leagueDF.loc[2017, "1B"] 
								    - leagueDF.loc[2017, "2B"] 
						            - leagueDF.loc[2017, "3B"] 
						            - leagueDF.loc[2017, "HR"] 
						            - leagueDF.loc[2017, "BB"]
						            - leagueDF.loc[2017, "IBB"] 
						            - leagueDF.loc[2017, "HBP"] 
						            - leagueDF.loc[2017, "SO"]) / PA
	return (lineup1, lineup2, leagueDF)

# creates and returns a dataframe containing baserunning probabilities for each 
# state
def fill_baserunning():
	playFile = open("2016plays.txt", "r")
	playData = list(csv.reader(playFile))

	# 24 possible states and 4 plays that we care about for baserunning stats
	states = ["0,000","0,100","0,010","0,001","0,110","0,011","0,101","0,111",
			  "1,000","1,100","1,010","1,001","1,110","1,011","1,101","1,111",
			  "2,000","2,100","2,010","2,001","2,110","2,011","2,101","2,111"]
	plays = ["1b", "2b", "3b", "bo"]

	# initialize the dataframe with empty dictionaries
	emptyDicts = [[{} for x in range(4)] for y in range(24)] 
	brDF = pd.DataFrame(emptyDicts, index=states, columns=plays)

	for index, row in enumerate(playData):
		play = row[5]
		if play == "2":
			play = "bo"
		elif play == "20":
			play = "1b"
		elif play == "21":
			play = "2b"
		elif play == "22":
			play = "3b"

		# only consider plays if 1B, 2B, 3B, or BO for the baserunning stats
		if play == "bo" or play == "1b" or play == "2b" or play == "3b":
			# figure out the current state
			out = row[0]
			if row[1] == "": 
				base1 = "0"
			else:
				base1 = "1"
			if row[2] == "":
				base2 = "0"
			else:
				base2 = "1"
			if row[3] == "":
				base3 = "0"
			else:
				base3 = "1"
			state = out + "," + base1 + base2 + base3

			# update the out-count
			newOut = int(out)
			if row[6] == "0":
				newOut += 1
			if base1 == "1" and row[7] == "0":
				newOut += 1
			if base2 == "1" and row[8] == "0":
				newOut += 1
			if base3 == "1" and row[9] == "0":
				newOut += 1

			# update the bases situations and count any runs scored
			newBase1 = "0"
			newBase2 = "0"
			newBase3 = "0"
			newRuns = 0
			for base in row[6:]:
				if base == "1":
					newBase1 = "1"
				elif base == "2":
					newBase2 = "1"
				elif base == "3":
					newBase3 = "1"
				elif base == "4" or base == "5" or base == "6":
					newRuns += 1
			newState = (str(newOut) + "," + newBase1 + newBase2 + newBase3
			            + "," + str(newRuns))

			# update the number of occurrences of new state in the dictionaries
			brDict = brDF.loc[state, play]
			if "total" in brDict:
				brDict["total"] += 1
			else:
				brDict["total"] = 1
			if newState in brDict:
				brDict[newState] += 1
			else:
				brDict[newState] = 1
	return brDF

	

# plays an entire game and returns 0 if the away team wins and 1 otherwise

# simulates multiple games between two teams and prints out the result
def simulate(lineup1, lineup2, leagueDF, brDF, numGames):
	awayWin = 0
	homeWin = 0
	for i in range(0, numGames):
		game = Game(lineup1, lineup2, leagueDF, brDF)
		result = game.playGame()
		if result == 0:
			awayWin += 1
		else:
			homeWin += 1
	print("awayWin: " + str(awayWin) + " | homeWin: " + str(homeWin))

def main(argv):
	batterDF, pitcherDF, leagueDF = read_data()
	lineup1, lineup2 = create_lineups(argv[1], argv[2], batterDF, pitcherDF)
	lineup1, lineup2, leagueDF = fill_statline(batterDF, pitcherDF, leagueDF, 
											   lineup1, lineup2)
	brDF = fill_baserunning()
	simulate(lineup1, lineup2, leagueDF, brDF, 1000)

if __name__ == "__main__": main(sys.argv)


