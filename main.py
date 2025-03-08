from utils.j360_crawl import log_in, sort_cots, crawl
import asyncio
import json
from dotenv import load_dotenv
import time

load_dotenv()

async def extract_jobs():
    await crawl()
    

asyncio.run(extract_jobs())