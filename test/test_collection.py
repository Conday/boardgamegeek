from __future__ import unicode_literals

from _common import *
from boardgamegeek import BGGError, BGGValueError, BGGItemNotFoundError
from boardgamegeek.objects.collection import CollectionBoardGame, Collection
from boardgamegeek.objects.games import BoardGameVersion, BoardGamePrivate


def test_get_collection_with_invalid_parameters(bgg):
    for invalid in [None, ""]:
        with pytest.raises(BGGValueError):
            bgg.collection(invalid)


def test_get_invalid_users_collection(bgg, mocker):
    mock_get = mocker.patch("requests.sessions.Session.get")
    mock_get.side_effect = simulate_bgg

    with pytest.raises(BGGItemNotFoundError):
        bgg.collection(TEST_INVALID_USER)


def test_get_valid_users_collection(bgg, mocker, null_logger):
    mock_get = mocker.patch("requests.sessions.Session.get")
    mock_get.side_effect = simulate_bgg

    collection = bgg.collection(TEST_VALID_USER, versions=True)

    assert collection is not None
    assert collection.owner == TEST_VALID_USER
    assert type(len(collection)) == int
    assert type(collection.items) == list

    # make sure we can iterate through the collection
    for g in collection:
        assert type(g) == CollectionBoardGame
        assert type(g.id) == int
        assert type(g.comment) in STR_TYPES_OR_NONE
        if g.version is not None:
            assert type(g.version) == BoardGameVersion
        repr(g)

    str(collection)
    repr(collection)

    # for coverage's sake
    collection._format(null_logger)
    assert type(collection.data()) == dict

    collection = bgg.collection(TEST_VALID_USER, versions=False)
    for g in collection:
        assert g.version is None

    # TODO: test the filters for the collection


def test_creating_collection_out_of_raw_data():
    # test raise exception if invalid items given
    with pytest.raises(BGGError):
        Collection({"items": [{"id": 102}]})

    # test that items are added to the collection from the constructor
    data = {
        "owner": "me",
        "items": [{
            "id": 100,
            "name": "foobar",
            "image": "",
            "thumbnail": "",
            "yearpublished": 1900,
            "numplays": 32,
            "comment": "This game is great!",
            "minplayers": 1,
            "maxplayers": 5,
            "minplaytime": 60,
            "maxplaytime": 120,
            "playingtime": 100,
            "stats": {
                "usersrated": 123,
                "ranks": [{
                    "id": "1",
                    "type": "subtype",
                    "name": "boardgame",
                    "friendlyname": "friendly",
                    "value": "10",
                    "bayesaverage": "0.51"
                }]
            },
            "private": {
                "comment": "private comment",
                "paid": 42.0,
                "currency": "USD",
                "currvalue": 23.0,
                "cv_currency": "EUR",
                "quantity": "1",
                "acquired_on": "2000-01-01",
                "acquired_from": "store",
                "location": "home",
            },
        }]
    }
    c = Collection(data)

    assert len(c) == 1
    assert c.owner == "me"

    ci = c[0]

    assert type(ci) == CollectionBoardGame
    assert ci.id == 100
    assert ci.name == "foobar"
    assert ci.year == 1900
    assert ci.numplays == 32
    assert ci.comment == "This game is great!"
    assert ci.min_players == 1
    assert ci.max_players == 5
    assert ci.min_playing_time == 60
    assert ci.max_playing_time == 120
    assert ci.playing_time == 100
    assert ci.bgg_rank == 10
    assert ci.users_rated == 123
    assert ci.rating_bayes_average is None
    assert ci.private is not None
    assert ci.private_comment == "private comment"
    assert ci.paid == 42.0
    assert ci.currency == "USD"
    assert ci.currvalue == 23.0
    assert ci.cv_currency == "EUR"
    assert ci.quantity == "1"
    assert ci.acquired_on == "2000-01-01"
    assert ci.acquired_from == "store"
    assert ci.location == "home"

    with pytest.raises(BGGError):
        # raises exception on invalid game data
        c.add_game({"bla": "bla"})


def test_creating_private_out_of_raw_data():
    private_data = {
        "comment": "private comment",
        "paid": 42.0,
        "currency": "USD",
        "currvalue": 23.0,
        "cv_currency": "EUR",
        "quantity": "1",
        "acquired_on": "2000-01-01",
        "acquired_from": "store",
        "location": "home"
    }
    private = BoardGamePrivate(private_data)

    assert private.paid == private_data['paid']
    assert private.currency == private_data['currency']
    assert private.comment == private_data['comment']
    assert private.quantity == private_data['quantity']
    assert private.currvalue == private_data["currvalue"]
    assert private.cv_currency == private_data["cv_currency"]
    assert private.acquired_on == private_data["acquired_on"]
    assert private.acquired_from == private_data["acquired_from"]
    assert private.location == private_data["location"]
