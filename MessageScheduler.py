from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
import datetime
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:/Users/noskc/Desktop/FriendMe Cloud Owner Credential.json"

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
        
        
message_scheduler = MessageScheduler()

message_scheduler.schedule_message('send_text_11', '+12623891501', 0, 10)