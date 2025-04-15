#!/bin/env python
# -*- encoding: utf-8 -*-

"A simple command-line ticket tracker"

import codecs
import datetime
import os
import pprint
import re
import sys
import tempfile
from xml.dom.minidom import Document

import docutils
from docutils.core import publish_string
from docutils.frontend import OptionParser
from docutils.parsers.rst import Parser
from docutils.utils import new_document
from docutils.writers.html4css1 import HTMLTranslator, Writer

TEAL = "cyan"
YELLOW = "yellow"
RED = "red"
BLUE = "blue"


class HTMLFragmentTranslator(HTMLTranslator):
    def __init__(self, document: Document):
        HTMLTranslator.__init__(self, document)
        self.head_prefix = ["", "", "", "", ""]
        self.body_prefix = [""]
        self.body_suffix = [""]
        self.stylesheet = [""]
        self.html_prolog = [""]
        self.head = [""]
        self.html_head = [""]
        self.embed_stylesheet = None


html_fragment_writer = Writer()
html_fragment_writer.translator_class = HTMLFragmentTranslator


def rst2html(rst_text, filtering=None):
    text = publish_string(rst_text, writer=html_fragment_writer).decode("utf-8")
    lines = text.split("\n")[7:-2]
    if filtering:
        lines = (l for l in lines if filtering(l))
    return "\n".join(lines)


# black background:
YELLOW = YELLOW

try:
    if not sys.stdout.isatty():
        raise ImportError
    import pygments
    import pygments.console
except ImportError:
    # stubs
    def colorize(txt):
        return txt

    def styled(txt, how):
        return txt

else:

    def colorize(txt):
        """Colorize *ReStructuredText* for a Terminal

        :arg str txt: The *ReStructuredText* content
        :returns: Colorized string"""
        col_lex = pygments.lexers.get_lexer_by_name("rst")
        col_fmt = pygments.formatters.get_formatter_by_name("terminal")
        return pygments.highlight(txt, col_lex, col_fmt)

    def styled(txt, how):
        """Apply a list of styles to some text

        :arg str txt: text to be styled
        :arg list(str) how: list of styles to apply
        :returns: colorized string for terminal
        """
        if not how:
            return txt
        if isinstance(how, (list, tuple)):
            mine = how.pop(0)
        else:
            mine = how
            how = None
        return styled(pygments.console.colorize(mine, txt), how)


try:
    raw_input
except NameError:  # if python3
    unicode = str
else:
    input = raw_input

try:
    import dateutil.parser
except ImportError:
    print("python-dateutil package not installed, start & stop commands will not work!")
CFGDIR = os.path.expanduser("~/.config/betterRest/")
if not os.path.exists(CFGDIR):
    os.mkdir(CFGDIR)

STYLEFILE = os.path.join(CFGDIR, "style.css")
JSCODEFILE = os.path.join(CFGDIR, "code.js")
if not os.path.exists(JSCODEFILE):
    import shutil

    import betterRest

    shutil.copy(
        os.path.join(os.path.dirname(betterRest.__file__), "style.css"), STYLEFILE
    )
    shutil.copy(
        os.path.join(os.path.dirname(betterRest.__file__), "code.js"), JSCODEFILE
    )

CFGFILE = os.path.join(CFGDIR, "config.py")

# Set default config
GLOBAL_COUNTER_NAME = "total-count"
REVERSE_ORDER = False
HTTP_PORT = 5555
BUGFILE = "tickets.rst"
DONEFILE = "done.rst"
DEBUG = False
SOURCE_MGR = True
USE_PAGER = True
TIMER_ATOM = 3600  # number of seconds to add "1" to timer, defaults to 1h
WHITE_BACKGROUND = False
SHORT_DISPLAY = False
USE_ICONS = {
    "ACTIVE": " ",
    "STOPPED": " ",
    "LOOKRIGHT": "»",
    "SEPARATOR": " ❭ ",
    "INACTIVE": "  ",
}
PLUGINS: list[str] = []

