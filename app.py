from flask import Flask, render_template, request, redirect, url_for
import pymysql
import credentials

app = Flask(__name__, template_folder="templates")


class Database:
    def __init__(self):
        self.con = pymysql.connect(
            host=credentials.DB_HOST,
            user=credentials.DB_USER,
            password=credentials.DB_PWD,
            db=credentials.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cur = self.con.cursor()

    def close(self):
        self.con.close()

    def get_all_tickets(self):
        query = """
        SELECT t.ticket_id, t.title, t.status, t.priority,
               u.full_name AS user_name,
               tech.full_name AS technician_name,
               d.name AS department_name
        FROM tickets t
        JOIN users u ON t.user_id = u.user_id
        LEFT JOIN technicians tech ON t.technician_id = tech.technician_id
        LEFT JOIN departments d ON t.department_id = d.department_id
        ORDER BY t.ticket_id
        """
        self.cur.execute(query)
        result = self.cur.fetchall()
        self.close()
        return result

    def get_all_users(self):
        self.cur.execute("SELECT * FROM users ORDER BY full_name")
        result = self.cur.fetchall()
        self.close()
        return result

    def create_user(self, full_name, email, department):
        self.cur.execute("""
            INSERT INTO users (full_name, email, department)
            VALUES (%s, %s, %s)
        """, (full_name, email, department))
        self.con.commit()
        self.close()

    def get_all_technicians(self):
        self.cur.execute("SELECT * FROM technicians ORDER BY full_name")
        result = self.cur.fetchall()
        self.close()
        return result

    def create_ticket(self, user_id, department_id, title, description, priority):
        if department_id == "":
            department_id = None

        self.cur.execute("""
            INSERT INTO tickets (user_id, department_id, title, description, priority, status)
            VALUES (%s, %s, %s, %s, %s, 'Open')
        """, (user_id, department_id, title, description, priority))
        self.con.commit()
        self.close()

    def get_ticket_by_id(self, ticket_id):
        self.cur.execute("""
            SELECT t.ticket_id, t.user_id, t.technician_id, t.department_id,
                   t.title, t.description, t.status, t.priority, t.created_at,
                   u.full_name AS user_name,
                   u.email AS user_email,
                   u.department,
                   tech.full_name AS technician_name,
                   d.name AS department_name
            FROM tickets t
            JOIN users u ON t.user_id = u.user_id
            LEFT JOIN technicians tech ON t.technician_id = tech.technician_id
            LEFT JOIN departments d ON t.department_id = d.department_id
            WHERE t.ticket_id = %s
        """, (ticket_id,))
        result = self.cur.fetchone()
        self.close()
        return result

    def update_ticket(self, ticket_id, title, description, status, priority, technician_id, department_id):
        if technician_id == "":
            technician_id = None
        if department_id == "":
            department_id = None

        self.cur.execute("""
            UPDATE tickets
            SET title = %s,
                description = %s,
                status = %s,
                priority = %s,
                technician_id = %s,
                department_id = %s
            WHERE ticket_id = %s
        """, (title, description, status, priority, technician_id, department_id, ticket_id))
        self.con.commit()
        self.close()

    def delete_ticket(self, ticket_id):
        self.cur.execute("DELETE FROM tickets WHERE ticket_id = %s", (ticket_id,))
        self.con.commit()
        self.close()

    def get_comments_by_ticket(self, ticket_id):
        self.cur.execute("""
            SELECT * FROM ticket_comments
            WHERE ticket_id = %s
            ORDER BY created_at DESC, comment_id DESC
        """, (ticket_id,))
        result = self.cur.fetchall()
        self.close()
        return result

    def add_comment(self, ticket_id, comment_text, commented_by):
        self.cur.execute("""
            INSERT INTO ticket_comments (ticket_id, comment_text, commented_by)
            VALUES (%s, %s, %s)
        """, (ticket_id, comment_text, commented_by))
        self.con.commit()
        self.close()

    def delete_comment(self, comment_id):
        self.cur.execute("DELETE FROM ticket_comments WHERE comment_id = %s", (comment_id,))
        self.con.commit()
        self.close()

    def delete_user(self, user_id):
        self.cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        self.con.commit()
        self.close()

    def get_departments(self):
        try:
           self.cur.execute("SELECT * FROM departments ORDER BY name")
           result = self.cur.fetchall()
        finally:
           self.con.close()
        return result

    def insert_department(self, name):
        try:
           self.cur.execute("INSERT INTO departments (name) VALUES (%s)", (name,))
           self.con.commit()
           return "Department added!"
        except:
           return "Error adding departmnet"
        finally:
           self.con.close()

    def get_departments(self):
        self.cur.execute("SELECT * FROM departments ORDER BY name")
        result = self.cur.fetchall()
        self.close()
        return result

    def insert_department(self, name):
        self.cur.execute("INSERT INTO departments (name) VALUES (%s)", (name,))
        self.con.commit()
        self.close()

    def delete_department(self, department_id):
        self.cur.execute("DELETE FROM departments WHERE department_id = %s", (department_id,))
        self.con.commit()
        self.close()

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/users")
def users():
    db = Database()
    result = db.get_all_users()
    return render_template("users.html", result=result)


@app.route("/users/create", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        department = request.form["department"]

        db = Database()
        db.create_user(full_name, email, department)

        return redirect(url_for("users"))

    db = Database()
    departments = db.get_departments()
    return render_template("create_user.html", departments=departments)

@app.route("/tickets")
def tickets():
    db = Database()
    result = db.get_all_tickets()
    return render_template("tickets.html", result=result)


@app.route("/tickets/create", methods=["GET", "POST"])
def create_ticket():
    if request.method == "POST":
        data = request.form
        user_id = data["user_id"]
        department_id = data["department_id"]
        title = data["title"]
        description = data["description"]
        priority = data["priority"]

        db = Database()
        db.create_ticket(user_id, department_id, title, description, priority)

        return redirect(url_for("tickets"))

    db = Database()
    users = db.get_all_users()

    db = Database()
    departments = db.get_departments()

    return render_template("create_ticket.html", users=users, departments=departments)

@app.route("/tickets/<int:ticket_id>/edit", methods=["GET", "POST"])
def edit_ticket(ticket_id):
    if request.method == "POST":
        data = request.form
        title = data["title"]
        description = data["description"]
        status = data["status"]
        priority = data["priority"]
        technician_id = data["technician_id"]
        department_id = data["department_id"]

        db = Database()
        db.update_ticket(ticket_id, title, description, status, priority, technician_id, department_id)

        return redirect(url_for("tickets"))

    db = Database()
    ticket = db.get_ticket_by_id(ticket_id)

    db = Database()
    technicians = db.get_all_technicians()

    db = Database()
    departments = db.get_departments()

    return render_template("edit_ticket.html", ticket=ticket, technicians=technicians, departments=departments)

@app.route("/tickets/<int:ticket_id>/delete", methods=["POST"])
def delete_ticket(ticket_id):
    db = Database()
    db.delete_ticket(ticket_id)
    return redirect(url_for("tickets"))


@app.route("/tickets/<int:ticket_id>/comment/add", methods=["POST"])
def add_comment(ticket_id):
    comment_text = request.form["comment_text"]
    commented_by = request.form["commented_by"]

    db = Database()
    db.add_comment(ticket_id, comment_text, commented_by)

    return redirect(url_for("ticket_details", ticket_id=ticket_id))


@app.route("/comments/<int:comment_id>/delete/<int:ticket_id>", methods=["POST"])
def delete_comment(comment_id, ticket_id):
    db = Database()
    db.delete_comment(comment_id)

    return redirect(url_for("ticket_details", ticket_id=ticket_id))

@app.route("/tickets/<int:ticket_id>")
def ticket_details(ticket_id):
    db = Database()
    ticket = db.get_ticket_by_id(ticket_id)

    db = Database()
    comments = db.get_comments_by_ticket(ticket_id)

    return render_template("ticket_details.html", ticket=ticket, comments=comments)

@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    db = Database()
    db.delete_user(user_id)
    return redirect(url_for("users"))

@app.route("/departments")
def departments():
    db = Database()
    result = db.get_departments()
    return render_template("departments.html", result=result)


@app.route("/departments/create", methods=["GET", "POST"])
def create_department():
    msg = ""
    if request.method == "POST":
        name = request.form["name"]
        db = Database()
        db.insert_department(name)
        return redirect(url_for("departments"))
    return render_template("create_department.html", msg=msg)


@app.route("/departments/<int:department_id>/delete", methods=["POST"])
def delete_department(department_id):
    db = Database()
    db.delete_department(department_id)
    return redirect(url_for("departments"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
