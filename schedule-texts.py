from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
import datetime
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random
import numpy as np
from lightfm import LightFM
import pickle
import scipy
from scipy.sparse import csr_matrix

# import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:/Users/noskc/Desktop/FriendMe Cloud Owner Credential.json"

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

setup_database_conn()

class MessageScheduler():
    def __init__(self):
        
        # Create a client.
        self.client = tasks_v2.CloudTasksClient()

        self.project = 'friendme-8b0c3'
        self.queue = 'message-send-queue'
        self.location = 'us-central1'
        self.url = 'https://us-central1-friendme-8b0c3.cloudfunctions.net/send-text-unauthenticated'
        
        #audience = 'https://us-central1-friendme-8b0c3.cloudfunctions.net/send-text'
        #service_account_email = 'jackson-s-computer@friendme-8b0c3.iam.gserviceaccount.com'
        
        # Construct the fully qualified queue name.
        self.parent = self.client.queue_path(self.project, self.location, self.queue)
        
    def send_message_payload(self, task_name, phone_number, quote_id, send_time_seconds):
        assert isinstance(phone_number, str)
        assert isinstance(quote_id, int)
        
        payload = {'PhoneNumber': phone_number, 'QuoteId': quote_id}
        
        # Construct the request body.
        task = {
            "http_request": {  # Specify the type of request.
                "http_method": tasks_v2.HttpMethod.POST,
                "url": self.url,  # The full url path that the task will be sent to.
                #"oidc_token": {"service_account_email": service_account_email, "audience": audience},
            }
        }
        
        # Convert dict to JSON string
        payload = json.dumps(payload)
        # specify http content-type to application/json
        task["http_request"]["headers"] = {"Content-type": "application/json"}
        # The API expects a payload of type bytes.
        converted_payload = payload.encode()
        # Add the payload to the request.
        task["http_request"]["body"] = converted_payload


        # Convert "seconds from now" into an rfc3339 datetime string.
        d = datetime.datetime.utcnow() + datetime.timedelta(seconds=send_time_seconds)
        # Create Timestamp protobuf.
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(d)
        # Add the timestamp to the tasks.
        task["schedule_time"] = timestamp

        # Add name to the task
        task["name"] = self.client.task_path(self.project, self.location, self.queue, task_name)

        # Use the client to build and send the task.
        response = self.client.create_task(request={"parent": self.parent, "task": task})

    #both are strings
    def schedule_message(self, task_name, phone_number, quote_id, send_time_seconds):
        assert isinstance(phone_number, str)
        assert isinstance(quote_id, int)
        
        self.send_message_payload(task_name, phone_number, quote_id, send_time_seconds)
        
        # set a very low sentiment to prevent double recommendation before a text is sent
        default_sentiment = 0.001
        db = firestore.client()
        quote_dictionary = db.collection(u'Quotes').document(str(quote_id)).get().to_dict()
        quote_dictionary['TotalSentiment'] += default_sentiment
        db.collection(u'Quotes').document(str(quote_id)).set(quote_dictionary)
        
        
        # set the initial recommender score to prevent double recommednation (in case there is never a response)
        user_dict = db.collection(u'BasicUserData').document(phone_number).get().to_dict()
        recommender_dictionary = db.collection(u'RecommenderScores').document(str(user_dict['UserId'])).get().to_dict()
        recommender_dictionary[str(quote_id)] = default_sentiment
        db.collection(u'RecommenderScores').document(str(user_dict['UserId'])).set(recommender_dictionary)
                      