SAMPLE_CONFIG = """# betterRest configuration file
BUGFILE="%s"
DONEFILE="%s"
DEBUG=%s
SOURCE_MGR=%s
REVERSE_ORDER=%s
USE_PAGER=%s
HTTP_PORT=%s
CSS="%s"
JS="%s"
WHITE_BACKGROUND=%s
PLUGINS=%s
USE_ICONS=%r
""" % (
    BUGFILE,
    DONEFILE,
    DEBUG,
    SOURCE_MGR,
    REVERSE_ORDER,
    USE_PAGER,
    HTTP_PORT,
    STYLEFILE,
    JSCODEFILE,
    WHITE_BACKGROUND,
    PLUGINS,
    USE_ICONS,
)

if not os.path.exists(CFGFILE):
    open(CFGFILE, "w").write(SAMPLE_CONFIG)
del SAMPLE_CONFIG

exec(open(CFGFILE).read())

if WHITE_BACKGROUND:
    YELLOW = RED

if USE_ICONS:
    ICONS = USE_ICONS
else:
    ICONS = {
        "ACTIVE": "*",
        "STOPPED": "!",
        "LOOKRIGHT": ">",
        "SEPARATOR": ", ",
        "INACTIVE": " ",
    }

if "DEBUG" in os.environ:
    DEBUG = True


import subprocess
from io import StringIO


class RealPager:
    def __init__(self, cmd=["less", "-iFRX"]):
        self.cmd = cmd

    def __enter__(self):
        self.oldstdout = sys.stdout
        sys.stdout = StringIO()

    def __exit__(self, *_a):
        sys.stdout.seek(0)
        text_data = sys.stdout.read().encode("utf-8")
        sys.stdout = self.oldstdout

        p = subprocess.Popen(self.cmd, text=False, stdin=subprocess.PIPE)
        p.communicate(text_data)


class NullPager:
    def __enter__(self):
        pass

    def __exit__(self, *_a):
        pass


Pager = RealPager if USE_PAGER else NullPager


def now(iso=True):
    """Returns a string representing current time"""
    r = datetime.datetime.now()
    if iso:
        r = r.isoformat().rsplit(".", 1)[0]
    return r


def read_paragraph(prefix=""):
    """Reads a paragraph"""
    blanklines = 0
    for _ in range(200):
        text = input(prefix)
        if not text:
            blanklines += 1
            if blanklines == 2:
                break
            yield ""
            continue
        blanklines = 0
        yield text


# For later if needed ? to create documents from nodes...
# http://agateau.com/2015/docutils-snippets/


class Bug:
    """Bug object, also used to store infos
    A Bug .rst file is a list of Bug objects

    The conversion happens in the :func:`load` method, called on init.
    """

    line_start = 0
    field_line = 0
    original_text = ""
    title_char = "="
    property_trans: dict[str, str] = {}

    def __init__(self, title):
        self.title = title.strip()
        self.description = ""
        self.comments = []
        self.attributes = {}

    @property
    def uid(self):
        return int(self["bugid"] or -42)

    @property
    def started(self):
        return "started" in self.attributes

    def string_as_list(self, i):
        if SHORT_DISPLAY:
            return "#%s" % self.uid

        return "%s%s%s #%d%s" % (
            (
                styled(ICONS["ACTIVE"], "bold")
                if self.started
                else (ICONS["STOPPED"] if self["timer"] != "" else ICONS["INACTIVE"])
            ),
            styled(str(i).ljust(3), "bold"),
            styled(self.title, ["standout", YELLOW if self.started else BLUE]),
            self.uid,
            styled(
                self["tags"].replace("#", " ") + "" * (20 - len(self["tags"])), TEAL
            ),
        )

    def __str__(self):
        r = []
        r.append(self.title)
        r.append(self.title_char * len(self.title))
        r.append("")
        for k, v in sorted(self.attributes.items()):
            name = self.property_rtrans.get(k, k)
            r.append(":%s: %s" % (name, v))
        r.append("")
        r.append(self.text)
        return "\n".join(r).rstrip("\n")

    def title_as_html(self):
        return rst2html(self.title)

    def as_html(self):
        return rst2html(self.get_text())

    @classmethod
    def finalize(kls):
        kls.property_rtrans = {v: k for k, v in Bug.property_trans.items()}

    @property
    def taglines(self):
        return self.field_line - self.line_start

    def get_text(self):
        return "\n".join(
            self.original_text.split("\n")[self.taglines + 1 :]
        )  # +1 to ignore blank separator line

    def set_text(self, val: list[str]):
        if not isinstance(val, (list, tuple)):
            val = val.split("\n")

        tag_lines = self.original_text.split("\n")[: self.taglines]
        self.original_text = "\n".join(
            tag_lines + [""] + val
        )  # [''] to add blank line separator

    text = property(get_text, set_text)

    @property
    def tags(self):
        mytags = self["tags"].split("#")
        return set(x.strip() for x in mytags if x)

    def add_tag(self, tagname):
        tags = self.tags
        tags.add(tagname)
        self["tags"] = "#" + "#".join(tags)

    def rm_tag(self, tagname):
        tags = self.tags
        tags.remove(tagname)
        if tags:
            self["tags"] = "#" + "#".join(tags)
        else:
            self["tags"] = ""

    @property
    def priority(self):
        return int(self.attributes.get("priority", "0").split(None, 1)[0])

    def __delitem__(self, name):
        try:
            del self.attributes[name]
        except KeyError:
            raise RuntimeError('No such attribute "%s"' % name)

    def __getitem__(self, name):
        return self.attributes.get(name, "")

    def __setitem__(self, name, val):
        self.attributes[name.rstrip().lower()] = str(val).rstrip()


