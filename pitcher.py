class Pitcher():
	def __init__(self, name, pitcherDF):
		self.name = name
		row = pitcherDF.loc[name]
		PA = row["TBF"]
		self.p1b = row["1B"] / PA
		self.p2b = row["2B"] / PA
		self.p3b = row["3B"] / PA
		self.phr = row["HR"] / PA
		self.ptw = (row["BB"] + row["IBB"] + row["HBP"]) / PA
		self.pso = row["SO"] / PA
		self.pbo = ((PA - row["1B"] - row["2B"] - row["3B"] - row["HR"] 
				              - row["BB"] - row["IBB"] - row["HBP"] - row["SO"]) / PA)

	def __repr__(self):
		return(self.name)