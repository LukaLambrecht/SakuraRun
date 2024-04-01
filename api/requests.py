#############################################
# Tools for performing GraphHopper requests #
#############################################
# See documentation here: https://docs.graphhopper.com/#section/Explore-our-APIs,
# specifically: https://docs.graphhopper.com/#operation/postRoute
# and: https://docs.graphhopper.com/#operation/postMatrix


def graphhopper_url(key, service='route'):
    # make GraphHopper request URL
    # input arguments:
    # - key: GraphHopper API key in str format
    # - service: valid GraphHopper service (e.g. 'route' or 'matrix')
    url = 'https://graphhopper.com/api/1/{}?key={}'.format(service, key)
    return url

def graphhopper_headers():
    # make GraphHopper request headers
    return {'Content-Type': 'application/json'}

def graphhopper_request(session, json, key, service='route'):
    # make GraphHopper request and return the result
    # input arguments:
    # - session: a requests.Session object
    # - json: request data in json format
    # - key: GraphHopper API key in str format
    # - service: valid GraphHopper service (e.g. 'route' or 'matrix')
    url = graphhopper_url(key, service=service)
    headers = graphhopper_headers()
    r = session.post(url, headers=headers, json=json)
    if r.status_code!=200:
        msg = 'WARNING: request returned status code {}.'.format(r.status_code)
        msg += ' Full response:\n{}'.format(r.json())
        print(msg)
    return r.json()
