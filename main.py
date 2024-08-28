import requests
import json
import pychromecast as pcc
import time
from gtts import gTTS
import http.server
import socketserver
import multiprocessing as mp
import random
import datetime


def get_weather():
    url=f"http://api.weatherapi.com/v1/forecast.json?key=cf0e99e479a14e4d928122816241908&q=kugayama&hours=10"
    res=requests.get(url)
    data=res.json()
    if "forecast" in data:
        for wdata in data["forecast"]["forecastday"][0]["hour"]:
            cTime=datetime.datetime.now()
            if wdata["time"] == (datetime.datetime.now()+datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:00"):
                if wdata['chance_of_rain'] > 50 or wdata['chance_of_snow'] > 50:
                    return "bad"
                else:
                    break
    return "good"

def get_ghome():
    ccs,browser=pcc.get_listed_chromecasts(friendly_names=["Google home"])
    for cc in ccs:
        if cc.cast_info.host=='192.168.10.102':
            return cc
    else:
        print("chromecast has not found")
        return None

def speak_ghome(cc,text):
    easter_egg=random.randint(1,1000)
    if easter_egg==1:
        text="普通に"+text
    tts = gTTS(text, lang='ja')
    tts.save("result.mp3")

    p=mp.Process(target=run_locservc)
    p.start()
    print("run local server")
    
    if easter_egg!=1:
        cc.media_controller.play_media('http://192.168.10.101:8000/teikei.mp3',"audio/mp3")   
    time.sleep(8)
    cc.media_controller.play_media('http://192.168.10.101:8000/result.mp3',"audio/mp3")
    time.sleep(5)

    p.kill()
    print("The end")

def run_locservc():
    PORT = 8000
    # サーバーを起動してファイルを提供
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), Handler)
    httpd.serve_forever()

if __name__=="__main__":
    while datetime.datetime.now().minute != 30:
        time.sleep(60)

    while True:    
        forecast_status=get_weather()
        with open("rain_status.txt","r") as f:
            last_rain_status=f.readline()
            if last_rain_status != forecast_status:
                cc=get_ghome()
                if cc!=None:
                    cc.wait()
                    cc.set_volume(0.5)
                    if last_rain_status=="bad" and forecast_status=="good":
                        speak_ghome(cc,"干せる!!")
                    else:
                        speak_ghome(cc,"ほせない!!")
        with open("rain_status.txt","w") as f:    
            f.write(forecast_status)
        time.sleep(3600)