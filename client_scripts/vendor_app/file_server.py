# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


from flask import Flask, render_template, request
from flask import Response
from flask import send_file, send_from_directory, safe_join, abort

app = Flask(__name__)
app.config["CLIENT_APP"] = "/home/chinmay/Documents/SampleProjects/firmware_update_v2/client_scripts/vendor_app/"

@app.route("/")
def index():
    pass

@app.route("/get-app/<app_name>")
def get_app(app_name):
    try:
        filename = f"{app_name}.py"
        return send_from_directory(app.config["CLIENT_APP"], path=filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
