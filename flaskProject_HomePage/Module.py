import folium
import base64
import requests
import json
import pandas as pd
import pymysql

import io
import os
from PIL import Image
import time
from selenium import webdriver

import hashlib
import hmac
import base64
import time

mag_api_path = '/home/ubuntu/git/13_SOA_TeamProject/flaskProject_HomePage/mag_api_folder/'
db = pymysql.connect(host='127.0.0.1', port=3306, user='root',passwd='1234',db='soa_earthquate_db',charset='utf8')

def coordinate2code(lat,lon):
    uri = "https://dapi.kakao.com/v2/local/geo/coord2regioncode.json?x="+str(lat) +"&y="+str(lon)
    header = {"Authorization": "KakaoAK db82855fdc12b468adda7056a0f5e6ff"}
    result = requests.get(uri,headers=header)
    result = json.loads(result.text)

    code = result['documents'][0]['code']
    code_administrate = code[0:8]
    return code_administrate

def code2pandas_data(code):
    cursor = db.cursor()
    sql = "SELECT * FROM soa_earthquate_db.administrate WHERE administrative_code = %s"
    cursor.execute(sql,code)
    result_sql = cursor.fetchall()
    cursor.close()
    result_pd = pd.DataFrame(result_sql)
    return result_pd


def fancy_html(code, pandas_data):
    code_administrate = code

    max_magnitude = 2
    Administrative_area = pandas_data.values[0][1]

    magnitude_3 = pandas_data.values[0][4]
    magnitude_4 = pandas_data.values[0][5]
    magnitude_5 = pandas_data.values[0][6]
    magnitude_6 = pandas_data.values[0][7]
    magnitude_7 = pandas_data.values[0][8]
    magnitude_8 = pandas_data.values[0][9]
    magnitude_9 = pandas_data.values[0][10]
    magnitude_10 = pandas_data.values[0][11] + pandas_data.values[0][12] + pandas_data.values[0][13]

    magnitude_7_up = magnitude_7 + magnitude_8 + magnitude_9 + magnitude_10

    if (magnitude_7_up > 0):
        if magnitude_10 > 0:
            max_magnitude = 10
        elif magnitude_9 > 0:
            max_magnitude = 9
        elif magnitude_8 > 0:
            max_magnitude = 8
        else:
            max_magnitude = 7
    elif magnitude_6 > 0:
        max_magnitude = 6
    elif magnitude_5 > 0:
        max_magnitude = 5
    elif magnitude_4 > 0:
        max_magnitude = 4
    elif (magnitude_3 > 0):
        max_magnitude = 3

    left_col_colour = "#2A799C"
    right_col_colour = "#C5DCE7"

    html = """<!DOCTYPE html>
<html>

<head syyle="margin-top:0";>
<h4 style="margin-bottom:0;" width="300px">{}</h4>""".format(Administrative_area) + """
</head>

    <table style="height: 126px; width: 300x;">
<tbody>
<tr>
    <th rowspan="4"><img src="data:image/jpeg;base64,{}"></img></th>
</tr>
<tr>
<td style="background-color: """ + left_col_colour + """;"><span style="color: #ffffff;">진도 V</span></td>
<td style="width: 65px;background-color: """ + right_col_colour + """;">{}</td>""".format(magnitude_5) + """
</tr>
<tr>
<td style="background-color: """ + left_col_colour + """;"><span style="color: #ffffff;">진도 VI</span></td>
<td style="width: 65px;background-color: """ + right_col_colour + """;">{}</td>""".format(magnitude_6) + """
</tr>
<tr>
<td style="background-color: """ + left_col_colour + """;"><span style="color: #ffffff;">진도 VII +</span></td>
<td style="width: 65px;background-color: """ + right_col_colour + """;">{}</td>""".format(magnitude_7_up) + """
</tr>
<tr>
<td><b><font size="1px">최대진도 {} </font></b></td>""".format(max_magnitude) + """
</tr>

</tbody>
</table>
</html>
"""
    return html, max_magnitude


def get_max_magnitude_path(max_magnitude):
    path = mag_api_path
    if max_magnitude == 10:
        path = path + 'mag10.png'
    elif max_magnitude == 9:
        path = path + 'mag9.png'
    elif max_magnitude == 8:
        path = path + 'mag8.png'
    elif max_magnitude == 7:
        path = path + 'mag7.png'
    elif max_magnitude == 6:
        path = path + 'mag6.png'
    elif max_magnitude == 5:
        path = path + 'mag5.png'
    elif max_magnitude == 4:
        path = path + 'mag4.png'
    elif max_magnitude == 3:
        path = path + 'mag3.png'
    else:
        path = path + 'mag2.png'

    return path

def make_map(code,result_pd, max_mag_image_path,html):
    m = folium.Map([result_pd.values[0][2],result_pd.values[0][3]], zoom_start=15)

    encoded = base64.b64encode(open(max_mag_image_path, 'rb').read()).decode()

    iframe = folium.IFrame(html.format(encoded), width=300, height=233)

    popup = folium.Popup(iframe, show=True)

    marker = folium.Marker([result_pd.values[0][2],result_pd.values[0][3]], popup=popup).add_to(m)

    m.add_child(marker)

    return m

def map_capture(m):
    delay=10
    fn='testmap.html'
    tmpurl='file://{path}/{mapfile}'.format(path=os.getcwd(),mapfile=fn)
    m.save(fn)

    chrome_path = mag_api_path+'chromedriver'
    browser = webdriver.Chrome(chrome_path)
    browser.get(tmpurl)
    #Give the map tiles some time to load
    #time.sleep(delay)
    browser.save_screenshot('./map.png')
    browser.quit()
    return Image.open('./map.png')

def crop_image(im):
    area = (284,20,710,400)
    cropped_img = im.crop(area)
    cropped_img = cropped_img.convert("RGB")
    cropped_img.save('./cropped_map.jpg')
    return cropped_img

def	make_signature(uri, access_key, timestamp):
    secret_key = "yg5QFFfU6tdSdhr7jdJN7hvzYQ6pGmiS96xVjd8U"# secret key (from portal or sub account)
    secret_key = bytes(secret_key, 'UTF-8')
    method = "POST"
    message = method + " " + uri + "\n" + timestamp + "\n" + access_key
    message = bytes(message, 'UTF-8')
    signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
    return signingKey

def image2base64(path):
    with open(path, 'rb') as img:
        base64_img = base64.b64encode(img.read()).decode('UTF-8')
    return base64_img



