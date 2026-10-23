from unittest.mock import AsyncMock, MagicMock

import pytest

from app.douyin import PageOperationError
from app.sender import _click_and_confirm_sticker


@pytest.mark.asyncio
async def test_failed_sticker_does_not_trigger_automatic_retry(monkeypatch) -> None:
    item = MagicMock()
    item.get_attribute = AsyncMock(return_value=None)
    item.click = AsyncMock()
    image = MagicMock()
    image.count = AsyncMock(return_value=0)
    item.locator.return_value = MagicMock(first=image)

    async def fail_confirmation(*_args, **_kwargs):
        raise PageOperationError("原生表情发送失败，页面提示可以重试")

    retry = AsyncMock(return_value=True)
    monkeypatch.setattr("app.sender._confirm_sticker_sent", fail_confirmation)
    monkeypatch.setattr("app.sender._click_retry_on_latest_failed_message", retry)

    with pytest.raises(PageOperationError, match="发送失败"):
        await _click_and_confirm_sticker(MagicMock(), item, ("anchor", "old"), "比心")

    retry.assert_not_awaited()


@pytest.mark.asyncio
async def test_uncertain_sticker_state_does_not_press_send(monkeypatch) -> None:
    item = MagicMock()
    item.get_attribute = AsyncMock(return_value=None)
    item.click = AsyncMock()
    image = MagicMock()
    image.count = AsyncMock(return_value=0)
    item.locator.return_value = MagicMock(first=image)

    async def unconfirmed(*_args, **_kwargs):
        raise PageOperationError("原生表情发送状态未能确认（发送超时或状态不确定），为避免重复不会自动重试")

    async def must_not_send(*_args, **_kwargs):
        raise AssertionError("状态不确定时不应再次按发送")

    monkeypatch.setattr("app.sender._confirm_sticker_sent", unconfirmed)
    monkeypatch.setattr("app.sender._publish_ready", AsyncMock(return_value=True))
    monkeypatch.setattr("app.sender._trigger_send", must_not_send)

    with pytest.raises(PageOperationError, match="发送状态未能确认"):
        await _click_and_confirm_sticker(MagicMock(), item, ("anchor", "old"), "比心")
