"""Test the interface.api.Tado object."""

import json
import unittest
from unittest import mock

from . import common

from PyTado.http import Http, TadoRequest
from PyTado.interface.api import Tado


class TadoTestCase(unittest.TestCase):
    """Test cases for tado class"""

    def setUp(self) -> None:
        super().setUp()
        login_patch = mock.patch("PyTado.http.Http._login", return_value=(1, "foo"))
        get_me_patch = mock.patch("PyTado.interface.api.Tado.get_me")
        login_patch.start()
        get_me_patch.start()
        self.addCleanup(login_patch.stop)
        self.addCleanup(get_me_patch.stop)

        self.http = Http("my@username.com", "mypassword")
        self.tado_client = Tado(self.http)

    def test_home_set_to_manual_mode(
        self,
    ):
        # Test that the Tado home can be set to auto geofencing mode when it is
        # supported and currently in manual mode.
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(
                common.load_fixture("tadov2.home_state.auto_supported.manual_mode.json")
            ),
        ):
            self.tado_client.get_home_state()

        with mock.patch("PyTado.http.Http.request"):
            self.tado_client.set_auto()

    def test_home_already_set_to_auto_mode(
        self,
    ):
        # Test that the Tado home remains set to auto geofencing mode when it is
        # supported, and already in auto mode.
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(
                common.load_fixture("tadov2.home_state.auto_supported.auto_mode.json")
            ),
        ):
            self.tado_client.get_home_state()

        with mock.patch("PyTado.http.Http.request"):
            self.tado_client.set_auto()

    def test_home_cant_be_set_to_auto_when_home_does_not_support_geofencing(
        self,
    ):
        # Test that the Tado home can't be set to auto geofencing mode when it
        # is not supported.
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(
                common.load_fixture("tadov2.home_state.auto_not_supported.json")
            ),
        ):
            self.tado_client.get_home_state()

        with mock.patch("PyTado.http.Http.request"):
            with self.assertRaises(Exception):
                self.tado_client.set_auto()

    def test_get_running_times(self):
        """Test the get_running_times method."""

        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("running_times.json")),
        ) as mock_request:
            running_times = self.tado_client.get_running_times("2023-08-01")

            mock_request.assert_called_once()

            assert running_times["lastUpdated"] == "2023-08-05T19:50:21Z"
            assert running_times["runningTimes"][0]["zones"][0]["id"] == 1

    def test_get_boiler_install_state(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(
                common.load_fixture("home_by_bridge.boiler_wiring_installation_state.json")
            ),
        ) as mock_request:
            boiler_temperature = self.tado_client.get_boiler_install_state(
                "IB123456789", "authcode"
            )

            mock_request.assert_called_once()

            assert boiler_temperature["boiler"]["outputTemperature"]["celsius"] == 38.01

    def test_get_boiler_max_output_temperature(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(
                common.load_fixture("home_by_bridge.boiler_max_output_temperature.json")
            ),
        ) as mock_request:
            boiler_temperature = self.tado_client.get_boiler_max_output_temperature(
                "IB123456789", "authcode"
            )

            mock_request.assert_called_once()

            assert boiler_temperature["boilerMaxOutputTemperatureInCelsius"] == 50.0

    def test_set_boiler_max_output_temperature(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.set_boiler_max_output_temperature(
                "IB123456789", "authcode", 75
            )

            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request: TadoRequest = args[0]

            self.assertEqual(request.command, "boilerMaxOutputTemperature")
            self.assertEqual(request.action, "PUT")
            self.assertEqual(request.payload, {"boilerMaxOutputTemperatureInCelsius": 75})

            # Verify the response
            self.assertTrue(response["success"])

    def test_get_me(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("home_1234/my_api_v2_me.json")),
        ) as mock_request:
            me = self.tado_client.get_me()

            mock_request.assert_called_once()
            assert me["homes"][0]["id"] == 1234

    def test_get_devices(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox/rooms_and_devices.json")),
        ) as mock_request:
            devices = self.tado_client.get_devices()

            mock_request.assert_called_once()
            assert devices["rooms"][0]["devices"][0]["serialNumber"] == "VA1234567890"

    def test_get_zones(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox/rooms_and_devices.json")),
        ) as mock_request:
            zones = self.tado_client.get_zones()

            mock_request.assert_called_once()
            assert zones["rooms"][0]["roomName"] == "Room 1"

    def test_get_zone_state(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox.heating.auto_mode.json")),
        ) as mock_request:
            zone_state = self.tado_client.get_zone_state(1)

            mock_request.assert_called_once()
            assert zone_state.current_temp == 24.00

    def test_get_zone_states(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox/rooms_and_devices.json")),
        ) as mock_request:
            zone_states = self.tado_client.get_zone_states()

            mock_request.assert_called_once()
            assert zone_states["rooms"][0]["roomName"] == "Room 1"

    def test_get_state(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox.heating.auto_mode.json")),
        ) as mock_request:
            state = self.tado_client.get_state(1)

            mock_request.assert_called_once()
            assert state["sensorDataPoints"]["insideTemperature"]["value"] == 24.00

    def test_get_capabilities(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("zone_with_swing_capabilities.json")),
        ) as mock_request:
            capabilities = self.tado_client.get_capabilities(1)

            mock_request.assert_called_once()
            assert capabilities["type"] == "AIR_CONDITIONING"

    def test_get_climate(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox.heating.auto_mode.json")),
        ) as mock_request:
            climate = self.tado_client.get_climate(1)

            mock_request.assert_called_once()
            assert climate["temperature"] == 24.00

    def test_get_timetable(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox.heating.auto_mode.json")),
        ) as mock_request:
            timetable = self.tado_client.get_timetable(1)

            mock_request.assert_called_once()
            assert timetable == 2

    def test_get_historic(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox.heating.auto_mode.json")),
        ) as mock_request:
            historic = self.tado_client.get_historic(1, "2023-08-01")

            mock_request.assert_called_once()
            assert historic["sensorDataPoints"]["insideTemperature"]["value"] == 24.00

    def test_set_timetable(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.set_timetable(1, 2)

            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request: TadoRequest = args[0]

            self.assertEqual(request.command, "zones/1/schedule/activeTimetable")
            self.assertEqual(request.action, "PUT")
            self.assertEqual(request.payload, {"id": 2})

            # Verify the response
            self.assertTrue(response["success"])

    def test_get_schedule(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox.heating.auto_mode.json")),
        ) as mock_request:
            schedule = self.tado_client.get_schedule(1, 2)

            mock_request.assert_called_once()
            assert schedule["sensorDataPoints"]["insideTemperature"]["value"] == 24.00

    def test_set_schedule(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.set_schedule(1, 2, "MONDAY", {"start": "00:00", "end": "07:05"})

            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request: TadoRequest = args[0]

            self.assertEqual(request.command, "zones/1/schedule/timetables/2/blocks/MONDAY")
            self.assertEqual(request.action, "PUT")
            self.assertEqual(request.payload, {"start": "00:00", "end": "07:05"})

            # Verify the response
            self.assertTrue(response["success"])

    def test_get_weather(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox.heating.auto_mode.json")),
        ) as mock_request:
            weather = self.tado_client.get_weather()

            mock_request.assert_called_once()
            assert weather["sensorDataPoints"]["insideTemperature"]["value"] == 24.00

    def test_get_air_comfort(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox.heating.auto_mode.json")),
        ) as mock_request:
            air_comfort = self.tado_client.get_air_comfort()

            mock_request.assert_called_once()
            assert air_comfort["sensorDataPoints"]["insideTemperature"]["value"] == 24.00

    def test_get_users(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox/rooms_and_devices.json")),
        ) as mock_request:
            users = self.tado_client.get_users()

            mock_request.assert_called_once()
            assert users["rooms"][0]["roomName"] == "Room 1"

    def test_get_mobile_devices(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox/rooms_and_devices.json")),
        ) as mock_request:
            mobile_devices = self.tado_client.get_mobile_devices()

            mock_request.assert_called_once()
            assert mobile_devices["rooms"][0]["roomName"] == "Room 1"

    def test_reset_zone_overlay(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.reset_zone_overlay(1)

            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request: TadoRequest = args[0]

            self.assertEqual(request.command, "zones/1/overlay")
            self.assertEqual(request.action, "DELETE")

            # Verify the response
            self.assertTrue(response["success"])

    def test_set_zone_overlay(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.set_zone_overlay(1, "MANUAL", 22.0, 3600)

            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request: TadoRequest = args[0]

            self.assertEqual(request.command, "zones/1/overlay")
            self.assertEqual(request.action, "PUT")
            self.assertEqual(request.payload, {
                "setting": {"type": "HEATING", "power": "ON", "temperature": {"celsius": 22.0}},
                "termination": {"typeSkillBasedApp": "MANUAL", "durationInSeconds": 3600},
            })

            # Verify the response
            self.assertTrue(response["success"])

    def test_get_zone_overlay_default(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox.heating.auto_mode.json")),
        ) as mock_request:
            overlay_default = self.tado_client.get_zone_overlay_default(1)

            mock_request.assert_called_once()
            assert overlay_default["sensorDataPoints"]["insideTemperature"]["value"] == 24.00

    def test_set_home(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.set_home()

            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request: TadoRequest = args[0]

            self.assertEqual(request.command, "presenceLock")
            self.assertEqual(request.action, "PUT")
            self.assertEqual(request.payload, {"homePresence": "HOME"})

            # Verify the response
            self.assertTrue(response["success"])

    def test_set_away(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.set_away()

            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request: TadoRequest = args[0]

            self.assertEqual(request.command, "presenceLock")
            self.assertEqual(request.action, "PUT")
            self.assertEqual(request.payload, {"homePresence": "AWAY"})

            # Verify the response
            self.assertTrue(response["success"])

    def test_change_presence(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.change_presence("HOME")

            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request: TadoRequest = args[0]

            self.assertEqual(request.command, "presenceLock")
            self.assertEqual(request.action, "PUT")
            self.assertEqual(request.payload, {"homePresence": "HOME"})

            # Verify the response
            self.assertTrue(response["success"])

    def test_set_child_lock(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.set_child_lock("VA1234567890", True)

            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request: TadoRequest = args[0]

            self.assertEqual(request.command, "childLock")
            self.assertEqual(request.action, "PUT")
            self.assertEqual(request.payload, {"childLockEnabled": True})

            # Verify the response
            self.assertTrue(response["success"])

    def test_set_auto(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.set_auto()

            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request: TadoRequest = args[0]

            self.assertEqual(request.command, "presenceLock")
            self.assertEqual(request.action, "DELETE")

            # Verify the response
            self.assertTrue(response["success"])

    def test_get_window_state(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox.heating.auto_mode.json")),
        ) as mock_request:
            window_state = self.tado_client.get_window_state(1)

            mock_request.assert_called_once()
            assert window_state["sensorDataPoints"]["insideTemperature"]["value"] == 24.00

    def test_get_open_window_detected(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox.heating.auto_mode.json")),
        ) as mock_request:
            open_window_detected = self.tado_client.get_open_window_detected(1)

            mock_request.assert_called_once()
            assert open_window_detected["openWindowDetected"] is False

    def test_set_open_window(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.set_open_window(1)

            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request: TadoRequest = args[0]

            self.assertEqual(request.command, "zones/1/state/openWindow/activate")
            self.assertEqual(request.action, "POST")

            # Verify the response
            self.assertTrue(response["success"])

    def test_reset_open_window(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.reset_open_window(1)

            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request: TadoRequest = args[0]

            self.assertEqual(request.command, "zones/1/state/openWindow")
            self.assertEqual(request.action, "DELETE")

            # Verify the response
            self.assertTrue(response["success"])

    def test_get_device_info(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox/rooms_and_devices.json")),
        ) as mock_request:
            device_info = self.tado_client.get_device_info("VA1234567890")

            mock_request.assert_called_once()
            assert device_info["rooms"][0]["devices"][0]["serialNumber"] == "VA1234567890"

    def test_set_temp_offset(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.set_temp_offset("VA1234567890", 2.0)

            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request: TadoRequest = args[0]

            self.assertEqual(request.command, "temperatureOffset")
            self.assertEqual(request.action, "PUT")
            self.assertEqual(request.payload, {"celsius": 2.0})

            # Verify the response
            self.assertTrue(response["success"])

    def test_get_eiq_tariffs(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox.heating.auto_mode.json")),
        ) as mock_request:
            eiq_tariffs = self.tado_client.get_eiq_tariffs()

            mock_request.assert_called_once()
            assert eiq_tariffs["sensorDataPoints"]["insideTemperature"]["value"] == 24.00

    def test_get_eiq_meter_readings(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox.heating.auto_mode.json")),
        ) as mock_request:
            eiq_meter_readings = self.tado_client.get_eiq_meter_readings()

            mock_request.assert_called_once()
            assert eiq_meter_readings["sensorDataPoints"]["insideTemperature"]["value"] == 24.00

    def test_set_eiq_meter_readings(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.set_eiq_meter_readings("2023-08-01", 100)

            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request: TadoRequest = args[0]

            self.assertEqual(request.command, "meterReadings")
            self.assertEqual(request.action, "POST")
            self.assertEqual(request.payload, {"date": "2023-08-01", "reading": 100})

            # Verify the response
            self.assertTrue(response["success"])

    def test_set_eiq_tariff(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.set_eiq_tariff("2023-08-01", "2023-08-31", 0.5, "m3", True)

            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request: TadoRequest = args[0]

            self.assertEqual(request.command, "tariffs")
            self.assertEqual(request.action, "POST")
            self.assertEqual(request.payload, {
                "tariffInCents": 50,
                "unit": "m3",
                "startDate": "2023-08-01",
                "endDate": "2023-08-31",
            })

            # Verify the response
            self.assertTrue(response["success"])

    def test_get_heating_circuits(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox.heating.auto_mode.json")),
        ) as mock_request:
            heating_circuits = self.tado_client.get_heating_circuits()

            mock_request.assert_called_once()
            assert heating_circuits["sensorDataPoints"]["insideTemperature"]["value"] == 24.00

    def test_get_zone_control(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value.json.loads(common.load_fixture("tadox.heating.auto_mode.json")),
        ) as mock_request:
            zone_control = self.tado_client.get_zone_control(1)

            mock_request.assert_called_once()
            assert zone_control["sensorDataPoints"]["insideTemperature"]["value"] == 24.00

    def test_set_zone_heating_circuit(self):
        with mock.patch(
            "PyTado.http.Http.request",
            return_value={"success": True},
        ) as mock_request:
            response = self.tado_client.set_zone_heating_circuit(1, 2)

            mock_request.assert_called_once()
            args, _ = mock_request.call_args
            request: TadoRequest = args[0]

            self.assertEqual(request.command, "zones/1/control/heatingCircuit")
            self.assertEqual(request.action, "PUT")
            self.assertEqual(request.payload, {"circuitNumber": 2})

            # Verify the response
            self.assertTrue(response["success"])
