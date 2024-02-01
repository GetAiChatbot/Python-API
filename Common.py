from xml.etree import ElementTree as ET
import sqlite3
import json
import requests

from datetime import datetime


def parse_contacts(response_text):
  root = ET.fromstring(response_text)
  contacts_data = []

  get_contacts_return_elements = root.findall(".//getContactsByTypeReturn")
  get_contacts_return_dicts = [
      element_to_dict(element) for element in get_contacts_return_elements
  ]
  json_data = json.dumps(get_contacts_return_dicts, indent=2)

  # phone_number = choose_phone_number(contact_data)

  loaded = json.loads(json_data)

  num = 0
  for d in loaded:
    # print(num)
    if num == 0:
      c = d["getContactsByTypeReturn"]
    else:
      c = d

    if c["homePhone"] is not None:
      homePhone = c["homePhone"].replace("(", "").replace(")", "").replace(
          "-", "").replace(" ", "")
    else:
      homePhone = ""

    if c["mobilePhone"] is not None:
      mobilePhone = c["mobilePhone"].replace("(", "").replace(")", "").replace(
          "-", "").replace(" ", "")
    else:

      print(mobilePhone)
    if c["workPhone"] is not None:
      workPhone = c["workPhone"].replace("(", "").replace(")", "").replace(
          "-", "").replace(" ", "")
    else:
      workPhone = ""

    contact_data = {
        "ID": c["ID"],
        "homePhone": homePhone,
        "mobilePhone": mobilePhone,
        "workPhone": workPhone,
        "address": c["address"],
        "ContactType": c["contactType"],
        "completeName": c["completeName"],
        "Email": c["email"],
        "NamedOnLease": c["namedOnLease"]
    }
    contacts_data.append(contact_data)
    num += 1

  return contacts_data


def element_to_dict(element):
  result = {}
  for child in element:
    if child.tag.endswith("}arrayType"):
      result[child.tag] = [element_to_dict(item) for item in child]
    else:
      result[child.tag] = element_to_dict(
          child) if len(child) > 0 else child.text
  return result


def save_contacts_to_database(contacts_data):
  try:
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS contacts_latest;")

    cursor.execute('''CREATE TABLE IF NOT EXISTS contacts_latest (
                              ID TEXT,
                              homePhone TEXT,
                              mobilePhone TEXT,
                              workPhone TEXT,
                              Address TEXT,
                              ContactType TEXT,
                              CompleteName TEXT,
                              Email TEXT,
                              NamedOnLease TEXT
                         )''')

    for contact_data in contacts_data:
      cursor.execute(
          '''INSERT INTO contacts_latest (ID, homePhone, mobilePhone,     workPhone, Address, ContactType, CompleteName, Email, NamedOnLease)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
          (contact_data['ID'], contact_data['homePhone'],
           contact_data['mobilePhone'], contact_data['workPhone'],
           contact_data['address'], contact_data['ContactType'],
           contact_data['completeName'], contact_data['Email'],
           contact_data['NamedOnLease']))

    conn.commit()
  except sqlite3.Error as e:
    print("Error saving contacts to database:", e)
  finally:
    conn.close()


def get_contacts_from_database(phone):
  try:
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()

    query = f"select * from contacts_latest where homePhone = '{phone}' or workphone = '{phone}' or mobilephone = '{phone}';"

    cursor.execute(query)

    # Fetch all results
    results = cursor.fetchall()

    column_names = [description[0] for description in cursor.description]

    # Print or process the results
    result_with_column_names = [
        dict(zip(column_names, row)) for row in results
    ]

    # Print or process the result
    # for row in result_with_column_names:
    #   print(row)

    return result_with_column_names
  except sqlite3.Error as e:
    print("Error saving contacts to database:", e)
  finally:
    cursor.close()
    conn.close()
