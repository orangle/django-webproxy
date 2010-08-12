'''
Created on Aug 10, 2010

@author: tribaal
'''
from django.http import HttpResponse
from django.core.servers import basehttp
import urllib2

class ProxyMiddleware:
    
    def process_request(self, request):
        """This is called every time a new request arrives in Django, but *before* the url resolution is
        made. 
        If this returns an HttpResponse -> nothing else is made by django and the HttpResponse is sent to client
        If this returns None -> the request is passed along to the url resolver for "normal" handling by Django """
        
        if request.META['QUERY_STRING']:
            querystring = request.META['PATH_INFO'] + '?' + request.META['QUERY_STRING']
        else:
            querystring = request.META['PATH_INFO']
        server_protocol = request.META['SERVER_PROTOCOL']
    
        outgoing_headers = {}
        data = []
        data.append(' '.join([request.method, querystring, server_protocol]))#
        for a, b in request.environ.iteritems():
            if a.startswith('HTTP_'):
                a = header_name(a)
                outgoing_headers[a] = b
                data.append('%s %s' % (a, b))
        data = '\r\n'.join(data) + '\r\n\r\n'
    
        # Instead of using sockets I now use urllib2, so that DNS "beautifying" is properly done.
        
        requ = urllib2.Request(querystring, None, outgoing_headers)
        
        remote = urllib2.urlopen(requ)
        
        status_code = remote.getcode()
        headers = remote.headers # This is a dict
        content = remote.read()
        
        # We should have all we need now.
        # I cleaned up the part with the sockets - it's much cleaner now.

        response = HttpResponse(content, status=int(status_code))
        for header in headers.keys():
            # We need to check if the header we forward is allowed (if it's not a hop by hop header)
            if not basehttp.is_hop_by_hop(header):
                response[header] = headers[header]

        return response



def header_name(name):
    """Convert header name like HTTP_XXXX_XXX to Xxxx-Xxx:"""
    words = name[5:].split('_')
    for i in range(len(words)):
        words[i] = words[i][0].upper() + words[i][1:].lower()
        
    result = '-'.join(words) + ':'
    return result


class HttpResponse2(object):
    """I'm not sure what this class is all about..."""
    status_code = 200

    def __init__(self, content=''):
        if not isinstance(content, basestring) and hasattr(content, '__iter__'):
            self._container = content
            self._is_string = False
        else:
            self._container = [content]
            self._is_string = True
        self.cookies = {}#SimpleCookie()
        self._headers = {}#{'content-type': ('Content-Type', content_type)}

    def items(self):
        return self._headers.values()

    def __iter__(self):
        self._iterator = iter(self._container)
        return self

    def next(self):
        chunk = self._iterator.next()
        if isinstance(chunk, unicode):
            chunk = chunk.encode(self._charset)
        return str(chunk)
