import datetime
import json
from io import BytesIO

from PIL import Image
from flask import Flask, render_template, render_template_string, redirect, url_for, request, jsonify, flash
from flask_and_minio import FlaskAndMinio
from flask_login import login_user, logout_user, login_required, current_user
from flask_mailman import EmailMessage
import forms.drone_form
from forms.forgot_form import ForgotForm
from forms.password_form import PasswordForm

from forms.task_form import TaskForm
import numpy as np
from config.config import Config
import models.drone_position
import models.drone_velocity
import models.image
import models.task
from models.user_drone import Users, Drone
from auth.reset_password_email_content import reset_password_email_html_content
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config.from_object(Config)
Config.db.init_app(app)
Config.mail.init_app(app)
Config.login_manager.init_app(app)
with app.app_context():
    Config.db.create_all()


@Config.login_manager.user_loader
def loader_user(user_id):
    return Config.db.session.get(Users, user_id)


@app.route("/login-register", methods=["GET", "POST"])
def login_register():
    if request.method == "POST" and request.form.get("action") == "login":
        user = (Config.db.session.query(Users).filter_by(username=request.form.get("username"))
                .filter_by(email=request.form.get("email")).first())
        if user is None:
            return render_template("login.html")
        if user.password == request.form.get("password"):
            login_user(user)
            return redirect(url_for("home"))
    elif request.method == "POST" and request.form.get("action") == "sign-up":
        user = Users(username=request.form.get("username"),
                     email=request.form.get("email"),
                     password=request.form.get("password"))
        Config.db.session.add(user)
        Config.db.session.commit()
        return redirect(url_for("login_register"))
    return render_template("login.html")


