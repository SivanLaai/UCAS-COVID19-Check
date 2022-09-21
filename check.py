"""
author: Les1ie, SivanLaai
mail: me@les1ie.com, lyhhap@163.com
license: CC BY-NC-SA 3.0
"""

import pytz
import requests
from datetime import datetime
import base64
import configparser

s = requests.Session()

def read_config():
    user = ""    # sep账号
    passwd = ""   # sep密码 在setting里面填写加密的密文
    api_key = ""  # server酱的api，填了可以微信通知打卡结果，不填没影响
    config = configparser.ConfigParser()
    config.read('setting.ini')
    if 'username' in config['DEFAULT']:
        user = config['DEFAULT']['username']
    if 'passwd' in config['DEFAULT']:
        passwd = str(base64.b64decode(config['DEFAULT']['passwd']), 'utf-8')
    if 'api_key' in config['DEFAULT']:
        api_key = config['DEFAULT']['api_key']
    return user, passwd, api_key

user, passwd, api_key = read_config()

def login(s: requests.Session, username, password):
    # r = s.get(
    #     "https://app.ucas.ac.cn/uc/wap/login?redirect=https%3A%2F%2Fapp.ucas.ac.cn%2Fsite%2FapplicationSquare%2Findex%3Fsid%3D2")
    # print(r.text)
    payload = {
        "username": username,
        "password": password
    }
    r = s.post("https://app.ucas.ac.cn/uc/wap/login/check", data=payload)

    # print(r.text)
    if r.json().get('m') != "操作成功":
        print(r.text)
        print("登录失败")
        if api_key:
            message(api_key, "登录失败", "")
        exit(1)


def get_daily(s: requests.Session):
    daily = s.get("https://app.ucas.ac.cn/ucasncov/api/default/daily?xgh=0&app_id=ucas")
    # info = s.get("https://app.ucas.ac.cn/ncov/api/default/index?xgh=0&app_id=ucas")
    j = daily.json()
    d = j.get('d', None)
    if d:

        return daily.json()['d']
    else:
        print("获取昨日信息失败")
        if api_key:
            message(api_key, "获取昨日信息失败", "")
        exit(1)


def submit(s: requests.Session, old: dict):
    new_daily = {
        "id": old["id"],
        "uid": old["uid"],
        "date": datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d"),
        "jzdz": old["jzdz"],
        "zrzsdd": old["zrzsdd"],
        "sfzx": "1", # 1 是
        "szgj": old["szgj"],
        "szdd": old["szdd"],
        "dqszdd": old["dqszdd"],
        "address": "北京市怀柔区",
        "area": "怀柔区",
        "province": "北京市",
        "city": old["city"],
        "geo_api_info": "{\"address\":\"北京市怀柔区\",\"details\":\"怀北镇中国科学院大学(雁栖湖校区)学园壹中国科学院大学雁栖湖校区西区\",\"province\":{\"label\":\"北京市\",\"value\":\"\"},\"city\":{\"label\":\"\",\"value\":\"\"},\"area\":{\"label\":\"怀柔区\",\"value\":\"\"}}",
        "szgj_api_info": old["szgj_api_info"],
        "szgj_select_info": old["szgj_select_info"],
        "created": old["created"],
        "dqsfzzgfxdq": old["dqsfzzgfxdq"],
        "zgfxljs": old["zgfxljs"],
        "tw": old["tw"],
        "sffrzz": old["sffrzz"],
        "dqqk1": old["dqqk1"],
        "dqqk1qt": old["dqqk1qt"],
        "dqqk2": old["dqqk2"],
        "dqqk2qt": old["dqqk2qt"],
        "sfjshsjc": "1", # 是否核酸检测 1 - 是 0 - 否
        "dyzymjzqk": old["dyzymjzqk"],
        "dyzjzsj": old["dyzjzsj"],
        "dyzwjzyy": old["dyzwjzyy"],
        "dezymjzqk": old["dezymjzqk"],
        "dezjzsj": old["dezjzsj"],
        "dezwjzyy": old["dezwjzyy"],
        "dszymjzqk": old["dszymjzqk"],
        "dszjzsj": old["dszjzsj"],
        "dszwjzyy": old["dszwjzyy"],
        "gtshryjkzk": old["gtshryjkzk"],
        "extinfo": old["extinfo"],
        "created_uid": old["created_uid"],
        "todaysfhsjc": "",
        "is_daily": old["is_daily"],
        "geo_api_infot": "{\"address\":\"北京市怀柔区\",\"details\":\"怀北镇中国科学院大学(雁栖湖校区)学园壹中国科学院大学雁栖湖校区西区\",\"province\":{\"label\":\"北京市\",\"value\":\"\"},\"city\":{\"label\":\"\",\"value\":\"\"},\"area\":{\"label\":\"怀柔区\",\"value\":\"\"}}",
        "old_szdd": old["old_szdd"],
        "old_city": "{\"address\":\"北京市怀柔区\",\"details\":\"怀北镇中国科学院大学(雁栖湖校区)学园壹中国科学院大学雁栖湖校区西区\",\"province\":{\"label\":\"北京市\",\"value\":\"\"},\"city\":{\"label\":\"\",\"value\":\"\"},\"area\":{\"label\":\"怀柔区\",\"value\":\"\"}}",
        "number": old["number"],
        "realname": old["realname"],
        'app_id': 'ucas',
    }

    r = s.post("https://app.ucas.ac.cn/ucasncov/api/default/save", data=new_daily)
    print("提交信息:", new_daily)
    # print(r.text)
    result = r.json()
    if result.get('m') == "操作成功":
        print("打卡成功")
        if api_key:
            message(api_key, "每天打卡成功", new_daily)
    else:
        print("打卡失败，错误信息: ", r.json().get("m"))
        if api_key:
            message(api_key, result.get('m'), new_daily)


def message(key, title, body):
    """
    微信通知打卡结果
    """
    msg_url = "https://sc.ftqq.com/{}.send?text={}&desp={}".format(key, title, body)
    requests.get(msg_url)


if __name__ == "__main__":
    print(datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S %Z"))
    login(s, user, passwd)
    yesterday = get_daily(s)
    submit(s, yesterday)
