import os
import time
import subprocess

BUG_TEMPLATE = """
This is some demo content
for testing purpose only


"""

def test_tag_untag(brpy):
    create_bug('foobar')
    h = brpy.FileHandler()
    bug = h.get(0)
    bug.add_tag('pif')
    bug.rm_tag('pif')
    assert 'pif' not in bug.tags
    print(bug.tags)

def test_delete_started(brpy):
    create_bug('foobar')
    h = brpy.FileHandler()
    bug = h.get(0)
    h.mark_started(0)
    h.mark_fixed(0)

def test_stop(brpy):
    create_bug('foobar')
    h = brpy.FileHandler()
    bug = h.get(0)
    assert bug['started'] == ''
    h.mark_started(0)
    assert bug['started'] != ''
    h.mark_stopped(0)
    assert bug['timer'] != ''
    remove_bug(0)

def test_multi_creation(brpy, nr=10):
    for n in range(10):
        create_bug("%3d-%s" % (n, time.time()))
    h = brpy.FileHandler()
    assert len(h) == nr
    assert int(h.info['total-count']) == nr

def test_create_and_delete(brpy):
    for n in range(2):
        create_bug("First bug")
        remove_bug(0)
        create_bug("Second bug")
        create_bug("Third bug")
        remove_bug(1)

    h = brpy.FileHandler()
    assert len(h) == 2 # 2 bugs remains
    assert int(h.info['total-count']) == 6 # 6 bugs where created in total

def test_iteration(brpy):
    for n in range(10):
        create_bug("Bug %s" % n)
    for b in brpy.FileHandler():
        str(b)
        b.string_as_list(0)

def remove_bug(num):
    h = get_handler()
    h.mark_fixed(num)

def create_bug(title):
    import br
    br.Bug.finalize()
    h = get_handler()
    b = br.Bug(title)
    b.original_text = BUG_TEMPLATE
    b['priority'] = '0'
    b['bugid'] = h.info['total-count']
    b['created'] = br.now()
    h.new_bug(b)

def get_handler():
    import br
    return br.FileHandler()
