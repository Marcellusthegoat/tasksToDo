from flask import Flask, redirect, render_template, session,request,flash
import pymongo
from bson.objectid import ObjectId
from passlib.hash import sha256_crypt

app = Flask(__name__)
client = pymongo.MongoClient("mongodb+srv://marcellusfieldridley:12345@cluster0.kxuyvqi.mongodb.net/")
db = client.checklist
app.secret_key = "^f6145sfg*&^Fs8"
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home",methods = ["POST","GET"])
def home():
    if request.method == "GET":
        tasks = list(db.tasks.find({"USER":session["username"]}))
        return render_template("home.html", tasks = tasks)

@app.route("/login", methods = ["POST","GET"])
def login():
    username  = request.form.get("username")
    password = request.form.get("password")
    user = db.users.find_one({"USER_NAME":username})
    if user:
        print(user)
        if sha256_crypt.verify(password,user["PASSWORD"]):
            print("valid redierecitnfg")
            session["username"] = username
            return redirect("/home")
        
    flash("incorrect user or password")
    return redirect("/")

@app.route("/register", methods = ["POST","GET"])
def register():
    username  = request.form.get("username")
    password = sha256_crypt.hash(request.form.get("password"))
    db.users.insert_one({"USER_NAME":username,"PASSWORD":password})
    session["username"] = username
    return redirect("/home")

@app.route("/newTask", methods = ["POST","GET"])
def inputTask():
    taskName = request.form.get("task")
    taskDescription = request.form.get("taskDescription")
    db.tasks.insert_one({"TASK_NAME":taskName,"TASK_DESCRIPTION":taskDescription,"USER":session["username"],"MARKED_AS_DONE":"False", "helpers":[]})
    return redirect("/home")

@app.route("/delete/<taskId>")
def delete(taskId):
    db.tasks.delete_one({"_id":ObjectId(taskId)})
    return redirect("/home")

@app.route("/editTask/<taskId>", methods = ["POST"])
def editTask(taskId):
    if request.method == "POST":
        e_taskName = request.form.get("editedTask")
        e_taskDescription = request.form.get("editedTaskDescription")
        db.tasks.update_one({"_id":ObjectId(taskId)},{"$set": {"TASK_NAME":e_taskName,"TASK_DESCRIPTION":e_taskDescription,"USER":session["username"]}})
        return redirect("/home")
    
@app.route("/addPeople/<taskId>", methods = ["POST","GET"])
def addPerson(taskId):
    personName = request.form.get("fullName")
    contactInfo = request.form.get("contactInfo")
    db.tasks.update_one({"_id":ObjectId(taskId)},{"$push": {"helpers":{"NAME":personName,"CONTACT":contactInfo}}})
    return redirect("/home")

@app.route("/markAsDone/<taskId>")
def markAsDone(taskId):
    task = list(db.tasks.find({"_id":ObjectId(taskId)}))[0]
    print(task)
    if task["MARKED_AS_DONE"] == "False":
        db.tasks.update_one({"_id":ObjectId(taskId)},{ "$set": {"MARKED_AS_DONE":"True"}})
    if task["MARKED_AS_DONE"] == "True":
        db.tasks.update_one({"_id":ObjectId(taskId)},{ "$set": {"MARKED_AS_DONE":"False"}})
    return redirect("/home")

@app.route("/deleteHelper/<helperName>")
def deleteHelper(helperName):
    if helperName != '':
        db.tasks.update_one({},{"$pull": { "helpers" : {"NAME":helperName}}})
        return redirect("/home")
    else:
        flash("There was an Error: Try Again Later")
        return redirect("/home")


@app.route("/editPerson/<helperName>", methods = ["POST","GET"])
def editPerson(helperName):
    print(helperName)
    e_name = request.form.get("fullName")
    e_contact = request.form.get("contactInfo")
    print(e_name,e_contact)
    db.tasks.update_one({"helpers.NAME":helperName},{"$set": {"helpers" :[{"NAME":e_name,"CONTACT":e_contact}]}})
    return redirect("/home")
    
@app.route("/logout")
def logout():
    session.clear
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)
