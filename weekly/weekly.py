#!/usr/bin/env python
# coding=utf8

from flask import Flask
from functools import wraps
from flask import redirect
from flask import url_for
from flask import request
from flask import render_template
from flask import session
from flask import jsonify
from flask import send_from_directory
import sqlite3
import hashlib
import os
import xlwt
import datetime
import decimal

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)
app.secret_key = '\x9a{R`\x03i\xba\xc7\x87O\x1b\xf5Zf\xeb\xb8\x89\x10x=\x98\x8a\xc19'


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        username = session.get('username')
        if username:
            return func(*args, **kwargs)
        return redirect(url_for('login'))
    return wrapper


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        session['username'] = username
        return redirect('/')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@authenticate
def index():
    username = session.get('username')

    startdate = None
    enddate = None
    items = None
    date = None
    num = None

    dbpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'weekly.db')
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    try:
        if request.method == 'GET':
            sql = 'SELECT id, next_start, next_end FROM t_weekly WHERE username="%s" ORDER BY rowid DESC;' % username
            cur.execute(sql)
            item = cur.fetchone()
            if item:
                startdate = item[1]
                enddate = item[2]
                sql = 'SELECT * FROM t_weekly_plan WHERE id="%s"' % item[0]
                cur.execute(sql)
                items = cur.fetchall()
        else:
            date = request.form['date']
            num = request.form['num']
            sql = 'SELECT id, current_start, current_end FROM t_weekly\
                   WHERE username="%s" AND "date"="%s" AND num="%s"' % (username, date, num)
            cur.execute(sql)
            item = cur.fetchone()
            if item:
                startdate = item[1]
                enddate = item[2]
                sql = 'SELECT * FROM t_weekly_finished WHERE id="%s"' % item[0]
                cur.execute(sql)
                items = cur.fetchall()
    except Exception, e:
        print e.message
    finally:
        cur.close()
        conn.close()

    return render_template('weekly.html', username=username, date=date, num=num, startdate=startdate, enddate=enddate, items=items)


@app.route('/save', methods=['POST'])
@authenticate
def save():
    json_data = request.json
    print json_data
    try:
        add_to_db(json_data)
    except Exception, e:
        return jsonify({'ret': False, 'err': e.message})
    return jsonify({'ret': True})


@app.route('/add', methods=['POST'])
@authenticate
def add():
    json_data = request.json
    print json_data
    try:
        add_to_db(json_data)
        filename = create_excel(json_data)
    except Exception, e:
        return jsonify({'ret': False, 'err': e.message})
    return jsonify({'ret': True, 'filename': filename})


@app.route('/download', methods=['GET'])
@authenticate
def download():
    filename = request.args['filename']
    dirname = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'excel')
    return send_from_directory(dirname,
                               filename,
                               mimetype='application/vnd.ms-excel',
                               as_attachment=True,
                               attachment_filename=filename)


