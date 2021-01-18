from datetime import datetime
import asyncio
from pyppeteer import launch
import logging
import sys

logger = logging.getLogger("asyncio")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

BASE_URL = "https://bmvs.onlineappointmentscheduling.net.au/oasis/"
FILE_PATH_TPL = "{}_{}.png"

expected_date_val_max = int(sys.argv[1])#20210130 # 20210130 # 20210330
suburb = "3008"
state = "VIC"
TAKE_SCREENSHOT = False


def get_current_ts():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


async def take_screen_shot(page, ts, file_name):
    if TAKE_SCREENSHOT:
        logger.debug("Taking Screenshot ...")
        await page.screenshot({'path': FILE_PATH_TPL.format(ts, file_name)})
        logger.debug("Screenshot taken ...")


async def main(ts):
    logger.debug("Launching Browser ...")
    browser = await launch({'headless': True})
    logger.debug("Opening new page ...")
    page = await browser.newPage()
    logger.debug("Opening '{}'".format(BASE_URL))
    await page.setViewport({"width": 800, "height": 1000})
    await page.goto(BASE_URL) #, {"waitUntil": 'load', "timeout": 30000}
    await take_screen_shot(page, ts, "Page1")

    # Click on Individual Booking
    logger.debug("Selecting Individual Booking ...")
    await page.click("[id='ContentPlaceHolder1_btnInd']")
    await take_screen_shot(page, ts, "Page2")

    # Provide Location details
    logger.debug("Providing Location Details ...")
    await page.waitFor('input[id=ContentPlaceHolder1_SelectLocation1_txtSuburb]')
    await page.focus('#ContentPlaceHolder1_SelectLocation1_txtSuburb') # TextBox
    await page.keyboard.type(suburb)
    await page.select('#ContentPlaceHolder1_SelectLocation1_ddlState', state) # Dropdown List
    await take_screen_shot(page, ts, "Page3")

    logger.debug("Submitting location Details ...")
    await page.click('input[type="submit"]') # Submit Button

    # Select Test Center
    logger.debug("Selecting Test Center ...")
    await page.waitFor('#rbLocation5')
    await page.click("#rbLocation5", {"clickCount": 1}) # Radio Button
    await take_screen_shot(page, ts, "Page4")

    await page.click("#ContentPlaceHolder1_btnCont")  # Button with ID

    # Select Required Tests
    await page.waitFor('#chkClass1_489')
    await page.click("#chkClass1_489", {"clickCount": 1})
    await page.click("#chkClass1_492", {"clickCount": 1})
    await take_screen_shot(page, ts, "Page5")

    await page.click("#ContentPlaceHolder1_btnCont")  # Button with ID

    # Now Check the Available date
    await page.waitFor('#ContentPlaceHolder1_SelectTime1_txtAppDate')
    elem = await page.querySelector("#ContentPlaceHolder1_SelectTime1_txtAppDate")
    await take_screen_shot(page, ts, "Page6")

    logger.debug("Date Elem : {}".format(elem.__dict__))
    date_val_obj = await elem.getProperty("value")
    date_val = date_val_obj.__dict__.get("_remoteObject", dict()).get("value")
    logger.debug("Date Value : {}".format(date_val))
    date_val_elems = date_val.split("/")
    date_val_int = int("{}{}{}".format(date_val_elems[2], date_val_elems[1], date_val_elems[0]))

    if date_val_int <= expected_date_val_max:
        logger.info(date_val)
    else:
        logger.info("Opps. Current Available Date is : {}".format(date_val))

    await browser.close()
    logger.debug("Browser closed ...")

this_ts = get_current_ts()
asyncio.get_event_loop().run_until_complete(main(this_ts))


