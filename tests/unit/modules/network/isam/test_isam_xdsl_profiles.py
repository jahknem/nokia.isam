from textwrap import dedent

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_profiles import (
    Xdsl_profilesTemplate,
)


def test_xdsl_profiles_parse_live_observed_fields():
    parsed = Xdsl_profilesTemplate().parse(
        dedent(
            """
            configure xdsl
            service-profile 11 name YPLAY-30-Privat
              version 1
              max-bitrate-down 33000
              max-bitrate-up 5500
              max-delay-down 10
              max-delay-up 10
              active
            exit
            spectrum-profile 2 name VDSL2-17a-SNR6dB
              version 1
              dis-ansi-t1413
              g993-2-17a
              rf-band-list not-used
              vdsl
                pbo 1
                  param-a 4000
                exit
              exit
              active
            exit
            """
        )
    )

    assert parsed["service_profiles"][0]["max_bitrate_down"] == 33000
    assert parsed["service_profiles"][0]["active"] is True
    assert parsed["spectrum_profiles"][0]["g993_2_17a"] is True
    assert parsed["spectrum_profiles"][0]["commands"] == ["vdsl pbo 1 param-a 4000"]


def test_xdsl_profiles_render_commands():
    rendered = Xdsl_profilesTemplate().render_profile(
        "vect_profiles",
        {
            "id": 10,
            "name": "vect-default",
            "version": 1,
            "band_control_up": "0:0",
            "active": True,
        },
    )

    assert rendered == [
        "configure xdsl vect-profile 10 name vect-default",
        "configure xdsl vect-profile 10 version 1",
        "configure xdsl vect-profile 10 band-control-up 0:0",
        "configure xdsl vect-profile 10 active",
    ]
