import json
from tinydb import TinyDB, Query
import sys

store_db = TinyDB('store_db.json')

def addItem(name, price, quantity):
	global store_db
	q = Query()

	if len(store_db.search(q.name == name)) == 0:
		store_db.insert({'name': name,
						'price': price,
						'quantity': quantity})
	else:
		print(f'item {name} already exists')

def listItems():
	global store_db
	q = Query()

	print(store_db.all())

def update(name, prop, value):
	global store_db
	q = Query()

	if len(sys.argv) == 5:
		if(prop == 'price'):
			store_db.update({'price': value}, q.name == name)
		elif(prop == 'quantity'):
			if value == 'inf':
				store_db.update({'quantity': value}, q.name == name)
			elif int(value) >= 0:
				store_db.update({'quantity': int(value)}, q.name == name)

if __name__ == '__main__':
	if(sys.argv[1] == 'add'):
		addItem(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
	elif(sys.argv[1] == 'list'):
		listItems()
	elif(sys.argv[1] == 'update'):
		update(sys.argv[2], sys.argv[3], sys.argv[4])