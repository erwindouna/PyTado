import pytest
from unittest import mock
from PyTado.__main__ import main
from PyTado.interface import Tado


def test_entry_point_no_args():
    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 2


@mock.patch("PyTado.__main__.Tado", autospec=True)
def test_entry_point_get_me(mock_tado):
    mock_tado_instance = mock_tado.return_value
    mock_tado_instance.get_me.return_value = {"name": "Test User"}

    test_args = [
        "--email",
        "test@example.com",
        "--password",
        "password",
        "get_me",
    ]

    with mock.patch("sys.argv", ["main.py"] + test_args):
        with pytest.raises(SystemExit) as excinfo:
            main()

    assert excinfo.value.code == 0
    mock_tado.assert_called_once_with("test@example.com", "password")
    mock_tado_instance.get_me.assert_called_once()


@mock.patch("PyTado.__main__.Tado", autospec=True)
def test_entry_point_get_state(mock_tado):
    mock_tado_instance = mock_tado.return_value
    mock_tado_instance.get_state.return_value = {"zone": 1, "state": "heating"}

    test_args = [
        "--email",
        "test@example.com",
        "--password",
        "password",
        "get_state",
        "--zone",
        "1",
    ]

    with mock.patch("sys.argv", ["main.py"] + test_args):
        with pytest.raises(SystemExit) as excinfo:
            main()

    assert excinfo.value.code == 0
    mock_tado.assert_called_once_with("test@example.com", "password")
    mock_tado_instance.get_state.assert_called_once_with(1)


@mock.patch("PyTado.__main__.Tado", autospec=True)
def test_entry_point_get_states(mock_tado):
    mock_tado_instance = mock_tado.return_value
    mock_tado_instance.get_zone_states.return_value = [{"zone": 1, "state": "heating"}]

    test_args = [
        "--email",
        "test@example.com",
        "--password",
        "password",
        "get_states",
    ]

    with mock.patch("sys.argv", ["main.py"] + test_args):
        with pytest.raises(SystemExit) as excinfo:
            main()

    assert excinfo.value.code == 0
    mock_tado.assert_called_once_with("test@example.com", "password")
    mock_tado_instance.get_zone_states.assert_called_once()


@mock.patch("PyTado.__main__.Tado", autospec=True)
def test_entry_point_get_capabilities(mock_tado):
    mock_tado_instance = mock_tado.return_value
    mock_tado_instance.get_capabilities.return_value = {"zone": 1, "capabilities": "full"}

    test_args = [
        "--email",
        "test@example.com",
        "--password",
        "password",
        "get_capabilities",
        "--zone",
        "1",
    ]

    with mock.patch("sys.argv", ["main.py"] + test_args):
        with pytest.raises(SystemExit) as excinfo:
            main()

    assert excinfo.value.code == 0
    mock_tado.assert_called_once_with("test@example.com", "password")
    mock_tado_instance.get_capabilities.assert_called_once_with(1)
