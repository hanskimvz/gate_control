import base64, json
import asyncio
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from urllib.error import URLError
from typing import Optional
from config import config_data, update_config, load_config_json
from utils.logger import get_logger

logger = get_logger()

def active_cgi(dev_ip, header = None, authkey='',cgi_str='', port=80):
    """장치에 CGI 명령을 실행하는 함수"""
    url = f'{dev_ip}:{port}/{cgi_str}'
    url = 'http://' + url.replace("//", "/").strip()
    # logger.debug(f"CGI request: {url}")

    try:
        # header가 딕셔너리가 아니거나 빈 문자열이면 None으로 설정
        headers = header if isinstance(header, dict) and header else None
        r = requests.get(url, headers=headers, auth=authkey, timeout=20)
    except Exception as e:
        logger.error(f"{url}: {str(e)}")
        return False
        
    return r.content

async def get_x_token(ip_addr, port=80, userid='admin', userpw='admin'):
    url = f'http://{ip_addr}:{port}/api/v1/user/login'
    data = {
        'username': userid,
        'password': userpw,
    }
    r = requests.post(url, json=data, timeout=20)
    # print (r.json())
    return r.json().get('data').get('token')

async def get_snapshot(cam_name: str = 'main') -> Optional[str]:
    """카메라에서 스냅샷을 가져옴"""
    global config_data
    try:
        cameras = config_data.get('CAMERAS', [])
        # print ("camera_config: ", cameras)
        if cam_name not in cameras:
            logger.error(f"카메라 이름 오류: {cam_name}")
            return None
        
        camera = cameras[cam_name]
        # print ("camera: ", camera)
        port = camera.get('port', 80)
        userid = camera.get('userid', '')
        userpw = camera.get('userpw', '')
        address = camera.get('address', '')
        snapshot_cgi = camera.get('snapshot_cgi', '/nvc-cgi/operator/snapshot.fcgi')
        header = camera.get('header', '')
        
        # url = f"http://{userid}:{userpw}@{address}{snapshot_cgi}"
        # logger.info(f"카메라 주소: {url}")

        rs = active_cgi(address, header=header, authkey=HTTPBasicAuth(userid, userpw), cgi_str=snapshot_cgi, port=port)
        if not rs:
            logger.error(f"카메라 스냅샷 가져오기 실패: {rs}")
            return None


        if header:
            rs = rs.decode('utf-8')
            rs = json.loads(rs)
        #     print (rs['data'][:100])
            img_data =rs.get('data')
            if not img_data:
                x_token = await get_x_token(address, port=port, userid=userid, userpw=userpw)
                print("x_token: ", x_token)
                update_config(f"CAMERAS.{cam_name}.header.X-Token", x_token)
                config_data = load_config_json()

            return f"data:image/jpg;base64,{img_data}"
        
        img_data = base64.b64encode(rs).decode('utf-8')
        return f"data:image/jpg;base64,{img_data}"
        

    except Exception as e:
        logger.error(f"스냅샷 가져오기 실패: {e}", exc_info=True)
        return None


async def put_do(cam_name: str = 'main', secs: int = 0 ) -> bool:
    """디지털 출력 제어 (문 열기, 문 닫기)"""
    cameras = config_data.get('CAMERAS', [])
    # print ("camera_config: ", cameras)
    if cam_name not in cameras:
        logger.error(f"카메라 이름 오류: {cam_name}")
        return None    

    camera = cameras[cam_name]
    port = camera.get('port', 80)
    userid = camera.get('userid', '')
    userpw = camera.get('userpw', '')
    address = camera.get('address', '')
    do_cgi = camera.get('DO_cgi', {})

    if secs == 0:
        cgi = do_cgi.get('on', '')
    elif secs == -1:
        cgi = do_cgi.get('off', '')
    else:
        cgi = do_cgi.get('trig', '')
        cgi = f"{cgi}{secs}"

    # url = f"http://{userid}:{userpw}@{address}/{cgi}"
    # print ("url: ", url)

    try:
        header = camera.get('header', '')
        ret = active_cgi(address, header=header, authkey=HTTPBasicAuth(userid, userpw), cgi_str=cgi, port=port)
        if not ret:
            logger.error(f"DO 제어 실패: {ret}")
            return False
        return True

    except Exception as e:
        logger.error(f"DO 제어 실패: {address} {cgi} {e}", exc_info=True)
        return False



