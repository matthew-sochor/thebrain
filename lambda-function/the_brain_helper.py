from response_helper import build_response, build_card
from elasticsearch_helper import *
from random import random

from datetime import datetime

def get_unknown_response():
    session_attributes = {}
    speech_output = "I'm sorry, I'm not sure what you want me to do.  Feel free to ask for help."
    reprompt_text = "Would you like me to remember a note or find a note?"
    should_end_session = False
    return build_response(session_attributes, speech_output, should_end_session, reprompt_text = reprompt_text)

def get_welcome_response():

    session_attributes = {}
    speech_output = "Whats up?"
    reprompt_text = "Would you like me to remember a note or find a note?"
    should_end_session = False
    return build_response(session_attributes, speech_output, should_end_session, reprompt_text = reprompt_text)
    
def end_session():

    session_attributes = {}
    sign_offs = ["Ciao", "Later Alligator", "Peace out cub scout", "Adios amigo", "You got it dude", "See ya", "Bye bye", "Sayonara"]
    speech_output = sign_offs[int(random()*(len(sign_offs)-1))]
    should_end_session = True
    return build_response(session_attributes, speech_output, should_end_session)
    
def save_session(session):

    if 'attributes' in session:
        session_attributes = session['attributes']

        if 'response' in session_attributes:
            response = session_attributes['response']
            i = session_attributes['index']
            output = response['hits']['hits'][0]['_source']['text']
            in_format = '%Y-%m-%dT%H:%M:%SZ'
            out_format = '%B %d, %Y at %I %p'
            timestamp = response['hits']['hits'][i]['_source']['timestamp']
            timestamp_obj = datetime.strptime(timestamp, in_format)
            human_time = datetime.strftime(timestamp_obj, out_format)
            card = build_card(output, human_time)
            speech_output = "My vast and uncanny memory has been sent to you across the aether."
            should_end_session = True
        else:
            speech_output = "I haven't looked for anything yet.  What else can I do for you?"
            reprompt_text = "Do you need anything else?"
            should_end_session = False
    else:
        session_attributes = {}
        speech_output = "Lets not get ahead of ourselves, can I find or take a note for you?"
        reprompt_text = "Whats cooking, good looking?"
        should_end_session = False
        card = False

    return build_response(session_attributes, speech_output, should_end_session, card = card)
    
def take_stub():
    session_attributes = {}
    speech_output = "To remember something say remember, followed by what your message."
    reprompt_text = "What do you want me to remember?"
    should_end_session = False
    return build_response(session_attributes, speech_output, should_end_session, reprompt_text = reprompt_text)
    
def find_stub():
    session_attributes = {}
    speech_output = "To find something say find, followed by what you are looking for."
    reprompt_text = "Whats do you want me to find?"
    should_end_session = False
    return build_response(session_attributes, speech_output, should_end_session, reprompt_text = reprompt_text)

def get_help_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "I take notes and read them back.  To take a note, please ask me to remember, followed by your message. " \
                    "To read a note, please ask me to find, followed by whatever you are looking for.  I can also tell you the time "\
                    "that you recorded your note and send it to your device.  What can I help you with?"
    reprompt_text = "Would you like me to remember a note or find a note?"
    should_end_session = False
    return build_response(session_attributes, speech_output, should_end_session, reprompt_text = reprompt_text)

def take_note(intent, session):
    
    session_attributes = {}
    user = session['user']['userId'].split('.')[-1]
    message = build_query(intent)
    timestamp = intent['timestamp']
    
    response = elasticsearch_post(user, message, timestamp)
    should_end_session = True
    if response:
        speech_output = "I will remember " + build_query(intent)
    else:
        speech_output = "I cannot remember things at this time. I am sorry, I am a feeble old man."
    
    return build_response(session_attributes, speech_output, should_end_session)

def find_note(intent, session):
    session_attributes = {}
    message = build_query(intent)
    user = session['user']['userId'].split('.')[-1].lower()
    
    response, query = elasticsearch_find(user,message)
    if response['hits']['total'] > 0:
        
        session_attributes['response']=response
        session_attributes['index']=0
        response_text = response['hits']['hits'][0]['_source']['text']
        if response['hits']['total'] > 1:
            speech_output = "I remember " + str(response['hits']['total']) + " things, first is: " + response_text+ ".  Anything else?"
        else:
            speech_output = "I remember " + response_text+ ".  Anything else?"

    else:
        speech_output = "I do not remember that, would you like to find something else?"
        
    reprompt_text = "Do you need anything else?"
    should_end_session = False
    
    return build_response(session_attributes, speech_output, should_end_session, reprompt_text = reprompt_text)
            

def get_time(intent, session):
    if 'attributes' in session:
        session_attributes = session['attributes']
        if 'response' in session_attributes:
            i = session_attributes['index']
            response = session_attributes['response']
            in_format = '%Y-%m-%dT%H:%M:%SZ'
            out_format = '%B %d, %Y at %I %p'
            timestamp = response['hits']['hits'][i]['_source']['timestamp']
            timestamp_obj = datetime.strptime(timestamp, in_format)
            human_time = datetime.strftime(timestamp_obj, out_format)
            speech_output = "This note was recorded at "+ human_time + ". Anything else?"
            
        else:
            speech_output = "I haven't looked for anything yet.  What else can I do for you?"
        
        reprompt_text = "Do you need anything else?"
        should_end_session = False
    else:
        session_attributes = {}
        speech_output = "Lets not get ahead of ourselves, can I find or take a note for you?"
        reprompt_text = "Whats cooking, good looking?"
        should_end_session = False
    return build_response(session_attributes, speech_output, should_end_session, reprompt_text = reprompt_text)

def get_next(intent, session):
    if 'attributes' in session:
        session_attributes = session['attributes']
        if 'response' in session_attributes:
            i = session_attributes['index'] + 1
            response = session_attributes['response']
            if i >= len(response['hits']['hits']):
                speech_output = "Sorry, that was the last thing I remembered.  Anything else?"
            else:
                session_attributes['index'] = i
                speech_output = "Next is " + response['hits']['hits'][i]['_source']['text'] + ". Anything else?"
        else:
            speech_output = "I haven't looked for anything yet.  What else can I do for you?"
        
        reprompt_text = "Do you need anything else?"
        should_end_session = False
    else:
        session_attributes = {}
        speech_output = "Lets not get ahead of ourselves, can I find or take a note for you?"
        reprompt_text = "Whats cooking, good looking?"
        should_end_session = False

    return build_response(session_attributes, speech_output, should_end_session, reprompt_text = reprompt_text)

def get_previous(intent, session):
    if 'attributes' in session:
        session_attributes = session['attributes']
        if 'response' in session_attributes:
            i = session_attributes['index'] - 1
            if i < 0:
                speech_output = "That was the last note.  Anything else?"
            else:
                session_attributes['index'] = i
                response = session_attributes['response']
                speech_output = "Before that is " + response['hits']['hits'][i]['_source']['text'] + ". Anything else?"
            
        else:
            speech_output = "I haven't looked for anything yet.  What else can I do for you?"

        reprompt_text = "Do you need anything else?"
        should_end_session = False
    else:
        session_attributes = {}
        speech_output = "Lets not get ahead of ourselves, can I find or take a note for you?"
        reprompt_text = "Whats cooking, good looking?"
        should_end_session = False
    
    return build_response(session_attributes, speech_output, should_end_session, reprompt_text = reprompt_text)
