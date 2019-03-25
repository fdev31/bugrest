__all__ = ['commands']
# TODO: implement ticket-type specific field support

import re

OUTWARD_TICKET = 'Implements'
INWARD_TICKET = 'Is implemented by'

# Stores the JIRA Config (Singleton class object, do not instanciate!)
class CFG:
    _pattern = re.compile('{[^}]+}')

    id_name = 'jira-id'
    project = 'XX'

    # read from ~/jiracli.ini
    # user = 'johndoe'
    #ticket_base_url = ''

    # Common fields to all ticket types
    fields = {}

    @classmethod
    def asDict(kls):
        return dict(
            (k,v) for (k,v) in kls.__dict__.items() if not (k[0] == '_' or isinstance(v, classmethod))
            )

    @classmethod
    def update(kls, config):
        for k, v in config.items():
            setattr(kls, k, v)


def cmd_jdump(handler, bugid):
    'jdump: [Jbugid] | dumps all low level data on given bug (DEBUG)'
    jira = get_jira_object()
    bugid = bugid.rstrip('_,')
    if bugid.startswith(CFG.id_name):
        bugid = bugid[len(CFG.id_name)+1:]
    jbug = jira.issue(bugid)
    with Pager():
        for field in dir(jbug.fields):
            v = getattr(jbug.fields, field)
            if field[0] == '_' or not v:
                continue
            print(styled("%s::"%field, 'bold'))
            print("  %s"%v)

def cmd_jlink(handler, bug, do, which):
    'jlink: <ticket Jbugid> <linktype> <other Jbugid> | makes a relationship between two tickets'
    jira = get_jira_object()
    jira.create_issue_link(do, bug.rstrip('_,'), which.rstrip('_,'))

def cmd_comments(handler, *bugids):
    'comments: [Jbugid]+ | show comments on all JIRA bugs or only the specified ones (WIP)'
    if not bugids:
        bugids = [b for b in (bug[CFG.id_name] for bug in handler) if b]
        print("Upading %d bugs"%len(bugids))
        input('Are you sure? (^C to cancel) ')
    jira = get_jira_object()

    for bugid in bugids:
        bugid = bugid.rstrip('_,')
        if bugid.startswith(CFG.id_name):
            bugid = bugid[len(CFG.id_name)+1:]
        jbug = jira.issue(bugid)
        for com in jbug.fields.comment.comments:
            print(CFG._pattern.sub('', com.body))


def cmd_log(handler):
    'log: [Jbugid]+ | execute custom LOG code (edit source) on all JIRA bugs or only the specified ones (WIP)'
    # templatable log
    prio_n1 = None
    for bug in handler:
        if bug['jira-id'].startswith(CFG.project) and bug['status'] != 'Rejected':
            if prio_n1 != bug.priority:
                print("")
            print("%s%s [%s]"%(CFG.ticket_base_url, bug.title, bug['status']))
            prio_n1 = bug.priority


def cmd_pull(handler, *bugids):
    'pull: [Jbugid]+ | pull all JIRA bugs or only the specified ones'
    if not bugids:
        bugids = [b for b in (bug[CFG.id_name] for bug in handler) if b]
        print("Upading %d bugs"%len(bugids))

    jira = get_jira_object()
    for bugid in bugids:
        bugid = bugid.rstrip('_,')
        print(bugid)
        if bugid.startswith(CFG.id_name):
            bugid = bugid[len(CFG.id_name)+1:]
        jbug = jira.issue(bugid)
        create_new = False
        bug_links = set([jbug.key])
        url_prefix = jbug.permalink().rsplit('/', 1)[0]

        def linkify(bugid):
            bug_links.add(bugid)
            return "%s_" % bugid

        bug_title = "%s %s"%(linkify(jbug.key), jbug.fields.summary)
        for b in handler:
            if b[CFG.id_name] == bugid:
                bug = b
                bug.title = bug_title
                break
        else:
            bug = Bug(bug_title)
            bug[CFG.id_name] = bugid
            create_new = True

        fields = 'status issuetype fixVersions'.split()
        fields.extend(CFG.fields.values())
        for field in fields:
            v = getattr(jbug.fields, field)
            if isinstance(v, (list, tuple)):
                v = v and v[0] or None
            if hasattr(v, 'name'):
                v = v.name
            if v:
                if field in Bug.property_trans:
                    field = Bug.property_trans[field]
                bug[field] = v
        if jbug.fields.description:
            all_text = [
                    "\n\n.. decoded text:\n\n%s\n" % '\n'.join("        "+l for l in strip_tags(jbug.fields.description).split('\n')),
                    "\n\n.. raw:: html\n\n%s\n" % '\n'.join("        "+l for l in jbug.fields.description.split('\n')),
                    ''
                    ]
        else:
            all_text = ["\n\nNO DESCRIPTION FOUND", ""]

        inwards = []
        outwards = []
        for link in jbug.fields.issuelinks:
            if 'inwardIssue' in link.raw:
                inwards.append(dict(link.raw['inwardIssue']))
            if 'outwardIssue' in link.raw:
                outwards.append(dict(link.raw['outwardIssue']))

        for title, kind in (OUTWARD_TICKET, outwards), (INWARD_TICKET, inwards):
            if kind:
                all_text.append("\n%s:\n"%title)
                for link in sorted(kind, key=lambda x: x['key']):
                    all_text.append('- [{bugtype}] {bugid} {summary} '.format(
                        bugtype=link['fields']['issuetype']['name'],
                        bugid=linkify(link['key']),
                        summary=link['fields']['summary']
                        ))

        if bug_links:
            all_text.append('')
        for link in bug_links:
            all_text.append('.. _%s: %s/%s'%(link, url_prefix, link))

        bug.original_text = '\n'.join(all_text)
        bug.line_start = 0
        bug.field_line = 0
        if create_new:
            handler.new_bug(bug)
    handler.save()

