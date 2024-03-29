import os

import pytest


@pytest.fixture(scope="function", autouse=True)
def nobug():
    """Remove bugs.rst file"""
    import betterRest.cli as br

    if os.path.exists(br.BUGFILE):
        os.unlink(br.BUGFILE)


@pytest.yield_fixture(scope="module", autouse=True)
def brpy():
    """Create br.py"""
    if not os.path.exists("br.py"):
        os.symlink("br", "br.py")
    import betterRest.cli as br

    yield br
    os.unlink("br.py")
    os.system("git checkout %s" % br.BUGFILE)
