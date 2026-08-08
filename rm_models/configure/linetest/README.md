# LineTest safe subset

`isam_linetest` parses, renders, and gathers declarative single LineTest
session and parameter configuration. It intentionally excludes session
commands, line-status changes, and all other test actions. The module never
sends configuration or test commands to a device.
