import datetime

# current_date = datetime.date.today()
week = ['Monday','Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

class Calendar_week():
    current_date = datetime.date.today()
    yr, wk_num, wk_day = current_date.isocalendar()
    month = current_date.strftime("%B")
    date = current_date.strftime("%d")
    week_day = current_date.strftime("%a")

    def return_weekarr(current_date,dates):
        dates = []
        for i in range(0,7):
            day = current_date + datetime.timedelta(days=i)
            dates.append(day.strftime("%d"))
        return str(dates)
