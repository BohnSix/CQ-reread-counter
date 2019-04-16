from cqhttp import CQHttp
import datetime
import threading
import sqlite3
from apscheduler.schedulers.blocking import BlockingScheduler


def report():
    conn = sqlite3.connect("GroupRecord.db")
    cursor = conn.cursor()
    cursor.execute("SELECT message, times FROM messages ORDER BY times DESC")
    values = cursor.fetchall()
    cursor.close()
    conn.close()

    all_times = 0
    re_times = 0
    for i in values:
        all_times += i[1]
        if i[1] != 1:
            re_times += 1

    msg = '''在过去的24小时内，本群共发发送消息%d条，其中有%条是复读消息。
                    信息密度为%.2f%%.\n\n
                    %s:共复读了%d次。\n
                    %s:共复读了%d次。\n
                    %s:共复读了%d次。\n\n
                    热爱生命，远离复读。真爱时间，从我做起。\n
          '''.format(all_times, re_times, values[0][0], values[0][1],
                     values[1][0], values[1][1], values[2][0], values[2][1])
    bot.send_group_msg(733508010, msg)


bot = CQHttp(api_root='http://127.0.0.1:5700')


@bot.on_message()
def handle_massage(context):
    new_message = context['message']
    bot.send_msg(733508010, "奇怪，应该能发消息呀")

    if context['group_id'] == 733508010:
        conn = sqlite3.connect("GroupRecord.db")
        cursor = conn.cursor()
        cursor.execute("SELECT times FROM messages WHERE message=?", (new_message,))
        values = cursor.fetchall()
        if len(values) == 0:
            cursor.execute("INSERT INTO messages (message, times) values (?, 1)", (new_message,))
        else:
            cursor.execute("UPDATE messages SET times=times+1 WHERE message=?", (new_message,))
        cursor.close()
        conn.commit()
        conn.close()

    return {"reply": None, 'at_sender': False}


bot.run(host='127.0.0.1', port=8080, debug=True)
bot.send_group_msg(733508010, "奇怪，应该能发消息呀")

sched = BlockingScheduler()
sched.add_job(report, 'cron', day_of_week='0-6', hour='22')
sched.start()
