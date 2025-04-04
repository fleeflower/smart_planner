import os
import re

from data_structure.Task import Task
from data_structure.Task import StaticTask
import datetime
import json
import requests
get_from_file=True
get_from_web=False
cookies = {
    'route': 'ad5adf69d86a66008f20cbfbb599eb2e',
    'GS_SESSIONID': '3e8fe2045c4ee1b8e0c28266236dc067',
    'EMAP_LANG': 'zh',
    'THEME': 'indigo',
    '_WEU': '_FPJX3V4WDhAUAleICL_hXwyQyPL1Xjgt0kUkcobbcQM3Eqlu3xkvep4AsCz26iSSZ149k714OQfb8WHsMI1xYg4dJjAo8kyM4vmK2HsD8LqKHwa11NpkuQE26eCcNZgg7DJBUfa7E*YY9bm*qrec7lINpyf1JVMugylVq_d0kQemJp1XI*ygDYu_1ME8szWnxH*6ll8mbP2RZJ7lrqDDciFzqRnqcbT',
    '_ga': 'GA1.1.1217582223.1742092774',
    '_ga_4CSM3ZYBN3': 'GS1.1.1742092774.1.0.1742092994.0.0.0',
    'amp.locale': 'zh_CN',
    'asessionid': '28e035f3-474a-406d-9432-2d5f81ec13f7',
    'iPlanetDirectoryPro': 'ITb1L6fcfCildtwWN2shpM',
    'JSESSIONID': 'o_oBOzfZbdcGnxPpxDoewQEnizfAXFoc9F3v_yRPr7oWufP0Wve-!-14817976',
}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://ehall.seu.edu.cn',
    'Referer': 'https://ehall.seu.edu.cn/jwapp/sys/wdkb/*default/index.do?t_s=1743777380126&EMAP_LANG=zh&THEME=indigo&amp_sec_version_=1&gid_=NEtFZmV6N0dYeWRCZjJDdFp2bU1RRHNWQm5VU3BsODhnd0pGcmZLTnhkOG8zWVF2VWZtYThoeFNGSXdzWmsya01mZkh5WTdBeDlYVlJCVHhzNkxLVlE9PQ',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': 'route=ad5adf69d86a66008f20cbfbb599eb2e; GS_SESSIONID=3e8fe2045c4ee1b8e0c28266236dc067; EMAP_LANG=zh; THEME=indigo; _WEU=_FPJX3V4WDhAUAleICL_hXwyQyPL1Xjgt0kUkcobbcQM3Eqlu3xkvep4AsCz26iSSZ149k714OQfb8WHsMI1xYg4dJjAo8kyM4vmK2HsD8LqKHwa11NpkuQE26eCcNZgg7DJBUfa7E*YY9bm*qrec7lINpyf1JVMugylVq_d0kQemJp1XI*ygDYu_1ME8szWnxH*6ll8mbP2RZJ7lrqDDciFzqRnqcbT; _ga=GA1.1.1217582223.1742092774; _ga_4CSM3ZYBN3=GS1.1.1742092774.1.0.1742092994.0.0.0; amp.locale=zh_CN; asessionid=28e035f3-474a-406d-9432-2d5f81ec13f7; iPlanetDirectoryPro=ITb1L6fcfCildtwWN2shpM; JSESSIONID=o_oBOzfZbdcGnxPpxDoewQEnizfAXFoc9F3v_yRPr7oWufP0Wve-!-14817976',
}


def switch_mode(mode:str)->None:
    global get_from_file,get_from_web
    if mode=="file":
        get_from_file=True
        get_from_web=False
    elif mode=="web":
        get_from_file=False
        get_from_web=True
    else:
        raise ValueError("Invalid mode")