class Visitor(docutils.nodes.GenericNodeVisitor):
    default_departure = None

    def __init__(self, doc, bugs):
        line_mapping = {}
        previous = None

        for i, pos in enumerate(b.line_stop + 1 for b in bugs):
            if i:
                r = range(previous, pos)
            else:
                r = range(pos)
            for line in r:
                line_mapping[line] = bugs[i]
            previous = pos

        self.line_mapping = line_mapping
        docutils.nodes.GenericNodeVisitor.__init__(self, doc)

    def visit_field(self, node):  # attributes
        b = self.line_mapping[node.line]
        b[node.children[0].astext().strip()] = node.children[1].astext().strip()
        b.field_line = max(getattr(self, "field_line", 0), node.line)

    def default_visit(self, node):
        if DEBUG:
            print("=", node.tagname)
            print("[[%s]]" % node.source)


class FileHandler:
    def __init__(self):
        self.bugs = []
        self.fixed_bugs = []
        self.info: Bug | None = None
        self.bugs_text = []
        self.mixed_priorities = False
        self.load()
        self.line_stop = None
        self.line_start = None

    @property
    def single_priority(self):
        return all(x.priority == 0 for x in self)

    def get(self, nr=None):
        notfound_txt = "Invalid bug id"
        if nr is None:
            raise RuntimeError(notfound_txt)
        if isinstance(nr, Bug):
            return nr
        if isinstance(nr, str) and not nr.isdigit():
            if nr[0] == "#":
                k = "bugid"
                v = nr[1:]
            elif ":" in nr:
                k, v = nr.split(":")
            else:
                raise RuntimeError(notfound_txt)
            for bug in self:
                if bug[k] == v:
                    return bug
        else:
            nr = int(nr)
            try:
                return self.bugs[nr]
            except IndexError:
                raise RuntimeError(notfound_txt)

        raise RuntimeError(notfound_txt)

    def save(self, done=False):
        if done:
            fname = DONEFILE
            source = self.fixed_bugs
        else:
            fname = BUGFILE
            source = [self.info] + self.bugs

        data = []
        for i, bug in enumerate(source):
            data.append(str(bug))
            if i + 1 != len(source):
                data.append("\n\n%s\n\n" % ("-" * 80))  # separator on single line
        # save only if didn't except before
        data.append("\n")
        o = codecs.open(fname, "w", encoding="utf-8")
        o.writelines(data)
        o.close()

    def load(self, done=False):
        if done:
            fname = DONEFILE
            source = self.fixed_bugs
        else:
            fname = BUGFILE
            source = self.bugs

        if os.path.exists(fname):
            parser = Parser()
            settings = OptionParser(components=(Parser,)).get_default_values()
            document = new_document(fname, settings)
            text = codecs.open(fname, encoding="utf-8").read()
            text_lines = text.split("\n")
            parser.parse(text, document)

            # search for tickets boundaries (-------)
            indices = [
                i
                for i, l in enumerate(text_lines)
                if l.startswith("------") and (i and not text_lines[i - 1].strip())
            ]

            start = 0
            nb_docs = len([doc for doc in document if doc.tagname == "section"])

            for i in range(nb_docs):
                if i:
                    start = indices[i - 1] + 2
                    # find the title
                    for title in text_lines[start:]:
                        title = title.strip()
                        if title and title[0] not in ":.":
                            break
                else:
                    for n, title in enumerate(text_lines):
                        t = title.strip()
                        if t and t[0] not in ".:" and title[0] not in " \t":
                            break
                start += 3
                if i + 1 == nb_docs:  # last element
                    stop = len(text_lines) - 1
                else:
                    stop = indices[i] - 1
                orig_text = text_lines[start:stop]
                b = Bug(title)
                b.original_text = "\n".join(orig_text).strip()
                b.line_start = start
                b.line_stop = stop

                if not i and not done:
                    self.info = b
                else:
                    if done:
                        self.fixed_bugs.append(b)
                    else:
                        self.bugs.append(b)

            if done:
                visitor = Visitor(document, self.fixed_bugs)
            else:
                visitor = Visitor(document, [self.info] + self.bugs)
            document.walk(visitor)

            if not done:  # sort bugs
                if REVERSE_ORDER:

                    def sorting(x):
                        return (-x.priority, x.uid)

                else:

                    def sorting(x):
                        return (x.priority, x.uid)

                source.sort(key=sorting)

        if not self.info:
            self.info = Bug("Tickets")
            self.info[GLOBAL_COUNTER_NAME] = 0

    def new_bug(self, bug):
        bug["created"] = now()
        cnt = int(self.info[GLOBAL_COUNTER_NAME])
        bug["bugid"] = cnt + 1
        self.info[GLOBAL_COUNTER_NAME] = cnt + 1
        self.bugs.append(bug)
        self.save()
        return bug.uid

    def mark_started(self, bugid):
        bug = self.get(bugid)
        bug["started"] = now()
        self.save()

    def mark_stopped(self, bugid):
        bug = self.get(bugid)
        if bug["started"]:
            if not bug["timer"]:
                old = 0
            else:
                old = int(bug["timer"])

            last_date = dateutil.parser.parse(bug["started"])
            old += (now(False) - last_date).seconds / TIMER_ATOM
            del bug["started"]
            bug["timer"] = int(old)
            self.save()
        else:
            print("Already stopped")

    def mark_fixed(self, bugid):
        bug = self.get(bugid)
        self.bugs.pop(self.bugs.index(bug))
        if bug["started"]:
            self.mark_stopped(bug)
        bug["fixed"] = now()
        self.fixed_bugs.insert(0, bug)
        self.save()
        self.save(True)

    def __iter__(self):
        return iter(self.bugs)

    def __len__(self):
        return len(self.bugs)


