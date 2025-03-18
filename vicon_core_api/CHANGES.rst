1.2.0
=====

C#
* No changes.

Python
* Updated package configuration to use pyproject.toml
* Added workaround to install script for newer versions of pip (21.3 and above). This fixes an error when running the install script directly from C:\Program Files


1.1.9
=====

C#
* No changes.

Python
* Added default implementation for Client callback on failure.


1.1.8
=====

C#
* No changes.

Python
* Added Python 3 support.


1.1.7 (2020-03-23)
==================

C#
* Fixed serialization of class parameters (e.g. ClusterDeviceServices.StatusLightUserSettingsData).
* Ensure client services schemas are registered before checking for compatibility with the server.
* Added ToString implementation to Result class.

Python
* No changes.


1.1.6 (2020-03-02)
==================

C#
* No changes.

Python
* Added separate timeout to client for sending commands.


1.1.5 (2019-10-31)
==================

C#
* No changes.

Python
* Fixed client failure to send all command data when a partial socket write occurs.
* Fixed client socket timeout not being set correctly.
* Allow setting no timeout on client socket.
* Better client error message on RPC failure when sending a command.


1.1.4 (2019-07-16)
==================

C#
* No changes.

Python
* Added implementation of __repr__ to Result.


1.1.3 (2019-04-17)
==================

C#
* Fixed ClientProvider sending two disconnection events when the server closes a connection, and creating an extra client connection on retry.

Python
* No changes.


1.1.2 (2018-11-15)
==================

C#
* Changed callback registration to avoid a deadlock occurring when a callback is triggered on one thread while registering for a callback on another thread.

Python
* No changes.


1.1.1 (2018-10-24)
==================

C#
* Disabled warning in Client.InitialiseConnectionAsync.

Python
* Added method to de-register a schema type to SchemaServices.


1.1.0 (2018-07-23)
==================

C#
* Fixed NullReferenceException if Client.ErrorEvent is not subscribed when an error occurs.
* ClientProvider will reconnect if network cable is unplugged and plugged back in.

Python
* No changes


1.0.0 (2018-06-13)
==================

* Initial release of Vicon Core API.
