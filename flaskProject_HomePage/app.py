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

    return max_mag_image_path

@app.route('/')
def hello_world():
    return render_template('index.html')


if __name__ == '__main__':
    app.run("0.0.0.0","5000")