# All commands


def cmd_filter(handler, *filters):
    var_sep = "="
    compiled_filters = []
    for filt_pat in filters:
        if var_sep in filt_pat:
            filt_key, filt_pat = (x.strip() for x in filt_pat.split(var_sep))
            regex = re.compile(filt_pat)
            if filt_key == "title":
                compiled_filters.append(lambda bug: regex.match(bug.title))
            elif filt_key == "text":
                compiled_filters.append(lambda bug: regex.match(bug.text))
            else:
                compiled_filters.append(lambda bug: regex.match(bug[filt_key]))
    for i, bug in enumerate(handler):
        if all(f(bug) for f in compiled_filters):
            print(bug.string_as_list(i))


def cmd_list(handler):
    priority = None
    show_priorities = not handler.single_priority
    max_bugid = 0
    verbose = not (SHORT_DISPLAY)
    for i, bug in enumerate(handler):
        if verbose and show_priorities and bug.priority != priority:
            priority = bug.priority
            print(styled("P%s:" % priority, YELLOW))
        max_bugid = max(max_bugid, bug.uid)
        print(bug.string_as_list(i))
    if max_bugid == 0 and len(handler) == 0 and verbose:
        print("Nothing to show here!")
    else:
        nb_fixed = max_bugid - len(handler)
        nb_active = len(handler)
        if verbose:
            print(
                "%s %s closed%s%s active%slatest is #%d"
                % (
                    ICONS["LOOKRIGHT"],
                    styled(str(nb_fixed), YELLOW),
                    ICONS["SEPARATOR"],
                    styled(str(nb_active), [YELLOW, "bold"]),
                    ICONS["SEPARATOR"],
                    max_bugid,
                )
            )


