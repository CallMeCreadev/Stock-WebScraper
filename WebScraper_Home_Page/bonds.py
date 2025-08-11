import datetime
from datetime import datetime, timedelta
from utils.utils import Utils

class Bonds:

    @staticmethod
    def get_bonds_list():
        bonds = {
            'HYG': 'High-yield',
            'TLT': 'Long-Term',
            'LQD': 'Investment-Grade',
            'AGG': 'Aggregate Bonds',
            'BNDX': 'International Bonds'
        }
        return bonds

    @staticmethod
    def get_bonds_dictionary(today=None):
        if today is None:
            today = datetime.now()
        bonds = Bonds.get_bonds_list()
        one_week_ago = (today - timedelta(days=7)).date()
        one_month_ago = (today - timedelta(days=30)).date()
        one_quarter_ago = (today - timedelta(days=90)).date()
        bonds_data_week = {}
        bonds_data_month = {}
        bonds_data_quarter = {}

        for ticker, sector in bonds.items():
            today_price, _ = Utils.get_historical_price(ticker, today)
            one_week_ago_price, one_week_ago_valid_date = Utils.get_historical_price(ticker, one_week_ago)
            one_month_ago_price, one_month_ago_valid_date = Utils.get_historical_price(ticker, one_month_ago)
            one_quarter_ago_price, one_quarter_ago_valid_date = Utils.get_historical_price(ticker, one_quarter_ago)
            bonds_data_week[ticker] = [today_price, one_week_ago_price]
            bonds_data_month[ticker] = [today_price, one_month_ago_price]
            bonds_data_quarter[ticker] = [today_price, one_quarter_ago_price]
        return bonds_data_week, bonds_data_month, bonds_data_quarter


if __name__ == "__main__":
    raw_data = Utils.process_bond_sector_data(Bonds.get_bonds_dictionary())
    clean = Utils.replace_second_num_lod(raw_data)
    print(clean)