commands = {k:v for k,v in globals().items() if k.startswith('cmd_')}

_jira_instance = None

def get_jira_config():
    return setup_jira_config(os.path.expanduser('~/.jiracli.ini'))

def get_jira_object():
    global _jira_instance
    if _jira_instance is None:
        import getpass
        from six.moves import configparser
        from six.moves import input
        from jira import JIRA
        conf = get_jira_config()
        options = {
            'server': conf.get('defaults', 'url'),
            'verify': True,
        }
        _jira_instance = JIRA(options, basic_auth=(conf.get('defaults', 'user'),
                                         conf.get('defaults', 'password')))

    return _jira_instance

def strip_tags(html, max_blank_lines=2):
    s = MLStripper()
    s.feed(html)

    if max_blank_lines:
        blank_count = 0
        clean_text = []

        for line in s.get_data().split('\n'):
            line = line.rstrip()
            this_is_blank = len(line) < 1
            if this_is_blank and blank_count >= max_blank_lines:
                continue
            clean_text.append(line)
            if this_is_blank:
                blank_count += 1
            else:
                blank_count = 0

        return '\n'.join(clean_text)
    else:
        return s.get_data()

try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)


def init(opts):
    try:
        CFG.fields.update(opts['config']['fields'])
    except KeyError:
        raise ValueError('configuration is missing', dict(template=CFG.asDict()))
    CFG.update(opts['config'])
    jcfg = get_jira_config()
    CFG.ticket_base_url = jcfg.get('defaults', 'url') + 'browse/'
    CFG.user = jcfg.get('defaults', 'user')
    Bug.property_trans.update(CFG.fields)

################################################################################

################################################################################
# Following code is a copy of jiracli/config.py file
# Copyright 2017 Thomas Bechtold <thomasbechtold@jpberlin.de>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import getpass
import os

from six.moves import configparser
from six.moves import input

def _config_credentials_get():
    """get username, password and url"""
    user = input("username:")
    password = getpass.getpass()
    url = input("url:")
    return user, password, url


def setup_jira_config(config_path):
    """get the configuration"""
    conf = configparser.RawConfigParser()
    conf.read([config_path])
    section_name = "defaults"
    if 'RESETLOGIN' in os.environ:
        conf.remove_section(section_name)
    if not conf.has_section(section_name):
        user, password, url = _config_credentials_get()
        conf.add_section(section_name)
        conf.set(section_name, "user", user)
        conf.set(section_name, "password", password)
        conf.set(section_name, "url", url)
        with os.fdopen(os.open(
                config_path, os.O_WRONLY | os.O_CREAT, 0o600), 'w') as f:
            conf.write(f)

    # some people prefer to not store the password on disk, so
    # ask every time for the password
    if not conf.has_option(section_name, "password"):
        password = getpass.getpass()
        conf.set(section_name, "password", password)

    # some optional configuration options
    if not conf.has_option(section_name, "verify"):
        conf.set(section_name, "verify", "true")

    return conf
