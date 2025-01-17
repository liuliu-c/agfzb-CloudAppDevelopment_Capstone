import requests
import json
from .models import CarDealer, DealerReview 
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
import http.client

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    api_key =None
    try:
        # Call get method of requests library with URL and parameters
        if api_key:
        # Basic authentication GET
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    #print(json_payload)
    try:
         
        #response = requests.post(url, headers={'Content-Type': 'application/json'}, json=json_payload)
        conn = http.client.HTTPSConnection("7f8c56ac.us-south.apigw.appdomain.cloud")

        payload = json_payload

        headers = {
            'content-type': "application/json",
            'accept': "application/json"
            }

        conn.request("POST", "/reviews_post/post-review", payload, headers)

        res = conn.getresponse()
        data = res.read()

        return data.decode("utf-8")
    except:
        #print(response)
        return "Post error occurred"
    #print(response)
    #return response

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["output"]
        #print(dealers)
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer#["doc"]
            #print(dealer)
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
        #print(results)
    return results



# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId = dealerId)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["output"]
        #print('haha', dealers)
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer#["doc"]
            
            #print(dealer)
            # Create a CarDealer object with values in `doc` object
            dealer_obj = DealerReview(dealership=dealer_doc["dealership"], name=dealer_doc["name"], purchase=dealer_doc["purchase"],
                                   id=dealer_doc["id"], review=dealer_doc["review"], purchase_date=dealer_doc["purchase_date"],
                                   car_make=dealer_doc["car_make"],
                                   car_model=dealer_doc["car_model"], car_year=dealer_doc["car_year"], sentiment = analyze_review_sentiments(dealer_doc["review"]))
            #dealer_obj.sentiment = analyze_review_sentiments(dealer_obj.review)
            results.append(dealer_obj)
            #print(dealer_obj.review)
        #print(results)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
    authenticator = IAMAuthenticator('QE5LWUcbPqTYklWccRyfyU6GnIVgIz3WVG3uo5ZwTlCQ')
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2021-08-01',
        authenticator=authenticator
        )

    natural_language_understanding.set_service_url('https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/4422bdbe-eb3f-42e1-a329-b62559ed7d9e')
    try:
        response = natural_language_understanding.analyze(
            text=text,
            features=Features(sentiment=SentimentOptions())).get_result()

        #print(json.dumps(response, indent=2))
        result = response["sentiment"]["document"]["label"]
        #result = "hi"
        return result
    except:
        # if not enough text, just return neutral
        return "neutral"


