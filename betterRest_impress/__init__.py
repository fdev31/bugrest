__all__ = ['commands']

import os

KEEP_TRANSFORMS = True

# Supported special attributes:
#
# - notitle
# - x
# - y
# - z
# - class
# - rotate
# - rot_x
# - rot_y
# - scale
# - rot_reset

SLIDE_TEMPLATE = '''<div class="step %(classes)s" data-rel-x="%(x)s" data-rel-y="%(y)s" data-rel-z="%(z)s"
data-rotate-x="%(rot_x)s" data-rotate-y="%(rot_y)s" data-rotate-z="%(rot_z)s" data-scale="%(scale)s"
data-transition-duration="%(duration)s" >
    %(title)s
        %(html)s
</div>'''

CUSTOM_CSS = '''
.substep { opacity: 0; }
.substep.substep-visible { opacity: 1; transition: opacity 1s; }
.admonition {
    border: solid 1px #333;
    padding: 0 1em;
}
.admonition > .admonition-title {
    font-weight: bold;
}
'''

class CFG:

    @classmethod
    def asDict(kls):
        return {}

def init(*a):
    return

def get_resource(fname):
    return open(os.path.join(os.path.dirname(__file__), 'static', fname)).read()

def cmd_impress(handler):
    "impress: generate an HTML slideshow (on stdout)"

    slide_duration = handler.info['duration'] or 1000

    text = ["""<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=1024" />
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <title>%(title)s</title>

    <meta name="description" content="impress.js is a presentation tool based on the power of CSS3 transforms and transitions in modern browsers and inspired by the idea behind prezi.com." />
    <meta name="author" content="Bartek Szopka" />

    <link href="http://fonts.googleapis.com/css?family=Open+Sans:regular,semibold,italic,italicsemibold|PT+Sans:400,700,400italic,700italic|PT+Serif:400,700,400italic,700italic" rel="stylesheet" />

    <style>%(css)s</style>
    <style>%(mermaid)s</style>

    <link rel="stylesheet" href="http://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/styles/default.min.css">
    <style>
    %(custom_css)s
    </style>
    <script src="http://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/highlight.min.js"></script>


    <link rel="shortcut icon" href="favicon.png" />
    <link rel="apple-touch-icon" href="apple-touch-icon.png" />
</head>
<body class="impress-not-supported">
<div class="fallback-message">
    <p>Your browser <b>doesn't support the features required</b> by impress.js, so you are presented with a simplified version of this presentation.</p>
    <p>For the best experience please use the latest <b>Chrome</b>, <b>Safari</b> or <b>Firefox</b> browser.</p>
</div>
<div id="impress" data-autoplay="%(autoplay)s" data-transition-duration="%(duration)s">
        <div class="step" id="title" data-x="0" data-y="0">
        <h1>%(html_title)s</h1>
        </div>
    """%{
        'autoplay': handler.info['autoplay'] or 0,
        'duration': slide_duration,
        'title': handler.info.title,
        'html_title': handler.info.title_as_html(),
        'css': get_resource('impress.css'),
        'custom_css': CUSTOM_CSS,
        'mermaid': get_resource('mermaid.css'),
        }]

    rotation = {
            'rot_x': 0,
            'rot_y': 0,
            'rot_z': 0,
            }

    for i, bug in enumerate(handler):

        if 'rot_reset' in bug.attributes:
            rotation.update({
                    'rot_x': 0,
                    'rot_y': 0,
                    'rot_z': 0,
                    })

        for k, k2 in ( ('rotate', 'rot_z'), ('rot_x', 'rot_x'), ('rot_y', 'rot_y') ):
            if k in bug.attributes:
                rotation[k2] += int(bug[k])

        props = {}

        if KEEP_TRANSFORMS:
            props.update(rotation)
        else:
            for k, k2 in ( ('rotate', 'rot_z'), ('rot_x', 'rot_x'), ('rot_y', 'rot_y') ):
                if k in bug.attributes:
                    props[k2] = bug[k]
                else:
                    props[k2] = 0

        props['title'] = '' if 'notitle' in bug.attributes else '<h1>%s</h1>'%bug.title
        props['html'] = bug.as_html()
        props['x'] = bug['x'] or 1600
        props['y'] = bug['y'] or 0
        props['z'] = bug['z'] or 0
        props['scale'] = bug['scale'] or 1
        props['classes'] = bug['class']
        props['duration'] = bug['duration'] or slide_duration

        text.append(SLIDE_TEMPLATE%props)

    text.append('''
            </div>
<script>
%(js)s
%(mermaid)s

impress().init();
mermaid.init();
document.querySelectorAll('pre.code').forEach( (e) => e.innerHTML = `<code>${e.innerHTML}</code>` )
hljs.initHighlightingOnLoad();
</script>

</body>
</html>
            '''%{
                'js': get_resource('impress.js') + get_resource('substep.js'),
                'mermaid': get_resource('mermaid.js'),
                })
    print('\n'.join(text))

commands = {k:v for k,v in globals().items() if k.startswith('cmd_')}

