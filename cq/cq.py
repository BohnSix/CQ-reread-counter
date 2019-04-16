import random

from cqhttp import CQHttp

import sqlite3
from apscheduler.schedulers.blocking import BlockingScheduler

try:
    conn = sqlite3.connect("Record.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE '937518271' (message varchar(255), times int)")
    cursor.execute("CREATE TABLE '878753509' (message varchar(255), times int)")
    values = cursor.fetchall()
    cursor.close()
    conn.close()
except Exception as e:
    pass

sched = BlockingScheduler()


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


@sched.scheduled_job('cron', day_of_week='mon-fri', hour='21', minute='23', second='10')
def report():
    get_report(878753509)  # 科协
    get_report(937518271)  # 科创


bot = CQHttp(api_root='http://127.0.0.1:5700')


@bot.on_message()
def handle_massage(context):
    new_message = context['message']

    if context['group_id'] == 878753509:
        conn = sqlite3.connect("Record.db")
        cursor = conn.cursor()
        cursor.execute("SELECT times FROM '878753509' WHERE message=?", (new_message,))
        values = cursor.fetchall()
        if len(values) == 0:
            cursor.execute("INSERT INTO '878753509' (message, times) values (?, 1)", (new_message,))
        else:
            cursor.execute("UPDATE '878753509' SET times=times+1 WHERE message=?", (new_message,))
        cursor.close()
        conn.commit()
        conn.close()

        if random.random() < 0.142857:
            return {"reply": new_message, 'at_sender': False}

    if context['group_id'] == 937518271:
        conn = sqlite3.connect("Record.db")
        cursor = conn.cursor()
        cursor.execute("SELECT times FROM '937518271' WHERE message=?", (new_message,))
        values = cursor.fetchall()
        if len(values) == 0:
            cursor.execute("INSERT INTO '937518271' (message, times) values (?, 1)", (new_message,))
        else:
            cursor.execute("UPDATE '937518271' SET times=times+1 WHERE message=?", (new_message,))
        cursor.close()
        conn.commit()
        conn.close()

    return {"reply": None, 'at_sender': False}


report()

sched.start()

bot.run(host='47.94.16.227', port=8080)
