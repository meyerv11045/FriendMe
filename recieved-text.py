import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from twilio.rest import Client
import numpy as np
import scipy
from scipy.sparse import csr_matrix
from lightfm import LightFM
import pickle
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
import datetime
import json

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

class User():
    def __init__(self, phone_number_from):
        self.phone_number = phone_number_from

        self.setup_steps = 5

        #grab our database
        self.db = firestore.client()
        self.user_data = self.db.collection(u'BasicUserData')
        self.my_user_data = self.user_data.document(self.phone_number).get()
        if self.my_user_data.exists:
            self.my_user_dictionary = self.my_user_data.to_dict()
        else:
            self.my_user_dictionary = None

        self.client = self.setup_twilio()
    
    def user_exists(self):
        return self.my_user_data.exists

    def user_active(self):
        return self.user_exists() and self.my_user_dictionary['IsActive']
    
    def deactivate(self):
        self.send_text('Sorry to see you go! If you ever want to reactivate your account just type "activate", and we will pick up right where we left off!', self.phone_number)
            
        self.my_user_dictionary['IsActive'] = False
        self.user_data.document(self.phone_number).set(self.my_user_dictionary)
        
    def activate(self):
        if self.user_setup_counter() < self.setup_steps:
            self.send_text('Welcome back! We love to see you again. Your setup was never completed, so we are going to continue the setup process. Remember to respond to the texts with emojis about how they make you feel!', self.phone_number)
        else:
            self.send_text('Welcome back! We love to see you again. Your preferences are back to the way they were. If you want to change your preferences type "preferences" and if you want to stop recieving texts type "stop".', self.phone_number)
        self.my_user_dictionary['IsActive'] = True
        self.user_data.document(self.phone_number).set(self.my_user_dictionary)
        
    def user_setup_counter(self):
        return self.my_user_dictionary['SetupCounter']

    def setup_twilio(self):
        account_sid = 'AC9b1fa6115543cf93d59f43ed2eab91fd'
        auth_token = '3f672fdc267d6f64d9ca4341c7188ad2'
        return Client(account_sid, auth_token)

    def send_text(self, myBody, myTo):
        myFrom = '3093883278'
        self.client.messages.create(body=myBody, from_=myFrom, to=myTo)

    def new_user(self):
        self.create_user_db()
        
        self.send_text('Hello! We are FriendMe, a texting service to bring a sprinkle of joy to your life. Every day, we will be sending you messages to make you happier. You can respond to messages with face emojis to keep track of your happiness. At the end of the week, we will report your happiness and progress towards a happier life!. For example, we will send something like:', self.phone_number)
        self.send_text('For example, we will send something like:\n"With the new day comes new strength and new thoughts."\nTo which you could respond:', self.phone_number)
        self.send_text(u"\U0001F604\U0001F917", self.phone_number)
        self.send_text('To get your baseline, we are going to send you 5 different messages. Respond to each with face emojis about how you feel!', self.phone_number)
        
    def create_user_db(self):
        #get recommender dictionary
        recommender_metadata_dict = self.db.collection(u'RecommenderScores').document('metadata').get().to_dict()
        #create new spot in recommender for new user
        self.my_user_dictionary = \
        {'IsActive':False,
        'SetupCounter':0,
        'WhenActivated':datetime.datetime.now(),
        'WhenDeactivated':datetime.datetime.min,
        'Premium':False,
        'Number':self.phone_number,
        'UserId':recommender_metadata_dict['NumUsers'],
        'LastQuote':-1,
        'LastQuoteScored':False,
        'LastQuoteSendTime':datetime.datetime.min}
        self.db.collection(u'RecommenderScores').document(str(recommender_metadata_dict['NumUsers'])).set({})
        #add one to number of users and reset
        recommender_metadata_dict['NumUsers'] += 1
        self.db.collection(u'RecommenderScores').document('metadata').set(recommender_metadata_dict)
        
        self.user_data.document(self.phone_number).set(self.my_user_dictionary)
    
    def setup_preferences(self, message_score):
        self.add_message_score(message_score)
        
        self.my_user_dictionary['SetupCounter'] += 1
        self.user_data.document(self.phone_number).set(self.my_user_dictionary)

    def add_message_score(self, message_score):
        last_quote_index = self.my_user_dictionary['LastQuote']
        last_quote_scored = self.my_user_dictionary['LastQuoteScored']
        
        if not last_quote_scored and last_quote_index != -1:
            # add to a quotes total sentiment
            quote_dictionary = self.db.collection(u'Quotes').document(str(last_quote_index)).get().to_dict()
            quote_dictionary['TotalSentiment'] += message_score
            self.db.collection(u'Quotes').document(str(last_quote_index)).set(quote_dictionary)
            
            # add to the recommender scores dictionary for the user
            recommender_dictionary = self.db.collection(u'RecommenderScores').document(str(self.my_user_dictionary['UserId'])).get().to_dict()
            recommender_dictionary[str(last_quote_index)] = message_score
            self.db.collection(u'RecommenderScores').document(str(self.my_user_dictionary['UserId'])).set(recommender_dictionary)

            self.my_user_dictionary['LastQuoteScored'] = True
            self.user_data.document(self.phone_number).set(self.my_user_dictionary)

    def finish_setup(self):
        self.my_user_dictionary['IsActive'] = True
        self.user_data.document(self.phone_number).set(self.my_user_dictionary)
        
        self.send_text('Setup complete! You will recieve your first text sometime soon. Additionally, our application allows for sharing your most recent text to another, spreading the love! This can be done by texting "share (phone number)" without the parentheses.', self.phone_number)
        self.send_text('You can track your own happiness meter or your sharing happiness meter by texting "meters" at any time. We will send your meters at the end of each week.', self.phone_number)
        self.send_text('Finally, consider getting premium for $0.99 a month to unlock features such as:\nFeature1\nFeature2\nFeature3\n\nTo deactivate your device at anytime, text "stop".', self.phone_number)
        
        
    def send_recommended_quote(self, seconds):
        recommender = Recommender()
        recommender.fit(10)
        
        quotes = recommender.recommend(self.my_user_dictionary['UserId'], 1)
        
        if len(quotes != 0):
            quote = quotes[0]
        else:
            return
        
        quote_index = int(quote[0])
        
        scheudler = MessageScheduler()
        task_name = '2_text_user_' + str(self.my_user_dictionary['UserId']) + '_quote_' + str(quote_index)
        
        scheudler.schedule_message(task_name, self.phone_number, quote_index, seconds)

    def share(self, sharing_user):
        if not sharing_user.user_exists() or sharing_user.user_active():
            scheudler = MessageScheduler()
            
            quote_index = self.my_user_dictionary['LastQuote']
            quote_dictionary = self.db.collection(u'Quotes').document(str(quote_index)).get().to_dict()
            quote_dictionary['TotalShares'] += 1
            self.db.collection(u'Quotes').document(str(quote_index)).set(quote_dictionary)
            
            
            if not sharing_user.user_exists():
                #TODO shorten
                sharing_user.send_text('Hello! We are FriendMe, a free texting service to bring a sprinkle of joy to your life.', sharing_user.phone_number)
                sharing_user.send_text('You are not currently a user, but another user shared a message with you! If you want to activate your own phone number for free, respond to this with "activate". You can cancel at anytime by texting "stop".', sharing_user.phone_number)
                task_name = '2_share_to_user_phonenum_' + str(sharing_user.phone_number[1:]) + '_from_user_' + str(self.my_user_dictionary['UserId']) + '_quote_' + str(quote_index) + '_total_shares_' + str(quote_dictionary['TotalShares'])
                scheudler.send_message_payload(task_name, sharing_user.phone_number, quote_index, 1)
            else:
                task_name = '2_share_to_user_' + str(sharing_user.my_user_dictionary['UserId']) + '_from_user_' + str(self.my_user_dictionary['UserId']) + '_quote_' + str(quote_index) + '_total_shares_' + str(quote_dictionary['TotalShares'])
                scheudler.schedule_message(task_name, sharing_user.phone_number, quote_index, 1)
                
            self.send_text('Shared message sent!', self.phone_number)
        else:
            self.send_text('The user you tried to share with has deactivated from FriendMe. No message was shared.', self.phone_number)
        
    def get_(self):
        
        
        
