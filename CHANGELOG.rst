Change Log
==========

0.0.4.3 - Alpha
---------------
* Bugfix: Python3 str error in setup

0.0.4.2 - Alpha
---------------
* Minor Feature: New ``STORE_S3_ACL`` optional setting. S3 Uploads will auto be set to ``private``
  unless ``STORE_S3_ACL`` specifies a different ACL.

0.0.4.1 - Alpha
---------------
* Hotfix: Filename changed when saved is set on the provider instance

0.0.4 - Alpha
-------------
* Changed: Minor change to API, Provider now requires file instance or path

0.0.3.1 - Alpha
---------------
* Hotfix: Bug in FlaskStoreType where settings a ``None`` value would break the
  Provider, now checks the value is the expected instance type

0.0.3 - Alpha
-------------
* Feature: SQLAlchemy Store Type
* Changed: Renamed ``stores`` to ``providers``
* Removed: Removed ``FileStore`` wrapper class - it was a bad idea.

0.0.2 - Alpha
-------------
* Feature: FileStore wrapper around provider files
* Bugfix: S3 url generation

0.0.1 - Alpha
-------------
* Feature: Local File Storage
* Feature: S3 File Storage
* Feature: S3 Gevented File Storage
