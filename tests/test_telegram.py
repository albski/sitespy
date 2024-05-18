import pytest
import sitespy.telegram as telegram
import pytest_httpx


@pytest.mark.asyncio
async def test_telegram(httpx_mock: pytest_httpx.HTTPXMock):
    telegram_data = telegram.Telegram("fake_token", ["111", "222", "333"])

    bot = telegram.AsyncTelegramBot(telegram_data)

    httpx_mock.add_response(
        url=f"https://api.telegram.org/bot{telegram_data.token}/sendMessage",
        json={"ok": True},
        status_code=200,
    )
    httpx_mock.add_response(
        url=f"https://api.telegram.org/bot{telegram_data.token}/sendMessage",
        json={"ok": False, "error_code": 500},
        status_code=500,
    )
    httpx_mock.add_response(
        url=f"https://api.telegram.org/bot{telegram_data.token}/sendMessage",
        json={"ok": True},
        status_code=200,
    )

    results = await bot.send_message("Hello, World!", in_background=False)
    print("Results from send_message:", results)
    assert len(httpx_mock.get_requests()) == 3