emoji_scores = {
    '😀' : 0.1,
    '😃' : 0.3,
    '😄' : 0.7,
    '😁' : 0.75,
    '😆' : 0.6,
    '😅' : 0.05,
    '😂' : 0.68,
    '🤣' : 0.72,
    '🥲' : -0.6,
    '☺️' : 0.56,
    '😊' : 0.6,
    '😇' : 0.45,
    '🙂' : 0.37,
    '🙃' : 0.15,
    '😉' : 0.17,
    '😌' : 0.56,
    '😍' : 0.85,
    '🥰' : 0.93,
    '😘' : 0.55,
    '😗' : 0.3,
    '😙' : 0.36,
    '😚' : 0.42,
    '😋' : 0.05,
    '😛' : -0.1,
    '😝' : -0.3,
    '😜' : -0.01,
    '🤪' : -0.03,
    '🤨' : -0.45,
    '🧐' : 0.03,
    '🤓' : 0.02,
    '😎' : 0.54,
    '🥸' : -0.05,
    '🤩' : 0.89,
    '🥳' : 0.87,
    '😏' : 0.23,
    '😒' : -0.46,
    '😞' : -0.6,
    '😔' : -0.65,
    '😟' : -0.35,
    '😕' : -0.33,
    '🙁' : -0.63,
    '☹️' : -0.76,
    '😣' : -0.58,
    '😖' : -.46,
    '😫' : 0.15,
    '😩' : 0.35,
    '🥺' : 0.7,
    '😢' : -0.87,
    '😭' : -0.98,
    '😤' : 0.03,
    '😠' : -0.2,
    '😡' : -0.5,
    '🤬' : -0.95,
    '🤯' : 0.6,
    '😳' : -0.15,
    '🥵' : 0.1,
    '🥶' : -0.1,
    '😶‍🌫️' : -0.05,
    '😱' : -0.76,
    '😨' : -0.48,
    '😰' : -0.8,
    '😥' : -0.87,
    '😓' : -0.63,
    '🤗' : 0.98,
    '🤔' : -0.15,
    '🤭' : -0.2,
    '🤫' : 0.01,
    '🤥' : -0.07,
    '😶' : -0.01,
    '😐' : -0.09,
    '😑' : -0.13,
    '😬' : -0.17,
    '🙄' : 0.03,
    '😯' : -0.02,
    '😦' : -0.09,
    '😧' : -0.14,
    '😮' : -0.06,
    '😲' : 0.01,
    '🥱' : -0.43,
    '😴' : -0.56,
    '🤤' : 0.86,
    '😪' : -0.13,
    '😮‍💨' : 0.2,
    '😵' : -0.7,
    '😵‍💫' : -0.57,
    '🤐' : -0.26,
    '🥴' : -0.54,
    '🤢' : -0.76,
    '🤮' : -0.88,
    '🤧' : -0.1,
    '😷' : -0.05,
    '🤒' : -0.1,
    '🤕' : -0.4,
    '🤑' : 0.5,
    '🤠' : 0.4
}

