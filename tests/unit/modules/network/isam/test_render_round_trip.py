"""Round-trip tests: parse → render → parse should produce identical results."""

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.efm_oam import EfmOamTemplate
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.l2cp import L2cpTemplate, L2cpSessionTemplate, L2cpUserPortTemplate
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.pppoe_client import PppoeClientTemplate, Pppoel2StatisticsTemplate


def test_efm_oam_round_trip():
    """Test EFM OAM parse → render → parse round trip."""
    config = """
configure efm-oam interface 1/1/8/1 admin-up passive-mode
configure efm-oam interface 1/1/8/2 keep-alive-intvl 5000
"""
    template = EfmOamTemplate()
    
    # Parse
    parsed = template.parse(config)
    assert len(parsed) == 2
    assert parsed[0]["name"] == "1/1/8/1"
    assert parsed[0]["admin_up"] is True
    assert parsed[0]["passive_mode"] is True
    
    # Render
    rendered = template.render(parsed)
    assert len(rendered) == 2
    assert "configure efm-oam interface 1/1/8/1 admin-up passive-mode" in rendered
    
    # Parse again
    reparsed = template.parse("\n".join(rendered))
    assert reparsed == parsed


def test_l2cp_round_trip():
    """Test L2CP parse → render → parse round trip."""
    config = """
configure l2cp partition-type gsmp
"""
    template = L2cpTemplate()
    
    # Parse
    parsed = template.parse(config)
    assert len(parsed) == 1
    assert parsed[0]["partition_type"] == "gsmp"
    
    # Render
    rendered = template.render(parsed)
    assert len(rendered) == 1
    assert "configure l2cp partition-type gsmp" in rendered
    
    # Parse again
    reparsed = template.parse("\n".join(rendered))
    assert reparsed == parsed


def test_l2cp_session_round_trip():
    """Test L2CP session parse → render → parse round trip."""
    config = """
configure l2cp session sess1 bras-ip-address 192.168.1.1 gsmp-version 1
configure l2cp session sess2 bras-ip-address 192.168.1.2 gsmp-version 2
"""
    template = L2cpSessionTemplate()
    
    # Parse
    parsed = template.parse(config)
    assert len(parsed) == 2
    assert parsed[0]["name"] == "sess1"
    assert parsed[0]["gsmp_version"] == "1"
    assert parsed[0]["bras_ip_address"] == "192.168.1.1"
    
    # Render
    rendered = template.render(parsed)
    assert len(rendered) == 2
    
    # Parse again
    reparsed = template.parse("\n".join(rendered))
    assert reparsed == parsed


def test_l2cp_user_port_round_trip():
    """Test L2CP user-port parse → render → parse round trip."""
    config = """
configure l2cp user-port 1/1/2/1/1/1/1 partition-id 1
configure l2cp user-port 1/1/2/1/1/1/2 partition-id 2
"""
    template = L2cpUserPortTemplate()
    
    # Parse
    parsed = template.parse(config)
    assert len(parsed) == 2
    assert parsed[0]["name"] == "1/1/2/1/1/1/1"
    assert parsed[0]["partition_id"] == "1"
    
    # Render
    rendered = template.render(parsed)
    assert len(rendered) == 2
    assert "configure l2cp user-port 1/1/2/1/1/1/1 partition-id 1" in rendered
    
    # Parse again
    reparsed = template.parse("\n".join(rendered))
    assert reparsed == parsed


def test_pppoe_client_interface_round_trip():
    """Test PPPoE client interface parse → render → parse round trip."""
    config = """
configure pppoe-client interface ppp1 client-id 100 username user1 password pass1
"""
    template = PppoeClientTemplate(kind="interface")
    
    # Parse
    parsed = template.parse(config)
    assert len(parsed) == 1
    assert parsed[0]["name"] == "ppp1"
    assert parsed[0]["client_id"] == 100
    assert parsed[0]["username"] == "user1"
    
    # Render
    rendered = template.render(parsed)
    assert len(rendered) == 1
    assert "configure pppoe-client interface ppp1" in rendered[0]
    
    # Parse again
    reparsed = template.parse("\n".join(rendered))
    assert reparsed == parsed


def test_pppoe_client_profile_round_trip():
    """Test PPPoE client profile parse → render → parse round trip."""
    config = """
configure pppoe-client ppp-profile prof1 ipversion ipv4 authproto pap mru 1492
"""
    template = PppoeClientTemplate(kind="profile")
    
    # Parse
    parsed = template.parse(config)
    assert len(parsed) == 1
    assert parsed[0]["name"] == "prof1"
    assert parsed[0]["ipversion"] == "ipv4"
    assert parsed[0]["authproto"] == "pap"
    assert parsed[0]["mru"] == 1492
    
    # Render
    rendered = template.render(parsed)
    assert len(rendered) == 1
    assert "configure pppoe-client ppp-profile prof1" in rendered[0]
    
    # Parse again
    reparsed = template.parse("\n".join(rendered))
    assert reparsed == parsed


def test_pppoel2_statistics_round_trip():
    """Test PPPoEL2 statistics parse → render → parse round trip."""
    config = """
configure pppoel2 statistics stats1
configure pppoel2 no statistics stats2
"""
    template = Pppoel2StatisticsTemplate()
    
    # Parse
    parsed = template.parse(config)
    assert len(parsed) == 2
    assert parsed[0]["name"] == "stats1"
    assert parsed[0]["enabled"] is True
    assert parsed[1]["name"] == "stats2"
    assert parsed[1]["enabled"] is False
    
    # Render
    rendered = template.render(parsed)
    assert len(rendered) == 2
    assert "configure pppoel2 statistics stats1" in rendered
    assert "configure pppoel2 no statistics stats2" in rendered
    
    # Parse again
    reparsed = template.parse("\n".join(rendered))
    assert reparsed == parsed
