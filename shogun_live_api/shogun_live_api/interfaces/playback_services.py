##################################################################################
## MIT License
##
## Copyright (c) 2019-2023 Vicon Motion Systems Ltd
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
"""Automatically generated PlaybackServices for Vicon Shogun Live API."""

from enum import Enum
from vicon_core_api import SchemaServices
from vicon_core_api import ViconInterface
from shogun_live_api.types.vicon_tick_135mhz import ViconTick135MHz #pylint: disable=unused-import


class PlaybackServices(ViconInterface):
    """Support for playing back from captured data on disk, or recent live data in the pause buffer."""

    class CaptureMetadata(object):
        """Metadata to aid identification and organization of captures.

        Members:
            capture_name < string >: Capture name.
            epoch_time < int >: Time of capture (UNIX Epoch time in seconds).
        """
        def __init__(self):
            """Initialiser for CaptureMetadata."""
            self.capture_name = ""
            self.epoch_time = 0

        def __str__(self):
            """Provide JSON string representation for CaptureMetadata."""
            return SchemaServices.write(self)


    class EOutputMode(Enum):
        """Data output mode.

        Enum Values:
            ENone: There is no data to output.
            ELive: Live data stream output.
            EReviewPlaying: Review data stream is playing.
            EReviewPaused: Review data stream is paused.
        """
        ENone = 0
        ELive = 1
        EReviewPlaying = 2
        EReviewPaused = 3


    class PlaybackState(object):
        """State of the playback system.

        Members:
            mode < PlaybackServices.EOutputMode >: Current data output mode.
            capture_name < string >: Current capture name. If playing back recent live data from the pause buffer, the capture name will be empty.
            start_tick < ViconTick135MHz >: Start of playback range.
            end_tick < ViconTick135MHz >: End of playback range. If there is no data available, this will be equal to the start tick.
            frame_period_in_ticks < int >: Frame period in ticks for playback (this can be different to the system frame period).
            session_id < int >: Synchronization session id. When a new sync session is started, the clock tick will reset to 0. Typical reasons for starting
                a new sync session include changing the system or a device frame rate, or connecting a new device.
        """
        def __init__(self):
            """Initialiser for PlaybackState."""
            self.mode = PlaybackServices.EOutputMode.ENone
            self.capture_name = ""
            self.start_tick = ViconTick135MHz()
            self.end_tick = ViconTick135MHz()
            self.frame_period_in_ticks = 0
            self.session_id = 0

        def __str__(self):
            """Provide JSON string representation for PlaybackState."""
            return SchemaServices.write(self)


    def capture_list(self):
        """Get the list of captures in the current review folder.

        Return:
            return < Result >: Ok - On success.
            captures < [PlaybackServices.CaptureMetadata] >: List of capture metadata.
        """
        return self.client.send_command("PlaybackServices.CaptureList")

    def review_folder(self):
        """Get the review folder path.

        Return:
            return < Result >: Ok - On success.
            folder < string >: The review folder path.
        """
        return self.client.send_command("PlaybackServices.ReviewFolder")

    def set_review_folder(self, folder):
        """Set the path for the review folder.

        Args:
            folder < string >: Path to a valid folder.

        Return:
            return < Result >: Ok - On success.
                InvalidArgument - If path does not correspond to a valid folder, or folder does not exist.
                NotPermitted - If the review folder is linked to the capture folder.
        """
        return self.client.send_command("PlaybackServices.SetReviewFolder", folder)

    def link_to_capture_folder(self):
        """Get if the review folder path should be linked to the capture folder path. If linked, the review folder will be set the same
        as the capture folder and change when it changes.

        Return:
            return < Result >: Ok - On success.
            linked < bool >: If the review folder is linked to the capture folder.
        """
        return self.client.send_command("PlaybackServices.LinkToCaptureFolder")

    def set_link_to_capture_folder(self, linked):
        """Set if the review folder path should be linked to the capture folder path.

        Args:
            linked < bool >: If the review folder is linked to the capture folder.

        Return:
            return < Result >: Ok - On success.
        """
        return self.client.send_command("PlaybackServices.SetLinkToCaptureFolder", linked)

    def state(self):
        """Get the current playback state.

        Return:
            return < Result >: Ok - On success.
            playback_state < PlaybackServices.PlaybackState >: Current playback state.
        """
        return self.client.send_command("PlaybackServices.State")

    def enter_capture_review(self, capture_name):
        """Review data in the capture folder.

        Args:
            capture_name < string >: Name of capture to open.

        Return:
            return < Result >: Ok - On success.
                NotPermitted - If already in review mode.
                NotFound - If the requested capture could not be found in the review folder.
                FileNotFound - If the requested capture was found but the MCP file required for review was not present.
        """
        return self.client.send_command("PlaybackServices.EnterCaptureReview", capture_name)

    def enter_live_review(self):
        """Review recent live data in the pause buffer.

        Return:
            return < Result >: Ok - On success.
                NotPermitted - If already in review mode.
        """
        return self.client.send_command("PlaybackServices.EnterLiveReview")

    def exit_review(self):
        """Exit the current review mode.

        Return:
            return < Result >: Ok - On success.
                Failed - Not in review mode.
        """
        return self.client.send_command("PlaybackServices.ExitReview")

    def play(self):
        """Start or resume playback. This has no effect in live output mode.

        Return:
            return < Result >: Ok - On success.
                NotPermitted - Playback controls are only provided in review mode.
        """
        return self.client.send_command("PlaybackServices.Play")

    def pause(self):
        """Pause playback. This has no effect in live output mode.

        Return:
            return < Result >: Ok - On success.
                NotPermitted - Playback controls are only provided in review mode.
        """
        return self.client.send_command("PlaybackServices.Pause")

    def tick(self):
        """Get the current clock tick at the data stream output.

        Return:
            return < Result >: Ok - On success.
            tick < ViconTick135MHz >: Clock tick at the current output frame.
        """
        return self.client.send_command("PlaybackServices.Tick")

    def set_tick(self, tick):
        """Set the clock tick at the data stream output. This has no effect in live output mode. If the requested tick is outside the
        playback range, it will be clamped to be within the playback range.

        Args:
            tick < ViconTick135MHz >: Clock tick for playback.

        Return:
            return < Result >: Ok - On success.
                NotPermitted - Playback controls are only provided in review mode.
                Failed - If the clock tick could not be set.
        """
        return self.client.send_command("PlaybackServices.SetTick", tick)

    def step_frames(self, frame_count):
        """Step forward or backward a number of frames. If playback loop is not enabled, this will be clamped to be within the playback
        range. This has no effect in live output mode, and playback must be stopped in order to step frames.

        Args:
            frame_count < int >: Number of frames to step.

        Return:
            return < Result >: Ok - On success
                .NotPermitted - Playback controls are only provided in review mode, and playback must be paused when stepping frames.
        """
        return self.client.send_command("PlaybackServices.StepFrames", frame_count)

    def loop_enabled(self):
        """If loop is enabled, playback will loop back to the start when reaching the end of the playback range.

        Return:
            return < Result >: Ok - On success.
            loop_enabled < bool >: Playback loop enabled value.
        """
        return self.client.send_command("PlaybackServices.LoopEnabled")

    def set_loop_enabled(self, loop_enabled):
        """Set the value of loop enabled. If loop is enabled, playback will loop back to the start when reaching the end of the playback
        range.

        Args:
            loop_enabled < bool >: Playback loop enabled value.

        Return:
            return < Result >: Ok - On success.
        """
        return self.client.send_command("PlaybackServices.SetLoopEnabled", loop_enabled)

    def add_capture_list_changed_callback(self, function):
        """Callback issued whenever the capture list changes."""
        return self.client.add_callback("PlaybackServices.CaptureListChangedCallback", function)

    def add_parameter_changed_callback(self, function):
        """Callback issued whenever a playback parameter changes."""
        return self.client.add_callback("PlaybackServices.ParameterChangedCallback", function)

    def add_state_changed_callback(self, function):
        """Callback issued whenever the playback state changes. Note that clock ticks do not trigger this callback."""
        return self.client.add_callback("PlaybackServices.StateChangedCallback", function)

    def remove_callback(self, callback_id):
        """Remove callback of any type using the id supplied when it was added."""
        return self.client.remove_callback(callback_id)



SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "TypeName": "PlaybackServices"}""")
SchemaServices.register_json_schema(PlaybackServices.CaptureMetadata, """{"Type": "NamedTuple", "TypeName": "PlaybackServices.CaptureMetadata", "SubSchemas": [["CaptureName", {"Type": "String"}],
                                                                         ["EpochTime", {"Type": "Int64"}]]}""")
SchemaServices.register_json_schema(PlaybackServices.EOutputMode, """{"Type": "Enum32", "TypeName": "PlaybackServices.EOutputMode", "EnumValues": [["None", 0], ["Live", 1], ["ReviewPlaying",
                                                                     2], ["ReviewPaused", 3]]}""")
SchemaServices.register_json_schema(PlaybackServices.PlaybackState, """{"Type": "NamedTuple", "TypeName": "PlaybackServices.PlaybackState", "SubSchemas": [["Mode", {"Type": "Ref", "TypeName":
                                                                       "PlaybackServices.EOutputMode"}], ["CaptureName", {"Type": "String"}], ["StartTick", {"Type": "Ref", "TypeName": "ViconTick135MHz"}],
                                                                       ["EndTick", {"Type": "Ref", "TypeName": "ViconTick135MHz"}], ["FramePeriodInTicks", {"Type": "UInt64"}], ["SessionId", {"Type":
                                                                       "UInt32"}]]}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "PlaybackServices.CaptureList", "SubSchemas": [["Return", {"Type":
                                                         "UInt32", "Role": "Result"}], ["Captures", {"Type": "List", "Role": "Output", "SubSchemas": [["", {"Type": "Ref", "TypeName":
                                                         "PlaybackServices.CaptureMetadata"}]]}]]}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "PlaybackServices.ReviewFolder", "SubSchemas": [["Return", {"Type":
                                                         "UInt32", "Role": "Result"}], ["Folder", {"Type": "String", "Role": "Output"}]]}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "PlaybackServices.SetReviewFolder", "SubSchemas": [["Return", {"Type":
                                                         "UInt32", "Role": "Result"}], ["Folder", {"Type": "String", "Role": "Input"}]]}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "PlaybackServices.LinkToCaptureFolder", "SubSchemas": [["Return",
                                                         {"Type": "UInt32", "Role": "Result"}], ["Linked", {"Type": "Bool", "Role": "Output"}]]}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "PlaybackServices.SetLinkToCaptureFolder", "SubSchemas": [["Return",
                                                         {"Type": "UInt32", "Role": "Result"}], ["Linked", {"Type": "Bool", "Role": "Input"}]]}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "PlaybackServices.State", "SubSchemas": [["Return", {"Type": "UInt32",
                                                         "Role": "Result"}], ["PlaybackState", {"Type": "Ref", "Role": "Output", "TypeName": "PlaybackServices.PlaybackState"}]]}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "PlaybackServices.EnterCaptureReview", "SubSchemas": [["Return", {"Type":
                                                         "UInt32", "Role": "Result"}], ["CaptureName", {"Type": "String", "Role": "Input"}]]}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "PlaybackServices.EnterLiveReview", "SubSchemas": [["Return", {"Type":
                                                         "UInt32", "Role": "Result"}]]}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "PlaybackServices.ExitReview", "SubSchemas": [["Return", {"Type":
                                                         "UInt32", "Role": "Result"}]]}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "PlaybackServices.Play", "SubSchemas": [["Return", {"Type": "UInt32",
                                                         "Role": "Result"}]]}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "PlaybackServices.Pause", "SubSchemas": [["Return", {"Type": "UInt32",
                                                         "Role": "Result"}]]}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "PlaybackServices.Tick", "SubSchemas": [["Return", {"Type": "UInt32",
                                                         "Role": "Result"}], ["Tick", {"Type": "Ref", "Role": "Output", "TypeName": "ViconTick135MHz"}]]}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "PlaybackServices.SetTick", "SubSchemas": [["Return", {"Type": "UInt32",
                                                         "Role": "Result"}], ["Tick", {"Type": "Ref", "Role": "Input", "TypeName": "ViconTick135MHz"}]]}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "PlaybackServices.StepFrames", "SubSchemas": [["Return", {"Type":
                                                         "UInt32", "Role": "Result"}], ["FrameCount", {"Type": "Int32", "Role": "Input"}]]}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "PlaybackServices.LoopEnabled", "SubSchemas": [["Return", {"Type":
                                                         "UInt32", "Role": "Result"}], ["LoopEnabled", {"Type": "Bool", "Role": "Output"}]]}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Function", "TypeName": "PlaybackServices.SetLoopEnabled", "SubSchemas": [["Return", {"Type":
                                                         "UInt32", "Role": "Result"}], ["LoopEnabled", {"Type": "Bool", "Role": "Input"}]]}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Callback", "TypeName": "PlaybackServices.CaptureListChangedCallback"}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Callback", "TypeName": "PlaybackServices.ParameterChangedCallback"}""")
SchemaServices.register_json_schema(PlaybackServices, """{"Type": "NamedTuple", "Role": "Callback", "TypeName": "PlaybackServices.StateChangedCallback"}""")