def callback(request):
    phone_number = request.form['From']
    body = request.form['Body']
    # phone_number = '+4143398750'
    # body = 'activate'
    my_user = User(phone_number)
    
    #the if elif block to controll all the commands of the application
    if not my_user.user_exists():
        my_user.new_user()
        my_user.send_recommended_quote(1)
        
        # Creates a new user
        
        return 'User creation and successful'
    elif body.lower() == 'stop':
        #stop command
        if my_user.user_exists and not my_user.user_active:
            my_user.deactivate()
        
        return 'User deactivated and successful'
    elif body.lower() == 'activate':
        #activate command
        if my_user.user_exists and my_user.user_active:
            my_user.activate()
            
        if my_user.user_setup_counter() < my_user.setup_steps:
            my_user.send_recommended_quote(1)
        
        return 'User activated and successful'
    elif body.split(' ')[0].lower() == 'share':
        #share command
        if len(body.split(' ')) > 2:
            my_user.send_text('Could not interpret. Please use the format: "share (phone number)".', my_user.phone_number)
            
        sharing_number = body.split(' ')[1]
        sharing_number.replace('-', '')
        
        if len(sharing_number) == 10:
            sharing_number = '1' + sharing_number
        sharing_number = '+' + sharing_number
        
        sharing_user = User(sharing_number)
        
        my_user.share(sharing_user)
        
        return 'User share and successful'
    
    #TODO some preferences command
    else:
        #the message was meant for scoring
        
        #attempt to score
        score = 0
        for i in body:
            score += emoji_scores.get(i, 0)
        
        #if score is 0 then the scoring message was not valid
        if score == 0:
            my_user.send_text('The message could not be interpretted. Please remember to include only face emojis for your responses, or the share, stop, or activate commands.', my_user.phone_number)
            return 'Score could not be interpretted, exited successfully'
        elif my_user.user_active():
            #normal user scoring case
            my_user.add_message_score(score)
        
        elif my_user.user_setup_counter() < my_user.setup_steps:
            #user scoring during setup phase
            my_user.setup_preferences(score)
            if my_user.user_setup_counter() == my_user.setup_steps:
                my_user.finish_setup()
                my_user.send_recommended_quote(900)
            else:
                my_user.send_recommended_quote(1)
        else:
            return 'User deactivated, no action taken.'
    
    return 'Should never see this. Some logic flow prevented successful completion of a command or action.'


# print(callback(None))
# def read_file_blob(bucket_name, destination_blob_name):
#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(destination_blob_name)
 
#     # read as string
#     read_output = blob.download_as_string()
 
#     return read_output