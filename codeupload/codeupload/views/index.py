from flask import Flask, Blueprint, render_template, redirect, request, session
import os
import uuid
from ..utils import helper
import json


ind = Blueprint('ind', __name__)


@ind.before_request
def process_request():
    if not session.get('user_info'):
        return redirect('/login')
    return None


@ind.route("/index", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        data_List = helper.fetch_all("select ctime, line from record where user_id=%s", (session['user_info']['id']),)
        chart_list = []
        for i in data_List:
            p = [i['ctime'].strftime('%m/%d'), int(i['line'])]
            chart_list.append(p)
        chart_list = json.dumps(chart_list)
        return render_template('index.html', chart_list=chart_list)
        # return render_template("test.html")
    date = request.form.get('time')
    
    if not date:
    # if date == str('0'):     这么写实在太垃圾了
        # data_List = helper.fetch_all("select ctime, line from record where user_id=%s", (session['user_info']['id']))
        
        return redirect('/index')
    else:
        data_List = helper.fetch_all("select ctime, line from record where user_id=%s and month(ctime)=%s", (session['user_info']['id'], date))
    chart_list = []
    for i in data_List:
        p = [i['ctime'].strftime('%m/%d'), int(i['line'])]
        chart_list.append(p)
    chart_list = json.dumps(chart_list)
    return render_template('index.html', chart_list=chart_list)


@ind.route('/user_list')
def user_list():
    data_list = helper.fetch_all("select user_id,user,SUM(line) as i from record  left join userinfo on record.user_id=userinfo.id group by user_id ORDER BY  i DESC", [],)
    print(data_list)
    # 找到最大代码量
    maxcode = 0
    for k in data_list:
        if k['i'] > maxcode:
            maxcode = k['i']
    # 找到最大代码量对应用户， 哎 ， mysql as字段 where 好像不能连用，只能是后端来做了
    maxuser = ""
    for k in data_list:
        if str(k['i']) == str(maxcode):
            maxuser = k['user']
    return render_template('user_list.html', data_list=data_list, maxcode=maxcode, maxuser=maxuser)


@ind.route("/detail/<int:nid>")
def detail(nid):
    data_List = helper.fetch_all("select ctime, line from record where user_id=%s", (nid,))
    username = helper.fetch_all("select user from record left join userinfo on record.user_id=userinfo.id where user_id=%s GROUP BY user", (nid,))
    username = json.dumps(username[0]['user'])
    chart_list = []
    for i in data_List:
        p = [i['ctime'].strftime('%m/%d'), int(i['line'])]
        chart_list.append(p)
    chart_list = json.dumps(chart_list)
    return render_template('detail.html', chart_list=chart_list, username=username)


@ind.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template('upload.html')
    file_obj = request.files.get('code')
    if not file_obj:
        return render_template('upload.html')
    name_ext = file_obj.filename.rsplit('.', maxsplit=1)
    if len(name_ext) != 2:
        return "上传zip文件"
    if name_ext[1] != 'zip':
        return "上传zip文件"
    import shutil
    file_path = os.path.join("files", file_obj.filename)
    file_obj.save(file_path)
    target_path = os.path.join('files', str(uuid.uuid4()))
    shutil._unpack_zipfile(file_path, target_path)
    os.remove(file_path)  # 删除zip文件
    total_num = 0
    for bath_path, folder_list, file_list in os.walk(target_path):  # 文件路径， 包含的文件夹， 包含的文件
        for file_name in file_list:
            file_path = os.path.join(bath_path, file_name)
            file_ext = file_path.rsplit('.', maxsplit=1)
            if len(file_ext) != 2:
                continue            # 返回while， for 循环开头
            if file_ext[1] != 'py':
                continue
            file_num = 0
            with open(file_path, 'rb') as f:
                for line in f:
                    line = line.strip()
                    #  stipt 为空时，默认删除空白符（包括'\n', '\r',  '\t',  ' ')
                    if not line:
                        continue
                    if line.startswith(b'#'):
                        continue
                    file_num += 1
            total_num += file_num
            import datetime
            ctime = datetime.date.today()
            data = helper.fetch_one("select id from record where ctime=%s and user_id=%s", (ctime, session['user_info']['id']))
            if data:
                return render_template("ready.html")
            helper.insert("insert into record(line,ctime,user_id)values(%s,%s,%s)",
                          (total_num, ctime, session['user_info']['id']))

            return render_template("seccess.html")









