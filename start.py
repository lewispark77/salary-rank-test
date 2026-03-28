import subprocess
import time
import sys

def main():
    print("==================================================")
    print(" 🚀 [억만장자 계급 테스트] 시스템 부팅을 시작합니다...")
    print("==================================================\n")

    # 1. FastAPI 백엔드 서버 켜기
    print("📡 [1/2] 백엔드 API 서버 엔진에 시동을 겁니다...")
    # 파이썬이 uvicorn을 백그라운드에서 실행하도록 명령
    backend = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--port", "8000"])
    
    # 서버가 켜질 때까지 딱 3초만 기다려줍니다.
    time.sleep(3)
    
    # 2. Streamlit 프론트엔드 웹 켜기
    print("\n🎨 [2/2] 프론트엔드 웹 화면을 브라우저에 띄웁니다!\n")
    frontend = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "salary_ui.py"])

    try:
        # 창이 바로 꺼지지 않고 계속 실행되도록 유지
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        # 터미널에서 Ctrl+C를 누르면 켜져 있던 두 서버를 모두 깔끔하게 죽입니다!
        print("\n\n🛑 종료 명령이 입력되었습니다. 서버를 모두 안전하게 끕니다...")
        backend.terminate()
        frontend.terminate()
        print("✅ 시스템이 완벽하게 종료되었습니다.")

if __name__ == "__main__":
    main()