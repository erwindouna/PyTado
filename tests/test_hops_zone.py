"""Test the TadoZone object."""

import json
import unittest
from unittest import mock

from . import common

from PyTado.http import Http
from PyTado.interface.api import TadoX


class TadoZoneTestCase(unittest.TestCase):
    """Test cases for zone class"""

    def setUp(self) -> None:
        super().setUp()
        login_patch = mock.patch(
            "PyTado.http.Http._login", return_value=(1, "foo")
        )
        is_x_line_patch = mock.patch(
            "PyTado.http.Http._check_x_line_generation", return_value=True
        )
        get_me_patch = mock.patch("PyTado.interface.api.Tado.get_me")
        login_patch.start()
        is_x_line_patch.start()
        get_me_patch.start()
        self.addCleanup(login_patch.stop)
        self.addCleanup(is_x_line_patch.stop)
        self.addCleanup(get_me_patch.stop)

        self.http = Http("my@username.com", "mypassword")
        self.tado_client = TadoX(self.http)

    def set_fixture(self, filename: str) -> None:
        def check_get_state(zone_id):
            assert zone_id == 1
            return json.loads(common.load_fixture(filename))

        get_state_patch = mock.patch(
            "PyTado.interface.api.TadoX.get_state",
            side_effect=check_get_state,
        )
        get_state_patch.start()
        self.addCleanup(get_state_patch.stop)

    def set_get_devices_fixture(self, filename: str) -> None:
        def get_devices():
            return json.loads(common.load_fixture(filename))

        get_devices_patch = mock.patch(
            "PyTado.interface.api.TadoX.get_devices",
            side_effect=get_devices,
        )
        get_devices_patch.start()
        self.addCleanup(get_devices_patch.stop)

    def test_tadox_heating_auto_mode(self):
        """Test general homes response."""

        self.set_fixture("home_1234/tadox.heating.auto_mode.json")
        mode = self.tado_client.get_zone_state(1)

        assert mode.ac_power is None
        assert mode.ac_power_timestamp is None
        assert mode.available is True
        assert mode.connection == "CONNECTED"
        assert mode.current_fan_speed is None
        assert mode.current_humidity == 38.00
        assert mode.current_humidity_timestamp is None
        assert mode.current_hvac_action == "HEATING"
        assert mode.current_hvac_mode == "SMART_SCHEDULE"
        assert mode.current_swing_mode == "OFF"
        assert mode.current_temp == 24.00
        assert mode.current_temp_timestamp is None
        assert mode.heating_power is None
        assert mode.heating_power_percentage == 100.0
        assert mode.heating_power_timestamp is None
        assert mode.is_away is None
        assert mode.link is None
        assert mode.open_window is False
        assert not mode.open_window_attr
        assert mode.overlay_active is False
        assert mode.overlay_termination_type is None
        assert mode.power == "ON"
        assert mode.precision == 0.01
        assert mode.preparation is False
        assert mode.tado_mode is None
        assert mode.target_temp == 22.0
        assert mode.zone_id == 1

    def test_tadox_heating_manual_mode(self):
        """Test general homes response."""

        self.set_fixture("home_1234/tadox.heating.manual_mode.json")
        mode = self.tado_client.get_zone_state(1)

        assert mode.ac_power is None
        assert mode.ac_power_timestamp is None
        assert mode.available is True
        assert mode.connection == "CONNECTED"
        assert mode.current_fan_speed is None
        assert mode.current_humidity == 38.00
        assert mode.current_humidity_timestamp is None
        assert mode.current_hvac_action == "HEATING"
        assert mode.current_hvac_mode == "HEAT"
        assert mode.current_swing_mode == "OFF"
        assert mode.current_temp == 24.07
        assert mode.current_temp_timestamp is None
        assert mode.heating_power is None
        assert mode.heating_power_percentage == 100.0
        assert mode.heating_power_timestamp is None
        assert mode.is_away is None
        assert mode.link is None
        assert mode.open_window is False
        assert not mode.open_window_attr
        assert mode.overlay_active is True
        assert mode.overlay_termination_type == "NEXT_TIME_BLOCK"
        assert mode.power == "ON"
        assert mode.precision == 0.01
        assert mode.preparation is False
        assert mode.tado_mode is None
        assert mode.target_temp == 25.5
        assert mode.zone_id == 1

    def test_tadox_heating_manual_off(self):
        """Test general homes response."""

        self.set_fixture("home_1234/tadox.heating.manual_off.json")
        mode = self.tado_client.get_zone_state(1)

        assert mode.ac_power is None
        assert mode.ac_power_timestamp is None
        assert mode.available is True
        assert mode.connection == "CONNECTED"
        assert mode.current_fan_speed is None
        assert mode.current_humidity == 38.00
        assert mode.current_humidity_timestamp is None
        assert mode.current_hvac_action == "OFF"
        assert mode.current_hvac_mode == "OFF"
        assert mode.current_swing_mode == "OFF"
        assert mode.current_temp == 24.08
        assert mode.current_temp_timestamp is None
        assert mode.heating_power is None
        assert mode.heating_power_percentage == 0.0
        assert mode.heating_power_timestamp is None
        assert mode.is_away is None
        assert mode.link is None
        assert mode.open_window is False
        assert not mode.open_window_attr
        assert mode.overlay_active is True
        assert mode.overlay_termination_type == "NEXT_TIME_BLOCK"
        assert mode.power == "OFF"
        assert mode.precision == 0.01
        assert mode.preparation is False
        assert mode.tado_mode is None
        assert mode.target_temp is None
        assert mode.zone_id == 1

    def test_get_devices(self):
        """ Test get_devices method """
        self.set_get_devices_fixture("tadox/rooms_and_devices.json")

        devices_and_rooms = self.tado_client.get_devices()
        rooms = devices_and_rooms['rooms']
        assert len(rooms) == 2
        room_1 = rooms[0]
        assert room_1['roomName'] == 'Room 1'
        assert room_1['devices'][0]['serialNumber'] == 'VA1234567890'

    def test_set_window_open(self):
        """ Test get_devices method """
        self.set_get_devices_fixture("tadox/rooms_and_devices.json")

        devices_and_rooms = self.tado_client.get_devices()
        for room in devices_and_rooms['rooms']:
            result = self.tado_client.set_open_window(zone=room)
            assert isinstance(result, dict)

    def test_reset_window_open(self):
        """ Test get_devices method """
        self.set_get_devices_fixture("tadox/rooms_and_devices.json")

        devices_and_rooms = self.tado_client.get_devices()
        for room in devices_and_rooms['rooms']:
            result = self.tado_client.reset_open_window(zone=room)
            assert isinstance(result, dict)

    def test_get_zone_state(self):
        """Test get_zone_state method"""
        self.set_fixture("home_1234/tadox.heating.auto_mode.json")
        zone_state = self.tado_client.get_zone_state(1)
        assert zone_state.current_temp == 24.00

    def test_get_zone_states(self):
        """Test get_zone_states method"""
        self.set_get_devices_fixture("tadox/rooms_and_devices.json")
        zone_states = self.tado_client.get_zone_states()
        assert zone_states["rooms"][0]["roomName"] == "Room 1"

    def test_get_state(self):
        """Test get_state method"""
        self.set_fixture("home_1234/tadox.heating.auto_mode.json")
        state = self.tado_client.get_state(1)
        assert state["sensorDataPoints"]["insideTemperature"]["value"] == 24.00

    def test_get_capabilities(self):
        """Test get_capabilities method"""
        with self.assertRaises(Exception):
            self.tado_client.get_capabilities(1)

    def test_get_climate(self):
        """Test get_climate method"""
        self.set_fixture("home_1234/tadox.heating.auto_mode.json")
        climate = self.tado_client.get_climate(1)
        assert climate["temperature"] == 24.00

    def test_set_timetable(self):
        """Test set_timetable method"""
        with self.assertRaises(Exception):
            self.tado_client.set_timetable(1, None)

    def test_get_schedule(self):
        """Test get_schedule method"""
        self.set_fixture("home_1234/tadox.heating.auto_mode.json")
        schedule = self.tado_client.get_schedule(1, None)
        assert schedule["sensorDataPoints"]["insideTemperature"]["value"] == 24.00

    def test_set_schedule(self):
        """Test set_schedule method"""
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.set_schedule(1, None, None, {"start": "00:00", "end": "07:05"})
            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request = args[0]
            self.assertEqual(request.command, "rooms/1/schedule")
            self.assertEqual(request.action, "PUT")
            self.assertEqual(request.payload, {"start": "00:00", "end": "07:05"})
            self.assertTrue(response["success"])

    def test_reset_zone_overlay(self):
        """Test reset_zone_overlay method"""
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.reset_zone_overlay(1)
            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request = args[0]
            self.assertEqual(request.command, "rooms/1/resumeSchedule")
            self.assertEqual(request.action, "PUT")
            self.assertTrue(response["success"])

    def test_set_zone_overlay(self):
        """Test set_zone_overlay method"""
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.set_zone_overlay(1, "MANUAL", 22.0, 3600)
            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request = args[0]
            self.assertEqual(request.command, "rooms/1/manualControl")
            self.assertEqual(request.action, "PUT")
            self.assertEqual(request.payload, {
                "setting": {"type": "HEATING", "power": "ON", "temperature": {"value": 22.0, "valueRaw": 22.0, "precision": 0.1}},
                "termination": {"type": "MANUAL", "durationInSeconds": 3600},
            })
            self.assertTrue(response["success"])

    def test_get_open_window_detected(self):
        """Test get_open_window_detected method"""
        self.set_fixture("home_1234/tadox.heating.auto_mode.json")
        open_window_detected = self.tado_client.get_open_window_detected(1)
        assert open_window_detected["openWindowDetected"] is False

    def test_set_open_window(self):
        """Test set_open_window method"""
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.set_open_window(1)
            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request = args[0]
            self.assertEqual(request.command, "rooms/1/openWindow")
            self.assertEqual(request.action, "PUT")
            self.assertTrue(response["success"])

    def test_reset_open_window(self):
        """Test reset_open_window method"""
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.reset_open_window(1)
            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request = args[0]
            self.assertEqual(request.command, "rooms/1/openWindow")
            self.assertEqual(request.action, "DELETE")
            self.assertTrue(response["success"])

    def test_get_device_info(self):
        """Test get_device_info method"""
        self.set_get_devices_fixture("tadox/rooms_and_devices.json")
        device_info = self.tado_client.get_device_info("VA1234567890")
        assert device_info["rooms"][0]["devices"][0]["serialNumber"] == "VA1234567890"

    def test_set_temp_offset(self):
        """Test set_temp_offset method"""
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.set_temp_offset("VA1234567890", 2.0)
            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request = args[0]
            self.assertEqual(request.command, "roomsAndDevices/devices/VA1234567890")
            self.assertEqual(request.action, "PUT")
            self.assertEqual(request.payload, {"temperatureOffset": 2.0})
            self.assertTrue(response["success"])

    def test_set_child_lock(self):
        """Test set_child_lock method"""
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.set_child_lock("VA1234567890", True)
            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request = args[0]
            self.assertEqual(request.command, "roomsAndDevices/devices/VA1234567890")
            self.assertEqual(request.action, "PUT")
            self.assertEqual(request.payload, {"childLockEnabled": True})
            self.assertTrue(response["success"])
