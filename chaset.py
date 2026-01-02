import sqlite3
from main import printTable, getTable, setCursor, conn, cursor

def setCursor(db):
    global conn, cursor
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

#db_name = f"databases/{input('Database name: ')}.db"
#setCursor(db_name)
#print(f"Connected to database: {db_name}")

#conn = sqlite3.connect(database='databases/Shiaverse.db')
conn = sqlite3.connect(database='databases/Minecraft.db')
cursor = conn.cursor()
print("Database list:", cursor.execute("PRAGMA database_list").fetchall())

def checkTable(name):
    cursor.execute(f"SELECT * FROM characters WHERE id={name}")
    results = cursor.fetchall()
    return results

def rowCount(table):
    cursor.execute(f"SELECT COUNT(*) FROM {table};")
    results = cursor.fetchone()
    if results:
        return int(results[0])
    return 0

def removeData(id):
    cursor.execute(f"DELETE FROM character_answers WHERE character_id IN {id};")
    conn.commit()

printTable('characters', cursor)
chosen = input("Pick one: ")
cont = checkTable(chosen)
print(cont)

if cont != []:
    num = 0
    ans = []
    removeData(f"({chosen})")
    questions = getTable('questions', cursor)
    while num < len(questions):
        inp = str(input(f"{questions[num][1]} ")).upper()
        if inp == 'Y' or inp == 'N' or inp == 'U':
            ans.append(inp)
            num += 1
    for i in range(len(ans)):
        cursor.execute(f"INSERT INTO character_answers (character_id, question_id, answer) VALUES ({chosen}, {i+1}, '{ans[i]}');")
        conn.commit()