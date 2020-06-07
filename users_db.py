

def listAllUserNames():
	from app import db
	allUserNames = db.engine.execute("SELECT username FROM users")
	print(allUserNames)
	print(allUserNames.cursor)
	#print(allusers.cursor)

	usernames = []
	for i in allUserNames.cursor:
		usernames.append(i)
	print(usernames)

	#result = [dict(zip(tuple (allUserNames.keys()) ,i)) for i in allUserNames.cursor]
	#print(result)
	return usernames