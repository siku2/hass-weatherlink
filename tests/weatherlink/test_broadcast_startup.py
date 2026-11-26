import asyncio
import logging
from unittest.mock import AsyncMock, Mock, patch

import pytest
from aiohttp import ClientConnectorError
from weatherlink import WeatherLinkBroadcast, WeatherLinkCoordinator


@pytest.mark.parametrize("failures, warnings", [(1, 0), (4, 1)])
def test_broadcast_startup_retries(caplog, failures, warnings):
    station = Mock(host="station", port=80, ssl=False)
    refusal = ClientConnectorError(station, ConnectionRefusedError(111, "refused"))
    listener = AsyncMock()
    listener.read.side_effect = asyncio.CancelledError
    coordinator = Mock(spec=WeatherLinkCoordinator)
    coordinator.session = Mock()
    caplog.set_level(logging.INFO, logger="weatherlink")

    with (
        patch.object(
            WeatherLinkBroadcast, "start", side_effect=[refusal] * failures + [listener]
        ) as start,
        patch("weatherlink.asyncio.sleep", new_callable=AsyncMock) as sleep,
        pytest.raises(asyncio.CancelledError),
    ):
        asyncio.run(
            WeatherLinkCoordinator._WeatherLinkCoordinator__broadcast_loop(coordinator)
        )

    assert start.await_count == failures + 1
    assert [call.args for call in sleep.await_args_list] == [(3.0,)] * failures
    listener.read.assert_awaited_once()
    listener.stop.assert_awaited_once()
    assert [r.levelno for r in caplog.records] == [logging.WARNING] * warnings + [
        logging.INFO
    ]
    assert all(r.exc_info is None for r in caplog.records)
