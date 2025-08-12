from .insiders_extract import InsiderExtract
from .bonds import Bonds
from .sectors import Sectors
from .ratios import Ratios
from .options_scraper import OptionsChainScraper
from utils.utils import Utils
class WebExtractor:

    @staticmethod
    def get_options():
        volumes = OptionsChainScraper.find_max_volumes()
        result = Utils.options_data_prep_function(volumes)
        return result

    @staticmethod
    def get_insiders():
        extractor = InsiderExtract()
        insider_dict = extractor.scrape_all_insider_plays()
        executive_dict = extractor.scrape_executive_plays()
        major_dict = extractor.scrape_major_insider_plays()
        result = Utils.insiders_data_prep(insider_dict, executive_dict, major_dict)
        return result

    @staticmethod
    def get_bonds():
        raw_data = Utils.process_bond_sector_data(Bonds.get_bonds_dictionary())
        clean = Utils.replace_second_num_lod(raw_data)
        return clean

    @staticmethod
    def get_ratios():
        result = Ratios.get_spy_ratios()
        return result

    @staticmethod
    def get_sectors():
        raw_data = Utils.process_bond_sector_data(Sectors.get_sectors_dictionary())
        clean = Utils.replace_second_num_lod(raw_data)
        return clean
