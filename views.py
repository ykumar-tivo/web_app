from app import app
from flask import render_template, request
from app import models
from jinja2 import Markup
import re
import json

header_list = ['Source Key', 'Source Gid', 'Type', 'Source', 'KG Gid', 'Tool Gid', 'Status', 'Solr Gid', 'Solr Index', 'Score', 'Max Score', 'Diff Score']
PAGE_LIMIT = 100

LINKIFY = re.compile('(([A-Z]{2,7})[0-9]+)')

@app.template_filter()
def linkify(s):
    return Markup(LINKIFY.sub(u'<a target="_blank" href="http://kg.tivo.com:8880/cgi-bin/gid_info.py?system=PROD&gid=\\1" title="\\1">\\1</a>', s))

app.jinja_env.filters['linkify'] = linkify

def get_gid_link(gid):
    return "<a href=%s>%s</a>" % ('http://10.28.218.80/tools/guid_page.py?gid=%s' % gid, gid)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', header_list=header_list, page_limit=PAGE_LIMIT)

def parse_query(query):
    params = query.strip().split('&')
    parser_params = []
    for each in params:
        if '<=' in each:
            parser_params.append(('__le__', each.split('<=')))
        elif '>=' in each:
            parser_params.append(('__ge__', each.split('>=')))
        elif '>' in each:
            parser_params.append(('__gt__', each.split('>')))
        elif '<' in each:
            parser_params.append(('__lt__', each.split('<')))
        elif '!=' in each:
            parser_params.append(('__ne__', each.split('!=')))
        elif '=' in each:
            parser_params.append(('__eq__', each.split('=')))

    return parser_params
    
def apply_query(query_obj, params):
    for op, kv in params:
        k, v = kv
        if k in set(['score', 'solr_index', 'max_score', 'diff_score']):
            v = int(v)
        query_obj = query_obj.filter(models.SolrReport.__getattribute__(models.SolrReport, k).__getattribute__(op)(v))
    return query_obj


@app.route('/data', methods=['GET'])
def get_data():
    draw = request.args.get('draw')
    start = int(request.args.get('start', 0) or 0)

    Solr = models.SolrReport

    query = models.db.session.query(Solr)
    
    search_value = request.args.get('search[value]')
    if search_value:
        if search_value.startswith('q:'):
            params = parse_query(search_value[2:])
            query = apply_query(query, params)
        else:
            query = query.filter(Solr.source_key.like(search_value + "%") | Solr.source_gid.like(search_value + "%"))

    order_value = int(request.args.get('order[0][column]', 0))
    if order_value: 
        order_column_name = request.args.get('columns[%s][data]' % order_value)
        order_column = order_column_name.lower().replace(' ', '_')
        direction = request.args.get('order[0][dir]') 
        if direction == 'asc':
            order = Solr.__getattribute__(Solr, order_column)
        else:
            order = Solr.__getattribute__(Solr, order_column).desc()
        query = query.order_by(order)

    r = query.offset(start).limit(PAGE_LIMIT)

    res = r.all()
    count = query.count()

    data = []
    for i in res:
        each_row = {"Source Key": i.source_key,
                    "Source Gid": get_gid_link(i.source_gid),
                    "Type": i.type,
                    "Source": i.source,
                    "KG Gid": linkify(i.kg_gid),
                    "Tool Gid": linkify(i.tool_gid),
                    "Status": i.status,
                    "Solr Gid": linkify(i.solr_gid),
                    "Solr Index": i.solr_index,
                    "Score": i.score,
                    "Max Score": i.max_score,
                    "Diff Score": i.diff_score
                }
        data.append(each_row)

    data = {"data": data,
            "draw": draw,
            "recordsTotal": count,
            "recordsFiltered": count
        }

    return json.dumps(data)
