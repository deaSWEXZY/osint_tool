from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import User, Channel
import json
from dotenv import load_dotenv
import os


class UserSearchTg:
    def __init__(self, target, export_file = ""):
        load_dotenv() # Hidden in .env file
        self.API_ID = int(os.getenv("API_ID_TG", 0))
        self.API_HASH = os.getenv("API_HASH_TG")
        self.TARGET = target
        self.EXPORT_FILE = export_file
        self.SAVE_DIR = "results_search_telegram"
        self.PATH_FOR_RESULTS_JSON = f"{self.SAVE_DIR}/{self.TARGET}_results.json"

        self.results = []
        self.client = TelegramClient('user_session', self.API_ID, self.API_HASH)

    async def search_engine(self):
        try:
            entity = await self.client.get_entity(self.TARGET)
            user_data = {
                "id": entity.id,
                "name": getattr(entity, 'first_name', getattr(entity, 'title', 'N/A')),
                "username": entity.username or "N/A",
                "bio": "N/A"
            }

            if isinstance(entity, User):
                full_user = await self.client(GetFullUserRequest(entity))
                user_data["bio"] = full_user.full_user.about or "N/A"
            elif isinstance(entity, Channel):
                full_channel = await self.client(GetFullChannelRequest(entity))
                user_data["bio"] = full_channel.full_chat.about or "N/A"
            self.results.append(user_data)
            print(f"Successfully scraped: {user_data['username']}")

        except Exception as e:
            print(f"Error: {e}")

    def saving_in_json(self):
        with open(self.PATH_FOR_RESULTS_JSON, "w") as file:
            json.dump(self.results, file, indent=4)

    def saving_results(self):
        if self.EXPORT_FILE == "json":
            os.makedirs(self.SAVE_DIR, exist_ok=True)
            self.saving_in_json()
        else:
            pass
    def running(self):
        with self.client:
            self.client.loop.run_until_complete(self.search_engine())

if __name__ == "__main__":
    test_target = 'durov'
    search = UserSearchTg(test_target, export_file="json")
    print("testing...")
    search.running()
    search.saving_results()
    