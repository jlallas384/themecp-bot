import os
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

COMMAND_PREFIX = ';themecp '
TOKEN = os.environ.get('TOKEN')
DATA_FOLDER = Path(__file__).parent.absolute().joinpath('data')
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL is None:
    DATABASE_URL = f'sqlite:///{DATA_FOLDER}/themecpbot.db'

if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
