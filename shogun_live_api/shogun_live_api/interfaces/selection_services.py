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
"""Automatically generated SelectionServices for Vicon Shogun Live API."""

from vicon_core_api import SchemaServices
from vicon_core_api import ViconInterface


class SelectionServices(ViconInterface):
    """Functions for selecting things in the application."""
    def selected_devices(self):
        """List of selected devices.

        Return:
            return < Result >: Ok - On success.
            device_urns < [string] >: Device URNs.
        """
        return self.client.send_command("SelectionServices.SelectedDevices")

    def set_selected_devices(self, device_urns):
        """Set the list of selected devices.

        Args:
            device_urns < [string] >: Device URNs.

        Return:
            return < Result >: Ok - On success.
                OkButPartial - On partial success (some devices were selected, but some could not be found).
                NotFound - If none of the requested devices could be found.
        """
        return self.client.send_command("SelectionServices.SetSelectedDevices", device_urns)

    def add_selected_devices(self, device_urns):
        """Add to the list of selected devices.

        Args:
            device_urns < [string] >: Device URNs to add.

        Return:
            return < Result >: Ok - On success.
                OkButPartial - On partial success (some devices were selected, but some could not be found).
                NotFound - If none of the requested devices could be found.
        """
        return self.client.send_command("SelectionServices.AddSelectedDevices", device_urns)

    def remove_selected_devices(self, device_urns):
        """Remove from the list of selected devices.

        Args:
            device_urns < [string] >: Device URNs to remove.

        Return:
            return < Result >: Ok - On success.
                OkButPartial - On partial success (some devices were deselected, but some could not be found).
                NotFound - If none of the requested devices could be found.
        """
        return self.client.send_command("SelectionServices.RemoveSelectedDevices", device_urns)

    def clear_selected_devices(self):
        """Clear selected devices.

        Return:
            return < Result >: Ok - On success.
        """
        return self.client.send_command("SelectionServices.ClearSelectedDevices")

    def add_selected_devices_changed_callback(self, function):
        """Callback issued whenever the list of selected devices has changed."""
        return self.client.add_callback("SelectionServices.SelectedDevicesChangedCallback", function)

    def remove_callback(self, callback_id):
        """Remove callback of any type using the id supplied when it was added."""
        return self.client.remove_callback(callback_id)



SchemaServices.register_json_schema(SelectionServices, """{"Type": "NamedTuple", "TypeName": "SelectionServices"}""")
SchemaServices.register_json_schema(SelectionServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "SelectionServices.SelectedDevices", "SubSchemas": [["Return", {"Type":
                                                          "UInt32", "Role": "Result"}], ["DeviceURNs", {"Type": "List", "Role": "Output", "SubSchemas": [["", {"Type": "String"}]]}]]}""")
SchemaServices.register_json_schema(SelectionServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "SelectionServices.SetSelectedDevices", "SubSchemas": [["Return",
                                                          {"Type": "UInt32", "Role": "Result"}], ["DeviceURNs", {"Type": "List", "Role": "Input", "SubSchemas": [["", {"Type": "String"}]]}]]}""")
SchemaServices.register_json_schema(SelectionServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "SelectionServices.AddSelectedDevices", "SubSchemas": [["Return",
                                                          {"Type": "UInt32", "Role": "Result"}], ["DeviceURNs", {"Type": "List", "Role": "Input", "SubSchemas": [["", {"Type": "String"}]]}]]}""")
SchemaServices.register_json_schema(SelectionServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "SelectionServices.RemoveSelectedDevices", "SubSchemas": [["Return",
                                                          {"Type": "UInt32", "Role": "Result"}], ["DeviceURNs", {"Type": "List", "Role": "Input", "SubSchemas": [["", {"Type": "String"}]]}]]}""")
SchemaServices.register_json_schema(SelectionServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "SelectionServices.ClearSelectedDevices", "SubSchemas": [["Return",
                                                          {"Type": "UInt32", "Role": "Result"}]]}""")
SchemaServices.register_json_schema(SelectionServices, """{"Type": "NamedTuple", "Role": "Callback", "TypeName": "SelectionServices.SelectedDevicesChangedCallback"}""")
