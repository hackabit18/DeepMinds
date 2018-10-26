from uuid import uuid4 as places_autocomplete_session_token
from googlemaps import convert
import requests

PLACES_FIND_FIELDS_BASIC = set([
    "formatted_address", "geometry", "icon", "id", "name",
    "permanently_closed", "photos", "place_id", "plus_code", "scope",
    "types",
])

PLACES_FIND_FIELDS_CONTACT = set(["opening_hours", ])

PLACES_FIND_FIELDS_ATMOSPHERE = set(["price_level", "rating"])

PLACES_FIND_FIELDS = (PLACES_FIND_FIELDS_BASIC ^
                      PLACES_FIND_FIELDS_CONTACT ^
                      PLACES_FIND_FIELDS_ATMOSPHERE)

PLACES_DETAIL_FIELDS_BASIC = set([
    "address_component", "adr_address", "alt_id", "formatted_address",
    "geometry", "icon", "id", "name", "permanently_closed", "photo",
    "place_id", "plus_code", "scope", "type", "url", "utc_offset", "vicinity",
])

PLACES_DETAIL_FIELDS_CONTACT = set([
    "formatted_phone_number", "international_phone_number", "opening_hours",
    "website",
])

PLACES_DETAIL_FIELDS_ATMOSPHERE = set(["price_level", "rating", "review", ])

PLACES_DETAIL_FIELDS = (PLACES_DETAIL_FIELDS_BASIC ^
                        PLACES_DETAIL_FIELDS_CONTACT ^
                        PLACES_DETAIL_FIELDS_ATMOSPHERE)

my_api_key = "AIzaSyB8AANr9xN32HPF3fgoDo2YyQjSCLgA3gU"


def find_place(input, input_type, fields=None, location_bias=None,
               language="English"):
    """
    A Find Place request takes a text input, and returns a place.
    The text input can be any kind of Places data, for example,
    a name, address, or phone number.
    :param input: The text input specifying which place to search for (for
                  example, a name, address, or phone number).
    :type input: string
    :param input_type: The type of input. This can be one of either 'textquery'
                  or 'phonenumber'.
    :type input_type: string
    :param fields: The fields specifying the types of place data to return,
                   separated by a comma. For full details see:
                   https://developers.google.com/places/web-service/search#FindPlaceRequests
    :type input: list
    :param location_bias: Prefer results in a specified area, by specifying
                          either a radius plus lat/lng, or two lat/lng pairs
                          representing the points of a rectangle. See:
                          https://developers.google.com/places/web-service/search#FindPlaceRequests
    :type location_bias: string
    :param language: The language in which to return results.
    :type langauge: string
    :rtype: result dict with the following keys:
            status: status code
            candidates: list of places
    """
    params = {"input": input, "inputtype": input_type}

    if input_type != "textquery" and input_type != "phonenumber":
        raise ValueError("Valid values for the `input_type` param for "
                         "`find_place` are 'textquery' or 'phonenumber', "
                         "the given value is invalid: '%s'" % input_type)

    if fields:
        invalid_fields = set(fields) - PLACES_FIND_FIELDS
        if invalid_fields:
            raise ValueError("Valid values for the `fields` param for "
                             "`find_place` are '%s', these given field(s) "
                             "are invalid: '%s'" % (
                                 "', '".join(PLACES_FIND_FIELDS),
                                 "', '".join(invalid_fields)))
        params["fields"] = convert.join_list(",", fields)

    if location_bias:
        valid = ["ipbias", "point", "circle", "rectangle"]
        if location_bias.split(":")[0] not in valid:
            raise ValueError("location_bias should be prefixed with one of: %s"
                             % valid)
        params["locationbias"] = location_bias
    if language:
        params["language"] = language

    params["key"] = my_api_key
    req = requests.get("https://maps.googleapis.com/maps/api/place/findplacefromtext/json", params)
    return req.json()


def place(place_id, session_token=None, fields=None, language="English"):
    """
    Comprehensive details for an individual place.
    :param place_id: A textual identifier that uniquely identifies a place,
        returned from a Places search.
    :type place_id: string
    :param session_token: A random string which identifies an autocomplete
                          session for billing purposes.
    :type session_token: string
    :param fields: The fields specifying the types of place data to return,
                   separated by a comma. For full details see:
                   https://cloud.google.com/maps-platform/user-guide/product-changes/#places
    :type input: list
    :param language: The language in which to return results.
    :type language: string
    :rtype: result dict with the following keys:
        result: dict containing place details
        html_attributions: set of attributions which must be displayed
    """
    params = {"placeid": place_id}

    if fields:
        invalid_fields = set(fields) - PLACES_DETAIL_FIELDS
        if invalid_fields:
            raise ValueError("Valid values for the `fields` param for "
                             "`place` are '%s', these given field(s) "
                             "are invalid: '%s'" % (
                                 "', '".join(PLACES_DETAIL_FIELDS),
                                 "', '".join(invalid_fields)))
        params["fields"] = convert.join_list(",", fields)

    if language:
        params["language"] = language
    if session_token:
        params["sessiontoken"] = session_token
    params["key"] = my_api_key
    ret = requests.get("https://maps.googleapis.com/maps/api/place/details/json", params)
    return ret.json()


def getReply(query):
    # query = "nearest eye doctor available"
    # output = find_place("hospital", "textquery", None, "point:23.420386, 85.434566")
    output = find_place(query, "textquery", None, "ipbias")
    # print(output)
    # print(output['candidates'])
    result = place(output['candidates'][0]['place_id'])

    return result, result['result']['name'], result['result']['formatted_address'], result['result']['formatted_phone_number']

    # print(result)
    # print(result['result']['name'])
    # print(result['result']['formatted_address'])
    # print(result['result']['formatted_phone_number'])
