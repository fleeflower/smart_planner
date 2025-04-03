import os
from data_structure.Task import Task
from data_structure.Task import StaticTask
import datetime
import json
import requests
get_from_file=True
get_from_web=False
cookies = {
    'route': 'ad5adf69d86a66008f20cbfbb599eb2e',
    'EMAP_LANG': 'zh',
    'THEME': 'indigo',
    'GS_SESSIONID': '0afe05e236c8e568dabdcbb53f723d3b',
    '_WEU': 'BzL4a_GPS_qNr*1S1YfDlzKnHsvjPNUMCARFM6xEwJQC9LqlA*8OPXlWwp0zQu18vSRum7ov_D8UWpJi4wZvQwSl4al0JeCR7zXkATCs0yR3c*vE9EYs9vrRp2dIokv4gJFT*h75ea915bvh8veRIzp*rhiR5EpSacIbaelknkir57uGCjpUSozEJ*R4M*QooLJjHqUo0llPNfRsS6zBNo..',
    '_ga': 'GA1.1.1217582223.1742092774',
    '_ga_4CSM3ZYBN3': 'GS1.1.1742092774.1.0.1742092994.0.0.0',
    'JSESSIONID': 'xvD6QSKhk8Pv5EFcuoDqNeIBgQkXaW2F7sqLSZKs5_S2qef1cBSt!-517359854',
}

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    'Referer': 'https://ehall.seu.edu.cn/jwapp/sys/bykbseuMobile/*default/index.do?ticket=ST-10064978-Zgecx15hzwkUajQ8mlP88erdjok-ecs-0002',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': 'route=ad5adf69d86a66008f20cbfbb599eb2e; EMAP_LANG=zh; THEME=indigo; GS_SESSIONID=0afe05e236c8e568dabdcbb53f723d3b; _WEU=BzL4a_GPS_qNr*1S1YfDlzKnHsvjPNUMCARFM6xEwJQC9LqlA*8OPXlWwp0zQu18vSRum7ov_D8UWpJi4wZvQwSl4al0JeCR7zXkATCs0yR3c*vE9EYs9vrRp2dIokv4gJFT*h75ea915bvh8veRIzp*rhiR5EpSacIbaelknkir57uGCjpUSozEJ*R4M*QooLJjHqUo0llPNfRsS6zBNo..; _ga=GA1.1.1217582223.1742092774; _ga_4CSM3ZYBN3=GS1.1.1742092774.1.0.1742092994.0.0.0; JSESSIONID=xvD6QSKhk8Pv5EFcuoDqNeIBgQkXaW2F7sqLSZKs5_S2qef1cBSt!-517359854',
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
        data['XQKSRQ'] = json_data['datas']['cxxljc']['rows'][0]['XQKSRQ']
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
        params = {
            'XNXQDM': '2024-2025-3',
            'SKZC': calculate_week_number(config_list['XQKSRQ']),
        }

        response = requests.get(
            'https://ehall.seu.edu.cn/jwapp/sys/bykbseuMobile/modules/wdkb/cxxszhxqkb.do',
            params=params,
            cookies=cookies,
            headers=headers,
        )
        json_data = json.loads(response.text)
        task_list = []
        for row in json_data['datas']['cxxszhxqkb']['rows']:
            if row['SKXQ'] == datetime.datetime.weekday(datetime.datetime.now())+1:
                task_list.append(StaticTask(start=datetime.datetime.strptime(config_list['DM_list'][str(row['KSJC'])]['start'], '%H:%M').time(), end=datetime.datetime.strptime(config_list['DM_list'][str(row['JSJC'])]['end'],'%H:%M').time(), name=row['KCM']))
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
    data=get_class_list()
    print(data)
