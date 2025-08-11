import datetime
from datetime import datetime, timedelta
from utils.utils import Utils

class Ratios:
    @staticmethod
    def get_ratios_list():
        labels = ["spy_dow", "spy_qqq", "spy_copper", "spy_hyg", "spy_rut", "spy_eqw"]
        tickers = ["^DJI", "QQQ", "HG=F", "^RUT", "HYG", "^SPXEW"]

        return labels, tickers

    @staticmethod
    def get_spy_ratios(today=None):
        if today is None:
            today = datetime.now()
        ratio_labels, tickers = Ratios.get_ratios_list()
        one_week_ago = (today - timedelta(days=7)).date()
        one_month_ago = (today - timedelta(days=30)).date()
        one_quarter_ago = (today - timedelta(days=90)).date()
        ticker_data_week = {}
        ticker_data_month = {}
        ticker_data_quarter = {}
        spy_current, _ = Utils.get_historical_price("SPY", today)
        spy_week, _ = Utils.get_historical_price("SPY", one_week_ago)
        spy_month, _ = Utils.get_historical_price("SPY", one_month_ago)
        spy_quarter, _ = Utils.get_historical_price("SPY", one_quarter_ago)

        for ticker in tickers:
            today_price, _ = Utils.get_historical_price(ticker, today)
            one_week_ago_price, _ = Utils.get_historical_price(ticker, one_week_ago)
            one_month_ago_price, _ = Utils.get_historical_price(ticker, one_month_ago)
            one_quarter_ago_price, _ = Utils.get_historical_price(ticker, one_quarter_ago)
            ticker_data_week[ticker] = [(spy_current / today_price) / (spy_current / today_price),
                                        (0-((spy_week / one_week_ago_price) - (spy_current / today_price)) / (
                                                 spy_current / today_price))]
            ticker_data_month[ticker] = [(spy_current / today_price) / (spy_current / today_price),
                                         (0-((spy_month / one_month_ago_price) - (spy_current / today_price)) / (
                                                     spy_current / today_price))]
            ticker_data_quarter[ticker] = [(spy_current / today_price) / (spy_current / today_price),
                                           (0-((spy_quarter / one_quarter_ago_price) - (spy_current / today_price)) / (
                                                    spy_current / today_price))]

        processed_week = Ratios.process_ratios(ticker_data_week)
        processed_month = Ratios.process_ratios(ticker_data_month)
        processed_quarter = Ratios.process_ratios(ticker_data_quarter)

        return processed_week, processed_month, processed_quarter


    @staticmethod
    def process_ratios(data):
        stacked_bars = {'DJI_SPY': data['^DJI'],
                        'QQQ_SPY': data['QQQ'],
                        'RUT_SPY': data['^RUT'],
                        'HYG_SPY': data['HYG'],
                        'HGF_SPY': data['HG=F'],
                        'EQW_SPY': data['^SPXEW']
                        }
        return stacked_bars

if __name__ == "__main__":
    print(Ratios.get_spy_ratios())