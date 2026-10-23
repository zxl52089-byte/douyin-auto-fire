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
