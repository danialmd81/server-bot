from sqlitedict import SqliteDict

my_sql = SqliteDict("my_sql.sqlite3", "Users")


class Users:
    username = ""
    auth_user = ""
    auth_pass = ""


def url():
    return my_sql["URL"]


def bot_token():
    return my_sql["BOT_TOKEN"]


def change_bot_token(token: str):
    my_sql["BOT_TOKEN"] = token
    my_sql.commit()


def add_user(user: Users):
    my_sql[user.username] = user.__dict__
    my_sql.commit()


def user(username: str):
    item = my_sql[username]
    temp_user = Users()
    temp_user.username = username
    temp_user.auth_user = item["auth_user"]
    temp_user.auth_pass = item["auth_pass"]
    return temp_user


def save(key, value, cache_file="cache.sqlite3"):
    try:
        with SqliteDict(cache_file) as mydict:
            mydict[key] = value
            mydict.commit()
    except Exception as ex:
        print("Error during storing data (Possibly unsupported):", ex)


def load(key, cache_file="cache.sqlite3"):
    try:
        with SqliteDict(cache_file) as mydict:
            value = mydict[
                key]  # No need to use commit(), since we are only loading data!
        return value
    except Exception as ex:
        print("Error during loading data:", ex)


# my_sql["URL"] = "https://iutbox.iut.ac.ir/
# user1 = Users()
# user1.username = "Danialmdh81"


# user2 = Users()
# user2.username = "Lo0111011001100101"

# ///////////////////////////////////////////////////////////////////////////////

# my_sql[user1.username] = user1.__dict__
# my_sql.commit()

# ///////////////////////////////////////////////////////////////////////////////

# ite = my_sql["Danialmdh81"]
# print(ite["auth_user"])
# print(ite["auth_pass"])
# print(ite["username"])
# print(my_sql["URL"])
# print(my_sql["BOT_TOKEN"])
