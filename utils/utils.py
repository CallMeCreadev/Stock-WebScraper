import yfinance as yf
import pandas as pd
import pytz
import time
from datetime import datetime, timedelta
class Utils:


    @staticmethod
    def insiders_data_prep_function(insider_data_all, insider_data_exc, insider_data_maj) :
        sb_insiders_weekly = {
            'all_purchases_to_sales': [insider_data_all['weekly_buys'], insider_data_all['weekly_sales']],
            'executive_purchases_to_sales': [insider_data_exc['weekly_buys'], insider_data_exc['weekly_sales']],
            'major_purchases_to_sales': [insider_data_maj['weekly_buys'], insider_data_maj['weekly_sales']]
        }
        sb_insiders_monthly = {
            'all_purchases_to_sales': [insider_data_all['monthly_buys'], insider_data_all['monthly_sales']],
            'executive_purchases_to_sales': [insider_data_exc['monthly_buys'], insider_data_exc['monthly_sales']],
            'major_purchases_to_sales': [insider_data_maj['monthly_buys'], insider_data_maj['monthly_sales']]
        }
        sb_insiders_quarterly = {
            'all_purchases_to_sales': [insider_data_all['quarterly_buys'], insider_data_all['quarterly_sales']],
            'executive_purchases_to_sales': [insider_data_exc['quarterly_buys'], insider_data_exc['quarterly_sales']],
            'major_purchases_to_sales': [insider_data_maj['quarterly_buys'], insider_data_maj['quarterly_sales']]
        }

        return [sb_insiders_weekly, sb_insiders_monthly, sb_insiders_quarterly]




    @staticmethod
    def options_data_barify(dollar1, dollar2):
        price = Utils.convert_dollar_to_float(dollar1)
        compare = Utils.convert_dollar_to_float(dollar2) - Utils.convert_dollar_to_float(dollar1)
        return price, compare

    @staticmethod
    def options_data_prep_function(list_frames):
        week_data = list_frames[0]
        month_data = list_frames[1]
        quarter_data = list_frames[2]

        proper_week_bars = {
            'price_to_max_pain': Utils.options_data_barify(week_data['current_price'], week_data['max_p']),
            'price_to_largest_call_OI':  Utils.options_data_barify(week_data['current_price'], week_data['highest_call_OI']),
            'price_to_expected_high': Utils.options_data_barify(week_data['current_price'], week_data['expected_high']),
            'price_to_expected_low': Utils.options_data_barify(week_data['current_price'], week_data['expected_low']),
        }
        proper_month_bars = {
            'price_to_max_pain': Utils.options_data_barify(month_data['current_price'], month_data['max_p']),
            'price_to_largest_call_OI':  Utils.options_data_barify(month_data['current_price'], month_data['highest_call_OI']),
            'price_to_expected_high': Utils.options_data_barify(month_data['current_price'], month_data['expected_high']),
            'price_to_expected_low': Utils.options_data_barify(month_data['current_price'], month_data['expected_low']),
        }
        proper_quarter_bars = {
            'price_to_max_pain': Utils.options_data_barify(quarter_data['current_price'], quarter_data['max_p']),
            'price_to_largest_call_OI':  Utils.options_data_barify(quarter_data['current_price'], quarter_data['highest_call_OI']),
            'price_to_expected_high': Utils.options_data_barify(quarter_data['current_price'], quarter_data['expected_high']),
            'price_to_expected_low': Utils.options_data_barify(quarter_data['current_price'], quarter_data['expected_low']),
        }

        proper_week_meta = {
            'put_call_ratio': week_data['put_call_ratio'],
            'total_OI': week_data['total_OI'],
            'date': week_data['date']
        }
        proper_month_meta = {
            'put_call_ratio': month_data['put_call_ratio'],
            'total_OI': month_data['total_OI'],
            'date': month_data['date']
        }
        proper_quarter_meta = {
            'put_call_ratio': quarter_data['put_call_ratio'],
            'total_OI': quarter_data['total_OI'],
            'date': quarter_data['date']
        }

        return [proper_week_bars,  proper_month_bars, proper_quarter_bars, proper_week_meta, proper_month_meta,
                proper_quarter_meta]





    @staticmethod
    def replace_second_num(lst):
        for key, value in lst.items():
            lst[key] = (value[0], value[1] - value[0])
        return lst

    def replace_second_num_lod(lst):
        count = 0
        for d in lst:
            count += 1
            if count > 8:
                break
            for key, value in d.items():
                d[key] = (value[0], value[1] - value[0])
        return lst

    @staticmethod
    def convert_dollar_to_float(value):
        if isinstance(value, str) and value.startswith("$"):
            return float(value[1:])
        else:
            return float(value)

    @staticmethod
    def insiders_data_prep(insider_dict, executive_dict, major_dict):
        insiders_data_prep_result = Utils.insiders_data_prep_function(insider_dict, executive_dict, major_dict)
        """insiders_data_prep_result = [{'all_purchases_to_sales': [86, 189], 'executive_purchases_to_sales': [0, 4],
                                      'major_purchases_to_sales': [1, 5]},
                                     {'all_purchases_to_sales': [604, 1145], 'executive_purchases_to_sales': [11, 38],
                                      'major_purchases_to_sales': [8, 10]},
                                     {'all_purchases_to_sales': [2824, 6373], 'executive_purchases_to_sales': [40, 267],
                                      'major_purchases_to_sales': [44, 97]}]"""
        insiders_week = Utils.replace_second_num(insiders_data_prep_result[0])
        insiders_month = Utils.replace_second_num(insiders_data_prep_result[1])
        insiders_quarter = Utils.replace_second_num(insiders_data_prep_result[2])
        return [insiders_week, insiders_month, insiders_quarter]

    @staticmethod
    def wait_for_page(sleep_time):
        time.sleep(sleep_time)
    
    @staticmethod
    def get_historical_price(ticker, date):
        stock = yf.Ticker(ticker)
        
        valid_date = Utils.find_closest_valid_date(ticker, date)
        if not valid_date:
            return None, None
        
        # Ensure we pass a clean, tz-naive day window
        start = pd.Timestamp(valid_date)  # works with date or datetime
        end = start + pd.Timedelta(days=1)
        
        # Pull a single daily bar
        hist = stock.history(start=start, end=end, interval="1d", auto_adjust=False)
        
        if hist is None or hist.empty or 'Close' not in hist:
            return None, None
        
        # Use positional indexing (future-proof)
        close = float(hist['Close'].iloc[0])  # or .iat[0] for a tiny speed bump
        return close, start.date()

    @staticmethod
    def find_closest_valid_date(ticker, target_date):
        stock = yf.Ticker(ticker)
        target_date = pd.Timestamp(target_date, tz=pytz.UTC)  # Make the target_date timezone-aware
        historical_data = stock.history(start=target_date - timedelta(days=30),
                                        end=target_date + timedelta(days=30))

        if not historical_data.empty:
            closest_date = historical_data.index.get_indexer([target_date], method='nearest')[0]
            return historical_data.index[closest_date]
        else:
            return None
    @staticmethod
    def get_current_price(ticker):
        stock = yf.Ticker(ticker)
        todays_data = stock.history(period='1d')
        return todays_data['Close'][0]

    @staticmethod
    def sum_1st_variable(my_dict):
        total_sum = 0
        for symbol in my_dict:
            total_sum += my_dict[symbol][0]
        return total_sum

    @staticmethod
    def sum_2nd_variable(my_dict):
        total_sum = 0
        for symbol in my_dict:
            total_sum += my_dict[symbol][1]
        return total_sum

    @staticmethod
    def apply_func_to_dict(original_dict, func, n1, n2):
        new_dict = {}
        for symbol, values in original_dict.items():
            new_dict[symbol] = (func(values[0], n1), func(values[1], n2))
        return new_dict

    @staticmethod
    def ratio(value, divider):
        return (value / divider) * 100.00


    @staticmethod
    def process_bond_sector_data(raw_data):
        bonds_data_week = raw_data[0]
        bonds_data_month = raw_data[1]
        bonds_data_quarter = raw_data[2]


        sum_today = Utils.sum_1st_variable(bonds_data_week)
        sum_weekly = Utils.sum_2nd_variable(bonds_data_week)
        sum_monthly = Utils.sum_2nd_variable(bonds_data_month)
        sum_quarterly = Utils.sum_2nd_variable(bonds_data_quarter)

        processed_data_week = Utils.apply_func_to_dict(bonds_data_week, Utils.ratio, sum_today, sum_weekly)
        processed_data_month = Utils.apply_func_to_dict(bonds_data_month, Utils.ratio, sum_today, sum_monthly)
        processed_data_quarter = Utils.apply_func_to_dict(bonds_data_quarter, Utils.ratio, sum_today, sum_quarterly)


        processed_data = [
                          processed_data_week, processed_data_month, processed_data_quarter,
                          ]

        return processed_data


if __name__ == "__main__":
    insiders_data_prep_result = [{'all_purchases_to_sales': [86, 189], 'executive_purchases_to_sales': [0, 4], 'major_purchases_to_sales': [1, 5]},
    {'all_purchases_to_sales': [604, 1145], 'executive_purchases_to_sales': [11, 38], 'major_purchases_to_sales': [8, 10]},
    {'all_purchases_to_sales': [2824, 6373], 'executive_purchases_to_sales': [40, 267], 'major_purchases_to_sales': [44, 97]}]
    insiders_week = Utils.replace_second_num(insiders_data_prep_result[0])
    insiders_month = Utils.replace_second_num(insiders_data_prep_result[1])
    insiders_quarter = Utils.replace_second_num(insiders_data_prep_result[2])
    print(insiders_week)
