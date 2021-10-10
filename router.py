from twilio.twiml.messaging_response import MessagingResponse
import sqlalchemy
from db_conn import DbConn

def router(request):
    user = request.form['From']
    body = request.form['Body']
    conn = DbConn()

    result = conn.query(f'SELECT SetupStatus from [UserInfo] where Phone = {user}')
    if len(result) == 1:
        # check if setup in progress
        if result['SetupStatus'] == 1:
            stmt = sqlalchemy.text('insert into {} ({}) values ({})'.format('UserInfo', 'Phone, SetupStatus, Active', f'{user}, 1, true'))
            conn.query

            resp = MessagingResponse()
            resp.message(f"Thanks! We will send with 5 starter texts right now to gauge your preferences!")    

            return str(resp)
        else:
            # if not in progress, proceed to store the sentiment
            store_sentiment(body)

    else:
        # Start setup of new user
        setup_user()
        stmt = sqlalchemy.text('insert into {} ({}) values ({})'.format('UserInfo', 'Phone, SetupStatus, Active', f'{user}, 1, true'))
        conn.query(stmt)

def setup_user():
    resp = MessagingResponse()
    resp.message(f"Welcome to FriendMe! Please respond with the number of personalized texts you want per day!")    
    return str(resp) 

def store_sentiment(body):
    sentiment = get_sentiment(body)
    # TODO: need to update the csr matrix directly with the sentimenet s
    pass

def get_sentiment(text):
    # TODO: use the dictionary jackson created to score the sentimenet of emojis
    pass