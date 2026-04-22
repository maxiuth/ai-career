import requests

def say_hi():
    print("Hi there!")
    
def test_api():
    results = requests.get(
    "https://api.openwebninja.com/jsearch/search",
    headers={
      "x-api-key": "ak_gl43m34brq9m9b9vutakbmni61uyt79ot3esad9xz7pmi9z"
    },
    params={
      "query": "software engineer"
    })
    
    print(results.json()['data'])

if __name__ == '__main__':
    test_api()  
