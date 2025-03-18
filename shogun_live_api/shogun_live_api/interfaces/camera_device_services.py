##################################################################################
## MIT License
##
## Copyright (c) 2023 Vicon Motion Systems Ltd
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in all
## copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.
##################################################################################
"""Automatically generated CameraDeviceServices for Vicon Shogun Live API."""

from enum import Enum
from vicon_core_api import SchemaServices
from vicon_core_api import ViconInterface


class CameraDeviceServices(ViconInterface):
    """Functions for monitoring and controlling camera devices connected to the application."""

    class EDeviceConnectionStatus(Enum):
        """Device connection status values.

        Enum Values:
            EMissing: Device has been discovered, but has never connected to the application.
            EDisconnected: Device is not connected.
            EConnected: Device is connected.
        """
        EMissing = 0
        EDisconnected = 1
        EConnected = 2


    def device_list(self):
        """List of camera devices discovered by the application. This includes devices that have connected to the application and devices
        listed in configuration files.

        Return:
            return < Result >: Ok - On success.
            device_urns < [string] >: Camera device URNs.
        """
        return self.client.send_command("CameraDeviceServices.DeviceList")

    def add_device_list_changed_callback(self, function):
        """Callback issued whenever the device list has changed."""
        return self.client.add_callback("CameraDeviceServices.DeviceListChangedCallback", function)

    def remove_missing_device(self, device_urn):
        """Remove a missing camera (discovered but never connected in this application session).

        Args:
            device_urn < string >: Device URN requested.

        Return:
            return < Result >: Ok - On success.
                NotFound - If device was not found.
                NotPermitted - If device is not missing.
        """
        return self.client.send_command("CameraDeviceServices.RemoveMissingDevice", device_urn)

    def remove_missing_devices(self):
        """Remove all missing cameras (discovered but never connected in this application session).

        Return:
            return < Result >: Ok - On success.
        """
        return self.client.send_command("CameraDeviceServices.RemoveMissingDevices")

    def connection_status(self, device_urn):
        """Get the connection status of a device.

        Args:
            device_urn < string >: Device URN requested.

        Return:
            return < Result >: Ok - On success.
                NotFound - If device was not found.
            value < CameraDeviceServices.EDeviceConnectionStatus >: Connection status value.
        """
        return self.client.send_command("CameraDeviceServices.ConnectionStatus", device_urn)

    def connection_status_delta(self, previous_change_id):
        """Get the connection status for every device that has changed its value since a previous request.

        Args:
            previous_change_id < int >: Previous change id received by the client.

        Return:
            return < Result >: Ok - On success.
                InvalidArgument - If PreviousChangeId is greater than the latest change id.
            current_change_id < int >: Latest change id at time of request.
            device_values < [(string,CameraDeviceServices.EDeviceConnectionStatus)] >: Device URN and connection status value for every device changed since PreviousChangeId.
        """
        return self.client.send_command("CameraDeviceServices.ConnectionStatusDelta", previous_change_id)

    def add_connection_status_changed_callback(self, function):
        """Callback issued whenever a connection status value changes."""
        return self.client.add_callback("CameraDeviceServices.ConnectionStatusChangedCallback", function)

    def contributing_status(self, device_urn):
        """Get the contributing status of a device.

        Args:
            device_urn < string >: Device URN requested.

        Return:
            return < Result >: Ok - On success.
                NotFound - If device was not found.
            value < bool >: Contributing status value. If true, the device is contributing data normally, otherwise the device has a problem that is
                preventing data output.
        """
        return self.client.send_command("CameraDeviceServices.ContributingStatus", device_urn)

    def contributing_status_delta(self, previous_change_id):
        """Get the contributing status for every device that has changed its value since a previous request.

        Args:
            previous_change_id < int >: Previous change id received by the client.

        Return:
            return < Result >: Ok - On success.
                InvalidArgument - If PreviousChangeId is greater than the latest change id.
            current_change_id < int >: Latest change id at time of request.
            device_values < [(string,bool)] >: Device URN and contributing status value for every device changed since PreviousChangeId.
        """
        return self.client.send_command("CameraDeviceServices.ContributingStatusDelta", previous_change_id)

    def add_contributing_status_changed_callback(self, function):
        """Callback issued whenever a contributing status value changes."""
        return self.client.add_callback("CameraDeviceServices.ContributingStatusChangedCallback", function)

    def device_type(self, device_urn):
        """Get the type of a device. This is set on device connection.

        Args:
            device_urn < string >: Device URN requested.

        Return:
            return < Result >: Ok - On success.
                NotAvailable - If device was missing.
                NotFound - If device was not found.
            value < string >: Device type.
        """
        return self.client.send_command("CameraDeviceServices.DeviceType", device_urn)

    def display_type(self, device_urn):
        """Get the type of a device as user-readable text. This is set on device discovery.

        Args:
            device_urn < string >: Device URN requested.

        Return:
            return < Result >: Ok - On success.
                NotFound - If device was not found.
            value < string >: Device display type.
        """
        return self.client.send_command("CameraDeviceServices.DisplayType", device_urn)

    def firmware_version(self, device_urn):
        """Get the firmware version of a device. This is set on device connection.

        Args:
            device_urn < string >: Device URN requested.

        Return:
            return < Result >: Ok - On success.
                NotFound - If device was not found.
            value < int >: Firmware version.
        """
        return self.client.send_command("CameraDeviceServices.FirmwareVersion", device_urn)

    def serial_number(self, device_urn):
        """Get the assigned serial number of a device. This is set on device connection.

        Args:
            device_urn < string >: Device URN requested.

        Return:
            return < Result >: Ok - On success.
                NotFound - If device was not found.
            value < string >: Serial number.
        """
        return self.client.send_command("CameraDeviceServices.SerialNumber", device_urn)

    def enabled(self, device_urn):
        """Get the enabled value of a device.

        Args:
            device_urn < string >: Device URN requested.

        Return:
            return < Result >: Ok - On success.
                NotFound - If device was not found.
            value < bool >: Enabled value.
        """
        return self.client.send_command("CameraDeviceServices.Enabled", device_urn)

    def enabled_delta(self, previous_change_id):
        """Get the enabled value for every device that has changed its value since a previous request.

        Args:
            previous_change_id < int >: Previous change id received by the client.

        Return:
            return < Result >: Ok - On success.
                InvalidArgument - If PreviousChangeId is greater than the latest change id.
            current_change_id < int >: Latest change id at time of request.
            device_values < [(string,bool)] >: Device URN and enabled value for every device changed since PreviousChangeId.
        """
        return self.client.send_command("CameraDeviceServices.EnabledDelta", previous_change_id)

    def set_enabled(self, device_urn, value):
        """Set the enabled value on a device.

        Args:
            device_urn < string >: Device URN to set.
            value < bool >: Enabled value.

        Return:
            return < Result >: Ok - On success.
                NotFound - If device was not found.
                NotAvailable - If device was missing.
        """
        return self.client.send_command("CameraDeviceServices.SetEnabled", device_urn, value)

    def add_enabled_changed_callback(self, function):
        """Callback issued whenever an enabled value changes."""
        return self.client.add_callback("CameraDeviceServices.EnabledChangedCallback", function)

    def name(self, device_urn):
        """Get the user-defined name of a device.

        Args:
            device_urn < string >: Device URN requested.

        Return:
            return < Result >: Ok - On success.
                NotFound - If device was not found.
            value < string >: Name of device.
        """
        return self.client.send_command("CameraDeviceServices.Name", device_urn)

    def name_delta(self, previous_change_id):
        """Get the name for every device that has changed its value since a previous request.

        Args:
            previous_change_id < int >: Previous change id received by the client.

        Return:
            return < Result >: Ok - On success.
                InvalidArgument - If PreviousChangeId is greater than the latest change id.
            current_change_id < int >: Latest change id at time of request.
            device_values < [(string,string)] >: Device URN and name for every device changed since PreviousChangeId.
        """
        return self.client.send_command("CameraDeviceServices.NameDelta", previous_change_id)

    def set_name(self, device_urn, value):
        """Set the user-defined name of a device.

        Args:
            device_urn < string >: Device URN to set.
            value < string >: Name of device.

        Return:
            return < Result >: Ok - On success.
                NotFound - If device was not found.
                NotAvailable - If device was missing.
        """
        return self.client.send_command("CameraDeviceServices.SetName", device_urn, value)

    def add_name_changed_callback(self, function):
        """Callback issued whenever a device name changes."""
        return self.client.add_callback("CameraDeviceServices.NameChangedCallback", function)

    def status_lights_enabled(self, device_urn):
        """Get the status lights enabled value of a device.

        Args:
            device_urn < string >: Device URN requested.

        Return:
            return < Result >: Ok - On success.
                NotFound - If device was not found.
            value < bool >: True if status lights are enabled.
        """
        return self.client.send_command("CameraDeviceServices.StatusLightsEnabled", device_urn)

    def status_lights_enabled_delta(self, previous_change_id):
        """Get the status lights enabled value for every device that has changed its value since a previous request.

        Args:
            previous_change_id < int >: Previous change id received by the client.

        Return:
            return < Result >: Ok - On success.
                InvalidArgument - If PreviousChangeId is greater than the latest change id.
            current_change_id < int >: Latest change id at time of request.
            device_values < [(string,bool)] >: Device URN and status lights enabled value for every device changed since PreviousChangeId.
        """
        return self.client.send_command("CameraDeviceServices.StatusLightsEnabledDelta", previous_change_id)

    def set_status_lights_enabled(self, device_urn, value):
        """Set the status lights enabled value on a device.

        Args:
            device_urn < string >: Device URN to set.
            value < bool >: Status lights enabled value.

        Return:
            return < Result >: Ok - On success.
                NotFound - If device was not found.
                NotAvailable - If device was missing.
        """
        return self.client.send_command("CameraDeviceServices.SetStatusLightsEnabled", device_urn, value)

    def add_status_lights_enabled_changed_callback(self, function):
        """Callback issued whenever a status lights enabled value changes."""
        return self.client.add_callback("CameraDeviceServices.StatusLightsEnabledChangedCallback", function)

    def user_id(self, device_urn):
        """Get the user id of a device. This is a unique number representing the order of the device in the application GUI.

        Args:
            device_urn < string >: Device URN requested.

        Return:
            return < Result >: Ok - On success.
                NotFound - If device was not found.
            value < int >: User id value.
        """
        return self.client.send_command("CameraDeviceServices.UserId", device_urn)

    def user_id_delta(self, previous_change_id):
        """Get the user id for every device that has changed its value since a previous request.

        Args:
            previous_change_id < int >: Previous change id received by the client.

        Return:
            return < Result >: Ok - On success.
                InvalidArgument - If PreviousChangeId is greater than the latest change id.
            current_change_id < int >: Latest change id at time of request.
            device_values < [(string,int)] >: Device URN and user id for every device changed since PreviousChangeId.
        """
        return self.client.send_command("CameraDeviceServices.UserIdDelta", previous_change_id)

    def add_user_id_changed_callback(self, function):
        """Callback issued whenever a user id changes."""
        return self.client.add_callback("CameraDeviceServices.UserIdChangedCallback", function)

    def reboot(self, device_urns):
        """Reboot one or more camera devices.

        Args:
            device_urns < [string] >: Device URNs to reboot.

        Return:
            return < Result >: Ok - On success.
        """
        return self.client.send_command("CameraDeviceServices.Reboot", device_urns)

    def reboot_all(self):
        """Reboot all devices. This is a broadcast command and will affect all Vicon devices connected to the application.

        Return:
            return < Result >: Ok - On success.
        """
        return self.client.send_command("CameraDeviceServices.RebootAll")

    def remove_callback(self, callback_id):
        """Remove callback of any type using the id supplied when it was added."""
        return self.client.remove_callback(callback_id)



SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "TypeName": "CameraDeviceServices"}""")
SchemaServices.register_json_schema(CameraDeviceServices.EDeviceConnectionStatus, """{"Type": "Enum32", "TypeName": "CameraDeviceServices.EDeviceConnectionStatus", "EnumValues": [["Missing", 0], ["Disconnected",
                                                                                     1], ["Connected", 2]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.DeviceList", "SubSchemas": [["Return", {"Type":
                                                             "UInt32", "Role": "Result"}], ["DeviceURNs", {"Type": "List", "Role": "Output", "SubSchemas": [["", {"Type": "String"}]]}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Callback", "TypeName": "CameraDeviceServices.DeviceListChangedCallback"}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.RemoveMissingDevice", "SubSchemas": [["Return",
                                                             {"Type": "UInt32", "Role": "Result"}], ["DeviceURN", {"Type": "String", "Role": "Input"}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.RemoveMissingDevices", "SubSchemas": [["Return",
                                                             {"Type": "UInt32", "Role": "Result"}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.ConnectionStatus", "SubSchemas": [["Return",
                                                             {"Type": "UInt32", "Role": "Result"}], ["DeviceURN", {"Type": "String", "Role": "Input"}], ["Value", {"Type": "Ref", "Role":
                                                             "Output", "TypeName": "CameraDeviceServices.EDeviceConnectionStatus"}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.ConnectionStatusDelta", "SubSchemas": [["Return",
                                                             {"Type": "UInt32", "Role": "Result"}], ["PreviousChangeId", {"Type": "UInt64", "Role": "Input"}], ["CurrentChangeId", {"Type":
                                                             "UInt64", "Role": "Output"}], ["DeviceValues", {"Type": "List", "Role": "Output", "SubSchemas": [["", {"Type": "Tuple",
                                                             "SubSchemas": [["", {"Type": "String"}], ["", {"Type": "Ref", "TypeName": "CameraDeviceServices.EDeviceConnectionStatus"}]]}]]}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Callback", "TypeName": "CameraDeviceServices.ConnectionStatusChangedCallback"}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.ContributingStatus", "SubSchemas": [["Return",
                                                             {"Type": "UInt32", "Role": "Result"}], ["DeviceURN", {"Type": "String", "Role": "Input"}], ["Value", {"Type": "Bool", "Role":
                                                             "Output"}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.ContributingStatusDelta", "SubSchemas": [["Return",
                                                             {"Type": "UInt32", "Role": "Result"}], ["PreviousChangeId", {"Type": "UInt64", "Role": "Input"}], ["CurrentChangeId", {"Type":
                                                             "UInt64", "Role": "Output"}], ["DeviceValues", {"Type": "List", "Role": "Output", "SubSchemas": [["", {"Type": "Tuple",
                                                             "SubSchemas": [["", {"Type": "String"}], ["", {"Type": "Bool"}]]}]]}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Callback", "TypeName": "CameraDeviceServices.ContributingStatusChangedCallback"}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.DeviceType", "SubSchemas": [["Return", {"Type":
                                                             "UInt32", "Role": "Result"}], ["DeviceURN", {"Type": "String", "Role": "Input"}], ["Value", {"Type": "String", "Role": "Output"}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.DisplayType", "SubSchemas": [["Return", {"Type":
                                                             "UInt32", "Role": "Result"}], ["DeviceURN", {"Type": "String", "Role": "Input"}], ["Value", {"Type": "String", "Role": "Output"}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.FirmwareVersion", "SubSchemas": [["Return",
                                                             {"Type": "UInt32", "Role": "Result"}], ["DeviceURN", {"Type": "String", "Role": "Input"}], ["Value", {"Type": "UInt32",
                                                             "Role": "Output"}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.SerialNumber", "SubSchemas": [["Return", {"Type":
                                                             "UInt32", "Role": "Result"}], ["DeviceURN", {"Type": "String", "Role": "Input"}], ["Value", {"Type": "String", "Role": "Output"}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.Enabled", "SubSchemas": [["Return", {"Type":
                                                             "UInt32", "Role": "Result"}], ["DeviceURN", {"Type": "String", "Role": "Input"}], ["Value", {"Type": "Bool", "Role": "Output"}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.EnabledDelta", "SubSchemas": [["Return", {"Type":
                                                             "UInt32", "Role": "Result"}], ["PreviousChangeId", {"Type": "UInt64", "Role": "Input"}], ["CurrentChangeId", {"Type": "UInt64",
                                                             "Role": "Output"}], ["DeviceValues", {"Type": "List", "Role": "Output", "SubSchemas": [["", {"Type": "Tuple", "SubSchemas":
                                                             [["", {"Type": "String"}], ["", {"Type": "Bool"}]]}]]}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.SetEnabled", "SubSchemas": [["Return", {"Type":
                                                             "UInt32", "Role": "Result"}], ["DeviceURN", {"Type": "String", "Role": "Input"}], ["Value", {"Type": "Bool", "Role": "Input"}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Callback", "TypeName": "CameraDeviceServices.EnabledChangedCallback"}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.Name", "SubSchemas": [["Return", {"Type": "UInt32",
                                                             "Role": "Result"}], ["DeviceURN", {"Type": "String", "Role": "Input"}], ["Value", {"Type": "String", "Role": "Output"}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.NameDelta", "SubSchemas": [["Return", {"Type":
                                                             "UInt32", "Role": "Result"}], ["PreviousChangeId", {"Type": "UInt64", "Role": "Input"}], ["CurrentChangeId", {"Type": "UInt64",
                                                             "Role": "Output"}], ["DeviceValues", {"Type": "List", "Role": "Output", "SubSchemas": [["", {"Type": "Tuple", "SubSchemas":
                                                             [["", {"Type": "String"}], ["", {"Type": "String"}]]}]]}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.SetName", "SubSchemas": [["Return", {"Type":
                                                             "UInt32", "Role": "Result"}], ["DeviceURN", {"Type": "String", "Role": "Input"}], ["Value", {"Type": "String", "Role": "Input"}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Callback", "TypeName": "CameraDeviceServices.NameChangedCallback"}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.StatusLightsEnabled", "SubSchemas": [["Return",
                                                             {"Type": "UInt32", "Role": "Result"}], ["DeviceURN", {"Type": "String", "Role": "Input"}], ["Value", {"Type": "Bool", "Role":
                                                             "Output"}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.StatusLightsEnabledDelta", "SubSchemas": [["Return",
                                                             {"Type": "UInt32", "Role": "Result"}], ["PreviousChangeId", {"Type": "UInt64", "Role": "Input"}], ["CurrentChangeId", {"Type":
                                                             "UInt64", "Role": "Output"}], ["DeviceValues", {"Type": "List", "Role": "Output", "SubSchemas": [["", {"Type": "Tuple",
                                                             "SubSchemas": [["", {"Type": "String"}], ["", {"Type": "Bool"}]]}]]}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.SetStatusLightsEnabled", "SubSchemas": [["Return",
                                                             {"Type": "UInt32", "Role": "Result"}], ["DeviceURN", {"Type": "String", "Role": "Input"}], ["Value", {"Type": "Bool", "Role":
                                                             "Input"}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Callback", "TypeName": "CameraDeviceServices.StatusLightsEnabledChangedCallback"}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.UserId", "SubSchemas": [["Return", {"Type":
                                                             "UInt32", "Role": "Result"}], ["DeviceURN", {"Type": "String", "Role": "Input"}], ["Value", {"Type": "UInt32", "Role": "Output"}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.UserIdDelta", "SubSchemas": [["Return", {"Type":
                                                             "UInt32", "Role": "Result"}], ["PreviousChangeId", {"Type": "UInt64", "Role": "Input"}], ["CurrentChangeId", {"Type": "UInt64",
                                                             "Role": "Output"}], ["DeviceValues", {"Type": "List", "Role": "Output", "SubSchemas": [["", {"Type": "Tuple", "SubSchemas":
                                                             [["", {"Type": "String"}], ["", {"Type": "UInt32"}]]}]]}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Callback", "TypeName": "CameraDeviceServices.UserIdChangedCallback"}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.Reboot", "SubSchemas": [["Return", {"Type":
                                                             "UInt32", "Role": "Result"}], ["DeviceURNs", {"Type": "List", "Role": "Input", "SubSchemas": [["", {"Type": "String"}]]}]]}""")
SchemaServices.register_json_schema(CameraDeviceServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "CameraDeviceServices.RebootAll", "SubSchemas": [["Return", {"Type":
                                                             "UInt32", "Role": "Result"}]]}""")
