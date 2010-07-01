import urllib
import Cookie
import httplib
import re
import argparse

host = 'www.register.intense-ro.net'

def download_cookie(username, password, debug_level = 0):
  request = '/?module=account&action=login'
  data = {
    'username': username,
    'password': password,
    'server': 'IntenseRO',
  }
  
  #Set up connection
  connection = httplib.HTTPConnection(host)
  connection.set_debuglevel(debug_level)
  connection.request("POST", request, urllib.urlencode(data))
  response = connection.getresponse()
  
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
  matches = re.search(r'"(/\?module=vote&action=out&id=\d+)"', body)
  
  if matches:
    return matches.groups()
  else:
    print "Nothing to vote for. Try again later."
    return list()

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
  parser = argparse.ArgumentParser(description="IntenseRO Auto Voter")
  parser.add_argument('username', metavar='user', type=str, help="Username")
  parser.add_argument('password', metavar='pass', type=str, help="Password")
  parser.add_argument('--debug', dest='debug_level', type=int, help="The debug level. Integer >= 0", default = 0)
  args = parser.parse_args()
  
  cookie = download_cookie(args.username, args.password, args.debug_level)
  urls = get_urls(cookie, args.debug_level)
  
  do_votes(cookie, urls, args.debug_level)
  