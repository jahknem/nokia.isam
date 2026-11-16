"""Targeted gathering cases: xDSL, line test, ethernet line and interface cage/alarm resources."""


def case(module, config, lines, sibling_config, sibling, marker, sibling_marker, answer=None):
    result = {"module": module, "config": config, "lines": lines, "sibling_config": sibling_config,
              "sibling": sibling, "marker": marker, "sibling_marker": sibling_marker}
    if answer is not None:
        result["answer"] = answer
    return result


def _scoped(command, lines, full):
    """Lines addressed by 'info configure <path>' (prefix match), or None for nothing."""
    path = "configure " + command[len("info configure "):]
    if command == full:
        return lines or None
    return [line for line in lines if line == path or line.startswith(path + " ")] or None


def _linetest_answer(command, lines):
    """'info configure linetest' is read without flat: attributes nested below their instance."""
    hits = _scoped(command, lines, "info configure linetest")
    if hits is None:
        return None
    blocks = []
    for line in hits:
        tokens = line.split()
        size = 5 if tokens[3] == "ltsession" else 6  # configure linetest single ltparm <session> <test>
        header, attrs = tokens[:size], tokens[size:]
        pairs = [" ".join(attrs[index:index + 2]) for index in range(0, len(attrs), 2)]
        if command == "info configure linetest":
            blocks.append("\n".join(["    " + " ".join(header[3:])] + ["      " + pair for pair in pairs] + ["    exit"]))
        else:
            blocks.append("\n".join([" ".join(header)] + ["  " + pair for pair in pairs] + ["exit"]))
    if command == "info configure linetest":
        return "configure linetest\n  single\n%s\n  exit\nexit\n" % "\n".join(blocks)
    return "\n".join(blocks) + "\n"


def _interface_alarm_answer(command, lines):
    """Whole read as captured live (one line per alarm), a single alarm as an indented block."""
    hits = _scoped(command, lines, "info configure interface alarm")
    if hits is None:
        return None
    if command == "info configure interface alarm":
        return "\n".join(hits) + "\n"
    blocks = []
    for line in hits:
        tokens = line.split()
        blocks.append("%s\n  %s\nexit" % (" ".join(tokens[:4]), " ".join(tokens[4:])))
    return "\n".join(blocks) + "\n"


def _profile_case(key, cli_type, target, sibling, target_name, sibling_name, attrs):
    return case("isam_xdsl_profiles", {key: [{"id": target}]},
                ["configure xdsl %s %s name %s %s" % (cli_type, target, target_name, attrs)],
                {key: [{"id": sibling}]},
                ["configure xdsl %s %s name %s %s" % (cli_type, sibling, sibling_name, attrs)],
                target_name, sibling_name)


CASES = {
    "xdsl_lines": case("isam_xdsl_lines", [{"name": "1/1/3/1"}],
                       ["configure xdsl line 1/1/3/1 service-profile 13 spectrum-profile 2 dpbo-profile 1 vect-profile 10 admin-up"],
                       [{"name": "1/1/3/10"}],
                       ["configure xdsl line 1/1/3/10 service-profile 14 spectrum-profile 2 dpbo-profile 1 vect-profile 10 admin-up"],
                       "1/1/3/1'", "1/1/3/10'"),
    "xdsl_boards:boards": case("isam_xdsl_boards", {"boards": [{"board_id": "1/1/3"}]},
                               ["configure xdsl board 1/1/3 dpbo-profile 1 vce-profile 10"],
                               {"boards": [{"board_id": "1/1/30"}]},
                               ["configure xdsl board 1/1/30 dpbo-profile 2 vce-profile 11"],
                               "1/1/3'", "1/1/30'"),
    "xdsl_boards:vp_boards": case("isam_xdsl_boards", {"vp_boards": [{"vp_board_id": "1/1/1"}]},
                                  ["configure xdsl vp-board 1/1/1 vp-link 1 lt-expect 1/1/4"],
                                  {"vp_boards": [{"vp_board_id": "1/1/10"}]},
                                  ["configure xdsl vp-board 1/1/10 vp-link 2 lt-expect 1/1/5"],
                                  "1/1/1'", "1/1/10'"),
    "xdsl_profiles:service_profiles": _profile_case(
        "service_profiles", "service-profile", 11, 110, "YPLAY-30-Privat", "YPLAY-50-Business",
        "version 1 max-bitrate-down 33000 max-bitrate-up 5500"),
    "xdsl_profiles:spectrum_profiles": _profile_case(
        "spectrum_profiles", "spectrum-profile", 1, 12, "ADSL-AnxBJ-SNR6dB", "VDSL-17a-SNR9dB", "version 1 dis-ansi-t1413"),
    "xdsl_profiles:dpbo_profiles": _profile_case(
        "dpbo_profiles", "dpbo-profile", 1, 13, "DPBO-ESEL-0249", "DPBO-KVZ-0310", "es-elect-length 249 active"),
    "xdsl_profiles:vect_profiles": _profile_case(
        "vect_profiles", "vect-profile", 10, 100, "vect-default", "vect-legacy", "version 1 band-control-up 0:0 active"),
    "xdsl_profiles:vce_profiles": _profile_case(
        "vce_profiles", "vce-profile", 10, 100, "vce-default", "vce-legacy", "version 1 vce-join-timeout auto active"),
    "linetest:sessions": case("isam_linetest", {"sessions": [{"session_id": "3"}]},
                              ["configure linetest single ltsession 3 ownerid lt-owner-a timeout-period 30"],
                              {"sessions": [{"session_id": "30"}]},
                              ["configure linetest single ltsession 30 ownerid lt-owner-b timeout-period 60"],
                              "lt-owner-a", "lt-owner-b", _linetest_answer),
    "linetest:parameters": case("isam_linetest", {"parameters": [{"session_id": "3", "test_name": "resistance"}]},
                                ["configure linetest single ltparm 3 resistance value1 1000 min-threshold 4711"],
                                {"parameters": [{"session_id": "3", "test_name": "capacitance"}]},
                                ["configure linetest single ltparm 3 capacitance value1 2000 min-threshold 8822"],
                                "4711", "8822", _linetest_answer),
    "ethernet_line": case("isam_ethernet_line", [{"if_index": "1/1/8/1"}],
                          ["configure ethernet line 1/1/8/1 port-type uni admin-up",
                           "configure ethernet line 1/1/8/1 mau 1 type 1000basebx10d power up"],
                          [{"if_index": "1/1/8/10"}],
                          ["configure ethernet line 1/1/8/10 port-type uni admin-up",
                           "configure ethernet line 1/1/8/10 mau 1 type 1000basebx10u power up"],
                          "1000basebx10d", "1000basebx10u"),
    "interface_cages": case("isam_interface_cages", [{"id": "lt:1/1/2:cage:1"}],
                            ["configure interface cage lt:1/1/2:cage:1 operational-mode gpon"],
                            [{"id": "lt:1/1/2:cage:10"}],
                            ["configure interface cage lt:1/1/2:cage:10 operational-mode xgspon"],
                            "lt:1/1/2:cage:1'", "lt:1/1/2:cage:10'"),
    "interface_alarms": case("isam_interface_alarms", [{"name": "epon"}],
                             ["configure interface alarm epon default-severity minor"],
                             [{"name": "eont"}],
                             ["configure interface alarm eont default-severity critical"],
                             "'epon'", "'eont'", _interface_alarm_answer),
}