cmd_ls = cmd_list


def cmd_cfg(handler):
    subprocess.call([os.environ["EDITOR"] or "vi", CFGFILE])


def cmd_edit(handler, *nrs):
    tmpfile = tempfile.mkstemp(suffix=".rst")[1]
    for nr in nrs:
        bug = handler.get(nr)
        open(tmpfile, "w+").write(bug.text)
        subprocess.call([os.environ["EDITOR"] or "vi", tmpfile])
        bug.text = open(tmpfile, "r").read()
    handler.save()


def cmd_show(handler, *nrs):
    def process(bug):
        print(colorize(unicode(bug).replace("raw:: html", "code:: html")))

    with Pager():
        if not nrs:
            for bug in reversed(list(handler)):
                process(bug)
                print("")
        else:
            for nr in nrs:
                bug = handler.get(nr)
                process(bug)


def cmd_grep(handler, *args):
    for i, bug in enumerate(handler):
        text = str(bug).lower()
        count = 0
        for pattern in args:
            if pattern.lower() in text:
                count += 1
        if count == len(args):
            print(bug.string_as_list(i))


def cmd_untag(handler, bug_nr, tagname):
    handler.get(bug_nr).rm_tag(tagname)
    handler.save()


def cmd_tag(handler, bug_nr=None, tagname=None):
    if bug_nr is None:
        # Just list
        all_tags = set()
        for bug in handler:
            all_tags = all_tags.union(bug.tags)
        for tag in sorted(all_tags):
            print(" %s" % tag)
        return

    if not tagname:
        tagname = bug_nr
        bug_nr = None

    if bug_nr is not None:
        bug = handler.get(bug_nr)
        bug.add_tag(tagname)
        handler.save()
    else:
        for i, bug in enumerate(handler):
            if tagname in bug["tags"]:
                print(bug.string_as_list(i))


def cmd_start(handler, nr=None):
    if nr is None:
        nr = input("nr: ")
    handler.mark_started(nr)


def cmd_stop(handler, nr=None):
    if nr is None:
        nr = input("nr: ")
    handler.mark_stopped(nr)


def cmd_remove(handler, *nrs):
    handler.load(True)  # loads current fixed bugs list too
    for nr in nrs:
        handler.mark_fixed(nr)


cmd_fix = cmd_delete = cmd_rm = cmd_remove


def cmd_add(handler, nr=None):
    if nr is None:
        nr = input("nr: ")
    bug = handler.get(nr)

    description = input("Title: ").rstrip()
    comment_text = [description]
    for line in read_paragraph("Comment: "):
        comment_text.append("    " + line)
    bug.original_text += "\n\n" + ("\n".join(comment_text).rstrip())
    handler.save()


def cmd_html(handler):
    text = codecs.open(BUGFILE, encoding="utf-8").read()
    text = text.rstrip().rstrip("-")
    print(
        publish_string(
            text,
            writer_name="html",
            settings_overrides={
                "stylesheet_path": STYLEFILE  # Replace with a pkg_resource thing or another hack to get data
            },
        ).decode("utf-8")
    )


def cmd_new(handler, title=None, description=None):
    if title is None:
        title = input("Title: ").rstrip()
    bug = Bug(title)
    if description:
        full_description = description
    else:
        full_description = []
        for line in read_paragraph("Description: "):
            if not full_description:
                line = line.strip()
            full_description.append(line)
    full_description.append("")
    bug.original_text = "\n" + "\n".join(full_description)
    bug["priority"] = "0"
    print("created #%d" % handler.new_bug(bug))


