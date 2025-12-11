import sys, os, time
import paramiko
import tarfile
import tempfile
import logging
import subprocess
import json
from datetime import datetime

logger = logging.getLogger(__name__)

CONFIG = {
    # 'host': os.getenv('SSH_HOST', '158.179.162.18'),
    'host': os.getenv('SSH_HOST', '192.168.1.251'),
    'username': os.getenv('SSH_USERNAME', 'hanskim'),
    "password": os.getenv('SSH_PASSWORD', 'wjdtjd'),
    # 'private_key': os.getenv('SSH_PRIVATE_KEY_PATH', "/home/hanskim/.ssh/hanskim_oracle2")
    
}

DEST_DIR = "/home/hanskim/GATE/"
# 로컬 프로젝트 디렉토리 (이 스크립트가 있는 위치)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# LOCAL_DIR = SCRIPT_DIR  # frontend 폴더

LOCAL_FILES = {
    'api': os.path.join(SCRIPT_DIR, 'backend', 'api.tar.gz'),
    'web': os.path.join(SCRIPT_DIR, 'frontend', 'dist', 'web.tar.gz'),
    'config': os.path.join(SCRIPT_DIR, 'config', 'config.json'),
    # 'bin': os.path.join(SCRIPT_DIR, "dataserver", 'bin.tar.gz'),
    'nginx_conf': os.path.join(SCRIPT_DIR, 'nginx.gate_control.conf'),
    'service': os.path.join(SCRIPT_DIR, 'gate_control.service')    
}

CONFIG_JSON_PATH = os.path.join(SCRIPT_DIR, 'config', 'config.json')

print (LOCAL_FILES)

def get_build_date():
    """현재 날짜를 YYYYMMDD 형식으로 반환"""
    return datetime.now().strftime("%Y%m%d")

def read_config_json():
    """config.json 파일을 읽어서 반환"""
    try:
        with open(CONFIG_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"config.json 읽기 실패: {e}")
        return None

