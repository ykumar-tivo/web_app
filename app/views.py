from app import app
from flask import render_template, request, jsonify
import json
from sqlalchemy import text
from app import models
from jinja2 import Markup
import re
import json
import plotly
from plotly.offline import plot
import plotly.graph_objs as go
from flask import Markup
import os

header_list = ['Source_key', 'Sk_type', 'Gid', 'Gid_type', 'score', 'Gid', 'Gid_type', 'score', 'Gid', 'Gid_type', 'score',\
              'Gid', 'Gid_type', 'score', 'Gid', 'Gid_type', 'score',]


PAGE_LIMIT = 100

LINKIFY = re.compile('(([A-Z]{2,7})[0-9]+)')
Lsh = models.ReportTable

@app.template_filter()
def linkify(s):
    return Markup(LINKIFY.sub(u'<a target="_blank" href="http://kg.tivo.com:8880/cgi-bin/gid_info.py?system=PROD&gid=\\1" title="\\1">\\1</a>', s))

app.jinja_env.filters['linkify'] = linkify

def get_gid_link(gid):
    return "<a target='_blank' href=%s>%s</a>" % ('http://10.28.218.80/tools/guid_page.py?gid=%s' % gid, gid)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', header_list=header_list, page_limit=PAGE_LIMIT)

def parse_query(query):
    params = query.strip().split('and')
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
        else:
            each = '='+each
            parser_params.append(('__eq__', each.split('=')))
    return parser_params

def apply_query(params, rank):
    filter_tuple = ()
    for op, kv in params:
        k, v = kv
        v = float(v)
        filter_tuple += (Lsh.__getattribute__(Lsh, rank).__getattribute__(op)(v),)
    return filter_tuple

@app.route('/data', methods=['GET'])
def get_data():
    draw = request.args.get('draw')
    start = int(request.args.get('start', 0) or 0)
    query = models.db.session.query(Lsh)
    username = request.args.get('username')
    form_id_string = request.args.get('id')
    length = 0
    form_id = -1
    params = ()
    if username:
        username = username[:-1]
        form_id_string = form_id_string[:-1]
        form_input = username.split(",")# list of strings
        form_id_list = form_id_string.split(",")# list of numbers
        length = len(form_id_list)
    if length > 0:
        for form_id in range(length):
            if form_id_list[form_id] == '0':
                params +=(Lsh.sk == form_input[form_id],)
            elif form_id_list[form_id] == '1':
                params += (Lsh.sk_entity_type == form_input[form_id],)
            elif form_id_list[form_id] == '2':
                params += (Lsh.gid1 == form_input[form_id],)
            elif form_id_list[form_id] == '3':
                params += (Lsh.gid1_entity_type == form_input[form_id],)
            elif form_id_list[form_id] == '4':
                parameters = parse_query(form_input[form_id])
                params += apply_query(parameters, "lsh_score1")
            elif form_id_list[form_id] == '5':
                params += (Lsh.gid2 == form_input[form_id],)
            elif form_id_list[form_id] == '6':
                params += (Lsh.gid2_entity_type == form_input[form_id],)
            elif form_id_list[form_id] == '7':
                parameters = parse_query(form_input[form_id])
                params += apply_query(parameters, "lsh_score2")
            elif form_id_list[form_id] == '8':
                params += (Lsh.gid3 == form_input[form_id],)
            elif form_id_list[form_id] == '9':
                params += (Lsh.gid3_entity_type == form_input[form_id],)
            elif form_id_list[form_id] == '10':
                parameters = parse_query(form_input[form_id])
                params += apply_query(parameters, "lsh_score3")
            elif form_id_list[form_id] == '11':
                params += (Lsh.gid4 == form_input[form_id],)
            elif form_id_list[form_id] == '12':
                params += (Lsh.gid4_entity_type == form_input[form_id],)
            elif form_id_list[form_id] == '13':
                parameters = parse_query(form_input[form_id])
                params += apply_query(parameters, "lsh_score4")
            elif form_id_list[form_id] == '14':
                params += (Lsh.gid5 == form_input[form_id],)
            elif form_id_list[form_id] == '15':
                params += (Lsh.gid5_entity_type == form_input[form_id],)
            elif form_id_list[form_id] == '16':
                parameters = parse_query(form_input[form_id])
                params += apply_query(parameters, "lsh_score5")


        query = query.filter(*params)

    order_value = int(request.args.get('order[0][column]', 0))
    if order_value:
        order_column_name = request.args.get('columns[%s][data]' % order_value)
        order_column = order_column_name.lower().replace(' ', '_')
        direction = request.args.get('order[0][dir]')
        if direction == 'asc':
            order = Lsh.__getattribute__(Lsh, order_column)
        else:
            order = Lsh.__getattribute__(Lsh, order_column).desc()
        query = query.order_by(order)
    r = query.offset(start).limit(PAGE_LIMIT)

    res = r.all()
    count = query.count()

    data = []
    for i in res:
        if i.gid1 == None:
            i.gid1 = ''
        if i.gid2 == None:
            i.gid2 = ''
        if i.gid3 == None:
            i.gid3 = ''
        if i.gid4 == None:
            i.gid4 = ''
        if i.gid5 == None:
            i.gid5 = ''
        each_row = {"Source Key": get_gid_link(i.sk),
                    "sk_entity_type": i.sk_entity_type,
                    "Gid1": linkify(i.gid1),
                    "Gid1_entity_type": i.gid1_entity_type,
                    "Lsh_score1": i.lsh_score1,
                    "Gid2": linkify(i.gid2),
                    "Gid2_entity_type": i.gid2_entity_type,
                    "Lsh_score2": i.lsh_score2,
                    "Gid3": linkify(i.gid3),
                    "Gid3_entity_type": i.gid3_entity_type,
                    "Lsh_score3": i.lsh_score3,
                    "Gid4": linkify(i.gid4),
                    "Gid4_entity_type": i.gid4_entity_type,
                    "Lsh_score4": i.lsh_score4,
                    "Gid5": linkify(i.gid5),
                    "Gid5_entity_type": i.gid5_entity_type,
                    "Lsh_score5": i.lsh_score5,
                }
        data.append(each_row)

    data = {"data": data,
            "draw": draw,
            "recordsTotal": count,
            "recordsFiltered": count
        }

    return json.dumps(data)

