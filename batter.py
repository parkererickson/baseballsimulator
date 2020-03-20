class Batter():
	def __init__(self, name, batterDF):
		self.name = name
		row = batterDF.loc[self.name]
		PA = row["PA"]
		self.p1b = row["1B"] / PA
		self.p2b = row["2B"] / PA
		self.p3b = row["3B"] / PA
		self.phr = row["HR"] / PA
		self.ptw = (row["BB"] + row["IBB"] + row["HBP"]) / PA
		self.pso = row["SO"] / PA
		self.pbo = ((PA - row["1B"] - row["2B"] - row["3B"] - row["HR"] 
				              - row["BB"] - row["IBB"] - row["HBP"] - row["SO"]) / PA)
		self.stance = "R"

	def getBattingStance(self):
		return self.stance

	def __repr__(self):
		return(self.name)