def write_config_json(config_data):
    """config.json 파일에 데이터를 저장"""
    try:
        with open(CONFIG_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        print(f"✓ config.json 업데이트 완료")
        return True
    except Exception as e:
        print(f"config.json 쓰기 실패: {e}")
        return False

def update_build_info(build_type):
    """
    config.json의 build 정보를 업데이트
    build_type: 'web', 'api' 중 하나
    """
    config = read_config_json()
    if not config:
        return False
    
    if 'build' not in config:
        config['build'] = {}
    
    build_date = get_build_date()
    config['build'][build_type] = build_date
    
    print(f"빌드 정보 업데이트: build.{build_type} = {build_date}")
    return write_config_json(config)

def progress_callback(transferred, total):
    """파일 전송 진행률 표시"""
    percentage = (transferred / total) * 100
    bar_length = 40
    filled_length = int(bar_length * transferred // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    print(f'\r[{bar}] {percentage:.1f}% ({transferred}/{total} bytes)', end='', flush=True)

def sshcmd(ssh, str):
    stdin, stdout, stderr = ssh.exec_command(str)
    lines = stdout.readlines()
    return (''.join(lines))

def ssh_exec_with_status(ssh, command, print_output=True):
    """SSH 명령어 실행 후 return 값과 출력을 반환"""
    print(f"실행: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    
    # 명령어 완료까지 대기
    exit_status = stdout.channel.recv_exit_status()
    
    # 출력 읽기
    output_lines = stdout.readlines()
    error_lines = stderr.readlines()
    
    if print_output:
        if output_lines:
            print("출력:", ''.join(output_lines))
        if error_lines:
            print("에러:", ''.join(error_lines))
    
    return {
        'exit_status': exit_status,
        'output': ''.join(output_lines),
        'error': ''.join(error_lines),
        'success': exit_status == 0
    }

def find_and_remove_pycache(ssh, base_path):
    """지정된 경로 아래의 모든 __pycache__ 폴더를 찾아서 삭제"""
    print(f"__pycache__ 폴더 검색 및 삭제 중: {base_path}")
    
    # find 명령어로 모든 __pycache__ 폴더 찾기
    find_cmd = f'find {base_path} -type d -name "__pycache__"'
    result = ssh_exec_with_status(ssh, find_cmd, print_output=False)
    
    if not result['success']:
        print(f"__pycache__ 폴더 검색 실패: {result['error']}")
        return
    
    pycache_dirs = result['output'].strip().split('\n')
    pycache_dirs = [dir.strip() for dir in pycache_dirs if dir.strip()]
    
    if not pycache_dirs:
        print("삭제할 __pycache__ 폴더가 없습니다.")
        return
    
    print(f"발견된 __pycache__ 폴더 {len(pycache_dirs)}개:")
    for dir_path in pycache_dirs:
        print(f"  - {dir_path}")
    
    # 각 __pycache__ 폴더 삭제
    for dir_path in pycache_dirs:
        rm_cmd = f'rm -rf "{dir_path}"'
        rm_result = ssh_exec_with_status(ssh, rm_cmd, print_output=False)
        if rm_result['success']:
            print(f"삭제 완료: {dir_path}")
        else:
            print(f"삭제 실패: {dir_path} - {rm_result['error']}")

# def release_bin(ssh):
#     print("\n----------------------------------release bin----------------------------------")
#     print(f"로컬 디렉토리: {LOCAL_FILES['bin']}")

#     # build 정보 업데이트
#     print("\nbuild.bin 정보 업데이트 중...")
#     if not update_build_info('bin'):
#         print("경고: build 정보 업데이트 실패")

#     # 2. 빌드된 dist 폴더를 tar.gz로 압축
#     print("\nbin 파일 압축 중...")
#     try:
#         with tarfile.open(LOCAL_FILES['bin'], 'w:gz') as tar:
#             tar.add(os.path.dirname(LOCAL_FILES['bin']), arcname="bin")
#         print(f"✓ 압축 완료: {LOCAL_FILES['bin']}")
#     except Exception as e:
#         print(f"압축 실패: {e}")
#         return   
    
#     print("\nconfig 파일 압축 중...")
#     try:
#         with tarfile.open(LOCAL_FILES['config'], 'w:gz') as tar:
#             tar.add(os.path.dirname(LOCAL_FILES['config']), arcname="config")
#         print(f"✓ 압축 완료: {LOCAL_FILES['config']}")
#     except Exception as e:
#         print(f"압축 실패: {e}")
#         return   
#     print ("파일 전송 중...")
#     try:
#         sftp = ssh.open_sftp()
#         sftp.put(LOCAL_FILES['bin'], os.path.join(DEST_DIR, 'bin.tar.gz'), callback=progress_callback)
#         sftp.put(LOCAL_FILES['config'], os.path.join(DEST_DIR, 'config.tar.gz'), callback=progress_callback)
#         print()  # 진행률 표시 후 줄바꿈
#         print("✓ 파일 전송 완료")
#         sftp.close()
#     except Exception as e:
#         print(f"파일 전송 실패: {e}")
#         return

#     print("\n원격 서버에서 압축 해제 중...")
#     extract_cmd = f"cd {DEST_DIR} && tar xzf {os.path.join(DEST_DIR, 'bin.tar.gz')} && rm -f {os.path.join(DEST_DIR, 'bin.tar.gz')}"
#     result = ssh_exec_with_status(ssh, extract_cmd, print_output=False)
#     if not result['success']:
#         print(f"압축 해제 실패 (exit code: {result['exit_status']})")
#         print(f"에러: {result['error']}")
#         return
#     print("✓ bin압축 해제 완료")

#     extract_cmd = f"cd {DEST_DIR} && tar xzf {os.path.join(DEST_DIR, 'config.tar.gz')} && rm -f {os.path.join(DEST_DIR, 'config.tar.gz')}"
#     result = ssh_exec_with_status(ssh, extract_cmd, print_output=False)
#     if not result['success']:
#         print(f"압축 해제 실패 (exit code: {result['exit_status']})")
#         print(f"에러: {result['error']}")
#         return
#     print("✓ config 압축 해제 완료")

def release_api(ssh):
    print("\n----------------------------------release api----------------------------------")
    print(f"로컬 디렉토리: {LOCAL_FILES['api']}")

    # build 정보 업데이트
    print("\nbuild.api 정보 업데이트 중...")
    if not update_build_info('api'):
        print("경고: build 정보 업데이트 실패")

    try:
        with tarfile.open(LOCAL_FILES['api'], 'w:gz') as tar:
            tar.add(os.path.dirname(LOCAL_FILES['api']), arcname="api")
        print(f"✓ 압축 완료: {LOCAL_FILES['api']}")
    except Exception as e:
        print(f"압축 실패: {e}")
        return        


    try:
        sftp = ssh.open_sftp()
        sftp.put(LOCAL_FILES['api'], os.path.join(DEST_DIR, 'api.tar.gz'), callback=progress_callback)
        print()
        print(LOCAL_FILES['config'], "->", os.path.join(DEST_DIR, 'config','config.json') )
        sftp.put(LOCAL_FILES['config'], os.path.join(DEST_DIR, 'config','config.json'), callback=progress_callback)
        print()  # 진행률 표시 후 줄바꿈
        print("✓ 파일 전송 완료")
        sftp.close()
    except Exception as e:
        print(f"파일 전송 실패: {e}")
        return

    print("\n[5/5] 원격 서버에서 압축 해제 중...")
    extract_cmd = f"cd {DEST_DIR} && tar xzf {os.path.join(DEST_DIR, 'api.tar.gz')} && rm -f {os.path.join(DEST_DIR, 'api.tar.gz')}"
    result = ssh_exec_with_status(ssh, extract_cmd, print_output=False)
    if not result['success']:
        print(f"압축 해제 실패 (exit code: {result['exit_status']})")
        print(f"에러: {result['error']}")
        return
    print("✓ 압축 해제 완료")

def run_web_build():
    # 기존 tar 파일이 있으면 삭제
    print("\n[1/5] 로컬에서 npm 빌드 실행 중...")
    
    # build 정보 업데이트
    print("\nbuild.web 정보 업데이트 중...")
    if not update_build_info('web'):
        print("경고: build 정보 업데이트 실패")
    
    work_dir = os.path.dirname(os.path.dirname(LOCAL_FILES['web']))
    print(f"실행 디렉토리: {work_dir}")
    try:
        result = subprocess.run(
            ["/usr/bin/npm", "run", "build"],
            cwd=work_dir,
            capture_output=True,
            text=True,
            shell=False  # 리스트 형태 명령어는 shell=False 사용
        )
        
        # stdout과 stderr 모두 출력
        if result.stdout:
            print("=== 빌드 출력 ===")
            print(result.stdout[-1000:])  # 마지막 1000자 출력
        
        if result.returncode != 0:
            print(f"\n❌ 빌드 실패 (exit code: {result.returncode})")
            if result.stderr:
                print("=== 에러 메시지 ===")
                print(result.stderr)
            return
            
        print("✓ 빌드 완료")
    except Exception as e:
        print(f"빌드 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return

    # 2. 빌드된 dist 폴더를 tar.gz로 압축
    print("\n[2/5] 빌드 파일 압축 중...")
    try:
        with tarfile.open(LOCAL_FILES['web'], 'w:gz') as tar:
            tar.add(os.path.dirname(LOCAL_FILES['web']), arcname="web")
        print(f"✓ 압축 완료: {LOCAL_FILES['web']}")
    except Exception as e:
        print(f"압축 실패: {e}")
        return        


def cleanup_remote_dir(ssh):
    print("\n----------------------------------cleanup remote dir----------------------------------")
    print(f"원격 디렉토리: {DEST_DIR}")
    remove_cmd = f"rm -rf {DEST_DIR}/*"
    result = ssh_exec_with_status(ssh, remove_cmd, print_output=False)
    print("✓ 기존 파일 제거 완료")
    create_dir_cmd = f"mkdir -p {os.path.join(DEST_DIR, 'web')}"
    result = ssh_exec_with_status(ssh, create_dir_cmd, print_output=False)
    print("✓ web 디렉토리 생성 완료")
    # create_dir_cmd = f"mkdir -p {os.path.join(DEST_DIR, 'bin')}"
    # result = ssh_exec_with_status(ssh, create_dir_cmd, print_output=False)
    print("✓ bin 디렉토리 생성 완료")
    create_dir_cmd = f"mkdir -p {os.path.join(DEST_DIR, 'api')}"
    result = ssh_exec_with_status(ssh, create_dir_cmd, print_output=False)
    print("✓ api 디렉토리 생성 완료")
    create_dir_cmd = f"mkdir -p {os.path.join(DEST_DIR, 'config')}"
    result = ssh_exec_with_status(ssh, create_dir_cmd, print_output=False)
    print("✓ config 디렉토리 생성 완료")    

def release_web(ssh):
    print("\n----------------------------------release web----------------------------------")
    print(f"로컬 디렉토리: {LOCAL_FILES['web']}")
    
    # 3. SFTP로 원격 서버에 전송
    print(f"\n[4/5] 파일 전송 중: {LOCAL_FILES['web']} -> {os.path.join(DEST_DIR, 'web.tar.gz')}")
    try:
        sftp = ssh.open_sftp()
        sftp.put(LOCAL_FILES['web'], os.path.join(DEST_DIR, 'web.tar.gz'), callback=progress_callback)
        print()  # 진행률 표시 후 줄바꿈
        print("✓ 파일 전송 완료")
        sftp.close()
    except Exception as e:
        print(f"파일 전송 실패: {e}")
        return
    # 5. 원격 서버에서 압축 해제
    
    print("\n[5/5] 원격 서버에서 압축 해제 중...")
    extract_cmd = f"cd {DEST_DIR} && tar xzf {os.path.join(DEST_DIR, 'web.tar.gz')} && rm -f {os.path.join(DEST_DIR, 'web.tar.gz')}"
    result = ssh_exec_with_status(ssh, extract_cmd, print_output=False)
    if not result['success']:
        print(f"압축 해제 실패 (exit code: {result['exit_status']})")
        print(f"에러: {result['error']}")
        return
    print("✓ 압축 해제 완료")

  

def cp_nginx_conf(ssh):
    remote_file = os.path.join(DEST_DIR, "nginx.gate_control.conf")
    try:
        sftp = ssh.open_sftp()
        sftp.put(LOCAL_FILES['nginx_conf'], remote_file, callback=progress_callback)
        print()  # 진행률 표시 후 줄바꿈
        print("✓ 파일 전송 완료")
        sftp.close()
    except Exception as e:
        print(f"파일 전송 실패: {e}")
        return

def cp_service_file(ssh):
    files = ["gate_control.service"]
    
    sftp = ssh.open_sftp()
    for file in files:
        try:
            sftp.put(os.path.join(SCRIPT_DIR, file), os.path.join(DEST_DIR, file), callback=progress_callback)
            print()  # 진행률 표시 후 줄바꿈
            print(f"✓ {file} 파일 전송 완료")
        except Exception as e:
            print(f"파일 전송 실패: {e}")
            continue
    sftp.close()
    

def main():
 
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("connect to server")
    
    try:
        # SSH 키 인증 사용
        ssh.connect(
            hostname=CONFIG['host'], 
            username=CONFIG['username'], 
            password=CONFIG['password']
            # key_filename=CONFIG['private_key']
        )
        print("SSH 키 인증 성공")
    except Exception as e:
        print(f"SSH 키 인증 실패: {e}")
        raise
    

    # cleanup_remote_dir(ssh)
    run_web_build()
    release_web(ssh)
    # release_api(ssh)
    # cp_nginx_conf(ssh)
    # cp_service_file(ssh)
    # release_bin(ssh)

       
    ssh.close()
    print("server disconnected")

if __name__ == '__main__':
    main()



