"""Tests for whos_who_lib — each case is a wrong match stage 2 found and fixed."""
import importlib.util
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import whos_who_lib as W  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "whos_who_orgs", os.path.join(os.path.dirname(os.path.abspath(__file__)), "whos-who-orgs.py"))
O = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(O)


def test_bare_country_tells_the_congos_apart():
    assert W.bare_country("République démocratique du Congo") == "COD"
    assert W.bare_country("government of drc") == "COD"
    assert W.bare_country("Congo") == "COG"


def test_bare_country_refuses_a_region_and_reads_sao_tome_whole():
    assert W.bare_country("government of karnataka") is None
    assert W.bare_country("gouvernement provincial tshopo") is None
    assert W.bare_country("government of sao tome and principe") == "STP"


def test_named_countries_must_agree():
    assert W.match_strength("Burkina Faso Ministry of Health", "ministry-of-health-eswatini", None) == 0
    assert W.match_strength("Togo AI", "ai-uganda", None) == 0
    assert W.match_strength("Huawei Namibia", "huawei", None) > 0


def test_a_region_stays_in_the_stem():
    assert W._key("somaliland-ministry-of-interior") != W._key("puntland-ministry-of-interior")


def test_written_form_must_be_the_slugs_own_name():
    assert O.owns("Ministère de l’Eau et de l’Énergie", "ministere-eau-energie-tchad")
    assert O.owns("Ministère de l’Education Nationale et de la Promotion Civique", "menpc-tchad")
    assert not O.owns("Government of Lesotho", "office-of-the-prime-minister-lesotho")
    assert not O.owns("Angola", "joao-lourenco")