@app.route("/reset_password", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = ForgotForm()
    if form.validate_on_submit():
        user = Config.db.session.query(Users).filter_by(email=request.form.get("email")).first()
        if user:
            send_reset_password_email(user)
        flash("Instructions to reset your password were sent to your email address, if it exists in our system.")
        return redirect(url_for("reset_password_request"))
    return render_template("reset_password_request.html", title="Reset Password", form=form)


def send_reset_password_email(user):
    reset_password_url = url_for(
        "reset_password",
        token=user.generate_reset_password_token(),
        user_id=user.id,
        _external=True
    )
    email_body = render_template_string(reset_password_email_html_content, reset_password_url=reset_password_url)
    message = EmailMessage(
        subject="Reset Your Password",
        body=email_body,
        to=[user.email]
    )
    message.content_subtype = "html"
    message.send()


@app.route("/reset_password/<token>/<int:user_id>", methods=["GET", "POST"])
def reset_password(token, user_id):
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    user = Users.validate_reset_password_token(token, user_id)
    if not user:
        return render_template("reset_password_error.html", title="Reset Password Error")
    form = PasswordForm()
    if form.validate_on_submit():
        user.password = form.new_password.data
        Config.db.session.commit()
        return render_template("reset_password_success.html", title="Reset Password Success")
    return render_template("reset_password.html", title="Reset Password", form=form)


@app.route("/home")
def home():
    return render_template("map.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/")
def index():
    return render_template("maplogin.html")


@app.route("/api/drones")
@login_required
def get_all_drones():
    user = Config.db.session.get(Users, current_user.id)
    if user:
        drones = user.drones
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return json.dumps(Drone.serialize_list(drones.all()))
    return render_template("drones.html")


@app.route("/api/drones", methods=["POST"])
@login_required
def create_drone():
    user_input = request.get_json()
    form = forms.drone_form.DroneForm(data=user_input)
    if form.validate():
        global_position = models.drone_position.Position(user_input["latitude"], user_input["longitude"],
                                                         user_input["altitude"])
        home_position = models.drone_position.Position(user_input["home_latitude"], user_input["home_longitude"],
                                                       user_input["home_altitude"])
        velocity = models.drone_velocity.Velocity(user_input["velocity_x"], user_input["velocity_y"],
                                                  user_input["velocity_z"])
        drone = Drone(name=form.name.data,
                      global_position=global_position,
                      home_position=home_position,
                      velocity=velocity,
                      connected=bool(user_input["connected"] == "Connected"),
                      tasks=list())
        user = Config.db.session.get(Users, current_user.id)
        if user:
            user.drones.append(drone)
            Config.db.session.add(drone)
            Config.db.session.commit()
            return json.dumps(Drone.serialize(drone))
    return render_template("drones.html")


@app.route('/api/drones/<int:drone_id>', methods=['GET'])
@login_required
def get_drone(drone_id):
    drone = Config.db.session.query(Drone).filter_by(id=drone_id).first()
    user = Config.db.session.get(Users, current_user.id)
    if drone in user.drones:
        return json.dumps(Drone.serialize(drone))
    return render_template("drones.html")


@app.route("/api/drones/<int:drone_id>", methods=['PATCH', 'PUT'])
@login_required
def update_drone(drone_id):
    drone = Config.db.session.query(Drone).filter_by(id=drone_id).first()
    if current_user in drone.users:
        data = request.get_json()
        form = forms.drone_form.DroneForm(data=data)
        if form.validate():
            drone.name = data["name"]
            global_position = models.drone_position.Position(data["latitude"], data["longitude"], data["altitude"])
            drone.global_position = global_position
            home_position = models.drone_position.Position(data["home_latitude"], data["home_longitude"], data["home_altitude"])
            drone.home_position = home_position
            velocity = models.drone_velocity.Velocity(data["velocity_x"], data["velocity_y"], data["velocity_z"])
            drone.velocity = velocity
            drone.connected = data["connected"] == "Connected"
            Config.db.session.commit()
            return json.dumps(Drone.serialize(drone))
    return render_template("drones.html")


@app.route("/api/drones/<int:drone_id>", methods=["DELETE"])
@login_required
def delete_drone(drone_id):
    drone = Config.db.session.query(Drone).filter_by(id=drone_id).first()
    if current_user in drone.users:
        Config.db.session.delete(drone)
        Config.db.session.commit()
    return render_template("drones.html")


@app.route("/api/drones/<int:drone_id>", methods=["POST"])
@login_required
def connect_drone(drone_id):
    drone = Config.db.session.query(Drone).filter_by(id=drone_id).first()
    drone.connected = not drone.connected
    Config.db.session.commit()
    return jsonify({"connected": drone.connected})


@app.route("/api/tasks", methods=["POST"])
@login_required
def create_task():
    data = request.get_json()
    form = TaskForm(data=data)
    print(data)
    if form.validate():
        print("validated")
        task = models.task.Task(title=data["title"],
                                date=datetime.datetime.fromisoformat(data["date"]),
                                completed=data["completed"] == "Completed",
                                drone_id=data["drone_id"],
                                images=list())
        drone = Config.db.session.query(Drone).filter_by(id=data["drone_id"]).first()
        if drone and current_user in drone.users:
            print("done")
            Config.db.session.add(task)
            Config.db.session.commit()
            task_serialized = models.task.Task.serialize(task)
            task_serialized["drone_name"] = drone.name
            task_serialized["drone_connected"] = drone.connected
            del task_serialized["drone"]
            return json.dumps(task_serialized, default=lambda obj: obj.isoformat())
    return render_template("tasks.html")


@app.route("/api/tasks")
@login_required
def get_all_tasks():
    tasks = Config.db.session.query(models.task.Task).all()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        task_serialize_list = models.task.Task.serialize_list(tasks)
        for task_serialized in task_serialize_list:
            if current_user not in task_serialized["drone"].users:
                continue
            task_serialized["drone_id"] = task_serialized["drone"].id
            task_serialized["drone_name"] = task_serialized["drone"].name
            task_serialized["drone_connected"] = task_serialized["drone"].connected
            del task_serialized["drone"]
        return json.dumps(task_serialize_list, default=lambda obj: obj.isoformat())
    return render_template("tasks.html")


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    task = Config.db.session.query(models.task.Task).get(task_id)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        task_serialized = models.task.Task.serialize(task)
        if current_user in task_serialized["drone"].users:
            task_serialized["drone_id"] = task_serialized["drone"].id
            task_serialized["drone_name"] = task_serialized["drone"].name
            task_serialized["drone_connected"] = task_serialized["drone"].connected
            del task_serialized["drone"]
        return json.dumps(task_serialized, default=lambda obj: obj.isoformat())
    return render_template("tasks.html")


@app.route("/api/tasks/<int:task_id>", methods=['PATCH', 'PUT'])
def update_task(task_id):
    task = Config.db.session.query(models.task.Task).filter_by(id=task_id).first()
    data = request.get_json()
    print(data)
    form = forms.task_form.TaskForm(data=data)
    if form.validate():
        drone = Config.db.session.query(Drone).filter_by(id=data["drone_id"]).first()
        if drone and current_user in drone.users:
            task.title = data["title"]
            task.date = datetime.datetime.fromisoformat(data["date"])
            task.completed = data["completed"] == "Completed"
            task.drone_id = data["drone_id"]
            Config.db.session.commit()
            task_serialized = models.task.Task.serialize(task)
            task_serialized["drone_name"] = drone.name
            task_serialized["drone_connected"] = drone.connected
            del task_serialized["drone"]
            return json.dumps(task_serialized, default=lambda obj: obj.isoformat())
    return render_template("tasks.html")


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    task = Config.db.session.query(models.task.Task).filter_by(id=task_id).first()
    Config.db.session.delete(task)
    Config.db.session.commit()
    return render_template("tasks.html")


@app.route("/api/tasks/<int:task_id>/execute", methods=["POST"])
@login_required
def execute_task(task_id):
    task = Config.db.session.query(models.task.Task).filter_by(id=task_id).first()
    drone = Config.db.session.query(models.user_drone.Drone).filter_by(id=task.drone_id).first()
    if not drone.connected:
        return render_template("tasks.html")
    for i in range(Config.NUM_IMAGES):
        pixels = np.uint8(np.random.randint(0, 256, size=(Config.IMAGE_WIDTH, Config.IMAGE_HEIGHT, Config.IMAGE_CHANNEL)))
        image = Image.fromarray(pixels)
        filename = secure_filename(str(task_id) + "_" + str(task.title) + "_" + str(task.date) + "_" + str(task.drone_id) + "_" + str(i) + ".png")
        image_buffer = BytesIO()
        image.save(image_buffer, format='PNG')
        image_buffer.seek(0)
        img = models.image.Image(filename=filename, task_id=task_id)
        Config.db.session.add(img)
        found = Config.minio_client.bucket_exists(Config.MINIO_BUCKET)
        if not found:
            Config.minio_client.make_bucket(Config.MINIO_BUCKET)
        try:
            Config.minio_client.put_object(Config.MINIO_BUCKET, filename, image_buffer, len(image_buffer.getvalue()))
        except Exception as e:
            return render_template("tasks.html")
    task.completed = True
    Config.db.session.commit()
    return render_template("tasks.html")


@app.route("/api/tasks/<int:task_id>/images")
@login_required
def view_all_images(task_id):
    return render_template('images.html')


@app.route("/api/tasks/<int:task_id>/images/view")
@login_required
def get_all_images(task_id):
    task = Config.db.session.query(models.task.Task).filter_by(id=task_id).first()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        image_serialize_list = models.task.Image.serialize_list(task.images)
        for image_serialized in image_serialize_list:
            image_serialized["task_id"] = task.id
            image_serialized["task_title"] = task.title
            image_serialized["task_date"] = task.date
            image_serialized["task_completed"] = task.completed
        json_data = json.dumps(image_serialize_list, default=lambda obj: obj.isoformat())
        return json_data
    return render_template("images.html")


@app.route("/api/tasks/<int:task_id>/images/view/<int:image_id>")
@login_required
def get_image(task_id, image_id):
    task = Config.db.session.query(models.task.Task).filter_by(id=task_id).first()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        image = task.images.filter_by(id=image_id).first()
        filename = image.filename
        url = Config.minio_client.get_presigned_url("GET", Config.MINIO_BUCKET, filename, expires=datetime.timedelta(hours=2))
        return jsonify({'url': url, 'filename': filename})
    return render_template("images.html")


if __name__ == "__main__":
    app.run(debug=True)
