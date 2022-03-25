from operator import ne
import sqlite3
dayList = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
noSessionString = "No Session"
thisWeekString = "This Week"
nextWeekString = "Next Week"

class DBHelper:
    
    def __init__(self, dbname="userData.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    # Timeslot Availability is captured in 16 bits for each day
    # First 8 bits represent this week, Last 8 bits represent next week
    # 0 means not available, 1 means available
    # The 8 bits represent these timeslots in this order: 7am, 9am, 11am, 1pm, 3pm, 5pm, 7pm, 9pm
    def setup(self):
        stmt = """CREATE TABLE IF NOT EXISTS userData ( 
                        username TEXT PRIMARY KEY,
                        inSession INTEGER DEFAULT 0,
                        Mon TEXT DEFAULT "0000000000000000",
                        Tue TEXT DEFAULT "0000000000000000",
                        Wed TEXT DEFAULT "0000000000000000",
                        Thu TEXT DEFAULT "0000000000000000",
                        Fri TEXT DEFAULT "0000000000000000",
                        Sat TEXT DEFAULT "0000000000000000",
                        Sun TEXT DEFAULT "0000000000000000"
                        )"""
        self.conn.execute(stmt)
        self.conn.commit()

    # Username Queries

    def handleUsername(self, username):
        stmt = """SELECT * FROM userData WHERE username = (?)"""
        args = (username, )
        queryReturn = [x[0] for x in self.conn.execute(stmt, args)]
        if len(queryReturn) == 0:
            self.__addUsername(username)

    def __addUsername(self, username):
        stmt = "INSERT INTO userData (username) VALUES (?)"
        args = (username, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def getAllUsernames(self):
        stmt = """SELECT username FROM userData"""
        return [x[0] for x in self.conn.execute(stmt)]

    # Session queries

    def setSession(self, username, state):
        # STATES (encoding - value passed in)
        # 0 - not amending, 1 - this week, 2 - next week
        inSession = self.determineSession(state)
        stmt2 = """UPDATE userData SET inSession = (?) WHERE username = (?)"""
        args2 = (inSession, username, )
        self.conn.execute(stmt2, args2)
        self.conn.commit()

    def determineSession(self, state):
        if state == noSessionString:
            return 0
        if state == thisWeekString:
            return 1
        if state == nextWeekString:
            return 2
        else:
            print("ERROR in determineSession: Bad Week State Input")

    def getSession(self, username):
        currSession = self.getSessionHelper(username)
        if currSession != thisWeekString and currSession != nextWeekString:
            print("ERROR in getSession: Wrong Session Input!")
            return
        return currSession

    def getSessionHelper(self, username):
        stmt = """SELECT inSession FROM userData WHERE username = (?)"""
        args = (username, )
        state = -1
        for x in self.conn.execute(stmt, args):
            state = x[0]
        if state == 0:
            return noSessionString
        if state == 1:
            return thisWeekString
        if state == 2:
            return nextWeekString

    # Timeslot queries

    def __setTimeslot(self, username, day, string):
        stmt = """UPDATE userData SET {day} = (?) WHERE username = (?)""".format(day = day)
        args = (string, username, )
        self.conn.execute(stmt, args)
        self.conn.commit()
    
    def getTimeslot(self, username, day):
        stmt = """SELECT {day} FROM userData WHERE username = (?)""".format(day = day)
        args = (username, )
        for x in self.conn.execute(stmt, args):
            return x[0]

    def getTimeslotForWeek(self, username, day):
        currentSession = self.getSession(username)
        timeslot = self.getTimeslot(username, day)
        if currentSession == thisWeekString:
            return timeslot[:8]
        if currentSession == nextWeekString:
            return timeslot[8:]

    def changeTimeslot(self, username, day, time):
        # Week will be recorded by current session
        currentSession = self.getSession(username)
        # Depending on the week, manipulate different substrings to changetimeslot
        currentTimeslot = self.getTimeslot(username, day)
        if currentSession == thisWeekString:
            requiredTimeslot = self.changeTimeslotHelper(currentTimeslot[:8], time) + currentTimeslot[8:]
        if currentSession == nextWeekString:
            requiredTimeslot = currentTimeslot[:8] + self.changeTimeslotHelper(currentTimeslot[8:], time)

        self.__setTimeslot(username, day, requiredTimeslot)

    def changeTimeslotHelper(self, string, time):
        flipBitIndex = -1
        if time == "7am":
            flipBitIndex = 0
        if time == "9am":
            flipBitIndex = 1
        if time == "11am":
            flipBitIndex = 2
        if time == "1pm":
            flipBitIndex = 3
        if time == "3pm":
            flipBitIndex = 4
        if time == "5pm":
            flipBitIndex = 5
        if time == "7pm":
            flipBitIndex = 6
        if time == "9pm":
            flipBitIndex = 7
        
        if flipBitIndex == -1:
            print("ERROR in changeTimeslotHelper: Something wrong with the time!")
            return -1
        return self.flipRequiredBit(string, flipBitIndex)

    def flipRequiredBit(self, string, index):
        bit = int(string[index])
        bit = (bit + 1) % 2
        return string[:index] + str(bit) + string[index + 1:]

    def rolloverSchedules(self):
        for username in self.getAllUsernames():
            for day in dayList:
                currentTimeslot = str(self.getTimeslot(username, day))
                currentTimeslot = currentTimeslot[8:] + "00000000"
                self.__setTimeslot(username, day, currentTimeslot)

    # Get All User Data

    def getAllUserData(self, username):
        stmt = "SELECT * FROM userData WHERE username = (?)"
        args = (username, )
        return self.conn.execute(stmt, args)

    # Purge data queries

    def purgeUserData(self):
        stmt = "DELETE FROM userData"
        self.conn.execute(stmt)
        self.conn.commit()
