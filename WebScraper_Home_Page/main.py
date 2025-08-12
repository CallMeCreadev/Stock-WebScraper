
from .web_extraction import WebExtractor
from .mongo_handler import MongoHandler


if __name__ == "__main__":

    insiders = WebExtractor.get_insiders()
    options = WebExtractor.get_options()
    bonds = WebExtractor.get_bonds()
    ratios = WebExtractor.get_ratios()
    sectors = WebExtractor.get_sectors()
    data = MongoHandler.combine_bonds_sectors_ratios_insiders_options_in_order(bonds, sectors, ratios, insiders, options)
    packaged_data = MongoHandler.package_data_for_mongo(data)
    print(packaged_data)
    MongoHandler.save_to_mongo_collection(packaged_data, "in_the_money", "basic_data")





