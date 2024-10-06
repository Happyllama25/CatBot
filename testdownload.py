from flask import Flask, send_from_directory, abort, render_template, url_for

flask_app = Flask(__name__)

@flask_app.route('/downloads/<file_ID>')
def download_file(file_ID):
    return render_template('index.html', file_ID=file_ID)

@flask_app.route('/media/<file_ID>')
def serve_file(file_ID):
    try:
        return send_from_directory("downloads", file_ID, as_attachment=True)
    except FileNotFoundError:
        abort(404)


flask_app.run(port=8129)
