# -*- coding: utf-8 -*-
# uWSGI Admin for Web2py

try:
    import uwsgi
    have_uwsgi = True
except:
    have_uwsgi = False
import time
import StringIO
from gluon.storage import Storage

#@auth.requires_signature()
def index():
    if not have_uwsgi:
        return "you aren't running web2py with uwsgi"
    template = template_view('main')
    return response.render(template, {})

#@auth.requires_signature()
def reload_uwsgi():
    if not have_uwsgi:
        return "you aren't running web2py with uwsgi"
    masterpid = uwsgi.masterpid()
    if masterpid > 0:
        form = FORM(INPUT(_type="submit", _value="Reload uWSGI"))
        if form.process().accepted:
            uwsgi.reload()
            response.flash = "uWSGI reloaded correctly"
    else:
        form = ''
        response.flash = "The uWSGI master process is not active"
    return form

#@auth.requires_signature()
def info():
    if not have_uwsgi:
        return "you aren't running web2py with uwsgi"
    info = Storage()
    info.masterpid = uwsgi.masterpid()
    info.version = uwsgi.version
    info.started_on = time.ctime(uwsgi.started_on)
    info.buffer_size = uwsgi.buffer_size
    info.total_requests = uwsgi.total_requests()
    info.logsize = uwsgi.logsize()
    info.numproc = uwsgi.numproc
    try:
        info.mode = uwsgi.mode
    except:
        pass
    try:
        info.pidfile = uwsgi.pidfile
    except:
        pass
    
    workers = uwsgi.workers()
    total_load = time.time() - uwsgi.started_on
    for w in workers:
        w['load'] = (100 * (w['running_time']/1000))/total_load
        w['last_spawn_str'] = time.ctime(w['last_spawn'])
        w['vsz_str'] = do_filesizeformat(w['vsz'])
        w['rss_str'] = do_filesizeformat(w['rss'])
    
    context = dict(info=info, workers=workers)
    template = template_view('info')
    return response.render(template, context)
    

def do_filesizeformat(value):
    """simplified from jinja2 filters"""
    
    bytes = float(value)
    base = 1000
    prefixes = ["kB","MB","GB"]
    if bytes == 1:
        return "1 Byte"
    elif bytes < base:
        return "%d Bytes" % bytes
    else:
        for i, prefix in enumerate(prefixes):
            unit = base ** (i + 2)
            if bytes < unit:
                return "%.1f %s" % (base * bytes / unit, prefix)
        return "%.1f %s" % (base * bytes / unit, prefix)


def template_view(template='main'):
    if template == 'main':
        return StringIO.StringIO("""
{{extend 'layout.html'}}

{{=LOAD('default', 'info.load', ajax=True, timeout=5000, times='Infinity')}}

{{=LOAD('default', 'reload_uwsgi.load', ajax=True)}}
        """)
    elif template == 'info':
        return StringIO.StringIO("""

<h1>uWSGI status</h1>
<dl class="dl-horizontal">
    <dt>masterpid</dt><dd>{{=info.masterpid}}</dd>
    <dt>version</dt><dd>{{=info.version}}</dd>
    <dt>buffer size</dt><dd>{{=info.buffer_size}} </dd>
    <dt>workers</dt><dd>{{=info.numproc}}</dd>
    <dt>total requests</dt><dd>{{=info.total_requests}}</dd>
    <dt>mode</dt><dd>{{=info.mode}}</dd>
    <dt>pidfile</dt><dd>{{=info.pidfile}}</dd>
</dl>

<br/>

<table class="table table-condensed table-hover">
    <caption>workers</caption>
    <thead>
        <tr>
            <th>#</th>
            <th>PID</th>
            <th>Requests</th>
            <th>Running Time (ms)</th>
            <th>Load</th>
            <th>Last Spawn</th>
            <th>Respawn Count</th>
            <th>Address Space (vsz)</th>
            <th>Resident Memory (rss)</th>
        </tr>
    </thead>
    <tbody>
        {{for w in workers:}}
            {{=TR(w['id'], w['pid'], w['requests'], w['running_time'], '%.2f' % w['load'], w['last_spawn_str'], w['respawn_count'], w['vsz_str'], w['rss_str'] )}}
        {{pass}}
    </tbody>
</table>
    """)