def create_excel(json_data):
    date = json_data['date']
    num = json_data['num']
    current_start = json_data['current_start']
    current_end = json_data['current_end']
    next_start = json_data['next_start']
    next_end = json_data['next_end']

    finished = json_data['finished']
    unfinished = json_data['unfinished']
    plan = json_data['plan']

    username = session.get('username')

    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    # borders.left_colour = 0x0
    # borders.right_colour = 0x0
    # borders.top_colour = 0x0
    # borders.bottom_colour = 0x0

    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    alignment.vert = xlwt.Alignment.VERT_CENTER
    alignment.wrap = xlwt.Alignment.WRAP_AT_RIGHT

    gary_pattern = xlwt.Pattern()
    gary_pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    gary_pattern.pattern_fore_colour = 0x16

    yellow_pattern = xlwt.Pattern()
    yellow_pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    yellow_pattern.pattern_fore_colour = 0x0d

    orange_pattern = xlwt.Pattern()
    orange_pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    orange_pattern.pattern_fore_colour = 0x34

    green_pattern = xlwt.Pattern()
    green_pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    green_pattern.pattern_fore_colour = 0x2a

    title_font = xlwt.Font()
    title_font.name = u'微软雅黑'
    title_font.height = 360
    title_alignment = xlwt.Alignment()
    title_alignment.vert = xlwt.Alignment.VERT_CENTER
    title_style = xlwt.XFStyle()
    title_style.font = title_font
    title_style.borders = borders
    title_style.alignment = title_alignment

    title2_font = xlwt.Font()
    title2_font.name = u'微软雅黑'
    title2_font.height = 240
    title2_font.bold = True
    title2_style = xlwt.XFStyle()
    title2_style.font = title2_font
    title2_style.borders = borders
    title2_style.alignment = alignment
    title2_style.pattern = gary_pattern

    title3_font = xlwt.Font()
    title3_font.name = u'微软雅黑'
    title3_font.height = 220
    title3_font.bold = True
    title3_style = xlwt.XFStyle()
    title3_style.font = title3_font
    title3_style.borders = borders
    title3_style.alignment = alignment
    title3_style.pattern = gary_pattern

    text_font = xlwt.Font()
    text_font.name = u'微软雅黑'
    text_font.height = 200
    text_style = xlwt.XFStyle()
    text_style.font = text_font
    text_style.borders = borders
    text_style.alignment = alignment

    date_style = xlwt.XFStyle()
    date_style.font = text_font
    date_style.borders = borders
    date_style.alignment = alignment

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')
    ws.row(0).height_mismatch = True
    ws.row(0).height = 1000
    ws.write_merge(0, 0, 0, 19, u' '*50+u'研发部个人工作周报', title_style)
    ws.write_merge(1, 2, 0, 0, u'姓名', title2_style)

    ws.row(1).height_mismatch = True
    ws.row(1).height = 700

    title2_style.pattern = yellow_pattern
    tmp_date = datetime.datetime.strptime(current_start, '%Y-%m-%d')
    current_start = tmp_date.strftime('%Y年%m月%d日')
    tmp_date = datetime.datetime.strptime(current_end, '%Y-%m-%d')
    current_end = tmp_date.strftime('%Y年%m月%d日')
    ws.write_merge(1, 1, 1, 7, u'本周完成工作（'+current_start+u'—'+current_end+u'）', title2_style)

    title2_style.pattern = orange_pattern
    ws.write_merge(1, 1, 8, 13, u'本周按计划未完成的工作', title2_style)

    title2_style.pattern = green_pattern
    tmp_date = datetime.datetime.strptime(next_start, '%Y-%m-%d')
    next_start = tmp_date.strftime('%Y年%m月%d日')
    tmp_date = datetime.datetime.strptime(next_end, '%Y-%m-%d')
    next_end = tmp_date.strftime('%Y年%m月%d日')
    ws.write_merge(1, 1, 14, 19, u'下周工作计划（'+next_start+u'—'+next_end+u'）', title2_style)

    ws.row(2).height_mismatch = True
    ws.row(2).height = 800

    ws.col(1).width = 1000
    ws.col(2).width = 6000
    ws.col(3).width = 4000
    ws.col(4).width = 4000
    ws.col(5).width = 4000
    ws.col(6).width = 3000
    ws.col(7).width = 4000
    ws.write(2, 1, u'编号', title3_style)
    ws.write(2, 2, u'本周完成的工作', title3_style)
    ws.write(2, 3, u'工作类型', title3_style)
    ws.write(2, 4, u'实际开始时间', title3_style)
    ws.write(2, 5, u'实际完成时间', title3_style)
    ws.write(2, 6, u'实际投入工时（h）', title3_style)
    ws.write(2, 7, u'实际提交成果物', title3_style)

    ws.col(8).width = 1000
    ws.col(9).width = 6000
    ws.col(10).width = 4000
    ws.col(11).width = 4000
    ws.col(12).width = 4000
    ws.col(13).width = 4000
    ws.write(2, 8, u'编号', title3_style)
    ws.write(2, 9, u'未完成工作', title3_style)
    ws.write(2, 10, u'实际进展', title3_style)
    ws.write(2, 11, u'原因说明', title3_style)
    ws.write(2, 12, u'计划完成时间', title3_style)
    ws.write(2, 13, u'所需支持', title3_style)

    ws.col(14).width = 1000
    ws.col(15).width = 6000
    ws.col(16).width = 4000
    ws.col(17).width = 4000
    ws.col(18).width = 3000
    ws.col(19).width = 4000
    ws.write(2, 14, u'编号', title3_style)
    ws.write(2, 15, u'计划工作内容', title3_style)
    ws.write(2, 16, u'计划开始时间', title3_style)
    ws.write(2, 17, u'计划完成时间', title3_style)
    ws.write(2, 18, u'计划投入工时（h）', title3_style)
    ws.write(2, 19, u'计划提交成果物', title3_style)

    max_len = 0
    if finished and max_len < len(finished):
        max_len = len(finished)
    if unfinished and max_len < len(unfinished):
        max_len = len(unfinished)
    if plan and max_len < len(plan):
        max_len = len(plan)

    if finished:
        for i in range(0, max_len):
            r = i+3
            c = 1
            if i < len(finished):
                item = finished[i]
                ws.write(r, c+0, i+1, text_style)
                ws.write(r, c+1, '['+item['project']+']'+item['content'], text_style)
                ws.write(r, c+2, item['type'], text_style)

                startdate = item['startdate']
                tmp_date = datetime.datetime.strptime(startdate, '%Y-%m-%d')
                startdate = tmp_date.strftime('%Y.%m.%d')
                enddate = item['enddate']
                tmp_date = datetime.datetime.strptime(enddate, '%Y-%m-%d')
                enddate = tmp_date.strftime('%Y.%m.%d')

                ws.write(r, c+3, startdate, text_style)
                ws.write(r, c+4, enddate, text_style)
                amount = decimal.Decimal('0')
                try:
                    amount = decimal.Decimal(item['amount'])
                except Exception, e:
                    print e
                ws.write(r, c+5, amount, text_style)
                ws.write(r, c+6, item['achievement'], text_style)
            else:
                ws.write(r, c+0, '', text_style)
                ws.write(r, c+1, '', text_style)
                ws.write(r, c+2, '', text_style)
                ws.write(r, c+3, '', text_style)
                ws.write(r, c+4, '', text_style)
                ws.write(r, c+5, '', text_style)
                ws.write(r, c+6, '', text_style)

    if unfinished:
        for i in range(0, max_len):
            r = i+3
            c = 8
            if i < len(unfinished):
                item = unfinished[i]
                ws.write(r, c+0, i+1, text_style)
                ws.write(r, c+1, '['+item['project']+']'+item['content'], text_style)
                ws.write(r, c+2, item['actual'], text_style)
                ws.write(r, c+3, item['reason'], text_style)

                plandate = item['plandate']
                tmp_date = datetime.datetime.strptime(plandate, '%Y-%m-%d')
                plandate = tmp_date.strftime('%Y.%m.%d')

                ws.write(r, c+4, plandate, text_style)
                ws.write(r, c+5, item['support'], text_style)
            else:
                ws.write(r, c+0, '', text_style)
                ws.write(r, c+1, '', text_style)
                ws.write(r, c+2, '', text_style)
                ws.write(r, c+3, '', text_style)
                ws.write(r, c+4, '', text_style)
                ws.write(r, c+5, '', text_style)

    if not unfinished or len(unfinished) == 0:
        ws.write_merge(3, 2+max_len, 8, 13, u'无', text_style)

    if plan:
        for i in range(0, max_len):
            r = i+3
            c = 14
            if i < len(plan):
                item = plan[i]
                ws.write(r, c+0, i+1, text_style)
                ws.write(r, c+1, '['+item['project']+']'+item['content'], text_style)

                startdate = item['startdate']
                tmp_date = datetime.datetime.strptime(startdate, '%Y-%m-%d')
                startdate = tmp_date.strftime('%Y.%m.%d')
                enddate = item['enddate']
                tmp_date = datetime.datetime.strptime(enddate, '%Y-%m-%d')
                enddate = tmp_date.strftime('%Y.%m.%d')

                ws.write(r, c+2, startdate, text_style)
                ws.write(r, c+3, enddate, text_style)
                amount = decimal.Decimal('0')
                try:
                    amount = decimal.Decimal(item['amount'])
                except Exception, e:
                    print e
                ws.write(r, c+4, amount, text_style)
                ws.write(r, c+5, item['achievement'], text_style)
            else:
                ws.write(r, c+0, '', text_style)
                ws.write(r, c+1, '', text_style)
                ws.write(r, c+2, '', text_style)
                ws.write(r, c+3, '', text_style)
                ws.write(r, c+4, '', text_style)
                ws.write(r, c+5, '', text_style)

    for i in range(0, max_len):
        ws.row(i+3).height_mismatch = True
        ws.row(i+3).height = 1200

    if max_len > 1:
        ws.write_merge(3, 2+max_len, 0, 0, username, text_style)
    else:
        ws.write(3, 0, username, text_style)

    savepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'excel')

    tmp_date = datetime.datetime.strptime(date, '%Y-%m')
    date = tmp_date.strftime('%Y年%m月')
    filename = date+u'第'+num+u'周个人工作周报—'+username+u'.xls'

    savepath = os.path.join(savepath, filename)
    wb.save(savepath)
    return filename


