from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import User, Channel
import json
import pandas as pd
from colorama import Fore, init
from dotenv import load_dotenv
import os

init(autoreset=True)

class UserSearchTg:
    def __init__(self, target, export_file = ""):
        load_dotenv() # Hidden in .env file
        self.API_ID = int(os.getenv("API_ID_TG", 0))
        self.API_HASH = os.getenv("API_HASH_TG")
        self.BOT_TOKEN = os.getenv("BOT_TOKEN_TG")
        self.TARGET = target
        self.EXPORT_FILE = export_file
        self.SAVE_DIR = "results_search"
        self.PATH_FOR_RESULTS_JSON = f"{self.SAVE_DIR}/{self.TARGET}_results_telegram.json"
        self.PATH_FOR_RESULTS_CSV = f"{self.SAVE_DIR}/{self.TARGET}_results_telegram.csv"

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

    def file_format_json(self):
        with open(self.PATH_FOR_RESULTS_JSON, "w") as file:
            json.dump(self.results, file, indent=4)

    def file_format_csv(self):
            pd.DataFrame(self.results).to_csv(self.PATH_FOR_RESULTS_CSV, index=False, encoding='utf-8')

    def saving_results(self):
        if self.EXPORT_FILE == "json":
            self.file_format_json()
            print(Fore.BLUE + f"[*] Results for Telegram securely saved to {self.PATH_FOR_RESULTS_CSV}")
        if self.EXPORT_FILE == "csv":
            self.file_format_csv()
            print(Fore.BLUE + f"[*] Results for Telegram securely saved to {self.PATH_FOR_RESULTS_JSON}")
        
    def running(self):
        self.client.start(bot_token=self.BOT_TOKEN)
        with self.client:
            self.client.loop.run_until_complete(self.search_engine())