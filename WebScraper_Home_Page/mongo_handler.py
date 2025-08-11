import os
from datetime import datetime, timedelta
from pymongo import MongoClient  # works the same
from dotenv import load_dotenv

# Load environment variables once
load_dotenv()

class MongoHandler:

    @staticmethod
    def combine_bonds_sectors_ratios_insiders_options_in_order(bonds, sectors, ratios, insiders, options):
        result = []
        for part in (bonds, sectors, ratios, insiders, options):
            if part is None:
                continue
            if isinstance(part, (list, tuple)):
                result.extend(part)
            else:
                raise TypeError(f"Expected list/tuple, got {type(part).__name__}")
        return result

    @staticmethod
    def create_nested_dict(name, timestamp, additional_info):
        return {"name": name, "timestamp": timestamp, "additional_info": additional_info}

    @staticmethod
    def package_data_for_mongo(list_of_dict):
        row_names = [
            "week-bonds", "month-bonds", "quarter-bonds",
            "week-sectors", "month-sectors", "quarter-sectors",
            "week-ratios", "month-ratios", "quarter-ratios",
            "week-insiders", "month-insiders", "quarter-insiders",
            "week-options", "month-options", "quarter-options",
            "meta-week-options", "meta-month-options", "meta-quarter-options"
        ]

        # Use UTC for consistency with delete filter
        now_utc = datetime.utcnow()

        # Trim to the shorter of the two to avoid IndexError
        n = min(len(list_of_dict), len(row_names))
        return [
            MongoHandler.create_nested_dict(row_names[i], now_utc, list_of_dict[i])
            for i in range(n)
        ]

    @staticmethod
    def delete_documents_older_than(mongo_collection, days):
        days_ago = datetime.utcnow() - timedelta(days=days)
        delete_result = mongo_collection.delete_many({"timestamp": {"$lt": days_ago}})
        print(f"{delete_result.deleted_count} documents deleted")

    @staticmethod
    def save_to_mongo_collection(documents, db_name, collection_name):
        if not documents:
            print("No documents to insert; skipping insert_many.")
            return None

        uri = MongoHandler.get_mongodb_uri()
        if not uri:
            raise RuntimeError("MONGODB_URI is not set in .env")

        # Context manager ensures close even on exceptions
        with MongoClient(uri) as client:
            try:
                client.admin.command("ping")
                print("Pinged your deployment. Connected to MongoDB!")
            except Exception as e:
                print("Failed to connect to MongoDB:", e)
                raise

            db = client[db_name]
            mongo_collection = db[collection_name]
            return mongo_collection.insert_many(documents)

    @staticmethod
    def get_mongodb_uri():
        return os.getenv("MONGODB_URI")

    @staticmethod
    def get_mongodb_db():
        return os.getenv("MONGODB_DB")  # optional, set in .env if you like


if __name__ == "__main__":
    uri = MongoHandler.get_mongodb_uri()
    if not uri:
        raise RuntimeError("MONGODB_URI missing from .env file")

    db_name = MongoHandler.get_mongodb_db() or "in_the_money"
    with MongoClient(uri) as client:
        db = client[db_name]
        mongo_collection = db["basic_data"]
        MongoHandler.delete_documents_older_than(mongo_collection, 5)
        print("Complete")
