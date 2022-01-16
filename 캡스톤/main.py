## server execution code
from flask import Flask, request
import json, os, numpy, uuid, time
from json import JSONEncoder
import personal_color
from time import sleep
from PIL import Image

## folder path settings
root_folder = "./"
result_folder = os.path.join(root_folder, "html/result")

app = Flask(
    __name__,
    static_url_path='',
    static_folder='html/',
)

@app.route('/')
@app.route('/home')
def home():
    return app.send_static_file("index.html")


@app.route('/upload', methods=['POST'])
def upload():
    # get list dir
    filelist = os.listdir(result_folder)
    # delete images 3 minute timeout
    ctime = time.time()
    for file in filelist:
        ftime = os.path.getmtime(f"{result_folder}/{file}")
        if (180 < ctime - ftime):
            os.remove(f"{result_folder}/{file}")
    # file image request get
    file = request.files["image"]
    # filename set use with uuid ( Deduplication )
    filename = uuid.uuid4().hex
    _, ext = os.path.splitext(file.filename)
    while (True):
        filename = uuid.uuid4().hex
        if (not (f"{result_folder}/{filename}{ext}" in filelist)):
            print(f"{result_folder}/{filename}{ext}")
            break
    file.save(os.path.join(result_folder, f"{filename}{ext}"))

    # personal color create
    personal_color.start(f"{result_folder}/{filename}", ext)
    output = {"output": filename, "ext": ext}
    output = json.dumps(output, cls=NumpyArrayEncoder)
    return outputJSON(json.loads(output), "ok")


@app.route('/select', methods=['POST'])
def select():
    filename = request.form["filename"]
    number = request.form["number"]
    fout = personal_color.final(number, filename)
    output = {"output": fout}
    output = json.dumps(output, cls=NumpyArrayEncoder)
    return outputJSON(json.loads(output), "ok")


def outputJSON(msg, status="error"):
    return {"data": msg, "status": status}


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


if __name__ == '__main__':
    app.run(debug=True)