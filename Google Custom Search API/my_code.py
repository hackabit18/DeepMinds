

# """Simple command-line example for Custom Search.
# Command-line application that does a search.
# """


# import pprint

from googleapiclient.discovery import build

# query - take output of DialogFlow
query = 'Medicines for Typhoid'
service = build("customsearch", "v1",
            developerKey="AIzaSyDPg23pWoQC6bzMh0g5P37XUKyPdih_jXI")

res = service.cse().list(    # pylint: disable=no-member
      q= query,
      cx='001132580745589424302:jbscnf14_dw',
    ).execute()
# pprint.pprint(res)
# print(len(res.items()))
# print(len(res['items']))
print('The top results from web are: ')
no_of_results = 3
for i in range(0,no_of_results):
    print(res['items'][i]['link'])