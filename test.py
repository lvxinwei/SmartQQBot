__author__ = 'lvxinwei'
import cookielib, urllib, urllib2, socket,json
from HttpRequests import *
import pickle,time
with open("data.txt", 'r') as f:
    data=pickle.load(f)
f.close()
req=HttpRequests(True)
reply_content="12345"
tuin=str(2891802047)
psessionid=data['psessionid']
client_id=data['client_id']
fix_content = str(reply_content.replace("\\", "\\\\\\\\").replace("\n", "\\\\n").replace("\t", "\\\\t")).decode("utf-8")
rsp = ""

req_url = "http://d.web2.qq.com/channel/send_buddy_msg2"
data = (
    ('r', '{{"to":{0}, "face":594, "content":"[\\"{4}\\", [\\"font\\", {{\\"name\\":\\"Arial\\", \\"size\\":\\"10\\", \\"style\\":[0, 0, 0], \\"color\\":\\"000000\\"}}]]", "clientid":"{1}", "msg_id":{2}, "psessionid":"{3}"}}'.format(tuin, client_id, "78652",  psessionid, fix_content)),
    ('clientid', client_id),
    ('psessionid', psessionid)
)
while True:
    rsp =req.post(req_url, data)
    rsp_json = json.loads(rsp)
    print rsp_json
    time.sleep(60)
#





