import re
import os
import json

import requests

"""
@Author  : Ray
@Version : 2.0
"""

s = requests.Session()
# cookies序列化文件
COOKIES_FILE_PATH = 'taobao_login_cookies.txt'


class TaoBaoLogin:

    def __init__(self, session):
        """
        帳號登入對象
        :param username: 用戶名
        :param ua: 淘寶的ua參數
        :param TPL_password2: 加密後的密碼
        :return:
        """
        # 檢測是否需要驗證碼的URL
        self.user_check_url = 'https://login.taobao.com/member/request_nick_check.do?_input_charset=utf-8'
        # 驗證淘寶用戶名的密碼URL
        self.verify_password_url = 'https://login.taobao.com/member/login.jhtml'
        # 訪問st碼URL
        self.vst_url = 'https://login.taobao.com/member/vst.htm?st={}'
        # 淘寶個人 主頁
        self.my_taobao_url = 'http://i.taobao.com/my_taobao.htm'

        # 淘寶用戶名
        self.username = 'kazauta1989@gmail.com'
        # 淘寶關鍵參數，包含用戶瀏覽器的訊息
        self.ua = '121#OIMlkpFG3/wlVlIiGBa2lVxY3cYkvujV5yFsxN05PM+0AKiJN3eSlmjYZc8fDujlVmgY+zP5DMtlLVl4foZ5lwlYKarfKuj9LnN9S7LIKMLWA3rJEtj5ll9YOc8fDujllwgY+a/5KM9VOQrJEmD5lwLYAcT+DujVlAqsQmykLlS9D0g6bqRVpSCge6GG9Xb0CcpR/hVhbZseCeHXQtK0bZibnjYSRw744Sk48u/hM2s0CNHLODYF2ZrDnnGKpCD0CZN883BhbZs0CeHXF960C6iDnnx9pXb0C6048u/mC60VMYzaE9UGlZi0aq9IR0mA0goC8QfmiCDLQ7eXfocVC6ibnulSlvOOLSYrvTxjgWF99pz3KekIMufy6TWOLPCjuAjVEg3XcODcId5viAQk+1m+I5hI8ryHgbyFyepyymWyBULlpLdFVTNNday95iDTimN1FbANybqiEfq2CEU+3zf/FOerqf4YUpepvriwyYvaiN5eR+HVNhdS9p7N0qbbyfz9K11xbJchfw5un3vCM7ULpgt1lU5TglRMmbhZ/4eKexyaJvTd3kieqnEeMswD0qiCS4r4iBXsfBtW4i6G31WA2pR9AIsmsT4hr3SLUlnM/Vsq7RdSSB1FG02XTwrp9w0Zadhe6myCrXH/5Zx+zv3DLutTYQMmO94J4DNtLf/ia1vJSVk9+lT9W6R3U0hv1Q+6qu+gPm408z2ERUdjk1/26lNiloWXnuJ5DhpX+FTZibJXRv7ao63+oOj92fQWBnWhSmelcSirwPZo51Ri6TJcA1pt2yC9cXqelU9otIHt0Grbb3G40AC8NQ9zEgkTFvJllf6ZJWtzqdKPd9MT6/BZ0KYhSHzLbbIJGVGBfK1OysS7h8WchaaS4yMQpUyVj7/okV4uAhmLFELuoNRf4nEZvG0+iKPj11oMaQeKrxTBwqDnshYozRFu1LsPcIOnlAnsokp0TNxpb6r2pjCXy7jl01dpvHoIjSOr+arR0/IS6qHpXB9R01wmjEtGHDWKky6SEAXBJR9SwD10bLiFRvgoEc0jq25BSQ3eNlZ0VaCMvISryoeKmE5lJRgtNkDS967ogqRl9SsNhHQLyxOUDSeUMKRVPkUYMOaCY109E95eCg2XYSrlpYm0mTQb9VQUtTvTz3QJ9xLz5fyLXtKTHQn4IEbfD6eYDmdYMqt/RqXF2lnJ2KLWCnDEGHNzQD3svCzek1eXlSA2XS1qIj9VC5btLUDDfw4da+fEmgpCsL29BexFmtrhvgJT2k22FWSb5K/0Zcy='
        self.TPL_password2 = '1102c1dffe03160ab32fc5823b7433b9692153129c594c86a7e1082648b710be50d33109d9f1aefa585ad0ed08d3c6fae6d2c921264e47e99ff45db56b6f216326255167de1f4ace50550ebb196dedee6502c38b9c0c6b810a32d13abbb1b761060535cfde85c55b2e10eaca5a173e90a1ba85f1a257d9b92b505f081ac02b21'

        # 請求超時時間
        self.timeout = 3
        # session對象，用於共享cookies
        self.session = session

        if not self.username:
            raise RuntimeError('請填寫淘寶用戶名稱')

    def _user_check(self):
        """
        第一步，判斷是否需要驗證碼
        檢測帳號是否需要驗證碼
        :return:
        """
        data = {
            'username': self.username,
            'ua': self.ua
        }
        try:
            response = self.session.post(self.user_check_url, data=data, timeout=self.timeout)
            response.raise_for_status()
        except Exception as e:
            print('檢測是否需要驗證碼請求失敗, 原因：')
            raise e
        needcode = response.json()['needcode']
        print('是否需要滑塊驗證：{}'.format(needcode))
        return needcode

    def _verify_password(self):
        """
        第二步，驗證用戶名稱和密碼
        驗證用戶密碼，並獲取st碼申請URL
        :return: 驗證成功返回st碼申請地址
        """
        verify_password_headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://login.taobao.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://login.taobao.com/member/login.jhtml?redirectURL=https%3A%2F%2Fwww.taobao.com%2F'
        }
        verify_password_data = {
            'TPL_username': self.username,
            'ncoToken': 'cffaf3d7783c19b9a0dad44db7c5465d1c1b00af',
            'slideCodeShow': 'false',
            'useMobile': 'false',
            'lang': 'zh_CN',
            'loginsite': 0,
            'newlogin': 0,
            'TPL_redirect_url': 'http://world.taobao.com/',
            'from': 'tb',
            'fc': 'default',
            'style': 'default',
            'keyLogin': 'false',
            'qrLogin': 'true',
            'newMini': 'false',
            'newMini2': 'false',
            'loginType': '3',
            'gvfdcname': '10',
            'gvfdcre': '68747470733A2F2F6C6F67696E2E74616F62616F2E636F6D2F6D656D6265722F6C6F676F75742E6A68746D6C3F73706D3D61323177752E3234313034362D74772E373630373037343436332E31372E3431636162366362474A4A69375526663D746F70266F75743D7472756526726564697265637455524C3D68747470732533412532462532467777772E74616F62616F2E636F6D253246',
            'TPL_password_2': self.TPL_password2,
            'loginASR': '1',
            'loginASRSuc': '1',
            'oslanguage': 'zh-TW',
            'sr': '1440*900',
            'osVer': 'macos|10.145',
            'naviVer': 'chrome|77.038659',
            'osACN': 'Mozilla',
            'osAV': '5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'osPF': 'MacIntel',
            'appkey': '00000000',
            'mobileLoginLink': 'https://login.taobao.com/member/login.jhtml?redirectURL=https://www.taobao.com/&useMobile=true',
            'showAssistantLink': 'true',
            'um_token': 'T71B6053FD08EDB5DEE48D42A87FD8C07D420907B49327544661D104C09',
            'ua': self.ua
        }
        try:
            response = self.session.post(self.verify_password_url, headers=verify_password_headers,
                                         data=verify_password_data,
                                         timeout=self.timeout)
            response.raise_for_status()
            # 獲取申請st碼地址
            # st_token_url = re.search(r'<script src="().*?"></script>', resp.text).group(1)
        except Exception as e:
            print('驗證用戶名和密碼請求失敗, 原因：')
            raise e
        # 提取申請st碼url
        apply_st_url_match = re.search(r'<script src="(.*?)"></script>', response.text)
        # 存在則返回
        if apply_st_url_match:
            print('驗證用戶密碼成功，st碼申請地址：{}'.format(apply_st_url_match.group(1)))
            return apply_st_url_match.group(1)
        else:
            raise RuntimeError('用戶密碼驗證失敗！response:{}'.format(response.text))

    def _apply_st(self):
        """
        第三步，申請st碼
        申請st碼
        :return: st碼
        """
        apply_st_url = self._verify_password()
        try:
            response = self.session.get(apply_st_url)
            response.raise_for_status()
        except Exception as e:
            print('申請st碼請求失敗，原因：')
            raise e
        st_match = re.search(r'"data":{"st":"(.*?)"}', response.text)
        if st_match:
            print('獲取st碼成功，st碼：{}'.format(st_match.group(1)))
            return st_match.group(1)
        else:
            raise RuntimeError('獲取st碼失敗！response：{}'.format(response.text))

    def login(self):
        """
        第四步，登入
        使用st碼登入
        :return:
        """
        # 加載cookies文件
        if self._load_cookies():
            return True
        # 判斷是否需要滑塊驗證
        self._user_check()
        st = self._apply_st()
        headers = {
            'Host': 'login.taobao.com',
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
        }
        try:
            response = self.session.get(self.vst_url.format(st), headers=headers)
            response.raise_for_status()
        except Exception as e:
            print('st碼請求登入，原因：')
            raise e
        # 登入成功，提取跳轉淘寶用戶主頁url
        my_taobao_match = re.search(r'top.location.href = "(.*?)"', response.text)
        if my_taobao_match:
            print('登入淘寶成功，跳轉連接：{}'.format(my_taobao_match.group(1)))
            self._serialization_cookies()
            return True
        else:
            raise RuntimeError('登入失敗！response：{}'.format(response.text))

    def _load_cookies(self):
        # 1、判斷cookies序列化文件是否存在
        if not os.path.exists(COOKIES_FILE_PATH):
            return False
        # 2、加载cookies
        self.session.cookies = self._deserialization_cookies()
        # 3、判断cookies是否過期
        try:
            self.get_taobao_nick_name()
        except Exception as e:
            os.remove(COOKIES_FILE_PATH)
            print('cookies過期，刪除cookies文件！')
            return False
        print('加载淘寶登入cookies成功!!!')
        return True

    def _serialization_cookies(self):
        """
        序列化cookies
        :return:
        """
        cookies_dict = requests.utils.dict_from_cookiejar(self.session.cookies)
        with open(COOKIES_FILE_PATH, 'w+', encoding='utf-8') as file:
            json.dump(cookies_dict, file)
            print('保存cookies文件成功！')

    def _deserialization_cookies(self):
        """
        反序列化cookies
        :return:
        """
        with open(COOKIES_FILE_PATH, 'r+', encoding='utf-8') as file:
            cookies_dict = json.load(file)
            cookies = requests.utils.cookiejar_from_dict(cookies_dict)
            return cookies

    def get_taobao_nick_name(self):
        """
        獲取淘寶暱稱
        :return: 淘寶暱稱
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
        }
        try:
            response = self.session.get(self.my_taobao_url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            print('獲取淘寶主頁請求失敗！原因：')
            raise e
        # 提取淘寶暱稱
        nick_name_match = re.search(r'<input id="mtb-nickname" type="hidden" value="(.*?)"/>', response.text)
        if nick_name_match:
            print('登入淘寶成功，你的用户名是：{}'.format(nick_name_match.group(1)))
            return nick_name_match.group(1)
        else:
            raise RuntimeError('獲取淘寶暱稱失敗！response：{}'.format(response.text))


if __name__ == '__main__':
    ul = TaoBaoLogin(s)
    ul.login()
    ul.get_taobao_nick_name()
