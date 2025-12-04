import asyncio
from aiohttp import web

from mayday import init_app, app


async def main():
    try:
        await init_app()
        app.logger.info("======= Serving on http://localhost:8000/ ======")
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8000)

        app.session_tracker.start()
        app.api_cache_refresher.start()

        max_attempts = 3
        attempt_number = 1
        while attempt_number < max_attempts:
            await asyncio.sleep(attempt_number * 2)
            try:
                if not app.hcp.logged_in:
                    await app.hcp.login()
                    break
            except Exception:
                attempt_number += 1
                continue
        else:
            app.logger.error("Initial Housecall Pro login never succeeded")

        if attempt_number <= max_attempts:
            await site.start()
            await asyncio.Event().wait()
        else:
            app.logger.error("Server never started. Critical integration (Housecall Pro) never started")

    finally:
        app.session_tracker.shutdown()
        app.api_cache_refresher.shutdown()
        app.hcp.shutdown()
        app.logger.info("Shutting down, goodbye")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())