from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
from telethon.tl.types import User, Channel
import json
import pandas as pd
from colorama import Fore, init, Style
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

    async def search_engine_username(self):
        print(f"\n{Fore.GREEN + Style.BRIGHT}Starting Telegram Search..\n")
        try:
            entity = await self.client.get_entity(self.TARGET)
            
            # Download pfp
            path = await self.client.download_profile_photo(
                entity=entity, 
                file=f"{self.SAVE_DIR}/{self.TARGET}_pfp.jpg"
            )

            user_data = {
                "id": entity.id,
                "name": getattr(entity, 'first_name', getattr(entity, 'title', 'N/A')),
                "username": entity.username or "N/A",
                "bio": "N/A"
            }

            if path:
                print(f"{Fore.LIGHTBLUE_EX}Profile picture saved to {path}")
            else:
                print(f"{Fore.RED}Target doesn't have a pfp.")

            if isinstance(entity, User):
                full_user = await self.client(GetFullUserRequest(entity))
                user_data["bio"] = full_user.full_user.about or "N/A"
            elif isinstance(entity, Channel):
                full_channel = await self.client(GetFullChannelRequest(entity))
                user_data["bio"] = full_channel.full_chat.about or "N/A"

            self.results.append(user_data)
            print(f"Successfully scraped: {user_data['username']}")

        except Exception as e:
            print(f"{Fore.RED}Error: {e}")

    async def search_engine_mobile(self, phone_number):
        print(f"{Fore.BLUE}[*] Querying Telegram for: {phone_number}")
        contact = InputPhoneContact(
            client_id=0,
            phone=phone_number,
            first_name="Search",
            last_name="Swexzyy"
        )

        try:
            result = await self.client(ImportContactsRequest([contact]))

            if result.users:
                user = result.users[0]
                user_data = {
                    "id": user.id,
                    "name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
                    "username": f"@{user.username}" if user.username else "N/A",
                    "bio": "N/A"
                }
                self.results.append(user_data)
                print(f"Match found: {user_data['name']} ({user_data['username']})")
            else:
                print("No match found...")
        except Exception as e:
            print(f"{Fore.RED}Error during lookup: {e}")

    def file_format_json(self):
        with open(self.PATH_FOR_RESULTS_JSON, "w") as file:
            json.dump(self.results, file, indent=4)

    def file_format_csv(self):
        pd.DataFrame(self.results).to_csv(self.PATH_FOR_RESULTS_CSV, index=False, encoding='utf-8')

    def saving_results(self):
        if self.EXPORT_FILE == "json":
            self.file_format_json()
            print(Fore.BLUE + f"[*] Results for Telegram securely saved to {self.PATH_FOR_RESULTS_JSON}")
        elif self.EXPORT_FILE == "csv":
            self.file_format_csv()
            print(Fore.BLUE + f"[*] Results for Telegram securely saved to {self.PATH_FOR_RESULTS_CSV}")
        else:
            print(Fore.BLUE + "[*] Results for Telegram not saved.")

    def running(self):
        # NOTE: Phone contact lookups require User session (no bot token)
        self.client.start()
        with self.client:
            self.client.loop.run_until_complete(self.search_engine_username())