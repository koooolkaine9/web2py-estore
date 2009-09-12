#

import re

# number of items in each row of catalog 
CATALOG_WIDTH = 4


# delimiter to use between words in URL
URL_DELIMITER = '-'
def pretty_url(id, name):
    """Create pretty URL from record name and ID
    """
    return '%s%s%d' % (re.sub('[^\w ]+', '', name).replace(' ', URL_DELIMITER), URL_DELIMITER, id)
    
def pretty_id(url):
    """Extract id from pretty URL
    """
    return int(url.rpartition(URL_DELIMITER)[-1])