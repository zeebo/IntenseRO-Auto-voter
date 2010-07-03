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
import tkMessageBox
import threading
import time

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
    return None

def do_vote(cookie, request, debug_level = 0):
  #Just send a connection to the specified request
  #and if it redirects us, it worked
  connection = httplib.HTTPConnection(host)
  connection.set_debuglevel(debug_level)
  connection.request("GET", request, headers = {'Cookie': cookie})  
  response = connection.getresponse()
  return response.status == 302

def do_votes(cookie, urls, debug_level = 0):
  for request in urls:
    retval = do_vote(cookie, request, debug_level)
    if retval:
      print "Voted sucessfully for %s" % request
    else:
      print "Unable to vote for %s" % request

def main():
  parser = optparse.OptionParser("usage: %prog [-d] [-c username password]")
  parser.add_option('-d', '--debug', dest='debug', action='store_const', const=1, help="turns on verbose debugging", default=0)
  parser.add_option('-c', '--command', dest='command', action='store_true', help="runs the program as a command line interface", default=False)
  (options, args) = parser.parse_args()

  if options.command:
    command_main(parser, options, args)
  else:
    frame = GUIFramework()
    frame.mainloop()

def command_main(parser, options, args):
  if len(args) != 2:
    parser.print_help()
    print "\nInvalid number of arguments.\n"
    sys.exit(1)
      
  username, password, debug_level = args[0], args[1], options.debug  
  cookie = download_cookie(username, password, debug_level)  
  if cookie is None:
    print "Authentication error"
    sys.exit(1)
  urls = get_urls(cookie, debug_level)  
  if urls is None:
    print "Nothing to vote for"
    sys.exit(1)  
  do_votes(cookie, urls, debug_level)  
  sys.exit(0)

class ProgressBar(Tkinter.Canvas):
  def __init__(self, master, maximum, *args, **kwargs):
    Tkinter.Canvas.__init__(self, *args, **kwargs)
    self.maximum = max(1, maximum)
    self.current = 0
    self.text = ''
    self.width = kwargs.get('width', self.winfo_width())
    self.height = kwargs.get('height', self.winfo_height())
    self.update()
  
  def set_maximum(self, number):
    self.maximum = number
    self.update()
  
  def set(self, number, text):
    self.text = text
    self.current = number
    self.update()
  
  def set_text(self, value):
    self.text = value
    self.update()
    
  def set_progress(self, value):
    self.current = value
    self.update()
  
  def update(self):
    self.delete(Tkinter.ALL)
    self.create_rectangle(3, 3, self.width, self.height)
    if self.current > 0:
      self.create_rectangle(4, 4, self.width * float(self.current)/float(self.maximum), self.height-1, fill="blue", outline="blue")
    self.create_text(self.width / 2, self.height / 2, text=self.text, fill="black", font=("Tahoma", "12"))
    self.master.update_idletasks()

class GUIFramework(Tkinter.Frame):
  def __init__(self, master=None):
    Tkinter.Frame.__init__(self, master)
    self.master.resizable(0,0)
    self.master.title("Voter")
    self.grid(padx=5, pady=5)
    self.CreateWidgets()
    
  def CreateWidgets(self):
    Tkinter.Label(self, text="Username ").grid(row=0, column=0, sticky=Tkinter.W)
    self.username = Tkinter.Entry(self)
    self.username.grid(row=0, column=1, columnspan=2, sticky=Tkinter.E)
    self.username.focus_set()
    
    Tkinter.Label(self, text="Password ").grid(row=1, column=0, sticky=Tkinter.W)
    self.password = Tkinter.Entry(self)
    self.password.grid(row=1, column=1, columnspan=2, sticky=Tkinter.E)
    
    self.progress = ProgressBar(self, maximum=14, width=250, height=30)
    self.progress.grid(row=2, column=0, columnspan=2, sticky=Tkinter.W)
    
    self.voteButton = Tkinter.Button(self, text="Vote", command=self.doVote, default=Tkinter.ACTIVE)
    self.voteButton.grid(row=2, column=2, sticky=Tkinter.E)
    
    self.bind("<Return>", self.doVote)
    
  def doVote(self):
    username, password = self.username.get(), self.password.get()
    
    if username is '' or password is '':
      tkMessageBox.showerror('Error', 'Fill out username and password')
      return
    
    threading.Thread(target=gui_do_work, args=(username, password, self.progress, self.voteButton)).run()
    
def gui_do_work(username, password, progress, button):
  button.config(state=Tkinter.DISABLED)
    
  def enable(pval, text):
    progress.set(pval, text)
    button.config(state=Tkinter.NORMAL)
  
  progress.set_text("Logging in...")
  
  cookie = download_cookie(username, password)    
  if cookie is None:
    enable(0, "Authentication error.")
    return
  progress.set_text("Logged in. Checking votes")
  
  vote_urls = get_urls(cookie)    
  if vote_urls is None:
    enable(0, "Nothing to vote for right now.")
    return
  progress.set_text("Downloaded vote site list")
  
  progress.set_maximum(len(vote_urls))
  failed = 0
  for i, request in enumerate(vote_urls):
    retval = do_vote(cookie, request)
    progress.set_progress(i + 1)
    if retval:
      progress.set_text("Voted sucessfully!")
    else:
      progress.set_text("Couldn't vote for some site..")
      failed += 1
  
  enable(len(vote_urls), "Complete! Failed to vote %d times." % failed)
  
if __name__ == "__main__":
  main()
  