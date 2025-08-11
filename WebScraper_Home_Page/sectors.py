import datetime
from datetime import datetime, timedelta
from utils.utils import Utils

class Sectors:

    @staticmethod
    def get_sectors_list():
        sectors = {
            'XLK': 'Technology',
            'XLY': 'Consumer Discretionary',
            'XLI': 'Industrials',
            'XLF': 'Financials',
            'XLC': 'Communication Services',
            'XLE': 'Energy',
            'XLB': 'Materials',
            'XLRE': 'Real Estate',
            'XLV': 'Health Care',
            'XLP': 'Consumer Staples',
            'XLU': 'Utilities'
        }
        return sectors

    @staticmethod
    def get_sectors_dictionary(today=None):
        if today is None:
            today = datetime.now()
        sectors = Sectors.get_sectors_list()
        one_week_ago = (today - timedelta(days=7)).date()
        one_month_ago = (today - timedelta(days=30)).date()
        one_quarter_ago = (today - timedelta(days=90)).date()
        sectors_data_week = {}
        sectors_data_month = {}
        sectors_data_quarter = {}

        for ticker, sector in sectors.items():
            today_price, _ = Utils.get_historical_price(ticker, today)
            one_week_ago_price, one_week_ago_valid_date = Utils.get_historical_price(ticker, one_week_ago)
            one_month_ago_price, one_month_ago_valid_date = Utils.get_historical_price(ticker, one_month_ago)
            one_quarter_ago_price, one_quarter_ago_valid_date = Utils.get_historical_price(ticker, one_quarter_ago)
            sectors_data_week[ticker] = [today_price, one_week_ago_price]
            sectors_data_month[ticker] = [today_price, one_month_ago_price]
            sectors_data_quarter[ticker] = [today_price, one_quarter_ago_price]
        return sectors_data_week, sectors_data_month, sectors_data_quarter



if __name__ == "__main__":
    raw_data = Utils.process_bond_sector_data(Sectors.get_sectors_dictionary())
    clean = Utils.replace_second_num_lod(raw_data)
    print(clean)
