from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.ont_software.ont_software import (
    parse_ont_sw_download,
    parse_ont_sw_version,
)


def test_parse_ont_sw_version_pipe_table():
    output = """
    sw-ver | sw-ver-size
    -------+------------
    R6.2.1 | 12345678
    R6.2.2 | 23456789
    """

    assert parse_ont_sw_version(output) == [
        {"sw_ver": "R6.2.1", "sw_ver_size": "12345678"},
        {"sw_ver": "R6.2.2", "sw_ver_size": "23456789"},
    ]


def test_parse_ont_sw_version_labeled_detail():
    output = """
    sw-ver: R6.2.1
    sw-ver-size = 12345678
    """

    assert parse_ont_sw_version(output) == [
        {"sw_ver": "R6.2.1", "sw_ver_size": "12345678"}
    ]


def test_parse_ont_sw_download_fixed_width_table():
    output = """
    ont planned inactive planned-notok download-notok download-inprogress ntlt-inprogress omci-inprogress ontswact-inprogress sw-version-mismatch sw-download-failure sw-delayactivate
    --- ------- -------- ------------- --------------- ------------------- --------------- ----------------- --------------------- -------------------- -------------------- -----------------
    1/1/1/1/1 no      no       no            no              yes                 no              no                no                    no                   no                   no
    """

    assert parse_ont_sw_download(output) == [
        {
            "ont": "1/1/1/1/1",
            "planned": "no",
            "inactive": "no",
            "planned_notok": "no",
            "download_notok": "no",
            "download_inprogress": "yes",
            "ntlt_inprogress": "no",
            "omci_inprogress": "no",
            "ontswact_inprogress": "no",
            "sw_version_mismatch": "no",
            "sw_download_failure": "no",
            "sw_delayactivate": "no",
        }
    ]


def test_parse_ont_sw_download_labeled_detail_and_empty_output():
    output = """
    planned: no
    download-inprogress: yes
    sw-version-mismatch: no
    sw-download-failure: no
    """

    assert parse_ont_sw_download(output) == [
        {
            "planned": "no",
            "download_inprogress": "yes",
            "sw_version_mismatch": "no",
            "sw_download_failure": "no",
        }
    ]
    assert parse_ont_sw_download("") == []
    assert parse_ont_sw_version("") == []


def test_parse_ont_sw_version_with_sw_ver_id_column():
    output = """
    sw-ver-id | sw-ver | sw-ver-size
    ----------+--------+------------
    1         | R6.2.1 | 12345678
    2         | R6.2.2 | 23456789
    """

    assert parse_ont_sw_version(output) == [
        {"sw_ver_id": "1", "sw_ver": "R6.2.1", "sw_ver_size": "12345678"},
        {"sw_ver_id": "2", "sw_ver": "R6.2.2", "sw_ver_size": "23456789"},
    ]


def test_parse_ont_sw_download_with_ont_idx_and_two_line_header():
    output = """
              |       |download  |ntlt
    ont-idx   |planned|inprogress|inprogress
    ----------+-------+----------+----------
    1/1/1/1/1  no      no         no
    1/1/1/1/2  yes     no         no
    """

    result = parse_ont_sw_download(output)
    assert len(result) == 2
    assert result[0]["ont"] == "1/1/1/1/1"
    assert result[0]["planned"] == "no"
    assert result[1]["ont"] == "1/1/1/1/2"
    assert result[1]["planned"] == "yes"


def test_parse_ont_sw_version_ignores_count_line():
    output = """
    sw-ver-id | sw-ver | sw-ver-size
    ----------+--------+------------
    1         | R6.2.1 | 12345678
    sw-version count : 1
    """

    result = parse_ont_sw_version(output)
    assert len(result) == 1
    assert result[0]["sw_ver"] == "R6.2.1"


def test_parse_ont_sw_download_ignores_count_line():
    output = """
    ont-idx | planned
    --------+--------
    1/1/1/1  no
    sw-download count : 1
    """

    result = parse_ont_sw_download(output)
    assert len(result) == 1
    assert result[0]["ont"] == "1/1/1/1"
