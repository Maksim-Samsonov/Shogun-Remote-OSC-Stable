1.10.0
======

* Updated package configuration to use pyproject.toml
* Added workaround to install script for newer versions of pip (21.3 and above). This fixes an error when running the install script directly from C:\Program Files
* Added CameraCalibrationServices.StartWandWaveSelected and CameraCalibrationServices.CameraCalibrationFolder.
* Added ApplicationServices.SystemConfigurationFolder.
* PlaybackServices: added functions to get and set the review folder. Added functions to get and set linking to the capture folder.
* Added SubjectServices.TrackingConfigurationFolder.
* Added CameraDeviceServices. This supports monitoring camera status and settings.
* Added SelectionServices. This supports control of device selection.
* Added ViewServices. This supports loading and saving of view settings files.


1.6.0
=====

* Added CameraCalibrationServices.StartWandWaveSelected.


1.5.0
=====

* Added CameraCalibrationServices.SetFloorExtents, StartRecoverCameraPosition, StopRecoverCameraPosition, and CancelRecoverCameraPosition.
* CameraCalibrationServices: added more error codes to ESetOriginReadyState.


1.4.0
=====

* SubjectCalibrationServices: removed solving template functions.
* Added Python 3 support.


1.3.0 (2020-12-05)
==================

* Added PlaybackServices. This allows for review of captured data, or recent live data in the pause buffer.
* Added LogServices. This allows control over message logging levels.
* Added CameraCalibrationServices.AutoNumberCameras - this sets camera user ids according to their position in the volume.
* ApplicationServices: added functions for getting licensing information.
* SubjectServices: subject types EProp and ETrackerObject replaced by ERigidObject.


1.2.1 (2018-08-22)
==================

* Added SubjectCalibrationServices. This provides functionality for control of live subject calibration.


1.2.0 (2018-06-19)
==================

* Added subject type argument to SubjectServices.import_subject
* Removed SubjectServices.import_subject_as_prop


1.0.0 (2017-05-26)
==================

* Initial release of shogun_live_api.
