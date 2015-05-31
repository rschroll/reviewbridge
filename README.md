Review Bridge
=============
This is a little application that lets you associate reviews in the
Ubuntu Touch Store with bugs on Launchpad.  This may help you keep track
of bugs that get reported as reviews instead of as bugs.

The review bridge is a small Python program that spins up a webserver on
your local machine.  You interact with it through your browser.

Usage modes
-----------
The review bridge can be used in two modes: **development** and
**production**.  They differ in two aspects:

1. Launchpad instance: In the development mode, bugs are reported on the
staging instance of Launchpad.  In production mode, the production
instance is used.

2. Resource location: In the development mode, the HTML and CSS
resources are loaded from files in the same directory as the Python
script.  In the production mode, these resources are baked into the
script itself.

Running
-------
There are three ways to get and run the review bridge.  Which is best
for you will depend on your desired usage.

###1. Development Mode
If you wish to work on review bridge itself, you should run it in
development mode.  You won't pollute the production Launchpad instance
with test bugs, and it's easier to edit the resources as separate files.
Obviously, you can only run in development mode after downloading the
sources.  You can download a [tarball][1], but I recommend cloning the git
repository:
```
git clone https://github.com/rschroll/reviewbridge.git
```
Then, just run the python script:
```
python reviewbridge.py
```
Your browser should open on the appropriate page.

###2. Production Mode from Source
So you've fixed a few bugs in this program and now you want to use it
for real.  From the project directory, run
```
./release.sh
```
This will create the a new python file with the resources baked in at
`release/reviewbridge.py`.  Just run that script, and you're in
production mode.

###3. Production Mode as a User
You just want to use the review bridge.  Don't worry about cloning
repositories or the like; just download [this script][2], place it
wherever you like, and run it:
```
python reviewbridge.py
```

[1]: https://github.com/rschroll/reviewbridge/archive/master.tar.gz
[2]: https://github.com/rschroll/reviewbridge/releases/download/version-0.0.1/reviewbridge.py

Usage
-----
The first step in using the review bridge is to create a new project.
Hit the *Add* button in the upper right and fill out the dialog:

**Project name:** The name for the review bridge to use.  Can be anything.

**Application ID:** The unique ID used to identify your application to the
Ubuntu Touch Store.  Usually in the form
*com.ubuntu.developer.developer-name.app-name* or
*app-name.developer-name*.

**Launchpad project:** The name of the Launchpad project where you wish to
track bugs.  The thing that follows *launchpad.net/* in the URL of your
project page.

The projects you've created will appear across the top of the page.
Click on any of them to load that project.  This may take several
seconds as we download all the bugs associated with your project.  You
may get prompted to authorize access to Launchpad at this point.

Once the project is loaded, a list of reviews will appear on the
left-hand side of the page.  Each review has the author, the star
rating, and an excerpt of their comment.  If you have already
categorized the review, an icon will indicate its status.

Clicking a review loads more information, including date and the version
of your app for which the review was created.  Below this are three
options for categorizing the review.

**Not a bug report:** This review does not report a problem with your app.
Yay!  A ☺ will appear in the review list.

**Existing bug:** This review reports a problem you already know about,
and maybe have already solved.  Select the bug number from the drop-down
to the right.  The review will get a 🐭 colored green for open bugs and
red for closed bugs.  (I couldn't find a widely-supported unicode bug
glyph.)

**New bug:** Better file this before you forget.  A automatic title and
a description taken from the review are suggested, but you probably wan
to edit both.

Whichever you choose, be sure to hit *Save* before moving on to the next
review.

Currently, you can only quit the review bridge by hitting `Ctrl-C` in
the terminal from which it was launched.

Implementation Details
----------------------
The details of each project are stored in the `reviewbridge/`
(production) or `reviewbridge-devel/` (development) folder in your
`$XDG_CONFIG_HOME` (`~/.config/` by default).  If you wish to remove a
project, just delete the appropriate file.  This may be necessary in
development mode if Launchpad's staging instance is reset.

License
-------
Copyright 2015 Robert Schroll

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
