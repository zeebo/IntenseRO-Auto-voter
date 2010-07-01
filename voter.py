import urllib
import Cookie
import httplib
import re
import sys
import optparse

host = 'www.register.intense-ro.net'

def download_cookie(username, password, debug_level = 0):
  request = '/?module=account&action=login&return_url='
  data = {
    'username': username,
    'password': password,
    'server': 'IntenseRO',
    #'return_url': '/',
  }
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
  }
  
  #Set up connection
  connection = httplib.HTTPConnection(host)
  connection.set_debuglevel(debug_level)
  connection.request("POST", request, urllib.urlencode(data), headers)
  response = connection.getresponse()
  
  if response.status != 302:
    print "Login error."
    return None
  
  #Get the session cookie
  cookie_header = response.getheader('set-cookie', '')
  
  #Parse the raw data
  jar = Cookie.BaseCookie(cookie_header)
  
  #Return the basic cookie string without expiry information for sending
  return ' '.join(["%s=%s;" % (key, jar[key].value) for key in jar])

def get_urls(cookie, debug_level = 0):
  request = '/?module=vote'
  
  connection = httplib.HTTPConnection(host)
  connection.set_debuglevel(debug_level)
  connection.request("GET", request, headers = {'Cookie': cookie})
  response = connection.getresponse()
  
  body = response.read()
  
  #Search for "/?module=vote&action=out&id=\d+"
  matches = re.findall(r'"(/\?module=vote&action=out&id=\d+)"', body)
  
  if len(matches):
    return matches
  else:
    print "Nothing to vote for. Try again later."
    return None

def do_votes(cookie, urls, debug_level = 0):
  for request in urls:
    connection = httplib.HTTPConnection(host)
    connection.set_debuglevel(debug_level)
    connection.request("GET", request, headers = {'Cookie': cookie})
    
    response = connection.getresponse()
    if response.status == 302:
      print "Sucessfully voted.."
    else:
      print "Problem voting for %s" % request

if __name__ == "__main__":
  parser = optparse.OptionParser("usage: %prog [options] username password")
  parser.add_option('-d', '--debug', dest='debug', action='store_const', const=1, help="Turns on verbose debugging", default=0)
  (options, args) = parser.parse_args()

  if len(args) != 2:
    parser.error("Incorrect number of arguments.")
  
  username, password, debug_level = args[0], args[1], options.debug
  
  cookie = download_cookie(username, password, debug_level)
  
  if cookie is None:
    sys.exit(1)
  
  urls = get_urls(cookie, debug_level)
  
  if urls is None:
    sys.exit(1)
  
  do_votes(cookie, urls, debug_level)
  
  sys.exit(0)
  