def calculate_week_number(start_date_str):
    """
    :param start_date_str:
    :return:
    """
    start_date_str = start_date_str.split()[0]
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    current_date = datetime.datetime.now()
    delta = current_date - start_date
    week_number = (delta.days // 7) + 1
    return week_number


import datetime


def get_week_dates(start_date_str, week_num):
    """
    :param start_date_str: 学期开始日期字符串 (格式：YYYY-MM-DD)
    :param week_num: 要获取的第几周
    :return: 该周的起始日期和结束日期 (datetime.date 元组)
    """
    start_date_str = start_date_str.split()[0]
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
    start_of_week = start_date + datetime.timedelta(days=(week_num - 1) * 7)
    end_of_week = start_of_week + datetime.timedelta(days=6)
    return start_of_week, end_of_week


def get_config_list()->dict:
    if os.path.exists("config.json"):
        with open("config.json") as file:
            return json.load(file)
    else:
        data = {
            'XN': '2024-2025',
            'XQ': '3',
        }
        response = requests.post(
            'https://ehall.seu.edu.cn/jwapp/sys/bykbseuMobile/modules/wdkb/cxxljc.do',
            cookies=cookies,
            headers=headers,
            data=data,
        )
        data = {}
        json_data = json.loads(response.text)
        data['when_semester_start'] = json_data['datas']['cxxljc']['rows'][0]['XQKSRQ']
        response = requests.get(
            'https://ehall.seu.edu.cn/jwapp/sys/bykbseuMobile/modules/wdkb/cxjcsj.do',
            cookies=cookies,
            headers=headers,
        )
        json_data = json.loads(response.text)
        DM_list = {}
        for row in json_data['datas']['cxjcsj']['rows']:
            timelist = {}
            timelist['start'] = row['KSSJ']
            timelist['end'] = row['JSSJ']
            DM_list[row['DM']] = timelist
        data['DM_list'] = DM_list
        with open("config.json", "w") as file:
            json.dump(data, file)
        return data

def is_today(start_date:datetime.datetime, end_date:datetime.datetime,circle_in_week:int,circle:str)->bool:
    """
    计算是否在规定时间内，或者循环任务是否在今天，或者是否是规定的星期几，返回布尔值
    :param start_date:
    :param end_date:
    :param circle_in_week:
    :param circle:
    :return:
    """
    if start_date.date() <= datetime.datetime.now().date() <= end_date.date():
        if circle_in_week is not None and circle is not None:
            if datetime.datetime.now().weekday() in circle_in_week:
                return True
            if datetime.datetime.today() - start_date.date()//circle == 0:
                return True
        else:
            return True
    return False



def get_task_list()->list[Task]:
    pass
def get_class_list()->list[StaticTask]:
    if get_from_web:
        config_list = get_config_list()
        data = '*order=%2BKSJC&XNXQDM=2024-2025-3&SKZC=6'

        response = requests.post(
            'https://ehall.seu.edu.cn/jwapp/sys/wdkb/modules/xskcb/xskcb.do',
            cookies=cookies,
            headers=headers,
            data=data,
        )
        json_data = json.loads(response.text)
        task_list = []
        for row in json_data['datas']['xskcb']['rows']:
            # if row['SKXQ'] == datetime.datetime.weekday(datetime.datetime.now())+1:
            start_week, end_week = re.findall(r'\d+', row['ZCMC'])
            task_list.append(StaticTask(start=datetime.datetime.strptime(config_list['DM_list'][str(row['KSJC'])]['start'], '%H:%M').time(), end=datetime.datetime.strptime(config_list['DM_list'][str(row['JSJC'])]['end'],'%H:%M').time(), name=row['KCM'],start_date=get_week_dates(config_list['when_semester_start'],int(start_week))[0],end_date=get_week_dates(config_list['when_semester_start'],int(end_week))[1],circle_in_week=row['SKXQ']))
        with open("test_list.json", "w") as f:
            json.dump([{
                'start': task.start.isoformat(),
                'end': task.end.isoformat(),
                'name': task.name,
                'start_date': task.start_date.strftime('%Y-%m-%d'),
                'end_date': task.end_date.strftime('%Y-%m-%d'),
                'circle_in_week': task.circle_in_week,
                'circle': task.circle,
                'is_fine_for_task': task.is_fine_for_task
            } for task in task_list], f, ensure_ascii=False)
        return task_list
    if get_from_file:
        with open("task_list.json") as file:
            task_list=json.load(file)
            return [StaticTask(task['start'], task['end'], task['name']
                               , other_detail=task['other_info'] if 'other_info' in task else None
                               , end_date=task['end_date'] if 'end_date' in task else datetime.datetime.today()
                               , start_date=task['start_date'] if 'start_date' in task else datetime.datetime.today()
                               , circle=task['circle'] if 'circle' in task else None
                               , circle_in_week=task['circle_in_week'] if 'circle_in_week' in task else None
                               , is_fine_for_task=task['is_fine_for_task'] if 'is_fine_for_task' in task else False)
                    for task in task_list if is_today(start_date=datetime.datetime.strptime(task['start_date'], '%Y-%m-%d'), end_date=datetime.datetime.strptime(task['end_date'], '%Y-%m-%d'), circle_in_week=task['circle_in_week'], circle=task['circle'])]

if __name__ == '__main__':
    switch_mode("web")
    datas=get_class_list()
    for data in datas:
        print(data)
