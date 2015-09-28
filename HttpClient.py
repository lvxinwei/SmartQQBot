import cookielib, urllib, urllib2, socket

class HttpClient:
  __cookieFile="cookie.txt"
  __cookie = cookielib.LWPCookieJar(__cookieFile)
  __req = urllib2.build_opener(urllib2.HTTPCookieProcessor(__cookie))
  __req.addheaders = [
    ('Accept', 'application/javascript, */*;q=0.8'),
    ('User-Agent', "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36")
  ]
  urllib2.install_opener(__req)
  def __saveCookie(self):
       self.__cookie.save(self.__cookieFile)
       print open(self.__cookieFile).read()
  def Get(self, url, refer=None):
    print url
    try:
      req = urllib2.Request(url)

      if not (refer is None):
        req.add_header('Referer', refer)
      ret= urllib2.urlopen(req).read()
      self.__saveCookie()
      return ret
    except urllib2.HTTPError, e:
      return e.read()

  def Post(self, url, data, refer=None):
    try:
      req = urllib2.Request(url, urllib.urlencode(data))

      if not (refer is None):
        req.add_header('Referer', refer)
      ret=urllib2.urlopen(req, timeout=180).read()
      self.__saveCookie()
      return ret
    except urllib2.HTTPError, e:
      return e.read()

  def Download(self, url, file):
    output = open(file, 'wb')
    output.write(urllib2.urlopen(url).read())
    output.close()

#  def urlencode(self, data):
#    return urllib.quote(data)

  def getCookie(self, key):
    for c in self.__cookie:
      if c.name == key:
        return c.value
    return ''

  def setCookie(self, key, val, domain):
    ck = cookielib.Cookie(version=0, name=key, value=val, port=None, port_specified=False, domain=domain, domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
    self.__cookie.set_cookie(ck)