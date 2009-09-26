#

import re


# delimiter to use between words in URL
URL_DELIMITER = '-'
def pretty_url(id, name):
    """Create pretty URL from record name and ID
    """
    return '%s%s%d' % (' '.join(re.sub('[^\w ]+', '', name).split()).replace(' ', URL_DELIMITER), URL_DELIMITER, id)
    
def pretty_id(url):
    """Extract id from pretty URL
    """
    return int(url.rpartition(URL_DELIMITER)[-1])
    
def pretty_text(s):
    "Make text pretty by capitalizing and using 'home' instead of 'default'"
    return s.replace('default', 'home').replace('_', ' ').capitalize()
       
def title():
    if response.title:
        return response.title
    elif request.function == 'index':
        return pretty_text(request.controller)
    else:
        return pretty_text(request.function)
