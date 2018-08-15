__all__ = ['commands']
# TODO: handle jira configuration as mapping (properties per ticket type)

import re

JTAG = re.compile('{[^}]+}')
JID = 'jira-id'
JPROJECT = 'XX'
JUID = 'johndoe'
JCOMPONENT = 'CORE'
JTICKET_PFX = 'http://'

# TODO: make metadata dependent on ticket type
JFIELDS = {}


def cmd_jdump(handler, bugid):
    'jdump: dumps all low level data on given bug'
    jira = get_jira_object()
    bugid = bugid.rstrip('_,')
    if bugid.startswith(JID):
        bugid = bugid[len(JID)+1:]
    jbug = jira.issue(bugid)
#     import pdb; pdb.set_trace()
    with Pager():
        for field in dir(jbug.fields):
            v = getattr(jbug.fields, field)
            if field[0] == '_' or not v:
                continue
            print(styled("%s::"%field, 'bold'))
            print("  %s"%v)


def cmd_jlink(handler, bug, do, which):
    'jlink: <ticket> <linktype> <other ticket>'
    jira = get_jira_object()
    jira.create_issue_link(do, bug, which)


def cmd_mkuitus(handler, *bugids):
    'mkuitus: [bug id]+ create new JIRA ticket(s) on configured project implementing ticket passed as parameter'
    jira = get_jira_object()

    for bugid in bugids:
        bugid = bugid.rstrip('_,')
        pus = jira.issue(bugid)
        epic = getattr(pus.fields, JFIELDS['EPIC'])
        components = [{'name': c.name} for c in pus.fields.components]
        components.append({'name': JCOMPONENT})
#         pus.update(fields=dict(components=components))
        issue_dict = {
                'project': JPROJECT,
                'issuetype': {'name': 'Technical User Story'},
                'assignee': {'name': JUID},
                JFIELDS['TYPE']: {'value': 'Business'},
                JFIELDS['EPIC']: epic,
                'summary': '[CPE UI] %s'%pus.fields.summary,
                'description': DESCRIPTION_TEMPLATE,
                }
        new_issue = jira.create_issue(fields=issue_dict)
        print("%s implements %s"%(new_issue.key, pus.key))
        jira.create_issue_link('Implements', new_issue.key, pus.key)


def cmd_comments(handler, *bugids):
    'comments: [bug id]+ show comments on all JIRA bugs or only the specified ones (WIP)'
    if not bugids:
        bugids = [b for b in (bug[JID] for bug in handler) if b]
        print("Upading %d bugs"%len(bugids))
        input('Are you sure? (^C to cancel) ')
    jira = get_jira_object()

    for bugid in bugids:
        bugid = bugid.rstrip('_,')
        if bugid.startswith(JID):
            bugid = bugid[len(JID)+1:]
        jbug = jira.issue(bugid)
        for com in jbug.fields.comment.comments:
            print(JTAG.sub('', com.body))
    import pdb; pdb.set_trace()


def cmd_log(handler):
    'log: [bug id]+ execute custom LOG code (edit source) on all JIRA bugs or only the specified ones'
    # templatable log
    prio_n1 = None
    for bug in handler:
        if bug['jira-id'].startswith(JPROJECT) and bug['status'] != 'Rejected':
            if prio_n1 != bug.priority:
                print("")
            print("%s%s [%s]"%(JTICKET_PFX, bug.title, bug['status']))
            prio_n1 = bug.priority


def cmd_update(handler, *bugids):
    'update: [bug id]+ execute custom UPDATE code (edit source) on all JIRA bugs or only the specified ones'
    if not bugids:
        bugids = [b for b in (bug[JID] for bug in handler) if b]
        print("Upading %d bugs"%len(bugids))
        input('Are you sure? (^C to cancel) ')
    jira = get_jira_object()

    for bugid in bugids:
        bugid = bugid.rstrip('_,')
        if bugid.startswith(JID):
            bugid = bugid[len(JID)+1:]
        print(bugid)
        jbug = jira.issue(bugid)

        # Update logic here:
        # customfield_15731 == UI Assessment
        jbug.update(customfield_15731 = {'value': 'To be assessed'})

def cmd_pull(handler, *bugids):
    'pull: [bug id]+ pull all JIRA bugs or only the specified ones'
    if not bugids:
        bugids = [b for b in (bug[JID] for bug in handler) if b]
        print("Upading %d bugs"%len(bugids))

    jira = get_jira_object()
    for bugid in bugids:
        bugid = bugid.rstrip('_,')
        print(bugid)
        if bugid.startswith(JID):
            bugid = bugid[len(JID)+1:]
        jbug = jira.issue(bugid)
        create_new = False
        bug_links = set([jbug.key])
        url_prefix = jbug.permalink().rsplit('/', 1)[0]

        def linkify(bugid):
            bug_links.add(bugid)
            return "%s_" % bugid

        bug_title = "%s %s"%(linkify(jbug.key), jbug.fields.summary)
        for b in handler:
            if b[JID] == bugid:
                bug = b
                bug.title = bug_title
                break
        else:
            bug = Bug(bug_title)
            bug[JID] = bugid
            create_new = True

        fields = 'status issuetype fixVersions'.split()
        fields.extend(JFIELDS.values())
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

        for title, kind in ('Implements', outwards), ('Is implemented by', inwards):
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

def get_jira_object():
    global _jira_instance
    if _jira_instance is None:
        import getpass
        from six.moves import configparser
        from six.moves import input
        from jira import JIRA

        conf = jira_config_get(os.path.expanduser('~/.jiracli.ini'))
        options = {
            'server': conf.get('defaults', 'url'),
            'verify': True,
        }
        _jira_instance = JIRA(options, basic_auth=(conf.get('defaults', 'user'),
                                         conf.get('defaults', 'password')))

    return _jira_instance



def strip_tags(html):
    s = MLStripper()
    s.feed(html)
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


DESCRIPTION_TEMPLATE = None

def init(env, opts):
    global DESCRIPTION_TEMPLATE, JPROJECT, JUID, JFIELDS, JTICKET_PFX, JCOMPONENT
    globals().update(env)
    JFIELDS = opts['config']['FIELDS']
    DESCRIPTION_TEMPLATE = open( os.path.join(opts['config_path'], opts['config']['TEMPLATE'])).read()
    JPROJECT = opts['config']['PROJECT']
    JUID = opts['config']['UID']
    JUID = opts['config']['COMPONENT']
    JTICKET_PFX = opts['config']['TICKETPREFIXURL']
    Bug.property_trans.update(JFIELDS)

DESCRIPTION_TEMPLATE = None

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


def jira_config_get(config_path):
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
