__all__ = ['commands']

class CFG:

    @classmethod
    def asDict(kls):
        return {}

jira_plugin = {}

def init(env, opts):
    # must be loaded after the jira plugin !!
    jira_plugin['mod'] = env['PLUGINS']['jira']
    jira_plugin['cfg'] =  env['PLUGINS']['jira'].CFG

def get_jira_object():
    return jira_plugin['mod'].get_jira_object()

def get_cfg():
    return jira_plugin['cfg']

def cmd_update(handler, *bugids):
    'update: [bug id]+ execute custom UPDATE code (edit source) on all JIRA bugs or only the specified ones'
    cfg = get_cfg()
    if not bugids:
        bugids = [b for b in (bug[cfg.id_name] for bug in handler) if b]
        print("Upading %d bugs"%len(bugids))
        input('Are you sure? (^C to cancel) ')
    jira = get_jira_object()

    for bugid in bugids:
        bugid = bugid.rstrip('_,')
        if bugid.startswith(cfg.id_name):
            bugid = bugid[len(cfg.id_name)+1:]
        print(bugid)
        jbug = jira.issue(bugid)
        # Update logic here:

commands = {k:v for k,v in globals().items() if k.startswith('cmd_')}
