import requests
import Common as c
import Variables as v
from datetime import datetime

from flask import Flask, request

app = Flask(__name__)


@app.route('/getContact')
def getContact():
  # Get the phone number from the query parameters
  phone = request.args.get('phone')
  # print(phone)

  # phone1 = phone.replace("+1", "")
  # print(phone1)

  current_time = datetime.now()
  contacts = []
  print(current_time.hour)

  contacts = c.get_contacts_from_database(phone)
  print(phone)
  count = len(contacts)
  
  if contacts:
    return {
        "status": "success",
        "message": "Contact Found",
        "contacts": contacts,
        "contacts available": count,

    }
  else:
    return {"status": "error", "message": "No Contact Found"}


@app.route('/refresh_data')
def refresh_data():
  r_text = ''
  r_status = 200

  with requests.Session() as s:
    try:
      r = s.post(v.url, headers=v.headers, data=v.payload, timeout=v.Timeout_)
      r_text = r.text
      r_status = r.status_code
      #print(r.text)
    except requests.exceptions.Timeout as e:
      print(e)

  response = r_text  #requests.post(url, headers=headers, timeout=(3.05, 27))

  if r_status == 200:
    contacts_data = c.parse_contacts(response)
    c.save_contacts_to_database(contacts_data)
    return {"status": "success", "message": "Data refreshed successfully."}
  else:
    return {"status": "error", "message": "Error refreshing data."}


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
