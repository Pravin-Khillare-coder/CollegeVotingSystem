from flask import Flask, render_template, request, redirect, jsonify
import os

app = Flask(__name__)

# ================= GLOBAL =================
voting_started = False

def get_file(type):
    return f"data/{type}.txt"

# ================= HOME =================
@app.route('/')
def login():
    return render_template("index.html")

# ================= ADMIN =================
@app.route('/admin', methods=['POST'])
def admin():
    if request.form['user'] == "admin" and request.form['pass'] == "admin123":
        return redirect('/admin-home')
    return "Invalid Admin!"

@app.route('/admin-home')
def admin_home():
    return render_template("admin.html")

# ================= STUDENT =================
@app.route('/student')
def student():
    return render_template("student.html")

# ================= STUDENT LOGIN =================
@app.route('/student-login', methods=['POST'])
def student_login():
    sid = request.form.get('id', '').strip()
    password = request.form.get('pass', '').strip()

    file = "data/students.txt"

    if not os.path.exists(file):
        return "fail"

    with open(file) as f:
        for line in f:
            d = line.strip().split(',')
            if len(d) >= 2 and d[0] == sid and d[1] == password:
                return "success"

    return "fail"

# ================= START / STOP =================
@app.route('/start')
def start():
    global voting_started
    voting_started = True
    return "ok"

@app.route('/stop')
def stop():
    global voting_started
    voting_started = False
    return "ok"

# ================= ADD =================
@app.route('/add', methods=['POST'])
def add():
    type = request.form.get('type').strip()
    cid = request.form.get('id').strip()
    name = request.form.get('name').strip()

    file = get_file(type)

    os.makedirs("data", exist_ok=True)

    if not os.path.exists(file):
        open(file, 'w').close()

    # ===== STRICT DUPLICATE CHECK =====
    with open(file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            data = line.split(",")

            if len(data) >= 2 and data[0].strip() == cid:
                return "Candidate Already Exists!"

    # ===== WRITE CLEANLY (NO SAME LINE ISSUE) =====
    with open(file, "a") as f:
        f.write(f"\n{cid},{name},0")

    return "Candidate Added Successfully!"

# ================= GET CANDIDATES =================
@app.route('/candidates/<type>')
def candidates(type):
    file = get_file(type)
    data = []

    if os.path.exists(file):
        with open(file) as f:
            for line in f:
                if line.strip():
                    data.append(line.strip().split(','))

    return jsonify({"candidates": data})

# ================= DELETE =================
@app.route('/delete', methods=['POST'])
def delete():
    type = request.form['type']
    cid = request.form['id']

    file = get_file(type)

    if not os.path.exists(file):
        return "File not found!"

    updated = []
    found = False

    with open(file) as f:
        for line in f:
            d = line.strip().split(',')
            if d[0] == cid:
                found = True
                continue
            updated.append(d)

    with open(file, 'w') as f:
        for d in updated:
            f.write(",".join(d) + "\n")

    return "Deleted Successfully!" if found else "Candidate Not Found!"

# ================= VOTE =================
@app.route('/vote', methods=['POST'])
def vote():
    global voting_started

    if not voting_started:
        return "Voting not started!"

    sid = request.form.get('sid').strip()
    type = request.form.get('type').strip()
    cid = request.form.get('id').strip()

    student_file = "data/students.txt"

    updated_students = []
    voted = False

    # check student + vote status
    with open(student_file) as f:
        for line in f:
            d = line.strip().split(',')

            if d[0] == sid:
                for i in range(2, len(d)):
                    key, val = d[i].split("=")

                    if key == type:
                        if val == "1":
                            return "Already Voted!"
                        else:
                            d[i] = f"{type}=1"
                            voted = True

            updated_students.append(d)

    if not voted:
        return "Vote Failed!"

    # save student file
    with open(student_file, 'w') as f:
        for d in updated_students:
            f.write(",".join(d) + "\n")

    # update candidate votes
    file = get_file(type)
    updated_candidates = []

    with open(file) as f:
        for line in f:
            d = line.strip().split(',')
            if d[0] == cid:
                d[2] = str(int(d[2]) + 1)
            updated_candidates.append(d)

    with open(file, 'w') as f:
        for d in updated_candidates:
            f.write(",".join(d) + "\n")

    return "Vote Casted Successfully!"

# ================= CHANGE PASSWORD =================
@app.route('/change-pass', methods=['POST'])
def change_pass():
    sid = request.form['id']
    old = request.form['old']
    new = request.form['new']

    file = "data/students.txt"
    updated = []
    found = False

    with open(file) as f:
        for line in f:
            d = line.strip().split(',')
            if d[0] == sid and d[1] == old:
                d[1] = new
                found = True
            updated.append(d)

    with open(file, 'w') as f:
        for d in updated:
            f.write(",".join(d) + "\n")

    return "Password Updated!" if found else "Wrong Password!"

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)