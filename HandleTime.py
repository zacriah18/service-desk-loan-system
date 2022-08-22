from datetime import datetime as dt
import datetime
import JsonReader


# convert seconds to milliseconds
def seconds_to_milli(time):
    return int(time * 1000)


# gets monday timestamp of current week
def get_unix_last_monday() -> int:
    days_since_monday = dt.today().date().weekday()  # default returns timestamp of monday
    return get_now_timestamp() - seconds_to_milli(days_since_monday * 24 * 60 * 60)  # convert to seconds


# Used Function in loanSystem.__init__, loanSystem.start_process
def get_now_timestamp() -> int:
    return seconds_to_milli(dt.now().timestamp())


# Used Function in loanSystem.state_decision
def get_today_timestamp(begin=True) -> int:  # if begin is true returns beginning of day, if false, end of day
    date = dt.today().date()
    #    date = datetime.date(date.year, date.month, date.day)
    if begin:
        time = datetime.time(0, 0)
    else:
        time = datetime.time(23, 59, 59, 999999)
    return seconds_to_milli(datetime.datetime.combine(date, time).timestamp())


# Used Function by loanSystem.start_process
def update_time_search_input() -> None:
    JsonReader.update_since_last_monday_input_data(get_unix_last_monday())