def cmd_unset(handler, nr, name=None):
    bug = handler.get(nr)
    if name is None:
        name = input("Attribute name: ").strip()
    if not bug:
        raise RuntimeError("Bug not found")
    del bug[name]
    handler.save()
    print(colorize(unicode(bug)))


def cmd_get(handler, nr, name=None, *args):
    if name is None:
        name = nr
        bugs = handler
    else:
        if args:
            # accept nested commands
            nrs = [nr, name] + list(args)[:-1]
            name = args[-1]
        else:
            nrs = [nr]
        bugs = (handler.get(nr) for bug in nrs)

    for bug in sorted(bugs, key=lambda o: (o[name], o.uid)):
        print(
            "%s: %s # %s %s"
            % (
                styled(name, YELLOW),
                styled(bug[name], "bold"),
                bug.title,
                styled("#%s" % bug.uid, TEAL),
            )
        )


def cmd_set(handler, nr, name=None, value=None):
    bug = handler.get(nr)

    if name is None:
        name = input("Attribute name: ").strip()
    if value is None:
        value = input("Value: ").strip()

    bug[name] = value
    handler.save()
    print(colorize(unicode(bug)))


def cmd_serve(handler, port=HTTP_PORT):
    import socket

    port = int(port)
    # python3 first:
    try:
        import socketserver
    except ImportError:
        import SocketServer as socketserver

    try:
        import http.server as SimpleHTTPServer
    except ImportError:
        import SimpleHTTPServer  # python2

    class BasicTCPServer(socketserver.ThreadingTCPServer):
        def server_bind(self):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            socketserver.ThreadingTCPServer.server_bind(self)

    class HTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            handler = FileHandler()
            handler.info.title_char = "#"
            text = []

            text.append(unicode(handler.info))
            text.append(
                """
.. contents::
    :local:
            """
            )

            text.append(
                """.. raw:: html

        <select class="filter_input" id="filter_name">
            <option value=""></option>
        </select><input class="filter_input" type="text" id="filter_value" /><button onclick="run_filter()">Filter</button>
        <input type="hidden" id="header_limit"></input>
            """
            )

            for bug in reversed(list(handler)):
                text.append(unicode(bug))
                text.append("")

            text.append("")
            text.append(".. raw:: html")
            text.append("")
            text.append("    <script>")
            text.extend("    " + line.rstrip() for line in open(JSCODEFILE).readlines())
            text.append("    </script>")
            if DEBUG:
                print("\n".join(text))

            self.wfile.write(
                publish_string(
                    "\n".join(text),
                    writer_name="html",
                    settings_overrides={
                        "stylesheet_path": STYLEFILE  # Replace with a pkg_resource thing or another hack to get data
                    },
                )
            )
            return

    httpd = BasicTCPServer(("0.0.0.0", port), HTTPHandler)
    try:
        print("HTTP server on port %s" % port)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("... bye bye!")


