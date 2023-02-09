import sqlite3
import datetime
    
def addTask(userId, title, description, done, hidden):
    initialize_database()
    
    db = sqlite3.connect("data.db")
    cur = db.cursor()
    dt = datetime.datetime.now()
    
    cur.execute(f"""INSERT INTO data 
                        (user_id, title, description, dt, done, hidden) VALUES 
                        ('{userId}','{title}','{description}','{dt}',{done},{hidden});
                        """)
    db.commit()

def getSingleTask(taskId):
    initialize_database()
    
    db = sqlite3.connect("data.db")
    cur = db.cursor()
    
    data = cur.execute(f"""SELECT * FROM data WHERE
                       id={taskId}
                       AND hidden = 0""").fetchone()
    
    return data

def getAllTasks(userId):
    initialize_database()
    
    db = sqlite3.connect("data.db")
    cur = db.cursor()
    
    data = cur.execute(f"SELECT * FROM data WHERE user_id='{str(userId)}' AND hidden = 0").fetchall()
    
    return data

def getDoneTasks(userId):
    initialize_database()
    
    db = sqlite3.connect("data.db")
    cur = db.cursor()
    
    data = cur.execute(f"""SELECT * FROM data WHERE
                            user_id='{str(userId)}' AND done=1 AND hidden = 0;""").fetchall()
    
    return data

def getUnderDoneTasks(userId):
    initialize_database()
    
    db = sqlite3.connect("data.db")
    cur = db.cursor()
    
    data = cur.execute(f"""SELECT * FROM data WHERE
                            user_id='{str(userId)}' 
                            AND done=0
                            AND hidden = 0;"""
                            ).fetchall()
    
    return data

def markDone(taskId):
    initialize_database()
    
    db = sqlite3.connect("data.db")
    cur = db.cursor()
    cur.execute(f"""UPDATE data
                        SET done=1
                        WHERE id = {taskId};
    """)
    db.commit()

def hideTask(taskId):
    initialize_database()
    
    db = sqlite3.connect("data.db")
    cur = db.cursor()
    cur.execute(f"""UPDATE data
                SET hidden = 1
                WHERE id = {taskId};
    """)
    db.commit()

def isUser(userId):
    initialize_database()
    
    db = sqlite3.connect("data.db")
    cur = db.cursor()
    cols = cur.execute(f"""SELECT * FROM users WHERE
                            user_id={userId}
                            """).fetchall()

    if len(cols) == 0:
        return False
    
    else:
        return True

def createUser(userId, status=0):
    initialize_database()
    
    db = sqlite3.connect("data.db")
    cur = db.cursor()
    
    if not isUser(userId):
        cur.execute(f"""INSERT INTO users 
                        (user_id, status) 
                        VALUES ('{userId}',{status});
                            """)
        db.commit()
    

def setUserStatus(userId, statusId):
    initialize_database()
    
    db = sqlite3.connect("data.db")
    cur = db.cursor()
    if isUser(userId):
        cur.execute(f"""UPDATE users
                            SET status={statusId}
                            WHERE user_id = '{userId}';
                            """)
        db.commit()
        
    else:
        createUser(userId, statusId)

def getUserStatus(userId):
    initialize_database()
    
    db = sqlite3.connect("data.db")
    cur = db.cursor()
    
    if isUser(userId):
        status = cur.execute(f"""SELECT status FROM users
                            WHERE user_id = '{userId}';
                            """).fetchone()
        return status[0]
    
    else:
        createUser(userId)

# run once to create database and table.
def initialize_database():
    
    # creating database file and connecting
    database = sqlite3.connect("data.db")
    
    # creating table of data if not exists.
    try:
        database.execute("""CREATE TABLE data(
                    id integer primary key autoincrement,
                    user_id VARCHAR(50),
                    title VARCHAR(50),
                    description VARCHAR(900),
                    dt VARCHAR(100),
                    done BOOL,
                    hidden BOOL);
                            """)
    except:
        pass
    
    # creating table of users if not exists.
    try:
        database.execute("""CREATE TABLE users(
                    user_id integer primary key,
                    status INTEGER
                    );
                        """)
    except:
        pass
