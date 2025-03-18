##################################################################################
## MIT License
##
## Copyright (c) 2020 Vicon Motion Systems Ltd
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
"""Module containing built-in services for the Vicon Core API terminal."""

from vicon_core_api.vicon_interface import ViconInterface


class TerminalServices(ViconInterface):
    """Functions for getting information about the Vicon Core API terminal."""

    def application_information(self):
        """Get information about the application running the Vicon Core API server.

        Return:
            return < Result >: Ok - On success.
            name < string >: Application name.
            version < string >: Application version.
            changeset < string >: Application changeset.
        """
        result, args, _ = self.client.send_raw_command("Terminal.AppInfo")
        return result, args[0], args[1], args[2]
