from ansible_collections.nokia.isam.plugins.modules import isam_igmp, isam_mcast_control
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.igmp.igmp import IgmpArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.mcast_control.mcast_control import Mcast_controlArgs


def test_igmp_schema_does_not_own_mcast_control():
    assert "mcast_control" not in IgmpArgs.argument_spec["config"]["options"]
    assert "configure igmp" in isam_igmp.DOCUMENTATION
    assert "configure mcast-control" not in isam_igmp.DOCUMENTATION


def test_mcast_control_schema_does_not_own_igmp():
    assert "igmp" not in Mcast_controlArgs.argument_spec["config"]["options"]
    assert "configure mcast-control" in isam_mcast_control.DOCUMENTATION
    assert "configure igmp" not in isam_mcast_control.DOCUMENTATION
