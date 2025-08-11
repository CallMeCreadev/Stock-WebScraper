import datetime
from urllib import parse
import requests
from bs4 import BeautifulSoup
from urllib import parse




class URLBuilder:
    def __init__(self, base_url, params=None):
        self.base_url = base_url
        self.params = params or {}

    def set_url_field(self, key, value):
        self.params[key] = value

    def build_url(self):
        query_string = parse.urlencode(self.params)
        return f'{self.base_url}?{query_string}'


class InsiderExtract:
    def __init__(self):
        self.params = {
            's': '',
            'o': '',
            'pl': '',
            'ph': '',
            'll': '',
            'lh': '',
            'fd': '-1',
            'fdr': '04/05/2023 - 04/21/2023',
            'td': '-1',
            'tdr': '04/05/2023 - 04/21/2023',
            'fdlyl': '',
            'fdlyh': '',
            'daysago': '',
            'xs': '',
            'xp': '',
            'vl': '',
            'vh': '',
            'ocl': '',
            'och': '',
            'sic1': '-1',
            'sicl': '100',
            'sich': '9999',
            'isofficer': '1',
            'iscob': '1',
            'isceo': '1',
            'ispres': '1',
            'iscoo': '1',
            'iscfo': '1',
            'isgc': '1',
            'isvp': '1',
            'isdirector': '1',
            'istenpercent': '1',
            'grp': '0',
            'nfl': '',
            'nfh': '',
            'nil': '',
            'nih': '',
            'nol': '',
            'noh': '',
            'v2l': '',
            'v2h': '',
            'oc2l': '',
            'oc2h': '',
            'sortcol': '0',
            'cnt': '5000',
            'page': '1'
        }

    def create_total_urls(self):
        url_builder = URLBuilder('http://openinsider.com/screener', params=self.params)
        lookback = 6
        sell_urls = {}
        buy_urls = {}
        dates = self.get_date_range(lookback)

        print(dates)
        url_builder.set_url_field('fdr', dates[lookback+1] + ' - ' + dates[0])
        url_builder.set_url_field('tdr', dates[lookback+1] + ' - ' + dates[0])
        url_builder.set_url_field('xs', '1')
        url_builder.set_url_field('xp', '')
        temp = url_builder.build_url()
        sell_urls[str(lookback+1)] = temp

        url_builder.set_url_field('fdr', dates[lookback + 1] + ' - ' + dates[0])
        url_builder.set_url_field('tdr', dates[lookback + 1] + ' - ' + dates[0])
        url_builder.set_url_field('xp', '1')
        url_builder.set_url_field('xs', '')
        temp = url_builder.build_url()
        buy_urls[str(lookback+1)] = temp



        for i in range(1, lookback+1):
            url_builder.set_url_field('fdr', dates[i] + ' - ' + dates[i-1])
            url_builder.set_url_field('tdr', dates[i] + ' - ' + dates[i-1])
            url_builder.set_url_field('xs', '1')
            url_builder.set_url_field('xp', '')
            sell_urls[str(i)] = url_builder.build_url()

            url_builder.set_url_field('fdr', dates[i] + ' - ' + dates[i - 1])
            url_builder.set_url_field('tdr', dates[i] + ' - ' + dates[i - 1])
            url_builder.set_url_field('xp', '1')
            url_builder.set_url_field('xs', '')
            buy_urls[str(i)] = url_builder.build_url()

        return sell_urls, buy_urls


    def count_purchase_elements(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            purchase_elements = soup.find_all("td", string="P - Purchase")
            return len(purchase_elements) - 1
        else:
            print(f"Error: {response.status_code}")
            return 0

    def get_date_range(self, n):
        today = datetime.datetime.now().date()
        dates = [today - datetime.timedelta(days=15 * (i+1)) for i in range(n)]
        prev_week_date = today - datetime.timedelta(days=7)
        dates.append(prev_week_date)
        dates.insert(0, today)  # Add today's date to the beginning of the list
        date_strings = [d.strftime('%m/%d/%Y') for d in dates]
        return date_strings

    def scrape_major_insider_plays(self):
        urls_to_scrape = self.get_major_insider_urls()
        major_insider_numbers = {
            'weekly_buys': self.count_purchase_elements(urls_to_scrape[0]),
            'weekly_sales': self.count_sale_elements(urls_to_scrape[1]),
            'monthly_buys': self.count_purchase_elements(urls_to_scrape[2]),
            'monthly_sales': self.count_sale_elements(urls_to_scrape[3]),
            'quarterly_buys': self.count_purchase_elements(urls_to_scrape[4]),
            'quarterly_sales': self.count_sale_elements(urls_to_scrape[5])
        }
        return major_insider_numbers

    def scrape_executive_plays(self):
        urls_to_scrape = self.get_executive_urls()
        executive_numbers = {
            'weekly_buys': self.count_purchase_elements(urls_to_scrape[0]),
            'weekly_sales': self.count_sale_elements(urls_to_scrape[1]),
            'monthly_buys': self.count_purchase_elements(urls_to_scrape[2]),
            'monthly_sales': self.count_sale_elements(urls_to_scrape[3]),
            'quarterly_buys': self.count_purchase_elements(urls_to_scrape[4]),
            'quarterly_sales': self.count_sale_elements(urls_to_scrape[5])
        }
        return executive_numbers


    def scrape_all_insider_plays(self):
        insider_extractor = InsiderExtract()
        url_sells, url_buys = insider_extractor.create_total_urls()
        weekly_buys = 0
        monthly_buys = 0
        quarterly_buys = 0
        weekly_sells = 0
        monthly_sells = 0
        quarterly_sells = 0
        for i in range(1, 8):
            if i < 3:
                monthly_buys += insider_extractor.count_purchase_elements(url_buys[str(i)])
                monthly_sells += insider_extractor.count_sale_elements(url_sells[str(i)])

            if i < 7:
                quarterly_buys += insider_extractor.count_purchase_elements(url_buys[str(i)])
                quarterly_sells += insider_extractor.count_sale_elements(url_sells[str(i)])

            if i == 7:
                weekly_buys = insider_extractor.count_purchase_elements(url_buys[str(i)])
                weekly_sells = insider_extractor.count_sale_elements(url_sells[str(i)])

        insider_numbers = {
            'weekly_buys': weekly_buys,
            'weekly_sales': weekly_sells,
            'monthly_buys': monthly_buys,
            'monthly_sales': monthly_sells,
            'quarterly_buys': quarterly_buys,
            'quarterly_sales': quarterly_sells
        }
        return insider_numbers

    def count_sale_elements(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            sale_elements = soup.find_all("td", string="S - Sale")
            return len(sale_elements) - 1
        else:
            print(f"Error: {response.status_code}")
            return 0

    def get_major_insider_urls(self):
        quarter_insider_sells = "http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=90&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=5000&vh=&ocl=&och=-20&sic1=-1&sicl=100&sich=9999&isofficer=1&iscob=1&isceo=1&ispres=1&iscoo=1&iscfo=1&isgc=1&isvp=1&isdirector=1&istenpercent=1&isother=1&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1"
        quarter_insider_buys = "http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=90&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=5000&vh=&ocl=20&och=&sic1=-1&sicl=100&sich=9999&isofficer=1&iscob=1&isceo=1&ispres=1&iscoo=1&iscfo=1&isgc=1&isvp=1&isdirector=1&istenpercent=1&isother=1&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1"
        month_insider_buys = "http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=30&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=5000&vh=&ocl=20&och=&sic1=-1&sicl=100&sich=9999&isofficer=1&iscob=1&isceo=1&ispres=1&iscoo=1&iscfo=1&isgc=1&isvp=1&isdirector=1&istenpercent=1&isother=1&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1"
        month_insider_sells = "http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=30&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=5000&vh=&ocl=&och=-20&sic1=-1&sicl=100&sich=9999&isofficer=1&iscob=1&isceo=1&ispres=1&iscoo=1&iscfo=1&isgc=1&isvp=1&isdirector=1&istenpercent=1&isother=1&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1"
        week_insider_sells = "http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=7&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=5000&vh=&ocl=&och=-20&sic1=-1&sicl=100&sich=9999&isofficer=1&iscob=1&isceo=1&ispres=1&iscoo=1&iscfo=1&isgc=1&isvp=1&isdirector=1&istenpercent=1&isother=1&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1"
        week_insider_buys = "http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=7&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=5000&vh=&ocl=20&och=&sic1=-1&sicl=100&sich=9999&isofficer=1&iscob=1&isceo=1&ispres=1&iscoo=1&iscfo=1&isgc=1&isvp=1&isdirector=1&istenpercent=1&isother=1&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1"

        param_urls = [week_insider_buys, week_insider_sells, month_insider_buys, month_insider_sells, quarter_insider_buys, quarter_insider_sells]
        return param_urls

    def get_executive_urls(self):
        weekly_executive_buys = "http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=7&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=500&vh=&ocl=10&och=&sic1=-1&sicl=100&sich=9999&isceo=1&iscoo=1&iscfo=1&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1"
        weekly_executive_sells = "http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=7&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=500&vh=&ocl=&och=-10&sic1=-1&sicl=100&sich=9999&isceo=1&iscoo=1&iscfo=1&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1"
        month_executive_buys = "http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=30&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=500&vh=&ocl=10&och=&sic1=-1&sicl=100&sich=9999&isceo=1&iscoo=1&iscfo=1&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1"
        month_executive_sells = "http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=30&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=500&vh=&ocl=&och=-10&sic1=-1&sicl=100&sich=9999&isceo=1&iscoo=1&iscfo=1&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1"
        quarter_executive_buys = "http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=90&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=500&vh=&ocl=10&och=&sic1=-1&sicl=100&sich=9999&isceo=1&iscoo=1&iscfo=1&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1"
        quarter_executive_sells = "http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=90&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=500&vh=&ocl=&och=-10&sic1=-1&sicl=100&sich=9999&isceo=1&iscoo=1&iscfo=1&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1"

        param_urls = [weekly_executive_buys, weekly_executive_sells, month_executive_buys, month_executive_sells, quarter_executive_buys, quarter_executive_sells]
        return param_urls





if __name__ == "__main__":
    insider_extractor = InsiderExtract()
    insider_dict = insider_extractor.scrape_all_insider_plays()
    executive_dict = insider_extractor.scrape_executive_plays()
    major_dict = insider_extractor.scrape_major_insider_plays()
    print(insider_dict)
    print(executive_dict)
    print(major_dict)


