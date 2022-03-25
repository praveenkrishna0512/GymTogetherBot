from dbhelper import DBHelper

db = DBHelper()

def main():
    db.setup()
    user1 = "@praveenk"
    db.handleUsername(user1)
    user2 = "@testrun2"
    user3 = "@testrun3"
    db.setSession(user1, "This Week")
    db.changeTimeslot(user1, "Mon", "9am")
    db.changeTimeslot(user1, "Mon", "11am")
    db.changeTimeslot(user1, "Mon", "1pm")
    db.setSession(user1, "Next Week")
    db.changeTimeslot(user1, "Mon", "5pm")
    db.changeTimeslot(user1, "Mon", "9pm")
    print(db.getTimeslot(user1, "Mon"))
    db.rolloverSchedules()
    print(db.getTimeslot(user1, "Mon"))
    db.rolloverSchedules()
    print(db.getTimeslot(user1, "Mon"))
    db.purgeUserData()

if __name__ == '__main__':
    main()