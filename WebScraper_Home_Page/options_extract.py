from utils.utils import Utils
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service



class OptionsExtract:

    @staticmethod
    def init_driver(driver_path):
        print(driver_path)
        service = Service(executable_path=driver_path)
        return webdriver.Chrome(service=service)

    @staticmethod
    def extract_tab_format(data, key_date):
        maxpain = {
            'current_price': data[1],
            'max_p': data[2],
            'highest call OI': data[3],
            'highest put OI': data[4],
            'total OI': data[7],
            'put_call_ratio': data[8],
            'date': str(key_date)
        }
        return maxpain

    @staticmethod
    def reformat_data(data, upper, lower):
        maxpain = {
            'current_price': data['current_price'],
            'max_p': data['max_p'],
            'highest call OI': data['highest call OI'],
            'highest put OI': data['highest put OI'],
            'total OI': data['total OI'],
            'put_call_ratio': data['put_call_ratio'],
            'date': data['date'],
            'expected_low': str(lower),
            'expected_high': str(upper)
        }
        return maxpain


    @staticmethod
    def to_html_parser_string(s):
        print(s)
        # Replace any double quotes with single quotes
        s = s.replace('"', "'")
        # Wrap the string in quotes
        s = '"' + s + '"'
        return s

    @staticmethod
    def get_expected_range(soup, target):
        for tr in soup.find_all('tr'):
            if len(tr.find_all('td')) > 5:
                td_fifth = tr.find_all('td')[4]
                for span in td_fifth.find_all('span'):
                    value_check = Utils.convert_dollar_to_float(span.text) - Utils.convert_dollar_to_float(target)
                    if value_check < 3  and value_check > -3:
                        print('Match found: ' + span.text)
                        call = tr.find_all('td')[0]
                        call_cost = call.text
                        put = tr.find_all('td')[5]
                        put_cost = put.text
                        total = Utils.convert_dollar_to_float(put_cost) + Utils.convert_dollar_to_float(call_cost)
                        expected_range = total * .85
                        price = Utils.convert_dollar_to_float(target)
                        lower = price - expected_range
                        upper = price + expected_range
                        return lower, upper

    @staticmethod
    def extract_data_from_column_by_class(soup, column_class, starting_column, number_of_columns, key_date):
        td_elements = soup.find_all('td', class_=column_class)

        if td_elements:
            values = [td.text.strip() for td in td_elements]
            data = values[starting_column:starting_column + number_of_columns]


            result = OptionsExtract.extract_tab_format(data, key_date)
            result_range = OptionsExtract.get_expected_range(soup, result['current_price'])
            if result_range is not None:
                lower, upper = result_range
                return OptionsExtract.reformat_data(result, upper, lower)
            else:
                return OptionsExtract.reformat_data(result, result['current_price'], result['current_price'])

        else:
            return None

    @staticmethod
    def simulate_user_interaction(driver, url, form_control, select_index):
        driver.get(url)


        Utils.wait_for_page(13)
        select = driver.find_element(By.CSS_SELECTOR, form_control)


        selector = Select(select)
        selector.select_by_index(select_index)
        selected_option = selector.first_selected_option
        key_date = selected_option.get_attribute("value")



        Utils.wait_for_page(8.5)
        html = driver.page_source

        return html, key_date

    @staticmethod
    def scrape_options_data(index):
        url = "https://maximum-pain.com/options/SPY"
        driver_path = "C:\\WebTools\\chromedriver.exe"
        options_dropdown = "select[formcontrolname='formMaturity']"
        number_of_columns = 9
        starting_column = 0

        driver = OptionsExtract.init_driver(driver_path)
        options_scrape_html, key_date = OptionsExtract.simulate_user_interaction(driver, url, options_dropdown, select_index = index)


        soup = BeautifulSoup(options_scrape_html, 'html.parser')
        if soup is None:
            print("soup is None")
        options_data_tab_1 = OptionsExtract.extract_data_from_column_by_class(soup, 'AlignRight', starting_column, number_of_columns, key_date)
        driver.quit()
        return options_data_tab_1
    @staticmethod
    def scrape_options_data_dictionaries(index):
        test_val = OptionsExtract.scrape_options_data(index)
        return test_val


    @staticmethod
    def find_max_volumes():
        max_volumes = []
        max_volume = 0
        today_dt = datetime.today()
        today_str = today_dt.strftime("%Y-%m-%d")
        first_pass = True
        second_pass = True
        for j in range(1, 61):
            print(j)
            target_dataframe = OptionsExtract.scrape_options_data(j)
            total_oi_str = target_dataframe['total OI']
            date_str = target_dataframe['date']
            total_oi_str = total_oi_str.replace(',', '')  # Remove commas from the string
            total_oi_float = float(total_oi_str)
            today = datetime.strptime(today_str, "%Y-%m-%d").date()
            date = datetime.strptime(date_str, "%m/%d/%Y").date()
            if total_oi_float > max_volume:
                max_volume = total_oi_float
                max_volume_dataframe = target_dataframe
            if (date - today).days >= 7 and first_pass:
                print(date)
                print(today)
                max_volumes.append(max_volume_dataframe)
                first_pass = False
            elif (date - today).days >= 26 and second_pass:
                print(date)
                print(today)
                max_volumes.append(max_volume_dataframe)
                second_pass = False
            elif (date - today).days >= 80:
                print(date)
                print(today)
                max_volumes.append(max_volume_dataframe)
                return max_volumes



if __name__ == "__main__":
    volumes = OptionsExtract.find_max_volumes()
    print(volumes[0])
    print(volumes[1])
    print(volumes[2])


#Go to https://www.stockninja.io/stocks/spy/options/
#Take the options data for 1 we