def add_to_db(json_data):
    date = json_data['date']
    num = json_data['num']
    current_start = json_data['current_start']
    current_end = json_data['current_end']
    next_start = json_data['next_start']
    next_end = json_data['next_end']

    finished = json_data['finished']
    unfinished = json_data['unfinished']
    plan = json_data['plan']

    username = session.get('username')
    tid = username+date+num
    tid = tid.encode('utf8')
    tid = hashlib.new('md5', tid).hexdigest()

    dbpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'weekly.db')
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    try:
        sql = 'DELETE FROM t_weekly WHERE id="%s"' % tid
        cur.execute(sql)
        sql = 'DELETE FROM t_weekly_finished WHERE id="%s"' % tid
        cur.execute(sql)
        sql = 'DELETE FROM t_weekly_plan WHERE id="%s"' % tid
        cur.execute(sql)
        sql = 'DELETE FROM t_weekly_unfinished WHERE id="%s"' % tid
        cur.execute(sql)

        sql = 'INSERT INTO t_weekly VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
        cur.execute(sql, (tid, username, date, num, current_start, current_end, next_start, next_end))

        if finished:
            for item in finished:
                print item
                sql = 'INSERT INTO t_weekly_finished VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
                cur.execute(sql, (tid,
                                  item['project'],
                                  item['content'],
                                  item['startdate'],
                                  item['enddate'],
                                  item['amount'],
                                  item['achievement'],
                                  item['type']
                                  )
                            )

        if unfinished:
            for item in unfinished:
                print item
                sql = 'INSERT INTO t_weekly_unfinished VALUES (?, ?, ?, ?, ?, ?, ?)'
                cur.execute(sql, (tid,
                                  item['project'],
                                  item['content'],
                                  item['actual'],
                                  item['reason'],
                                  item['plandate'],
                                  item['support']
                                  )
                            )

        if plan:
            for item in plan:
                print item
                sql = 'INSERT INTO t_weekly_plan VALUES (?, ?, ?, ?, ?, ?, ?)'
                cur.execute(sql, (tid,
                                  item['project'],
                                  item['content'],
                                  item['startdate'],
                                  item['enddate'],
                                  item['amount'],
                                  item['achievement']
                                  )
                            )

        conn.commit()
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=80)
