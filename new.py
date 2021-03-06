# -*- coding: utf-8 -*-

# Code by Yinzo:        https://github.com/Yinzo
# Origin repository:    https://github.com/Yinzo/SmartQQBot

import random
import time
import datetime
import re
import json
import logging
import os
import pickle
from HttpRequests import *

logging.basicConfig(
    filename='smartqq.log',
    level=logging.DEBUG,
    format='%(asctime)s  %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
)


def get_revalue(html, rex, er, ex):
    v = re.search(rex, html)
    if v is None:
        if ex:
            logging.error(er)
            raise TypeError(er)
        else:
            logging.warning(er)
        return ''
    return v.group(1)


def date_to_millis(d):
    return int(time.mktime(d.timetuple())) * 1000

class QQ:
    def __init__(self):
        self.dataFileName="data.txt"
        self.req = HttpRequests();
        self.friend_list = {}
        self.data={}
        self.data['client_id']= int(random.uniform(111111, 888888))
        self.data['ptwebqq'] = ''
        self.data['psessionid'] = ''
        self.data['selfuin']=''
        self.appid = 0
        self.data['vfwebqq'] = ''
        self.qrcode_path = "./vcode.jpg"  # QRCode保存路径
        self.username = ''
        self.account = 0
    def __saveData(self):
        with open(self.dataFileName, 'w') as f:
             pickle.dump(self.data,f)
        f.close()
    def login_by_qrcode(self):
        logging.info("Requesting the login pages...")
        initurl_html = self.req.get('http://w.qq.com/login.html')
        print initurl_html
        initurl = get_revalue(initurl_html, r'\.src = "(.+?)"', "Get Login Url Error.", 1)
        html = self.req.get(initurl + '0')
        appid = get_revalue(html, r'var g_appid =encodeURIComponent\("(\d+)"\);', 'Get AppId Error', 1)
        sign = get_revalue(html, r'var g_login_sig=encodeURIComponent\("(.*?)"\);', 'Get Login Sign Error', 0)
        js_ver = get_revalue(html, r'var g_pt_version=encodeURIComponent\("(\d+)"\);', 'Get g_pt_version Error', 1)
        mibao_css = get_revalue(html, r'var g_mibao_css=encodeURIComponent\("(.+?)"\);', 'Get g_mibao_css Error', 1)
        star_time = date_to_millis(datetime.datetime.utcnow())
        error_times = 0
        ret = []
        while True:
            error_times += 1
            vcodeUrl='https://ssl.ptlogin2.qq.com/ptqrshow?appid={0}&e=0&l=L&s=8&d=72&v=4'.format(appid)
            self.req.downloadFile(vcodeUrl,self.qrcode_path)
            print "Please scan the downloaded QRCode"

            while True:
                checkLoginUrl='https://ssl.ptlogin2.qq.com/ptqrlogin?webqq_type=10&remember_uin=1&login2qq=1&aid={0}&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=0-0-{1}&mibao_css={2}&t=undefined&g=1&js_type=0&js_ver={3}&login_sig={4}'.format(
                        appid, date_to_millis(datetime.datetime.utcnow()) - star_time, mibao_css, js_ver, sign);
                html = self.req.get(checkLoginUrl,{'Referer':initurl})
                ret = html.split("'")
                print ret
                time.sleep(2)
                if ret[1] in ('0', '65'):  # 65: QRCode 失效, 0: 验证成功, 66: 未失效, 67: 验证中
                    break
            if ret[1] == '0' or error_times > 10:
                break

        if ret[1] != '0':
            return
        print "QRCode scaned, now logging in."

        # 删除QRCode文件
        if os.path.exists(self.qrcode_path):
            os.remove(self.qrcode_path)

        # 记录登陆账号的昵称
        self.username = ret[11]
        url = get_revalue(self.req.get(ret[5]), r' src="(.+?)"', 'Get mibao_res Url Error.', 0)
        if url != '':
            html = self.req.get(url.replace('&amp;', '&'))
            url = get_revalue(html, r'location\.href="(.+?)"', 'Get Redirect Url Error', 1)
            self.req.get(url)
        self.data['ptwebqq'] = self.req.getCookies()['ptwebqq']
        print self.data
        login_error = 1
        ret = {}
        while login_error > 0:
            try:
                html = self.req.post('http://d.web2.qq.com/channel/login2', {
                    'r': '{{"ptwebqq":"{0}","clientid":{1},"psessionid":"{2}","status":"online"}}'.format(self.data['ptwebqq'] ,
                                                                                                          self.data['client_id'] ,
                                                                                                          self.data['psessionid'] )
                }, {'Referer':"http://d.web2.qq.com/proxy.html?v=20030916001&callback=1&id=2"} )
                ret = json.loads(html)
                login_error = 0
            except:
                login_error += 1
                print "login fail, retrying..."
                exit()

        if ret['retcode'] != 0:
            print ret
            return

        self.data['vfwebqq']  = ret['result']['vfwebqq']
        self.data['psessionid']  = ret['result']['psessionid']
        self.data['selfuin'] = ret['result']['uin']
        self.__saveData()

        #print "QQ：{0} login successfully, Username：{1}".format(self.account, self.username)
        print self.username

    def relogin(self, error_times=0):
        if error_times >= 10:
            return False
        try:
            html = self.req.post('http://d.web2.qq.com/channel/login2', {
                'r': '{{"ptwebqq":"{0}","clientid":{1},"psessionid":"{2}","key":"","status":"online"}}'.format(
                    self.data['ptwebqq'] ,
                    self.data['client_id'] ,
                    self.data['psessionid'] )
            } )
            ret = json.loads(html)
            self.data['vfwebqq']  = ret['result']['vfwebqq']
            self.data['psessionid']  = ret['result']['psessionid']
            return True
        except:
            logging.info("login fail, retryng..." + str(error_times))
            return self.relogin(error_times + 1)

    def check_msg(self, error_times=0):
        if error_times >= 5:
            if not self.relogin():
                raise IOError("Account offline.")
            else:
                error_times = 0

        # 调用后进入单次轮询，等待服务器发回状态。
        html = self.req.post('http://d.web2.qq.com/channel/poll2', {
            'r': '{{"ptwebqq":"{1}","clientid":{2},"psessionid":"{0}","key":""}}'.format(self.data['psessionid'] , self.data['ptwebqq'] ,
                                                                                         self.data['client_id'] )
        })

        try:
            if html == "":
                return self.check_msg()
            ret = json.loads(html)
            print ret

            ret_code = ret['retcode']

            if ret_code in (102,):
                logging.info("received retcode: " + str(ret_code) + ": No message.")
                time.sleep(1)
                return

            if ret_code in (103,):
                logging.warning("received retcode: " + str(ret_code) + ": Check error.retrying.." + str(error_times))
                time.sleep(1)
                return self.check_msg(error_times + 1)

            if ret_code in (121,):
                logging.warning("received retcode: " + str(ret_code))
                return self.check_msg(5)

            elif ret_code == 0:
                msg_list = []
                pm_list = []
                sess_list = []
                group_list = []
                notify_list = []
                for msg in ret['result']:
                    ret_type = msg['poll_type']
                    if ret_type == 'message':
                        pm_list.append(PmMsg(msg))
                    elif ret_type == 'group_message':
                        group_list.append(GroupMsg(msg))
                    elif ret_type == 'sess_message':
                        sess_list.append(SessMsg(msg))
                    elif ret_type == 'input_notify':
                        notify_list.append(InputNotify(msg))
                    elif ret_code == 'kick_message':
                        notify_list.append(KickMessage(msg))
                    else:
                        logging.warning("unknown message type: " + str(ret_type) + "details:    " + str(msg))

                group_list.sort(key=lambda x: x.seq)
                msg_list += pm_list + sess_list + group_list + notify_list
                if not msg_list:
                    return
                return msg_list
            elif ret_code == 100006:
                print "POST data error"
                return

            elif ret_code == 116:
                self.data['ptwebqq'] = ret['p']
                self.__saveData()
                return
            else:
                print "unknown retcode " + str(ret_code)
                return
        except ValueError, e:
            print "Check error occured: " + str(e)
            time.sleep(1)
            return self.check_msg(error_times + 1)
        except BaseException, e:
            time.sleep(1)
            return self.check_msg(error_times + 1)
if __name__ =="__main__":
    qq=QQ();
    qq.login_by_qrcode()
    print qq.data
    print qq.uin_to_account(2891802047)
    while True:
        qq.check_msg()



