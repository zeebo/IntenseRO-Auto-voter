#!/usr/bin/python
#
# Voter.py - IntenseRO Automatic Voter
# by zeebo
#

import urllib
import Cookie
import httplib
import re
import sys
import optparse
import Tkinter

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
      print "Sucessfully voted for %s" % request
    else:
      print "Problem voting for %s" % request

def main():
  parser = optparse.OptionParser("usage: %prog [options] username password")
  parser.add_option('-d', '--debug', dest='debug', action='store_const', const=1, help="Turns on verbose debugging", default=0)
  (options, args) = parser.parse_args()

  if len(args) != 2:
    parser.print_help()
    print "\nInvalid number of arguments.\n"
    sys.exit(1)
  
  username, password, debug_level = args[0], args[1], options.debug
  
  cookie = download_cookie(username, password, debug_level)
  
  if cookie is None:
    sys.exit(1)
  
  urls = get_urls(cookie, debug_level)
  
  if urls is None:
    sys.exit(1)
  
  do_votes(cookie, urls, debug_level)
  
  sys.exit(0)

class GUIFramework(Tkinter.Frame):
  def __init__(self, master=None):
    Tkinter.Frame.__init__(self, master)
    
    self.master.title("Voter")
    self.grid(padx=10, pady=10)
    self.CreateWidgets()
    self.master.geometry('+500-500')
    self.master.lift()
    
  def CreateWidgets(self):
    self.usernameLabel = Tkinter.Label(self, text="Username ")
    self.usernameLabel.grid(row=0, column=0)
    
    self.usernameEdit = Tkinter.Entry(self)
    self.usernameEdit.grid(row=0, column=1, columnspan=2)
    
    self.passwordLabel = Tkinter.Label(self, text="Password ")
    self.passwordLabel.grid(row=1, column=0)
    
    self.passwordEdit = Tkinter.Entry(self)
    self.passwordEdit.grid(row=1, column=1, columnspan=2)
    
    self.voteButton = Tkinter.Button(self, text="Vote", command=self.doVote)
    self.voteButton.grid(row=2, column=2)
  
  def doVote(self):
    print "Login info: %s/%s" % (self.usernameEdit.get(), self.passwordEdit.get())

if __name__ == "__main__":
  frame = GUIFramework()
  frame.mainloop()
  