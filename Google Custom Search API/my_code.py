

"""Simple command-line example for Custom Search.
Command-line application that does a search.
"""


import pprint

from googleapiclient.discovery import build


service = build("customsearch", "v1",
            developerKey="AIzaSyDPg23pWoQC6bzMh0g5P37XUKyPdih_jXI")

res = service.cse().list(    # pylint: disable=no-member
      q='lectures',
      cx='017576662512468239146:omuauf_lfve',
    ).execute()
pprint.pprint(res)

