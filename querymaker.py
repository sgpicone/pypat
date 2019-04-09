import csv, os, sqlite3 as sql

conn = sql.connect('patco.db')
cur = conn.cursor()
files = [f for f in os.listdir('.') if os.path.isfile(f) and os.path.splitext(f)[1] == '.csv']
for fi in files:
    with open(fi,'rb') as csvfile:
        reader = csv.reader(csvfile,delimiter=',')
        cols = reader.next()
        tableName = os.path.splitext(fi)[0]
        query = "CREATE TABLE " + tableName + " (\n"
        for c in cols:
            query += c + " varchar(255),\n"
        query = query[:-2]+"\n);"
        print query
        cur.execute(query)
        for row in reader:
            query = "INSERT INTO " + tableName + " VALUES ("
            query += ",".join(["\"" + it + "\"" for it in row])
            query += ");"
            print query
            cur.execute(query)
        conn.commit()

conn.close()



