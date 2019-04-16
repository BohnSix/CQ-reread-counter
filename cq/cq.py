import random
import sqlite3

from cqhttp import CQHttp
from apscheduler.schedulers.background import BackgroundScheduler


def init():
    conn = sqlite3.connect("Record.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE '937518271' (message varchar(255), times int)")
    cursor.execute("CREATE TABLE '878753509' (message varchar(255), times int)")
    cursor.close()
    conn.close()


def get_report(group_id):
    conn = sqlite3.connect("Record.db")
    cursor = conn.cursor()
    cursor.execute("SELECT message, times FROM {} ORDER BY times DESC".format(group_id))

    values = cursor.fetchall()

    all_times = 0
    re_times = 0
    head = ""
    msg = ""

    for i in values:
        all_times += i[1]
        if i[1] != 1:
            re_times += 1
        if i[1] >= 3:
            msg += "{}:共复读了{}次。\n".format(i[0], i[1])

    msg += "热爱生命，远离复读。珍惜时间，从我做起。"
    if all_times == 0 or re_times == 0:
        msg = ""
    else:
        head = "在过去的24小时内，本群共发送消息{}条，其中有{}条是复读消息。信息密度为{:.2f}%.\n其中：\n\n".format(all_times, re_times,
                                                                                (1 - re_times * 1.0 / all_times) * 100)
    cursor.execute("DELETE FROM " + group_id)
    bot.send_group_msg(group_id=group_id, message=head + msg)

    cursor.close()
    conn.close()


def handler(context, group_id):
    if context['group_id'] == group_id:

        new_message = context['message']

        conn = sqlite3.connect("Record.db")
        cursor = conn.cursor()
        cursor.execute("SELECT times FROM '{}' WHERE message=?".format(group_id), (new_message,))
        values = cursor.fetchall()
        if len(values) == 0:
            cursor.execute("INSERT INTO '{}' (message, times) values (?, 1)".format(group_id), (new_message,))
        else:
            cursor.execute("UPDATE '{}' SET times=times+1 WHERE message=?".format(group_id), (new_message,))
        cursor.close()
        conn.commit()
        conn.close()

    if context['group_id'] == 878753509:
        if random.random() < 0.01:
            return {"reply": new_message, 'at_sender': False}


sched = BackgroundScheduler()


def report():
    get_report(878753509)  # 科协
    get_report(937518271)  # 科创


try:
    init()
except Exception as e:
    pass

bot = CQHttp(api_root='http://127.0.0.1:5700')


@bot.on_message()
def handle_massage(context):
    handler(context, 878753509)
    handler(context, 937518271)

    return {"reply": None, 'at_sender': False}


sched.add_job(report, 'cron', hour='23', minute='55')

sched.start()

bot.run(host='127.0.0.1', port=8080, debug=True)
