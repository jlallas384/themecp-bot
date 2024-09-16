import os
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

COMMAND_PREFIX = ';themecp '
TOKEN = os.environ.get('TOKEN')
DATA_FOLDER = Path(__file__).parent.absolute().joinpath('data')
DATABASE_URL = f'sqlite:///{DATA_FOLDER}/themecpbot.db'
# DATABASE_URL = f'sqlite:///:memory:'
