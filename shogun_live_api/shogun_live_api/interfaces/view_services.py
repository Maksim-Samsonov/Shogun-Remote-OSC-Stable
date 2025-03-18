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
"""Automatically generated ViewServices for Vicon Shogun Live API."""

from vicon_core_api import SchemaServices
from vicon_core_api import ViconInterface


class ViewServices(ViconInterface):
    """Functions for managing the application view settings."""
    def load_view_settings(self, file_path):
        """Load a view settings from file. The file path must be accessible from the remote host.

        Args:
            file_path < string >: Absolute path to view file.

        Return:
            return < Result >: Ok - On success.
                NotFound - If view file does not exist.
                FileIOFailure - If view file could not be loaded.
        """
        return self.client.send_command("ViewServices.LoadViewSettings", file_path)

    def save_view_settings(self, file_path):
        """Save view settings to a file. The file path must be accessible from the remote host.

        Args:
            file_path < string >: Absolute path to desired location of view file.

        Return:
            return < Result >: Ok - On success.
                FileIOFailure - If view file could not be saved.
        """
        return self.client.send_command("ViewServices.SaveViewSettings", file_path)

    def installed_view_settings_folder(self):
        """Get the folder path for pre-installed view files.

        Return:
            return < Result >: Ok - On success.
            folder_path < string >: Absolute path to installed view settings folder.
        """
        return self.client.send_command("ViewServices.InstalledViewSettingsFolder")

    def user_view_settings_folder(self):
        """Get the folder path for the current user view files.

        Return:
            return < Result >: Ok - On success.
            folder_path < string >: Absolute path to current user view settings folder.
        """
        return self.client.send_command("ViewServices.UserViewSettingsFolder")



SchemaServices.register_json_schema(ViewServices, """{"Type": "NamedTuple", "TypeName": "ViewServices"}""")
SchemaServices.register_json_schema(ViewServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "ViewServices.LoadViewSettings", "SubSchemas": [["Return", {"Type":
                                                     "UInt32", "Role": "Result"}], ["FilePath", {"Type": "String", "Role": "Input"}]]}""")
SchemaServices.register_json_schema(ViewServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "ViewServices.SaveViewSettings", "SubSchemas": [["Return", {"Type":
                                                     "UInt32", "Role": "Result"}], ["FilePath", {"Type": "String", "Role": "Input"}]]}""")
SchemaServices.register_json_schema(ViewServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "ViewServices.InstalledViewSettingsFolder", "SubSchemas": [["Return",
                                                     {"Type": "UInt32", "Role": "Result"}], ["FolderPath", {"Type": "String", "Role": "Output"}]]}""")
SchemaServices.register_json_schema(ViewServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "ViewServices.UserViewSettingsFolder", "SubSchemas": [["Return", {"Type":
                                                     "UInt32", "Role": "Result"}], ["FolderPath", {"Type": "String", "Role": "Output"}]]}""")
