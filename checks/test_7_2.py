"""Task 7.2 · get_devices() and api_to_inventory() in netlab/inventory.py, live against the lab's API."""
import gen
import pytest
from conftest import ROOT, call

from netlab.inventory import ApiError, api_to_inventory, get_devices, load_inventory


def test_reshape_unseen():
    for _ in range(20):
        devices, api = gen.inventory()
        got = call(api_to_inventory, api)
        assert got == devices, f"for the API's devices\n{api}\nwe expected\n{devices}\nand got\n{got}"


def test_live(lab_up):
    env = lab_up.env()
    results = call(get_devices, env["LAB_API_URL"], env["LAB_API_TOKEN"])
    assert isinstance(results, list), f"get_devices should return the results list, not {type(results).__name__}"
    status, body = lab_up.api_get("/api/devices/")
    assert results == body["results"], "get_devices should return the JSON's results, as they are"
    assert call(api_to_inventory, results) == call(load_inventory, ROOT / "inventory.yml"), \
        "the API and inventory.yml should give the same list of devices"


def test_bad_token(lab_up):
    env = lab_up.env()
    with pytest.raises(ApiError) as e:
        call(get_devices, env["LAB_API_URL"], "not-the-token")
    assert "403" in str(e.value), f"say what the API answered (403) in the message: {e.value}"


def test_no_answer(lab_up):
    with pytest.raises(ApiError):
        call(get_devices, "http://api:8999", "x")
