import json, urllib.parse, urllib.request
import os.path

def read_webhose_key():
    """
    Reads Webhose API key from a file named 'search.key'.
    Returns either None (no key found), or a string representing the key.
    """

    webhose_api_key = None

    try:
        if os.path.isfile('search.key'):
            file_name = 'search.key'
        else:
            file_name = '../search.key'

        with open(file_name, 'r') as f:
            webhose_api_key = f.readline().strip()
    except:
        raise IOError("'search.key' file not found.")

    return webhose_api_key

def run_query(search_terms, size=10):
    """
    Given a string containing search terms (search_terms), and a number of results
    to return (size, default is 10), returns a list of results  from the Webhose
    API, with each result consisting of a title, link, and summary.
    """

    webhose_api_key = read_webhose_key()

    if not webhose_api_key:
        raise KeyError("Webhose API key not found")  #? wouldn't the IOError in the function already have been raised? or does the function contiue after raising an error?

    root_url = 'http://webhose.io/search'

    # format the search query, escape special characters
    query_string = urllib.parse.quote(search_terms)

    search_url = '{root_url}?token={key}&format=json&q={query}&sort=relevancy&size={size}'.format(
        root_url=root_url,
        key=webhose_api_key,
        query=query_string,
        size=size
    )

    results = []

    try:
        # Connect to the Webhose API and convert the response to a python dictionary
        response = urllib.request.urlopen(search_url).read().decode('utf-8')
        response_json = json.loads(response)

        for post in response_json['posts']:
            results.append({
                'title': post['title'],
                'link': post['url'],
                'summary': post['text'][:200]
            })
    except:
        print("ERROR when querying Webhose API.")

    return results


if __name__ == '__main__':
    import sys

    query_string = sys.argv[1]

    try:
        size = int(sys.argv[2])
    except:
        # How access name of errir thrown?
        print("Size defaulting to 5.")
        size = 5

    results = run_query(query_string, size)

    for result in results:
        print("{}\n{}\n{}".format(result['title'], result['link'], result['summary']))
        print("--------------")
