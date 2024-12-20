from tinydb import TinyDB, Query

db = TinyDB('qcoin_db.json')
qdb = db.table('users', cache_size=0)

Q = Query()

for user in qdb:
	newBalance = (user['coins'] + 1000)
	qdb.update({'coins': newBalance}, Q.user_id == user['user_id'])

print('Payday! 1000 added to every user')