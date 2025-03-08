// Login
function login() {
    let emailInput = document.querySelector('#id_username');
    let pwdInput = document.querySelector('#id_password');
    let submitButton = document.querySelector(".login-form button[type='submit']");
    emailInput.value = "koussawojean@gmail.com";
    pwdInput.value = "NmdpJ360-2704";
    submitButton.click();
}
if (document.readyState === 'complete') { login(); } else { window.addEventListener('load', login); }


// Login check

() => {
    let itemsList = document.querySelector(".results-list");
    return itemsList;
}

// Sorting
async function sortDescCot() {
    let itemsList;
    let limitDateButton;
    while (!(!!itemsList && !!limitDateButton)) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        itemsList = document.querySelector(".results-list");
        limitDateButton = document.querySelector("#filters > div > div > div.col-sm-12.toggles > div > span > span.btn-group > a:nth-child(2)");
        console.log('why????')
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
console.log('why!!!');

// sort v2
function sortDescCot() {
    let itemsList = document.querySelector(".results-list");
    let limitDateButton = document.querySelector("#filters > div > div > div.col-sm-12.toggles > div > span > span.btn-group > a:nth-child(2)");
    let sortDescLimitDate = () => {
        limitDateButton.click();
        itemsSortObserver.disconnect()
    }
    let itemsSortObserver = new MutationObserver(sortDescLimitDate);
    itemsSortObserver.observe(itemsList, {childList: true, subtree: true});
    limitDateButton.click(); // First click
    window.removeEventListener('load', sortDescCot);
}
if (document.readyState === "complete") { console.log('doc ready'); sortDescCot(); } else { window.addEventListener('load', sortDescCot); }


// Sorting check
() => {
    let dropDownIcon = document.querySelector(".sort-item [ng-show=\"filters.order_by == '-date_limite'\"]");
    return !dropDownIcon.classList.contains('ng-hide');
}

// Next page

async function getAndWaitNextPage() {
    const getCurrentCommit = () => document.querySelector(".results-list").textContent.trim();
    const initialCommit = getCurrentCommit();
    document.querySelector("a[ng-click=\"selectPage(page + 1)\"]").click();
    while (getCurrentCommit() === initialCommit) {
        await new Promise(resolve => setTimeout(resolve, 100));
    }
}
getAndWaitNextPage();
