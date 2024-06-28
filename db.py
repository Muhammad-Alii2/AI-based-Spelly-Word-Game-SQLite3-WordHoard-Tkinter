import sqlite3

connection = sqlite3.connect('mydb')
cursor = connection.cursor()

cursor.execute('''create table if not exists Wordlist (
    Id integer primary key autoincrement,
    Word text not null unique
    )'''
)

connection.commit()

file_path = 'D:\\INTERNSHIP\\GEXTON\\3rd Task\\wordlist.txt'

with open(file_path, 'r') as file:
    words = file.read().splitlines()

for word in words:
    cursor.execute('insert into Wordlist (word) values (?)', (word,))

connection.commit()
connection.close()