from flask import Flask
from flask import render_template
from Module import *
app = Flask(__name__)

@app.route('/abc')
def hi_world():
    lat = 126.97195
    lon = 37.58267

    code = coordinate2code(lat, lon)  # 카카오 API 함수 호출(횟수 제한)
    pd_mag_data = code2pandas_data(code)

    html, max_mag = fancy_html(code, pd_mag_data)
    max_mag_image_path = get_max_magnitude_path(max_mag)
    mag_map = make_map(code, pd_mag_data, max_mag_image_path, html)

    map_image = map_capture(mag_map)

    cropped_image = crop_image(map_image)
    base64_cropped_image = image2base64('./cropped_map.jpg')

    contnet = "(%s,  " % lat + "%s)" % lon + "의 지진정보"
    to = "01041396848"

    timestamp = int(time.time() * 1000)
    timestamp = str(timestamp)  # 1970년1월 1일 00:00:00 협정 세계시(UTC)부터의 경과 시간을 밀리초(Millisecond)로 나타낸 것

    url = "https://sens.apigw.ntruss.com"  # 해당 상품 URL
    requestUrl = "/sms/v2/services/"
    requestUrl2 = "/messages"
    serviceId = "ncp:sms:kr:261750529825:soa13_mms"
    access_key = "7oEHauk6RbFG2hDyEHJp"  # access key id (from portal or sub account)

    uri = requestUrl + serviceId + requestUrl2
    apiUrl = url + uri

    messages = {
        "to": to,
        "subject": "지진알림",
        "content": contnet}
    files = {
        "name": "cropped_map.jpg",
        "body": base64_cropped_image
    }
    body = {
        "type": "MMS",
        "contentType": "COMM",
        "from": "01041396848",
        "subject": "지진알림",
        "content": contnet,
        "messages": [messages],
        "files": [files]
    }
    body2 = json.dumps(body)
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'X-ncp-apigw-timestamp': timestamp,
        'x-ncp-iam-access-key': access_key,
        'x-ncp-apigw-signature-v2': make_signature(uri, access_key, timestamp)
    }
    res = requests.post(apiUrl, headers=headers, data=body2)

    res.request  # 내가 보낸 request 객체에 접근 가능
    res.status_code  # 응답 코드
    res.raise_for_status()  # 200 OK 코드가 아닌 경우 에러 발동

    return res.json()

@app.route('/')
def hello_world():
    return render_template('index.html')


if __name__ == '__main__':
    app.run("0.0.0.0","5000")
