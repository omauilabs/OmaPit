"""Configured credential-bearing clients refuse HTTP redirects."""
import urllib.request
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):return None

def open_request(request,timeout=5):
    return urllib.request.build_opener(NoRedirect()).open(request,timeout=timeout)
