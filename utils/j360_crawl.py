import json
import os
import csv
import asyncio
import time
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BrowserConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy, LLMExtractionStrategy
from models.AOYulcom import AOYulcom
from utils.crawl_utils import store_to_csv

COT_EXTRACT_SCHEMA = {
    "name": "CoT",
    "baseSelector": ".result",
    "baseFields": [{"name": "url", "attribute": "href", "type": "attribute", },],
    "fields": [
        {"name": "title", "selector": ".title", "type": "text" },
        {"name": "deadline", "selector": ".deadline span span:nth-child(2)", "type": "text" },
        {"name": "location", "selector": ".country span", "type": "text" },
        {"name": "amounts", "selector": ".[ng-show='result.amount'] .detail-extra-value", "type": "text" },
        {"name": "publication", "selector": ".[ng-show='result.extraction_date'] .detail-extra-value", "type": "text" },
    ]
}


LOGIN_SCRIPT = [
    """
        function login() {
            let emailInput = document.querySelector('#id_username');
            let pwdInput = document.querySelector('#id_password');
            let submitButton = document.querySelector(".login-form button[type='submit']");
            emailInput.value = \"""" + os.getenv("ACCOUNT_EMAIL") + """\";
            pwdInput.value = \"""" + os.getenv("ACCOUNT_PASS") + """\";
            submitButton.click();
        }
        if (document.readyState === 'complete') { login(); } else { window.addEventListener('load', login); }
    """,
]

LOGIN_CHECK_SCRIPT = """() => {
    let itemsList = document.querySelector(".results-list");
    return itemsList;
}"""


SORT_COT_SCRIPT = [
    """
        async function sortDescCot() {
            let itemsList;
            let limitDateButton;
            while (!(!!itemsList && !!limitDateButton)) {
                await new Promise(resolve => setTimeout(resolve, 1000));
                itemsList = document.querySelector(".results-list");
                limitDateButton = document.querySelector("#filters > div > div > div.col-sm-12.toggles > div > span > span.btn-group > a:nth-child(2)");
            }
            let sortDescLimitDate = () => {
                limitDateButton.click();
                itemsSortObserver.disconnect()
            }
            let itemsSortObserver = new MutationObserver(sortDescLimitDate);
            itemsSortObserver.observe(itemsList, {childList: true, subtree: true});
            limitDateButton.click(); // First click
        }
        await sortDescCot();
    """,
]

SORT_COT_CHECK_SCRIPT = """() => {
    let dropDownIcon = document.querySelector(".sort-item [ng-show=\"filters.order_by == '-date_limite'\"]");
    return !dropDownIcon.classList.contains('ng-hide');
}"""


NEXT_PAGE_SCRIPT = """
    async function getAndWaitNextPage() {
        const getCurrentCommit = () => document.querySelector(".results-list").textContent.trim();
        const initialCommit = getCurrentCommit();
        document.querySelector("a[ng-click=\"selectPage(page + 1)\"]").click();
        while (getCurrentCommit() === initialCommit) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }
    getAndWaitNextPage();
"""

async def log_in(crawler, session_id="cot_crawl") :
    crawler_config = CrawlerRunConfig(
        cache_mode = CacheMode.BYPASS,
        js_code=LOGIN_SCRIPT,
        wait_for=f"js:{LOGIN_CHECK_SCRIPT}",
        session_id=session_id,
    )
    return await crawler.arun(
        url="https://app.j360.info/#/my-monitoring/searches/45511",
        config=crawler_config,
    )


async def sort_cots(crawler, session_id="cot_crawl") :
    crawler_config = CrawlerRunConfig(
        cache_mode = CacheMode.BYPASS,
        js_code=SORT_COT_SCRIPT,
        wait_for=f"js:{SORT_COT_CHECK_SCRIPT}",
        session_id=session_id,
    )
    return await crawler.arun(
        url="https://app.j360.info/#/my-monitoring/searches/45511",
        config=crawler_config,
    )

async def extract_cots(crawler, session_id="cot_crawl") :
    data = []
    extraction_strategy = JsonCssExtractionStrategy(COT_EXTRACT_SCHEMA, verbose=True)
    for page in range(50) :
        crawler_config = CrawlerRunConfig(
            session_id=session_id,
            extraction_strategy=extraction_strategy,
            cache_mode = CacheMode.BYPASS,
            js_code=NEXT_PAGE_SCRIPT if page else None,
            js_only=page>0,
        )
        result = await crawler.arun(
            url="https://app.j360.info/#/my-monitoring/searches/45511",
            config=crawler_config,
        )
        data = data + json.loads(result.extracted_content)
        store_to_csv(data, f"./temp/j360_crawl{page}.csv")
        time.sleep(2)
    return data


async def crawl(session_id="cot_crawl") :
    browser_config = BrowserConfig(
        browser_type = "chromium",
        verbose = True,
        headless = False,
    )
    async with AsyncWebCrawler(config=browser_config) as crawler:
        login_result = await log_in(crawler, session_id)
        sort_result = await sort_cots(crawler, session_id)
        time.sleep(2)
        if not sort_result.success :
            print('error sorting')
            return []
        data = await extract_cots(crawler, session_id)
        data = format_data_url(data)
        print(json.dumps(data, indent=2))
        store_to_csv(data, 'j360_crawl.csv')
        return data


def format_data_url(data) :
    formated = []
    for datum in data :
        datum['url'] = "https://app.j360.info/"+datum['url']
        formated.append(datum)
    return formated
    
