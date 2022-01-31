# Picks date, time from user
# processes the picked data
# sends the data to server
import requests

def requester(date, draft_id):

    data = {
            "date":date,
            "draft_id":draft_id
        }

    boomerang_endpoint = "127.0.0.1:5000/schedulePrint"

    requests.post(url=boomerang_endpoint, data = data)