def main():
    try:
        cmd = sys.argv[1]
        if cmd.endswith(".rst"):
            global BUGFILE, SOURCE_MGR
            BUGFILE = cmd
            sys.argv.pop(0)
            SOURCE_MGR = False  # Don't try to find the file
            # this may fail and be caught by the same except
            # will provide default arguments but BUGFILE will be set
            cmd = sys.argv[1]
    except IndexError:
        cmd = "list"
        args = []
    else:
        args = sys.argv[2:]

    if SOURCE_MGR:  # track .<vcs> files as root if option enabled
        fold = os.path.abspath(os.path.curdir)
        found = None
        current_path = ""
        for fold in fold.split(os.path.sep):
            if fold:
                current_path += fold + os.path.sep
                # norm
            else:
                current_path += os.path.sep
            for scm in "svn hg git bzr".split():
                if os.path.isdir("%s.%s" % (current_path, scm)):
                    found = current_path
        if found:
            os.chdir(found)

    if "-q" in sys.argv:
        global SHORT_DISPLAY
        sys.argv.pop(sys.argv.index("-q"))
        SHORT_DISPLAY = True

    handler = FileHandler()

    commands = {k: v for k, v in globals().items() if k.startswith("cmd_")}
    extra_docs = {}

    shared_plugins = {}

    for plugin in PLUGINS:
        try:
            plug_mod = __import__("betterRest_%s" % plugin)
        except ImportError:
            print("%s plugin not found" % plugin.title())
        else:
            g = globals()
            entry_name = "PLUGIN_" + plugin
            default_conf = plug_mod.CFG.asDict()
            if not entry_name in g and default_conf:
                print(
                    "%s is not configured, consider adding to your %s similar snippet:\n%s = %s"
                    % (plugin, CFGFILE, entry_name, pprint.pformat(default_conf))
                )
            else:
                try:
                    plug_mod.Bug = Bug
                    plug_mod.plugins = shared_plugins
                    plug_mod.all_commands = commands
                    plug_mod.init(
                        {"config": g[entry_name] if entry_name in g else default_conf}
                    )
                except Exception as e:
                    print(
                        'Plugin "%s" failed to load: %s\nYou may need to update %s'
                        % (plugin, e, CFGFILE)
                    )
                    print("Details here:\n%s" % ("=" * 80))
                    raise
                else:
                    shared_plugins[plugin] = plug_mod
                    conflicts = set(commands).intersection(plug_mod.commands)
                    conflicts.difference_update(set(getattr(plug_mod, "overrides", [])))
                    if conflicts:
                        for conflict in conflicts:
                            print(
                                'WARNING! "%s" is provided by %s and %s plugins, enable only one!'
                                % (
                                    conflict[4:],
                                    plugin,
                                    commands[conflict].__code__.co_filename.rsplit(
                                        os.path.sep, 2
                                    )[1],
                                )
                            )

                    commands.update(plug_mod.commands)
                    extra_docs[plugin] = [
                        fn.__doc__ for fn in plug_mod.commands.values()
                    ]

    Bug.finalize()
    fn = commands.get("cmd_" + cmd)  # find function matching command
    if fn is None:
        matching = [c for c in commands if c.startswith("cmd_" + cmd)]
        if len(matching) == 1:
            fn = commands[matching[0]]

    if fn is not None:
        fn(handler, *args)
    else:

        def render_doc(doc):
            name, desc = doc.split(": ", 1)
            if " | " in desc:
                args, desc = desc.split(" | ", 1)
                args = args
                desc = " " + desc
            else:
                args = ""
            print("%s %s%s" % (styled("%10s" % name, YELLOW), styled(args, BLUE), desc))

        print("\nSyntax: %s [filename.rst] [command]\n" % os.path.basename(sys.argv[0]))

        docs = """\
     cfg: edits the configuration file
    list: short listing of bugs (default action)
    show: [bug id] | detailed listing of bugs, ReStructuredText format (save as .rst or .txt)
    html: same as above, but in html format
   serve: publish the html content using HTTP server
     new: open a new bug
      rm: [bug id] | remove some bug (mark as fixed)
     add: [bug id] | add some comment to a bug
    edit: [bug id] | edit text of given bug(s)
  filter: [pattern] | returns list of matching bugs (use -q for a quiet output)
   start: [bug id] | starts counting elapsed time for this bug
    stop: [bug id] | stops counting elapsed time for this bug
     tag: [bug id] [tag name] OR [tag name] | adds a tag to a bug OR list matching tickets
   untag: [bug id] [tag name] | removes a tag
     get: [bug id] [attr name] | prints an attribute value
     set: [bug id] [attr name] [value] | adds an attribute to a bug
   unset: [bug id] [attr name] | removes an attribute
    grep: [pattern] | list bugs containing given pattern(s)"""
        for doc in docs.split("\n"):
            render_doc(doc)

        for plugin_name, docs in extra_docs.items():
            print("\n%s::" % plugin_name)
            for doc in docs:
                render_doc(doc)


def commandline():
    if DEBUG:
        main()
        raise SystemExit(0)
    try:
        main()
    except RuntimeError as e:
        print("ERROR: " + " ".join(e.args))
    except ValueError as e:
        print("ERROR: Argument have incorrect value")
    except TypeError as e:
        print("ERROR: %s" % e.args[0].split(" ", 1)[1])


if __name__ == "__main__":
    commandline()