class Recommender():
    def __init__(self, *args):
        if len(args) == 1:
            file_name = args[0]
            self.load(file_name)
        
            self.load_matrix_from_db()
        elif len(args) == 0:
            self.load_matrix_from_db()

            model_factors = round(((self.num_items + self.num_users) / 2) ** 0.85)
            self.model = LightFM(loss='logistic', no_components = model_factors)
        else:
            raise ValueError('Wrong number of parameters to create a Recommender')

    def load_matrix_from_db(self):
        db = firestore.client()
        recommender_scores = db.collection(u'RecommenderScores')

        metadata = recommender_scores.document('metadata').get().to_dict()
        self.num_users = metadata['NumUsers']
        self.num_items = metadata['NumQuotes']
        
        self.matrix = csr_matrix((self.num_users, self.num_items), dtype=np.float32)
        lil_matrix = self.matrix.tolil()
        
        for i in range(self.num_users):
            scores_dictionary = recommender_scores.document(str(i)).get().to_dict()
            for j in scores_dictionary.keys():
                lil_matrix[int(i), int(j)] = scores_dictionary[j]
        
        self.matrix = lil_matrix.tocsr()
        
    def change_model_factors(self, new_factors):
        self.model = LightFM(loss='logistic', no_components = new_factors)

    def add_new_item(self, num=1):
        self.matrix._shape = (self.num_users, self.num_items + num)
        self.matrix.indptr = np.hstack((self.matrix.indptr, self.matrix.indptr[-1]))

        self.num_items += num

    def add_new_user(self, num = 1):
        self.matrix._shape = (self.num_users + num,self.num_items)
        self.matrix.indptr = np.hstack((self.matrix.indptr, self.matrix.indptr[-1]))
        
        self.num_users += num

    def fit(self, num_times = 1):
        self.model.fit_partial(self.matrix, epochs = num_times, verbose=False)

    def reset_fit(self, num_times = 1):
        self.model.fit(self.matrix, epochs = num_times, verbose=False)

    def recommend(self, user_id, number_output):
        if user_id >= self.num_users:
            return None

        item_ids_with_rating = np.matrix(scipy.sparse.find(self.matrix[user_id, :])[1])
        user_items_test = np.setdiff1d(np.arange(0,self.num_items),item_ids_with_rating)
        
        if len(user_items_test) == 0:
            return None
        
        recommendations = np.array(self.model.predict(user_id, user_items_test))
        recommendations = np.column_stack((user_items_test,recommendations))
        
        sorted_recommendations = recommendations[np.flip(recommendations[:,1].argsort())]
        
        return sorted_recommendations[:number_output,:]
    
    def save(self, file_name):
        with open(file_name + '.pickle', 'wb') as f:
            pickle.dump((self.num_users, self.num_items, self.model), f, protocol=pickle.HIGHEST_PROTOCOL)
            
    def load(self, file_name):
        with open(file_name + '.pickle', 'rb') as f:
            (self.num_users, self.num_items, self.model) = pickle.load(f)

    def print_matrix(self):
        print(self.matrix.toarray())
    
    def edit_matrix(self, user_list, item_list, score_list):
        assert(len(user_list) == len(item_list) and len(item_list) == len(score_list))

        lil_matrix = self.matrix.tolil()
        
        for i in range(len(user_list)):
            assert(item_list[i] < self.num_items and user_list[i] < self.num_users)
            
            lil_matrix[user_list[i], item_list[i]] = score_list[i]
           
            
        self.matrix = lil_matrix.tocsr()

def callback(request):
    db = firestore.client()
    
    recommender = Recommender()
    recommender.fit(20)
    
    scheduler = MessageScheduler()
    
    # change the last quote field
    user_data = db.collection(u'BasicUserData').get()
    for user in user_data:
        user_dict = user.to_dict()
        if user_dict['IsActive']:
            quotes = recommender.recommend(user_dict['UserId'], 1)
        
            if len(quotes != 0):
                quote = quotes[0]
            else:
                return
                
            quote_index = int(quote[0])
                
            task_name = '2_text_user_' + str(user_dict['UserId']) + '_quote_' + str(quote_index)
        
            scheduler.schedule_message(task_name, user_dict['Number'], quote_index, random.randint(1, 43200))
            
    return 'Success'
            
# print(callback(None))