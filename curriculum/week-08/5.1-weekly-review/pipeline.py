#!/Users/davidyerrington/virtualenvs/data/bin/python

import requests, pandas as pd, sqlite3 as db
from bs4 import BeautifulSoup
import pprint, re

class pipeline():

    dsn = {
        'database_file': 'corpus.db'
    }

    pp      =   pprint.PrettyPrinter(indent=4)
    conn    =   False

    def __init__(self):
        self.set_dbh()

    def __del__(self):
        self.conn.close()

    def set_dbh(self):
        self.conn = db.connect(self.dsn['database_file']) 

    def get_http(self, url):

        result  =   requests.get(url)

        if result.status_code == 200:
            return result.content
        else: 
            raise Exception('Response not 200')
        # print result.status_code

    def get_text(self, content):

        soup        =   BeautifulSoup(content)
        stripped    =   [p.getText() for p in soup.findAll('p')]
        return "\n".join(stripped)

    def get_http_text(self, url):

        try:
            print "Fetching %s..." % url
            content = self.get_http(url)
            return self.get_text(content)
        except:
            return None   

    def get_hrefs(self, url, domain=False, relative=True, prepend=False):

        content     =   self.get_http(url)
        soup        =   BeautifulSoup(content)
        relative_path   =   '/' if relative else ''
        domain          =   'http://%s' % domain if domain else ''
        prepend         =   '%s' % prepend if prepend else ''

        urls = []

        for a in soup.findAll('a'):
            match = re.search('href="(%s[^"]+)' % relative_path, str(a))
            if match:
                urls.append('%s%s%s' % (prepend, domain, match.group(1)))

        return list(set(urls))

    def process_urls(self, urls):

        processed = []

        for url in urls:
            try:
                content         =   self.get_http(url)
                content_text    =   self.get_text(content)

                processed.append({
                    'url': url,
                    'text_length': len(content_text),
                    'content_text': content_text
                })

            except:
                continue

        return processed


# urls = [
#     'http://www.cnn.com/2015/09/01/us/san-antonio-bexar-county-texas-police-shooting/index.html', 
#     'http://www.cnn.com/2015/09/01/us/texas-abilene-police-officer-killed/index.html', 
#     'http://www.cnn.com/2015/09/01/politics/china-russia-cyberattacks-military/index.html', 
#     'http://www.cnn.com/2015/09/01/politics/cnn-debate-criteria-amendment/index.html', 
#     'http://www.cnn.com/2015/09/01/americas/guatemala-president-immunity-stripped/index.html'
# ]

data    =   pipeline()
cnn_politics    =   data.get_hrefs('http://www.cnn.com/politics', domain="cnn.com")
cnn_df          =   pd.DataFrame(cnn_politics, columns=['url'])
cnn_df['outlet']            =  'cnn'
cnn_df['political_view']    =  'progressive'
cnn_df['content_text']      =  cnn_df['url'].map(lambda url: data.get_http_text(url))
print cnn_df.head(10)
cnn_df.to_sql('content', con=data.conn, if_exists='replace')

#data    =   pipeline()
#drudgereport    =   data.get_hrefs('http://www.drudgereport.com/', relative=False)
#drudge_df       =   pd.DataFrame(drudgereport, columns=['url'])
#drudge_df['outlet']         =   'drudgereport'
#drudge_df['political_view'] =   'conservative'
#drudge_df['content_text']   =   drudge_df['url'].map(lambda url: data.get_http_text(url))
# print drudge_df.head(10)
#drudge_df.to_sql('content', con=data.conn, if_exists='append')


# print data.get_http_text('http://www.cnn.com/2015/09/01/politics/china-russia-cyberattacks-military/index.html')

# print data.process_urls(urls)
# content =   data.get_http('http://www.cnn.com/2015/09/01/politics/donald-trump-dick-cheney-liz-cheney-book/index.html')
# print data.get_text(content)
