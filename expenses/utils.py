import json
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


def read_from_json(file):
    with open(file) as f:
      data = json.load(f)
    return data


def safely_round(val, decimals=2):
    try:
        return round(val, decimals)
    except Exception:
        return 0   


def get_fallback_if_none(val, fallback):
    return safely_round(val, 2) if val else fallback


def get_percentage(a, b):
    if(a == 0 or b == 0):
        return 0
    return safely_round(((a / b) * 100), 2)


def get_current_week_iso_num():
    return date.today().isocalendar()[1]


def get_current_month_num():
    return date.today().month


def reformat_date(date, format):
    return date.strftime(format)


def get_current_date_num(date_type):
    if date_type == 'week' or date_type == 'weekend':
        return get_current_week_iso_num()
    else:
        return get_current_month_num()
    

def get_first_and_last_day_of_current_month():
    today = datetime.now()
    first_day_of_current_month = today.replace(day=1)
    next_month_date = today + relativedelta(months=+1)
    next_month_first_day_date = next_month_date.replace(day=1)
    last_day_of_the_current_month = next_month_first_day_date - timedelta(days=1)
    return {
      'first_day': first_day_of_current_month,
      'last_day': last_day_of_the_current_month
    }

def get_months_list():
    return [
        'January', 
        'February', 
        'March', 
        'April', 
        'May', 
        'June',
        'July', 
        'August', 
        'September', 
        'October', 
        'November', 
        'December'
    ]


def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)


class DateGenerator:

    @staticmethod
    def get_date(date=None):
        # Returns a date object that represents todays date or a date passed as an arugment!
        if(date is not None):
          return datetime.strptime(str(date), "%Y-%m-%d")
        else:
          return datetime.now()

    @staticmethod
    def get_date_one_week_ago():
        todays_date = DateGenerator.get_date()
        changed_date = todays_date + timedelta(days=-7)
        return DateGenerator.get_formated_date(changed_date)

    @staticmethod
    def get_date_two_week_ago():
        todays_date = DateGenerator.get_date()
        changed_date = todays_date + timedelta(days=-14)
        return DateGenerator.get_formated_date(changed_date)

    @staticmethod
    def get_date_three_week_ago():
        todays_date = DateGenerator.get_date()
        changed_date = todays_date + timedelta(days=-21)
        return DateGenerator.get_formated_date(changed_date)

    @staticmethod
    def get_date_one_month_ago():
        todays_date = DateGenerator.get_date()
        changed_date = todays_date.replace(month=todays_date.month -1)
        return DateGenerator.get_formated_date(changed_date)

    @staticmethod
    def get_date_two_months_ago():
        todays_date = DateGenerator.get_date()
        changed_date = todays_date.replace(month=todays_date.month -2)
        return DateGenerator.get_formated_date(changed_date)

    @staticmethod
    def get_date_three_months_ago():
        todays_date = DateGenerator.get_date()
        changed_date = todays_date.replace(month=todays_date.month -3)
        return DateGenerator.get_formated_date(changed_date)

    @staticmethod
    def modify_date_with_timedelta(date, num_days):
        todays_date = DateGenerator.get_date(date) if date else DateGenerator.get_date()
        changed_date = todays_date + timedelta(days=num_days)
        return DateGenerator.get_formated_date(changed_date)

    @staticmethod
    def get_formated_date(date=None):
        # Returns a date string in the format : yyyy-mm-dd!
        if date:
          return datetime.strftime(date, '%Y-%m-%d')
        else:
          return datetime.strftime(DateGenerator.get_date(), '%Y-%m-%d')


class ExpenseGenerator:
    def __init__(self, model, expense_config, owner):
        self.model = model
        self.expense_obj = expense_config
        self.owner = owner
        self.expenses_by_date = read_from_json('expenses/expensesByDate.json')
        #self.expenses_by_date_length = len(self.expenses_by_date)

    def modify_expense_date(self, expense_index, date_section, expense_data, days_to_add):
        if(expense_index != 0 and
          (date_section == "today" or
          date_section == "one_month_ago" or
          date_section == "two_month_ago" or
          date_section == "three_month_ago")):

          days_to_add += 1
          current_date = expense_data['date']
          expense_data['date'] = DateGenerator.modify_date_with_timedelta(current_date, days_to_add)

    def generate_expenses(self):
        expenses = []

        for date_section in self.expenses_by_date:
          days_to_add = 0
          date_section_expenses = self.expenses_by_date[date_section]

          for expense_data in date_section_expenses:
            expense_index = date_section_expenses.index(expense_data)
            self.add_date_to_expense(date_section, expense_data)
            self.modify_expense_date(expense_index, date_section, expense_data, days_to_add)

            expense = self.model(
              amount=expense_data['amount'],
              content=expense_data['content'],
              category=expense_data['category'],
              source=expense_data['source'],
              date=expense_data['date'],
              owner=self.owner
            )
            expenses.append(expense)
        return expenses

    def add_date_to_expense(self, date, expense):
        if(date == 'today'):
          expense['date'] = DateGenerator.get_formated_date()
        elif(date == 'one_week_ago'):
          expense['date'] = DateGenerator.get_date_one_week_ago()
        elif(date == 'two_weeks_ago'):
          expense['date'] = DateGenerator.get_date_two_week_ago()
        elif(date == 'three_weeks_ago'):
          expense['date'] = DateGenerator.get_date_three_week_ago()
        elif(date == 'one_month_ago'):
          expense['date'] = DateGenerator.get_date_one_month_ago()
        elif(date == 'two_month_ago'):
          expense['date'] = DateGenerator.get_date_two_months_ago()
        elif(date == 'three_month_ago'):
          expense['date'] = DateGenerator.get_date_three_months_ago()
        else:
          print(f'Unrecognized date given: ', {date})

