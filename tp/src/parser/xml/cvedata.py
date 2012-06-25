from lxml import etree
from lxml import objectify

xmlfile = "custom.xml"

class CVEData:
	"""
		Helper class to manage CVE data from https://cve.mitre.org/data/downloads/index.html
		Hides all of the lxml stuff.
	"""

	def __init__(self, filename):
		self._tree = objectify.parse(filename)
		self._root = self._tree.getroot()
		self._items = self._root.item[0]

		self._init_votes()

	def get_status(self):
		return self._items.status.text
	
	def get_phase(self):
		"""
			Returns a dict with the phase text and date.
			dict keys: "text" and "date".
		"""
		date = self._items.phase.get("date")
		text = self._items.phase.text

		return {"text": text, "date": date}

	def get_description(self):
		return self._items.desc

	def _init_votes(self):
		"""
			According to schema @ https://cve.mitre.org/schema/cve/cve_1.0.xsd
			There are 7 vote types:
				- accept
				- modify
				- noop
				- recast
				- reject
				- reviewing
				- revote

			This method helps sort it out and check which, if any, apply to this item. 
			Returns a tuple, with the vote types represents the keys and the values being a list with respected data.
		"""

		d = {}
		vote_types = ['accept', 'modify', 'noop', 'recast', 'reject', 'reviewing', 'revot']

		votes = self._items.votes

		for i in range(len(vote_types)):
			if hasattr(votes, vote_types[i]):
				v = votes.__getattr__(vote_types[i])
				text = v
				count = v.get("count")

				t = ( text, count)

				d[vote_types[i]] = t
			else:
				t= ("", "0")
				d[vote_types[i]] = t

		self._votes = d

	def get_votes(self):
		return self._votes
		
	def get_comments(self):
		
		self._comments = []
		c = self._items.comments.comment
		print len(c)

		for i in range(len(c)):
			text = c[i]		
			author =  c[i].get("voter")
			
		
			self._comments.append([author, text])

		return self._comments

if __name__ == "__main__":
	data = CVEData(xmlfile)
	print "Status: " + data.get_status()
	
	phase = data.get_phase()
	print "Phase: " + phase["text"]
	print "-- Date: " + phase["date"]

	print "Description: " + data.get_description()

	

	i = ['accept', 'modify', 'noop', 'recast', 'reject', 'reviewing', 'revot']
	votes = data.get_votes()
	for v in range(len(i)):
		print votes[i[v]]


	c = data.get_comments()
	for i in range(len(c)):
		print "Author: "  + c[i][0]
		print "Comment: " + c[i][1]
		
		




