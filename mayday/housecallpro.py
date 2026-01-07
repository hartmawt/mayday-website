import asyncio
import calendar
import json
import os
from datetime import datetime

from playwright.async_api import async_playwright
from requests import Session

from mayday.logger import logger


HOUSECALLPRO_USERNAME = os.environ["HOUSECALLPRO_USERNAME"]
HOUSECALLPRO_PASSWORD = os.environ["HOUSECALLPRO_PASSWORD"]
SERVICE_CATEGORY = os.environ.get("SEVICE_CATEGORY", "pbcat_6a37aed5cdfa46e0b83c3ad4101db1f0")
DOMAIN = os.environ.get("SEVICE_CATEGORY", "pro.housecallpro.com")
SERVICES_URI = os.environ.get("SERVICES_URI", "/alpha/pricebook/services")
CALENDAR_URI = os.environ.get("CALENDAR_URI", "/alpha/scheduling/calendar_items/organization_calendar_items?start_date=%s&end_date=%s")


LOGIN_URL = f"https://{DOMAIN}"
SERVICES_URL = f"https://{DOMAIN}{SERVICES_URI}?pricebook_category_uuid={SERVICE_CATEGORY}"
CALENDAR_URL = f"https://{DOMAIN}/{CALENDAR_URI}"


class HouseCallProIntegration:
    def __init__(self):
        self.session = Session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }
        self.logged_in = False
        self.keep_alive = True

    def shutdown(self):
        self.keep_alive = False
        if self.logged_in:
            self.session.delete(f"https://{DOMAIN}/api/sessions")

    async def playwright(self):
        # Playwright setup
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch()
        context = await browser.new_context(ignore_https_errors=True)
        await context.set_extra_http_headers(self.session.headers)
        driver = await context.new_page()

        async def close():
            await browser.close()
            await playwright.stop()

        return type('Mock Object', (object,), {
            'playwright': playwright,
            'browser': browser,
            'context': context,
            'driver': driver,
            'close': close
        })

    async def login(self):
        logger.info(f"Starting login process for {DOMAIN}")
        logger.info(f"Username configured: {bool(HOUSECALLPRO_USERNAME)}")
        logger.info(f"Password configured: {bool(HOUSECALLPRO_PASSWORD)}")
        
        playwright = await self.playwright()
        try:
            logger.info(f"Navigating to login URL: {LOGIN_URL}")
            await playwright.driver.goto(LOGIN_URL, wait_until="domcontentloaded")
            logger.info("Page loaded successfully")
            
            username_field = playwright.driver.locator('//*[@id="email"]')
            await username_field.wait_for(state="visible")
            await username_field.fill(HOUSECALLPRO_USERNAME)

            password_field = playwright.driver.locator('//*[@id="password"]')
            await password_field.wait_for(state="visible")
            await password_field.fill(HOUSECALLPRO_PASSWORD)

            submit_button = playwright.driver.locator("//span[text()='Sign in']")
            await submit_button.wait_for(state="visible")
            await submit_button.click()

            await asyncio.sleep(2)
            current_url = playwright.driver.url
            page_title = await playwright.driver.title()
            logger.info(f"After login click - URL: {current_url}, Title: {page_title}")
            two_factor_indicators = [
                "//input[@type='text' and contains(@placeholder, 'code')]",
                "//input[@type='text' and contains(@placeholder, 'verification')]",
                "//*[contains(text(), 'verification code')]",
                "//*[contains(text(), 'two-factor')]",
                "//*[contains(text(), '2FA')]",
                "//*[contains(text(), 'authenticator')]",
                "//*[contains(text(), 'Enter code')]"
            ]
            
            two_factor_detected = False
            for indicator in two_factor_indicators:
                try:
                    element = playwright.driver.locator(indicator)
                    if await element.count() > 0:
                        logger.warning(f"Two-factor authentication detected! Found element: {indicator}")
                        two_factor_detected = True
                        break
                except Exception:
                    continue
            
            if two_factor_detected:
                logger.error("Login requires two-factor authentication. This is not currently supported.")
                try:
                    page_content = await playwright.driver.content()
                    logger.debug("Two-factor page content available for inspection")
                except Exception:
                    pass
                raise Exception("Two-factor authentication required but not supported")

            logger.info("Waiting for ajs_user_id cookie to confirm login success")
            max_wait_time = 30
            cookie_found = False

            for _ in range(max_wait_time):
                cookies = await playwright.context.cookies()
                for cookie in cookies:
                    if cookie['name'] == 'ajs_user_id':
                        logger.info(f"ajs_user_id cookie found: {cookie['value'][:10]}...")
                        cookie_found = True
                        break

                if cookie_found:
                    break

                await asyncio.sleep(1)

            if not cookie_found:
                raise Exception("Login failed: ajs_user_id cookie not found within timeout period")

            logger.info("Login successful - ajs_user_id cookie confirmed")

            logger.info("Extracting cookies from browser session")
            cookie_count = 0
            for c in await playwright.context.cookies():
                cookie = {k:v for k,v in c.items() if k not in ['httpOnly', 'sameSite']}
                self.session.cookies.set(**cookie)
                cookie_count += 1
            logger.info(f"Extracted {cookie_count} cookies")
            
            # Get current URL from playwright
            ping_url = playwright.driver.url
            logger.info(f"Current URL after login: {ping_url}")

            # Login success, keep the session alive
            logger.info(f"Login succeeded with {DOMAIN}")
            async def ping(session, keep_alive, ping_url, interval=5*60):
                while keep_alive:
                    for _ in range(interval):
                        await asyncio.sleep(1)
                        if not keep_alive:
                            break

                    if keep_alive:
                        try:
                            session.get(ping_url)
                        except:
                            pass

            self.logged_in = True
            asyncio.ensure_future(ping(self.session, self.keep_alive, ping_url))
        
        except Exception as e:
            logger.error(f"Login failed with {DOMAIN}. Error details: {str(e)}")
            logger.error(f"Current page URL: {playwright.driver.url if playwright.driver else 'Unknown'}")
            
            # Try to capture page content for debugging
            try:
                page_content = await playwright.driver.content()
                if "error" in page_content.lower() or "invalid" in page_content.lower():
                    logger.error("Page contains error messages - check credentials or page structure")
                logger.debug(f"Page title: {await playwright.driver.title()}")
            except:
                logger.error("Could not capture page content for debugging")
                
            raise Exception(f"Login failed. Error: {e}")

        finally:
            await playwright.close()
    
    def get_calendar(self):
        # Check if we're logged in before attempting to fetch calendar
        if not self.logged_in:
            logger.info("HCP get_calendar called before login completion - login process may still be running")
            logger.info("Returning empty calendar data")
            return {"items": []}

        now = datetime.now()

        # Current month and year
        current_month = now.month
        current_year = now.year
        
        # Determine the number of days in the current month
        days_in_month = calendar.monthrange(current_year, current_month)[1]
    
        start_date = f"{current_year}-{current_month}-01T00:00:00.000Z"
        end_date = f"{current_year}-{current_month}-{days_in_month}T23:00:00.000Z"

        resp = self.session.get(CALENDAR_URL % (start_date, end_date))

        logger.info("Successfully gathered calendar events")
        return json.loads(resp.text)

    def get_services(self):
        services = {"online_bookable": []}

        # Check if we're logged in before attempting to fetch services
        if not self.logged_in:
            logger.info("HCP get_services called before login completion - login process may still be running")
            logger.info("Returning empty services - cache will be refreshed once login completes")
            return services

        try:
            resp = self.session.get(SERVICES_URL)
            logger.info(f"HCP API response status: {resp.status_code}")

            if resp.status_code != 200:
                logger.error(f"HCP API error: {resp.status_code} - {resp.text[:200]}")
                return services

            services_json = json.loads(resp.text)
            logger.info(f"HCP API response keys: {list(services_json.keys()) if services_json else 'None'}")

            data = services_json.get("data")
            if not data:
                logger.warning("No 'data' key in HCP API response or data is empty")
                logger.info(f"Full response: {services_json}")
                return services

            for service in data:
                services["online_bookable"].append({
                    "uuid": service["uuid"],
                    "name": service["name"],
                    "description": service["description"],
                    "image": service["image"] or "/static/img/service.png",
                    "price": int(service["price"]) / (10 ** 2) if service["price"] else ""
                })

            logger.info(f"Successfully gathered {len(services['online_bookable'])} HCP services")

        except Exception as e:
            logger.error(f"Error in HCP get_services: {e}")
            logger.error(f"Response text: {resp.text[:500] if 'resp' in locals() else 'No response'}")
            return services
        
        return services

