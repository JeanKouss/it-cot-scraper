from utils.j360_crawl import crawl
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def extract_jobs():
    await crawl()
    

asyncio.run(extract_jobs())