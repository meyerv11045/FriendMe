import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
from twilio.rest import Client
import datetime

def setup_database_conn():
        credentials_key = \
        '''{"type": "service_account",
            "project_id": "friendme-8b0c3",
            "private_key_id": "eea37c37939eebf964e423901ddc0c878c191c99",
            "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDd70SUdzrjfRGA\\nRmmgxWhlXi5nYrhvzn/UQNo6Am2CVuZn0FhAe0ITdOMNxxKDhPKpwO+9T2jaxbuC\\nw/uXhrLR2J51kNOASL+hlN5I6AiKgoBz/LNaUwrvnZlY6yS3/Efb2feRUEYHNdGh\\nEv2LPfOUXdKh2UWz5EL6/XvPBfkMKi+5ASTbsQ0TummeVTc7rTf2ZHE1yJN9r32U\\nHD0BGGAuI31YQQkHMmu5FAr5uzC2gaA/SMZdU7HrZZhs7IXBwNLVik6B2cpTDhIm\\nhKuxkkc9MyDRWrFUviKM/c4doXjp3ti9eIADk5czNcUiTBIwz8x0P7yK9aM2Gxc0\\nqkbdIiXFAgMBAAECggEACj+68IpDB29mqABYb2q+Y/QB+5dFAjDMmW43RbeH/B1s\\nPX4THUMz7XcX5zJ6yeURWcKFr73jjzrTanoHe9tmFafFxZMfGU0CwIEB9Ob2QgM9\\n0F1qoPC10BP8mW0egHqfjOkXdDf7S+jx2djpKY1+Wqssh3njrKeNak7bcVeKxUN1\\ndWJs9gNfQc5n6cGzuFN/t3oEIGi0vNYLE5cZ5yNb0e9T0CMRgEuFf8F1bdprfQb3\\njiWEtYuF+yukzLEti0io5B9dyKrZ/PzvPn1IUyGEMFGANqKTkunN9usnSvyghIHk\\nxGAnkNsZaZroi/r/1/UGkNs9uAMTvOGCO9DLHal1gQKBgQDxYbuYVrqLAdjD0fyi\\n84d3NxRTBoTfgIK4fYfwwjqV6cxyZjzCfa3V/gaVuj8K0vegkqEfRkQmPGvbLAQw\\nzCxl6JEf7LauVp2P0912j7P1m4Wx3UdyzMUNHH05xh/GmEFFBRTJ40Y3iLioDAWX\\nLhfrqjUIcBCwAgFRmGSPZgVTBQKBgQDrYAlAhh5zwnvJkH3XZge4oQ3AV7X3cV9c\\nGwFJpTxcaDErYx5Q/sCdvi+SqFeexFSeLeV0gI/x+VvG89n5e4wJYt1cbOespFl7\\nZKrx75hsdZeQsRnIMiutNd/DZvNLnq5YG0b/15YjK2nF2IYFBEB7l4SV+JHSrwaa\\nfIIISoeDwQKBgQC7X0tZGNHbgAZ9E28SKwqYDyh2vpO8Tyyp+7/fs1X48zEiCJzX\\nuOmNOJBx/85aH6PbgJcUCN5z8+khjEyAeK1qOhsVdhHkyRWsBSFfnHNsj1o71HJW\\n+f9oixnmFBaseZoI8sXNZeAm0bnNsO9SCJTG+iwKrbs2dYgCh9JfwikV5QKBgA8c\\n63spIWttYWVf0bSy6GwCa0+eUiDBNs5DLaH86hNE3WNbyeaJdPSr8YIJLRcUpBpD\\n+Cey2Ys/55Sus6BBPoybvHriwz1ikBxMKm2+ZJsSMdkohe9EyWklvGhfg9+nIKqn\\nlbd3sDwx3WjGrlREIZ/N6sV2YGaWtmXU+MRvhKQBAoGABCP0fsHihg2naHQB5WtT\\nsBRsEWjL/UDNGx8OieCiucMZO6QDNKlaW5G5vGG2/UFsEU7jVQMEPnBH4LQAr08A\\ngPvuJ9scKhEq7DkP/BCuYBjEBWfo13JSTVEJjsvrnir3uAtCyTFHLI2g1cuTt0FX\\n+xcIyGcoTs77mX7u6mO7l2c=\\n-----END PRIVATE KEY-----\\n",
            "client_email": "firebase-adminsdk-r2yc8@friendme-8b0c3.iam.gserviceaccount.com",
            "client_id": "107548936594713464478",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-r2yc8%40friendme-8b0c3.iam.gserviceaccount.com"
        }'''
        creds = json.loads(credentials_key)
        cred = credentials.Certificate(creds)
        firebase_admin.initialize_app(cred)

def add_quote(quotes_data, quote, num):
    quote_dictionary = \
        {'Text':quote,
        'TotalSends':0,
        'TotalSentiment':0,
        'TotalShares':0}
        
    quotes_data.document(str(num)).set(quote_dictionary)

setup_database_conn()
db = firestore.client()
quotes_data = db.collection(u'Quotes')

counter = 0
cur_quotes = []
for i in quotes_data.get():
    cur_quotes.append(i.get('Text'))
    counter += 1

with open('QuotesToAdd.txt') as f:
    lines = f.read().splitlines()

#remove duplicates
lines = list(dict.fromkeys(lines))

new_quotes = l3 = [x for x in lines if x not in cur_quotes]

print('Attempting to add', len(new_quotes), 'quotes.')

for quote in new_quotes:
    add_quote(quotes_data, quote, counter)
    counter += 1

print('Success')