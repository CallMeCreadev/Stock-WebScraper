from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import os, time

class OptionsChainScraper:
    @staticmethod
    def init_driver(headless=True, use_chromium=False):
        opts = Options()
        if headless:
            opts.add_argument("--headless=new")      # use "--headless" if "new" isn't supported
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1920,1080")

        # If the process runs as root (cron/systemd), avoid sandbox errors:
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            opts.add_argument("--no-sandbox")

        # Only if you’re using Chromium from apt instead of Google Chrome:
        # if use_chromium:
        #     opts.binary_location = "/usr/bin/chromium-browser"

        service = Service()  # Selenium Manager handles chromedriver
        return webdriver.Chrome(service=service, options=opts)
    @staticmethod
    def get_options_chain_summary(driver, table_id, ticker_price, option_type):
        table = driver.find_element(By.ID, table_id)
        open_interest_sum = 0
        nearest_strike_diff = float('inf')
        p_nearest_strike_diff = float('inf')
        last_price_nearest_strike = None
        max_open_interest = 0
        strike_with_max_oi = None
        last_price_matching_strike = None
        rows = table.find_elements(By.TAG_NAME, 'tr')[1:]
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            strike = float(cells[0].text.strip())
            last_price = float(cells[4].text.strip())
            open_interest = int(cells[6].text.strip())
            open_interest_sum += open_interest
            if open_interest > max_open_interest:
                max_open_interest = open_interest
                strike_with_max_oi = strike
            if option_type == 'call':
                strike_diff = abs(strike - ticker_price)
                if strike_diff < nearest_strike_diff:
                    nearest_strike_diff = strike_diff
                    last_price_nearest_strike = last_price
            elif option_type == 'put':
                p_strike_diff = abs(strike - ticker_price)
                if p_strike_diff < p_nearest_strike_diff:
                    p_nearest_strike_diff = p_strike_diff
                    last_price_matching_strike = last_price
        if option_type == 'call':
            return {
                'total_open_interest': open_interest_sum,
                'last_price_nearest_strike': last_price_nearest_strike,
                'strike_with_max_oi': strike_with_max_oi
            }
        elif option_type == 'put':
            return {
                'total_open_interest': open_interest_sum,
                'last_price_matching_strike': last_price_matching_strike
            }

    @staticmethod
    def get_ticker_price(driver):
        ticker_price_element = driver.find_element(By.ID, 'ticker-price')
        return float(ticker_price_element.text.strip())

    @staticmethod
    def get_max_pain_value(driver):
        max_pain_element = driver.find_element(By.XPATH, "//div[@id='max-pain-container']//span[@class='stat-highlight']")
        return float(max_pain_element.text.strip().replace('$', ''))

    @staticmethod
    def prune_data(data):
        current_date = datetime.now()
        pruned_data = {
            'within_7_days': None,
            'within_30_days': None,
            'within_90_days': None
        }
        max_open_interest_7_days = 0
        max_open_interest_30_days = 0
        max_open_interest_90_days = 0
        for entry in data:
            entry_date = datetime.strptime(entry['date'], '%Y-%m-%d')
            days_diff = (entry_date - current_date).days
            if 0 <= days_diff <= 7 and entry['total_open_interest'] > max_open_interest_7_days:
                pruned_data['within_7_days'] = entry
                max_open_interest_7_days = entry['total_open_interest']
            if 0 <= days_diff <= 30 and entry['total_open_interest'] > max_open_interest_30_days:
                pruned_data['within_30_days'] = entry
                max_open_interest_30_days = entry['total_open_interest']
            if 0 <= days_diff <= 90 and entry['total_open_interest'] > max_open_interest_90_days:
                pruned_data['within_90_days'] = entry
                max_open_interest_90_days = entry['total_open_interest']
        return pruned_data
    
    @staticmethod
    def find_max_volumes():
        url = 'https://www.stockninja.io/stocks/spy/options/'
        driver = OptionsChainScraper.init_driver(headless=True)
        driver.get(url)
        
        wait = WebDriverWait(driver, 10)
        select_element = wait.until(EC.presence_of_element_located((By.ID, 'options-date')))
        select = Select(select_element)
        
        data = []
        for i in range(16):
            select_element = wait.until(EC.presence_of_element_located((By.ID, 'options-date')))
            select = Select(select_element)
            options = select.options
            
            option = options[i]
            date = option.get_attribute('value')
            
            select.select_by_index(i)
            time.sleep(3)
            
            ticker_price = OptionsChainScraper.get_ticker_price(driver)
            max_pain = OptionsChainScraper.get_max_pain_value(driver)
            
            calls_summary = OptionsChainScraper.get_options_chain_summary(driver, 'call-options-chain', ticker_price,
                                                                          'call')
            puts_summary = OptionsChainScraper.get_options_chain_summary(driver, 'put-options-chain', ticker_price,
                                                                         'put')
            if calls_summary['total_open_interest'] == 0 or puts_summary['total_open_interest'] == 0:
                continue
            
            expected_high = ticker_price + calls_summary['last_price_nearest_strike']
            expected_low = ticker_price - puts_summary['last_price_matching_strike']
            put_call_ratio = round(puts_summary['total_open_interest'] / calls_summary['total_open_interest'], 2)
            total_oi = puts_summary['total_open_interest'] + calls_summary['total_open_interest']
            
            data.append({
                'date': date,
                'ticker_price': ticker_price,
                'max_pain': max_pain,
                'total_open_interest': calls_summary['total_open_interest'],
                'expected_high': expected_high,
                'expected_low': expected_low,
                'strike_with_max_oi': calls_summary['strike_with_max_oi'],
                'put_call_ratio': put_call_ratio,
                'total_oi': total_oi
            })
        
        driver.quit()
        driver.quit()
        
        pruned_data = OptionsChainScraper.prune_data(data)
        
        final_data = []
        for key in ['within_7_days', 'within_30_days', 'within_90_days']:
            entry = pruned_data.get(key)
            if entry:
                final_data.append({
                    'date': entry['date'],
                    'current_price': entry['ticker_price'],
                    'max_p': entry['max_pain'],
                    'highest_call_OI': entry['strike_with_max_oi'],
                    'expected_high': entry['expected_high'],
                    'expected_low': entry['expected_low'],
                    'put_call_ratio': entry['put_call_ratio'],
                    'total_OI': entry['total_oi']
                })
            else:
                final_data.append({
                    'date': None,
                    'current_price': None,
                    'max_p': None,
                    'highest_call_OI': None,
                    'expected_high': None,
                    'expected_low': None,
                    'put_call_ratio': None,
                    'total_OI': None
                })
        
        return final_data



