# coding: utf-8

import glob
import io
import logging
import os
import pytest
import re
import sys
import xml.etree.ElementTree as ET

from boardgamegeek import BGGClient, BGGClientLegacy, CacheBackendNone


# Kinda hard to test without having a "test" user
TEST_VALID_USER = "fagentu007"
TEST_VALID_USER_ID = 818216
TEST_USER_WITH_LOTS_OF_FRIENDS = "Solamar"        # user chosen randomly (..after a long search :)) ), just needed
                                                  # someone with lots of friends :D
TEST_INVALID_USER = "someOneThatHopefullyWontExistPlsGuysDontCreateThisUser"
TEST_INVALID_GAME_NAME = "blablablathisgamewonteverexist"
TEST_GAME_NAME = "Agricola"
TEST_GAME_ID = 31260

#TEST_GAME_NAME_2 = "Merchant of Venus (second edition)"
#TEST_GAME_ID_2 = 131646

TEST_GAME_NAME_2 = "Advanced Third Reich"
TEST_GAME_ID_2 = 283

TEST_GUILD_ID = 1229
TEST_GUILD_ID_2 = 930

TEST_GAME_WITH_IMPLEMENTATIONS_ID = 28720 # Brass

TEST_GAME_EXPANSION_ID = 223555 # Scythe: The Wind Gambit

TEST_GAME_ACCESSORY_ID = 104163 # Descent: Journeys in the Dark (second edition) – Conversion Kit

TEST_GEEKLIST_ID = 1
TEST_GEEKLIST_INVALID_ID = -1

if sys.version_info >= (3,):
    STR_TYPES_OR_NONE = [str, type(None)]
else:
    STR_TYPES_OR_NONE = [str, unicode, type(None)]

# The top level directory for our XML files
XML_PATH = os.path.join(os.path.dirname(__file__), "xml")
STATUS_PATH = os.path.join(os.path.dirname(__file__), "status")


@pytest.fixture
def xml():
    xml_code = """
    <root>
        <node1 attr="hello1" int_attr="1">text</node1>
        <node2 attr="hello2" int_attr="2" />
        <list>
            <li attr="elem1" int_attr="1" />
            <li attr="elem2" int_attr="2" />
            <li attr="elem3" int_attr="3" />
            <li attr="elem4" int_attr="4" />
        </list>
    </root>
    """
    return ET.fromstring(xml_code)


def glob_xml_name(filepath, allow_any=False):
    """
    Get the name (or raise an exception) of an XML sample in ``XML_PATH`` matching a glob pattern.
    :param str filepath: glob pattern to use for search
    :param bool allow_any: If multiple files match the pattern, controls whether an exception is thrown (if ``False``) or one of the multiple files is picked & used (if ``True``).
    :retval str: the pathname of a matching file
    :raises FileNotFoundError: if no file matches the given pattern
    :raises FileExistsError: if multiple files match the given pattern and ``allowAny`` is ``False``
    ::
    """
    filenames = glob.glob(os.path.join(XML_PATH, os.path.basename(filepath)))
    if 1 == len(filenames) or (filenames and allow_any):
        return filenames[0]
    elif filenames:
        raise FileExistsError(f"Found multiple XML samples matching '{filepath}'")
    else:
        raise FileNotFoundError(f"No XML samples matching: '{filepath}'")


def glob_xml_contents(filepath, allow_any=False):
    """
    Get the content (or raise an exception) of an XML sample in ``XML_PATH`` matching a glob pattern.
    :param str filepath: glob pattern to use for search
    :param bool allow_any: If multiple files match the pattern, controls whether an exception is thrown (if ``False``) or one of the multiple files is picked & used (if ``True``).
    :retval str: the contents of a matching file
    :raises FileNotFoundError: if no file matches the given pattern
    :raises FileExistsError: if multiple files match the given pattern and ``allowAny`` is ``False``
    ::
    """
    filename = glob_xml_name(filepath, allow_any=allow_any)
    with open(filename) as xml_file:
        xml = xml_file.read()
    return xml


def open_and_parse_xml(which_xml, params=None, allow_any=False):
    """
    Get an XML sample and return the parsed result.
    :param str which_xml: partial URL endpoint or glob pattern for the XML sample
    :param dict params: query parameters (only if which_xml is an endpoint)
    :param bool allow_any: If multiple files match the pattern, controls whether an exception is thrown (if ``False``) or one of the multiple files is picked & used (if ``True``).
    :retval xml.etree.ElementTree.Element: the contents of a matching file, parsed as XML
    :raises FileNotFoundError: if no file matches the given pattern
    :raises FileExistsError: if multiple files match the given pattern and ``allowAny`` is ``False``
    """
    if params is not None:
        response = simulate_bgg("/" + which_xml, params, timeout=-1)
        xml = response.text
    else:
        xml = glob_xml_contents(which_xml, allow_any=allow_any)

    if sys.version_info >= (3,):
        return ET.fromstring(xml)
    else:
        return ET.fromstring(xml.encode("utf-8"))


@pytest.fixture
def xml_collection_minimal():
    return open_and_parse_xml("collection@*&which=minimal")


@pytest.fixture
def xml_collection_brief():
    return open_and_parse_xml("collection@*&which=brief")


@pytest.fixture
def xml_collection_error():
    return open_and_parse_xml("collection", {"username": TEST_INVALID_USER, "subtype": "boardgame", "stats": 1})


@pytest.fixture
def xml_collection_full():
    return open_and_parse_xml("collection@*&which=full")


@pytest.fixture
def xml_collection_without_stats():
    return open_and_parse_xml("collection@*&which=nostats", allow_any=True)


@pytest.fixture
def bgg():
    return BGGClient(cache=CacheBackendNone(), retries=2, retry_delay=1)


@pytest.fixture
def legacy_bgg():
    return BGGClientLegacy(cache=CacheBackendNone(), retries=2, retry_delay=1)


@pytest.fixture
def null_logger():
    # create logger
    logger = logging.getLogger("null")
    logger.setLevel(logging.ERROR)
    return logger


class MockResponse:
    """
    A simple object which contains all the fields we need from a response

    :param str text: the text to be returned with the response
    """
    def __init__(self, text, status_code=200):
        self.headers = {"content-type": "text/xml"}
        self.status_code = status_code
        self.text = text


def simulate_bgg(url, params, timeout):
    last_slash = url.rindex('/')
    fragment = url[last_slash + 1:]

    sorted_params = sorted(params.items(), key=lambda t: t[0])
    query_string = '&'.join([str(k) + "=" + str(v) for k, v in sorted_params])

    filename = os.path.join(XML_PATH, fragment + "@" + query_string)

    with io.open(filename, "r", encoding="utf-8") as xmlfile:
        response_text = xmlfile.read()

    return MockResponse(response_text)


def simulate_legacy_bgg(url, params, timeout):
    fragment = re.search(r"(?:/)([^/]*/[^/]*)$", url).group(1).replace('/', '%25')

    if len(params)>0:
        sorted_params = sorted(params.items(), key=lambda t: t[0])
        query_string = '&'.join([str(k) + "=" + str(v) for k, v in sorted_params])
        fragment = fragment + "@" + query_string

    xml_filename = os.path.join(XML_PATH, fragment)
    with io.open(xml_filename, "r", encoding="utf-8") as xmlfile:
        response_text = xmlfile.read()

    status_filename = os.path.join(STATUS_PATH, fragment)
    if os.path.isfile(status_filename):
        with io.open(status_filename, "r", encoding="utf-8") as statusfile:
            response_status = int(statusfile.read())
    else:
        response_status = 200

    return MockResponse(response_text, response_status)
