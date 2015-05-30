#!/usr/bin/env python
# coding: utf-8

# A basic Python script that acts as a bridge between Ubuntu touch reviews
# and Launcpad bugs.  Run it and your web browser should open.
#
# Copyright 2015 Robert Schroll
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import shutil
import urllib2
import json
import os
import sys

cachedir = os.path.expanduser('~/.launchpadlib/cache/')
from launchpadlib.launchpad import Launchpad

DEVEL = True

CONFIG_DIR = os.path.join(os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config')),
    'reviewbridge-devel' if DEVEL else 'reviewbridge')
if not os.path.isdir(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

class ReviewBridgeServer(HTTPServer):
    
    def __init__(self, *args):
        HTTPServer.__init__(self, *args)
        self.keep_running = True
        
        def launchpad_failure():
            print "Failed to authenticate with Launchpad"
            sys.exit(1)
        
        self.launchpad = Launchpad.login_with('Review Bridge', 'staging' if DEVEL else 'production',
            credential_save_failed=launchpad_failure)
    
    def run(self):
        while self.keep_running:
            self.handle_request()

class ReviewBridgeHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        path = urlparse.unquote(parsed_path.path[1:])  # strip leading /
        if path == 'halt':
            return self.halt()
        if path == '':
            if DEVEL:
                return self.static('index.html', "text/html")
            else:
                return self.serve_unicode(INDEX_HTML, "text/html")
        if path == 'style.css':
            if DEVEL:
                return self.static('style.css', "text/css")
            else:
                return self.serve_unicode(STYLE_CSS, "text/css")
        if path == 'projects':
            return self.get_projects()
        if path.startswith('project/'):
            return self.get_project(path[8:])
        if path.startswith('reviews/'):
            return self.get_reviews(path[8:])
        if path.startswith('bugs/'):
            return self.get_bugs(path[5:])
        return self.send_error(404, "You can't always get what you want.")
    
    def do_POST(self):
        parsed_path = urlparse.urlparse(self.path)
        path = urlparse.unquote(parsed_path.path[1:])  # strip leading /
        content_len = int(self.headers.getheader('content-length', 0))
        obj = json.loads(self.rfile.read(content_len))
        if path == "add_project":
            return self.add_project(**obj)
        if path == "new_bug":
            return self.new_bug(**obj)
        if path == "update_review":
            return self.update_review(**obj)
        return self.send_error(404, "blah");
    
    def log_message(self, *args):
        pass
    
    def halt(self):
        self.server.keep_running = False
        self.serve_string(HALT, "text/html")
     
    def serve_string(self, s, mimetype):
        self.send_response(200)
        self.send_header("Content-type", mimetype)
        self.send_header("Content-Length", str(len(s)))
        self.end_headers()
        self.wfile.write(s)
    
    def serve_unicode(self, u, mimetype):
        self.serve_string(u.encode('utf-8'), mimetype)
    
    def serve_json(self, obj):
        self.serve_string(json.dumps(obj), "application/javascript");
    
    def static(self, path, type_):
        resource_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            f = open(os.path.join(resource_dir, path), 'rb')
        except IOError:
            self.send_error(404)
            return
        
        self.send_response(200)
        self.send_header("Content-type", type_)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        shutil.copyfileobj(f, self.wfile)
    
    def get_projects(self):
        projects = os.listdir(CONFIG_DIR)
        projects.sort()
        self.serve_json(projects)
    
    def get_project(self, project):
        self.static(os.path.join(CONFIG_DIR, project), "application/javascript")
    
    def get_reviews(self, appid):
        try:
            remote = urllib2.urlopen(
                "https://reviews.ubuntu.com/click/api/1.0/reviews/?package_name=" + appid)
        except urllib2.URLError as error:
            self.send_error(500, str(error))
        else:
            code = remote.getcode()
            if code >= 400:
                self.send_error(code, remote.read())
                return
            self.send_response(code)
            self.send_header("Content-type", remote.info().gettype())
            self.end_headers()
            shutil.copyfileobj(remote, self.wfile)
    
    def parse_task(self, task):
        bug = task.bug
        return bug.id, {'title': bug.title, 'description': bug.description, 'link': bug.web_link,
            'status': "open" if task.status in ("New", "Incomplete", "Confirmed", "Triaged", "In Progress")
                           else "closed"}
    
    def get_bugs(self, project):
        tasks = self.server.launchpad.projects[project].searchTasks()
        self.serve_json(dict(self.parse_task(t) for t in tasks))
    
    def add_project(self, name, id, launchpad):
        if not name or name in os.listdir(CONFIG_DIR):
            return self.serve_json({'result': 'Error', 'field': 'name'})
        if not id:
            return self.serve_json({'result': 'Error', 'field': 'id'})
        if not launchpad or not self.server.launchpad.projects.search(text=launchpad):
            return self.serve_json({'result': 'Error', 'field': 'launchpad'})
        
        with open(os.path.join(CONFIG_DIR, name), 'w') as f:
            json.dump({'appid': id, 'lp_project': launchpad, 'review_map': {}}, f)
        self.serve_json({'result': 'OK'})
    
    def new_bug(self, title, description, project):
        project_data = json.load(open(os.path.join(CONFIG_DIR, project), 'r'))
        bug = self.server.launchpad.bugs.createBug(
            target=self.server.launchpad.projects[project_data['lp_project']],
            title=title, description=description)
        self.serve_json({'result': 'OK', 'num': bug.id, 'link': bug.web_link})
    
    def update_review(self, project, review, bug):
        project_file = os.path.join(CONFIG_DIR, project)
        project_data = json.load(open(project_file, 'r'))
        project_data['review_map'][review] = bug
        json.dump(project_data, open(project_file, 'w'))
        self.serve_json({'result': 'OK'});


INDEX_HTML = u"""
%INDEX_HTML%
"""
STYLE_CSS = u"""
%STYLE_CSS%
"""
HALT = """
<html><body>You may close this window.</body></html>
"""


if __name__ == '__main__':
    import webbrowser
    
    server = ReviewBridgeServer(('localhost', 0), ReviewBridgeHandler)
    url = 'http://localhost:%i/' % server.server_port
    webbrowser.open(url)
    print "Open " + url
    server.run()
