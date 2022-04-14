from __future__ import unicode_literals

from _common import *
from boardgamegeek.exceptions import BGGApiError, BGGItemNotFoundError
from boardgamegeek.objects.collection import Collection
from boardgamegeek.loaders.collection import create_collection_from_xml, add_collection_items_from_xml

MISSING_STR_VAL = "missing"
MISSING_INT_VAL = -1
MISSING_FLOAT_VAL = -10.


def test_create_collection_from_xml_error(xml_collection_error):
    with pytest.raises(BGGItemNotFoundError,
                       match=re.escape(xml_collection_error.findtext("*/message", default=MISSING_STR_VAL))):
        create_collection_from_xml(xml_collection_error, TEST_INVALID_USER)


def test_create_collection_from_xml_minimal(xml_collection_minimal):
    # in
    collection = create_collection_from_xml(xml_collection_minimal, TEST_VALID_USER)

    # post
    assert collection.owner == TEST_VALID_USER


def test_add_collection_items_from_xml_without_stats(xml_collection_without_stats, mocker):
    # pre
    with pytest.raises(BGGApiError, match="missing 'stats'"):
        collection = mocker.MagicMock(Collection)

        # in
        add_collection_items_from_xml(collection, xml_collection_without_stats, "boardgame")


def test_add_collection_items_from_xml_minimal(xml_collection_minimal, mocker):
    # pre
    collection = mocker.MagicMock(Collection)

    # in
    add_collection_items_from_xml(collection, xml_collection_minimal, "boardgame")

    # post
    collection.add_game.assert_called()
    actual = collection.add_game.call_args.args[0]
    assert actual is not None

    item = xml_collection_minimal.find("item[@subtype='boardgame']")
    expected = {
        "id": int(item.attrib.get("objectid", MISSING_INT_VAL)),
        "comment": "",
        "name": None,
        "image": None,
        "thumbnail": None,
        "rating": None,
        "yearpublished": 0,
        "numplays": 0,
        "minplayers": 0,
        "maxplayers": 0,
        "minplaytime": 0,
        "maxplaytime": 0,
        "playingtime": 0,
        "stats": {
            "usersrated": None,
            "average": None,
            "bayesaverage": None,
            "stddev": None,
            "median": None,
            "ranks": [],
        }
    }
    assert actual == expected


def test_add_collection_items_from_xml_brief(xml_collection_brief, mocker):
    # pre
    collection = mocker.MagicMock(Collection)

    # in
    add_collection_items_from_xml(collection, xml_collection_brief, "boardgame")

    # post
    collection.add_game.assert_called()
    actual = collection.add_game.call_args.args[0]
    assert actual is not None

    item = xml_collection_brief.find("item[@subtype='boardgame']")
    stats = item.find("stats")
    expected = {
        "id": int(item.attrib.get("objectid", MISSING_INT_VAL)),
        "name": item.findtext("name", default=MISSING_STR_VAL),
        "comment": "",
        "image": None,
        "thumbnail": None,
        "yearpublished": 0,
        "numplays": 0,
        "stats": {
            "usersrated": None,
            "average": None,
            "bayesaverage": None,
            "stddev": None,
            "median": None,
            "ranks": [],
        },
        "rating": float(stats.find("rating").attrib.get("value", MISSING_FLOAT_VAL)),
    }

    del stats.attrib["numowned"]
    for key, value in stats.attrib.items():
        expected[key] = int(value)
    status = item.find("status")
    for key, value in status.attrib.items():
        expected[key] = value

    assert actual == expected


def test_add_collection_items_from_xml_full(xml_collection_full, mocker):
    # pre
    collection = mocker.MagicMock(Collection)

    # in
    add_collection_items_from_xml(collection, xml_collection_full, "boardgame")

    # post
    collection.add_game.assert_called()
    actual = collection.add_game.call_args.args[0]
    assert actual is not None

    item = xml_collection_full.find("item[@subtype='boardgame']")
    stats = item.find("stats")
    private = item.find("privateinfo")
    expected = {
        "id": int(item.attrib.get("objectid", MISSING_INT_VAL)),
        "name": item.findtext("name", default=MISSING_STR_VAL),
        "comment": item.findtext("comment", default=MISSING_STR_VAL),
        "image": item.findtext("image", default=MISSING_STR_VAL),
        "thumbnail": item.findtext("thumbnail", default=MISSING_STR_VAL),
        "yearpublished": int(item.findtext("yearpublished", default=MISSING_INT_VAL)),
        "numplays": int(item.findtext("numplays", default=MISSING_INT_VAL)),
        "stats": {
            "usersrated": None,
            "average": None,
            "bayesaverage": None,
            "stddev": None,
            "median": None,
            "ranks": [],
        },
        "rating": float(stats.find("rating").attrib.get("value", MISSING_FLOAT_VAL)),
        "private": {
            "comment": private.findtext("privatecomment", default=MISSING_STR_VAL),
            "paid": float(private.attrib.get("pricepaid", MISSING_FLOAT_VAL)),
            "currency": private.attrib.get("pp_currency", MISSING_STR_VAL),
            "currvalue": float(private.attrib.get("currvalue", MISSING_FLOAT_VAL)),
            "cv_currency": private.attrib.get("cv_currency", MISSING_STR_VAL),
            "quantity": int(private.attrib.get("quantity", MISSING_INT_VAL)),
            "acquired_on": private.attrib.get("acquisitiondate", MISSING_STR_VAL),
            "acquired_from": private.attrib.get("acquiredfrom", MISSING_STR_VAL),
            "location": private.attrib.get("inventorylocation", MISSING_STR_VAL),
        }
    }

    del stats.attrib["numowned"]
    for key, value in stats.attrib.items():
        expected[key] = int(value)
    for rank in stats.findall("ranks/rank"):
        expected["stats"]["ranks"].append({
            "type": rank.attrib.get("type", MISSING_STR_VAL),
            "id": rank.attrib.get("id", MISSING_INT_VAL),
            "name": rank.attrib.get("name", MISSING_STR_VAL),
            "friendlyname": rank.attrib.get("friendlyname", MISSING_STR_VAL),
            "value": rank.attrib.get("value", MISSING_STR_VAL),
            "bayesaverage": float(rank.attrib.get("bayesaverage", MISSING_FLOAT_VAL)),
        })
    status = item.find("status")
    for key, value in status.attrib.items():
        expected[key] = value

    assert actual == expected
