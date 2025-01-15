import json
import unittest
from unittest import mock

from . import common

from PyTado.http import Http
from PyTado.interface import Tado
import PyTado.interface.api as API


class TestTadoInterface(unittest.TestCase):
    """Test cases for main tado interface class"""

    def test_interface_with_tado_api(self):
        login_patch = mock.patch(
            "PyTado.http.Http._login", return_value=(1, "foo")
        )
        login_mock = login_patch.start()
        check_x_patch = mock.patch(
            "PyTado.http.Http._check_x_line_generation", return_value=False
        )
        check_x_patch.start()
        self.addCleanup(check_x_patch.stop)

        with mock.patch("PyTado.interface.api.my_tado.Tado.get_me") as mock_it:
            tado_interface = Tado("my@username.com", "mypassword")
            tado_interface.get_me()

            assert not tado_interface._http.is_x_line
            mock_it.assert_called_once()

        with mock.patch(
            "PyTado.interface.api.hops_tado.TadoX.get_me"
        ) as mock_it:
            tado_interface = Tado("my@username.com", "mypassword")
            tado_interface.get_me()

            mock_it.assert_not_called()

        assert login_mock.call_count == 2

    def test_interface_with_tadox_api(self):
        login_patch = mock.patch(
            "PyTado.http.Http._login", return_value=(1, "foo")
        )
        login_mock = login_patch.start()
        check_x_patch = mock.patch(
            "PyTado.http.Http._check_x_line_generation", return_value=True
        )
        check_x_patch.start()
        self.addCleanup(check_x_patch.stop)

        with mock.patch(
            "PyTado.interface.api.hops_tado.TadoX.get_me"
        ) as mock_it:
            tado_interface = Tado("my@username.com", "mypassword")
            tado_interface.get_me()

            mock_it.assert_called_once()
            assert tado_interface._http.is_x_line

        login_mock.assert_called_once()

    def test_error_handling_on_api_calls(self):
        login_patch = mock.patch(
            "PyTado.http.Http._login", return_value=(1, "foo")
        )
        login_mock = login_patch.start()
        check_x_patch = mock.patch(
            "PyTado.http.Http._check_x_line_generation", return_value=False
        )
        check_x_patch.start()
        self.addCleanup(check_x_patch.stop)

        with mock.patch("PyTado.interface.api.my_tado.Tado.get_me") as mock_it:
            mock_it.side_effect = Exception("API Error")

            tado_interface = Tado("my@username.com", "mypassword")

            with self.assertRaises(Exception) as context:
                tado_interface.get_me()

                self.assertIn("API Error", str(context.exception))

    def test_get_me(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_me",
            return_value={"homes": [{"id": 1234}]},
        ) as mock_get_me:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_me()
            mock_get_me.assert_called_once()
            self.assertEqual(result, {"homes": [{"id": 1234}]})

    def test_get_devices(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_devices",
            return_value=[{"id": 1, "name": "Device 1"}],
        ) as mock_get_devices:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_devices()
            mock_get_devices.assert_called_once()
            self.assertEqual(result, [{"id": 1, "name": "Device 1"}])

    def test_get_zones(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_zones",
            return_value=[{"id": 1, "name": "Zone 1"}],
        ) as mock_get_zones:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_zones()
            mock_get_zones.assert_called_once()
            self.assertEqual(result, [{"id": 1, "name": "Zone 1"}])

    def test_get_zone_state(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_zone_state",
            return_value={"id": 1, "state": "heating"},
        ) as mock_get_zone_state:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_zone_state(1)
            mock_get_zone_state.assert_called_once_with(1)
            self.assertEqual(result, {"id": 1, "state": "heating"})

    def test_get_zone_states(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_zone_states",
            return_value=[{"id": 1, "state": "heating"}],
        ) as mock_get_zone_states:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_zone_states()
            mock_get_zone_states.assert_called_once()
            self.assertEqual(result, [{"id": 1, "state": "heating"}])

    def test_get_state(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_state",
            return_value={"id": 1, "state": "heating"},
        ) as mock_get_state:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_state(1)
            mock_get_state.assert_called_once_with(1)
            self.assertEqual(result, {"id": 1, "state": "heating"})

    def test_get_home_state(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_home_state",
            return_value={"state": "home"},
        ) as mock_get_home_state:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_home_state()
            mock_get_home_state.assert_called_once()
            self.assertEqual(result, {"state": "home"})

    def test_get_auto_geofencing_supported(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_auto_geofencing_supported",
            return_value=True,
        ) as mock_get_auto_geofencing_supported:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_auto_geofencing_supported()
            mock_get_auto_geofencing_supported.assert_called_once()
            self.assertTrue(result)

    def test_get_capabilities(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_capabilities",
            return_value={"capabilities": "full"},
        ) as mock_get_capabilities:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_capabilities(1)
            mock_get_capabilities.assert_called_once_with(1)
            self.assertEqual(result, {"capabilities": "full"})

    def test_get_climate(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_climate",
            return_value={"temperature": 22.0, "humidity": 50.0},
        ) as mock_get_climate:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_climate(1)
            mock_get_climate.assert_called_once_with(1)
            self.assertEqual(result, {"temperature": 22.0, "humidity": 50.0})

    def test_get_timetable(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_timetable",
            return_value=2,
        ) as mock_get_timetable:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_timetable(1)
            mock_get_timetable.assert_called_once_with(1)
            self.assertEqual(result, 2)

    def test_get_historic(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_historic",
            return_value={"date": "2023-08-01", "data": "some_data"},
        ) as mock_get_historic:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_historic(1, "2023-08-01")
            mock_get_historic.assert_called_once_with(1, "2023-08-01")
            self.assertEqual(result, {"date": "2023-08-01", "data": "some_data"})

    def test_set_timetable(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.set_timetable",
            return_value={"success": True},
        ) as mock_set_timetable:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.set_timetable(1, 2)
            mock_set_timetable.assert_called_once_with(1, 2)
            self.assertEqual(result, {"success": True})

    def test_get_schedule(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_schedule",
            return_value={"schedule": "some_schedule"},
        ) as mock_get_schedule:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_schedule(1, 2)
            mock_get_schedule.assert_called_once_with(1, 2)
            self.assertEqual(result, {"schedule": "some_schedule"})

    def test_set_schedule(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.set_schedule",
            return_value={"success": True},
        ) as mock_set_schedule:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.set_schedule(1, 2, "MONDAY", {"start": "00:00", "end": "07:05"})
            mock_set_schedule.assert_called_once_with(1, 2, "MONDAY", {"start": "00:00", "end": "07:05"})
            self.assertEqual(result, {"success": True})

    def test_get_weather(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_weather",
            return_value={"weather": "sunny"},
        ) as mock_get_weather:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_weather()
            mock_get_weather.assert_called_once()
            self.assertEqual(result, {"weather": "sunny"})

    def test_get_air_comfort(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_air_comfort",
            return_value={"air_comfort": "good"},
        ) as mock_get_air_comfort:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_air_comfort()
            mock_get_air_comfort.assert_called_once()
            self.assertEqual(result, {"air_comfort": "good"})

    def test_get_users(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_users",
            return_value=[{"id": 1, "name": "User 1"}],
        ) as mock_get_users:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_users()
            mock_get_users.assert_called_once()
            self.assertEqual(result, [{"id": 1, "name": "User 1"}])

    def test_get_mobile_devices(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_mobile_devices",
            return_value=[{"id": 1, "name": "Device 1"}],
        ) as mock_get_mobile_devices:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_mobile_devices()
            mock_get_mobile_devices.assert_called_once()
            self.assertEqual(result, [{"id": 1, "name": "Device 1"}])

    def test_reset_zone_overlay(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.reset_zone_overlay",
            return_value={"success": True},
        ) as mock_reset_zone_overlay:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.reset_zone_overlay(1)
            mock_reset_zone_overlay.assert_called_once_with(1)
            self.assertEqual(result, {"success": True})

    def test_set_zone_overlay(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.set_zone_overlay",
            return_value={"success": True},
        ) as mock_set_zone_overlay:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.set_zone_overlay(1, "MANUAL", 22.0, 3600)
            mock_set_zone_overlay.assert_called_once_with(1, "MANUAL", 22.0, 3600)
            self.assertEqual(result, {"success": True})

    def test_get_zone_overlay_default(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_zone_overlay_default",
            return_value={"default": "some_default"},
        ) as mock_get_zone_overlay_default:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_zone_overlay_default(1)
            mock_get_zone_overlay_default.assert_called_once_with(1)
            self.assertEqual(result, {"default": "some_default"})

    def test_set_home(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.set_home",
            return_value={"success": True},
        ) as mock_set_home:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.set_home()
            mock_set_home.assert_called_once()
            self.assertEqual(result, {"success": True})

    def test_set_away(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.set_away",
            return_value={"success": True},
        ) as mock_set_away:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.set_away()
            mock_set_away.assert_called_once()
            self.assertEqual(result, {"success": True})

    def test_change_presence(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.change_presence",
            return_value={"success": True},
        ) as mock_change_presence:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.change_presence("HOME")
            mock_change_presence.assert_called_once_with("HOME")
            self.assertEqual(result, {"success": True})

    def test_set_child_lock(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.set_child_lock",
            return_value={"success": True},
        ) as mock_set_child_lock:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.set_child_lock("VA1234567890", True)
            mock_set_child_lock.assert_called_once_with("VA1234567890", True)
            self.assertEqual(result, {"success": True})

    def test_set_auto(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.set_auto",
            return_value={"success": True},
        ) as mock_set_auto:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.set_auto()
            mock_set_auto.assert_called_once()
            self.assertEqual(result, {"success": True})

    def test_get_window_state(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_window_state",
            return_value={"window_state": "closed"},
        ) as mock_get_window_state:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_window_state(1)
            mock_get_window_state.assert_called_once_with(1)
            self.assertEqual(result, {"window_state": "closed"})

    def test_get_open_window_detected(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_open_window_detected",
            return_value={"open_window_detected": False},
        ) as mock_get_open_window_detected:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_open_window_detected(1)
            mock_get_open_window_detected.assert_called_once_with(1)
            self.assertEqual(result, {"open_window_detected": False})

    def test_set_open_window(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.set_open_window",
            return_value={"success": True},
        ) as mock_set_open_window:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.set_open_window(1)
            mock_set_open_window.assert_called_once_with(1)
            self.assertEqual(result, {"success": True})

    def test_reset_open_window(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.reset_open_window",
            return_value={"success": True},
        ) as mock_reset_open_window:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.reset_open_window(1)
            mock_reset_open_window.assert_called_once_with(1)
            self.assertEqual(result, {"success": True})

    def test_get_device_info(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_device_info",
            return_value={"device_info": "some_info"},
        ) as mock_get_device_info:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_device_info("VA1234567890")
            mock_get_device_info.assert_called_once_with("VA1234567890")
            self.assertEqual(result, {"device_info": "some_info"})

    def test_set_temp_offset(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.set_temp_offset",
            return_value={"success": True},
        ) as mock_set_temp_offset:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.set_temp_offset("VA1234567890", 2.0)
            mock_set_temp_offset.assert_called_once_with("VA1234567890", 2.0)
            self.assertEqual(result, {"success": True})

    def test_get_eiq_tariffs(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_eiq_tariffs",
            return_value={"tariffs": "some_tariffs"},
        ) as mock_get_eiq_tariffs:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_eiq_tariffs()
            mock_get_eiq_tariffs.assert_called_once()
            self.assertEqual(result, {"tariffs": "some_tariffs"})

    def test_get_eiq_meter_readings(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_eiq_meter_readings",
            return_value={"meter_readings": "some_readings"},
        ) as mock_get_eiq_meter_readings:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_eiq_meter_readings()
            mock_get_eiq_meter_readings.assert_called_once()
            self.assertEqual(result, {"meter_readings": "some_readings"})

    def test_set_eiq_meter_readings(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.set_eiq_meter_readings",
            return_value={"success": True},
        ) as mock_set_eiq_meter_readings:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.set_eiq_meter_readings("2023-08-01", 100)
            mock_set_eiq_meter_readings.assert_called_once_with("2023-08-01", 100)
            self.assertEqual(result, {"success": True})

    def test_set_eiq_tariff(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.set_eiq_tariff",
            return_value={"success": True},
        ) as mock_set_eiq_tariff:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.set_eiq_tariff("2023-08-01", "2023-08-31", 0.5, "m3", True)
            mock_set_eiq_tariff.assert_called_once_with("2023-08-01", "2023-08-31", 0.5, "m3", True)
            self.assertEqual(result, {"success": True})

    def test_get_heating_circuits(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_heating_circuits",
            return_value=[{"id": 1, "name": "Circuit 1"}],
        ) as mock_get_heating_circuits:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_heating_circuits()
            mock_get_heating_circuits.assert_called_once()
            self.assertEqual(result, [{"id": 1, "name": "Circuit 1"}])

    def test_get_zone_control(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_zone_control",
            return_value={"control": "some_control"},
        ) as mock_get_zone_control:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_zone_control(1)
            mock_get_zone_control.assert_called_once_with(1)
            self.assertEqual(result, {"control": "some_control"})

    def test_set_zone_heating_circuit(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.set_zone_heating_circuit",
            return_value={"success": True},
        ) as mock_set_zone_heating_circuit:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.set_zone_heating_circuit(1, 2)
            mock_set_zone_heating_circuit.assert_called_once_with(1, 2)
            self.assertEqual(result, {"success": True})

    def test_get_running_times(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_running_times",
            return_value={"running_times": "some_times"},
        ) as mock_get_running_times:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_running_times("2023-08-01")
            mock_get_running_times.assert_called_once_with("2023-08-01")
            self.assertEqual(result, {"running_times": "some_times"})

    def test_get_boiler_install_state(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_boiler_install_state",
            return_value={"install_state": "some_state"},
        ) as mock_get_boiler_install_state:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_boiler_install_state("IB123456789", "authcode")
            mock_get_boiler_install_state.assert_called_once_with("IB123456789", "authcode")
            self.assertEqual(result, {"install_state": "some_state"})

    def test_get_boiler_max_output_temperature(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.get_boiler_max_output_temperature",
            return_value={"max_output_temperature": 75.0},
        ) as mock_get_boiler_max_output_temperature:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.get_boiler_max_output_temperature("IB123456789", "authcode")
            mock_get_boiler_max_output_temperature.assert_called_once_with("IB123456789", "authcode")
            self.assertEqual(result, {"max_output_temperature": 75.0})

    def test_set_boiler_max_output_temperature(self):
        with mock.patch(
            "PyTado.interface.api.my_tado.Tado.set_boiler_max_output_temperature",
            return_value={"success": True},
        ) as mock_set_boiler_max_output_temperature:
            tado_interface = Tado("my@username.com", "mypassword")
            result = tado_interface.set_boiler_max_output_temperature("IB123456789", "authcode", 75)
            mock_set_boiler_max_output_temperature.assert_called_once_with("IB123456789", "authcode", 75)
            self.assertEqual(result, {"success": True})
