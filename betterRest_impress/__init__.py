__all__ = ['commands']
import os

# Supported special attributes:
#
# - notitle
# - x
# - y

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
    <script src="http://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/highlight.min.js"></script>


    <link rel="shortcut icon" href="favicon.png" />
    <link rel="apple-touch-icon" href="apple-touch-icon.png" />
</head>
<body class="impress-not-supported">
<div class="fallback-message">
    <p>Your browser <b>doesn't support the features required</b> by impress.js, so you are presented with a simplified version of this presentation.</p>
    <p>For the best experience please use the latest <b>Chrome</b>, <b>Safari</b> or <b>Firefox</b> browser.</p>
</div>
<div id="impress" data-autoplay="7">
        <div class="step" id="title" data-x="0" data-y="-1500">
        <h1>%(title)s</h1>
        </div>
    """%{
        'title': handler.info.title,
        'css': get_resource('impress.css'),
        'mermaid': get_resource('mermaid.css'),
        }]

    for i, bug in enumerate(handler):
        props = {
                'title': '' if 'notitle' in bug.attributes else '<h1>%s</h1>'%bug.title,
                'html': bug.get_html(),
                'x': bug['x'] or i*2000,
                'y': bug['y'] or 0,
                }

        text.append('''
<div class="step" data-x="%(x)s" data-y="%(y)s">
    %(title)s
        %(html)s
</div>
                '''%props)

    text.append('''
            </div>
<div id="impress-toolbar"></div>
<div class="hint">
    <p>Use a spacebar or arrow keys to navigate. <br/>
       Press 'P' to launch speaker console.</p>
</div>
<script>
if ("ontouchstart" in document.documentElement) {
    document.querySelector(".hint").innerHTML = "<p>Swipe left or right to navigate</p>";
}

%(js)s
%(mermaid)s

impress().init();
mermaid.init();
hljs.initHighlightingOnLoad();
</script>


</body>
</html>
            '''%{
                'js': get_resource('impress.js'),
                'mermaid': get_resource('mermaid.js'),
                })
    print('\n'.join(text))

commands = {k:v for k,v in globals().items() if k.startswith('cmd_')}

