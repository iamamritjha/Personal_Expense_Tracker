from calendar import weekday
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, flash
import io
import base64
import matplotlib.pyplot as plt
import datetime
import numpy as np

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Use a secure key here

def get_db():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="1234",  # apna password yahan dalen
        database="expense_db"
    )

def get_user_by_email(email):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    cur.close()
    db.close()
    return user

def get_expenses_for_user(username):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM expenses WHERE username=%s ORDER BY date_time DESC", (username,))
    expenses = cur.fetchall()
    cur.close()
    db.close()
    for e in expenses:
        if isinstance(e['date_time'], str):
            e['date_time'] = datetime.datetime.strptime(e['date_time'], "%Y-%m-%d %H:%M:%S")
    return expenses

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                        (request.form['username'], request.form['email'], request.form['password']))
            db.commit()
            flash("Signup successful! Please login.", "success")
            return redirect(url_for('login'))
        except mysql.connector.Error:
            flash("Email already exists!", "error")
        finally:
            cur.close()
            db.close()
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = get_user_by_email(request.form['email'])
        if user and user['password'] == request.form['password']:
            session['user_name'] = user['username']
            flash("Login successful.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials.", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    username = session['user_name']
    expenses = get_expenses_for_user(username)
    now = datetime.datetime.now()
    month = now.month
    year = now.year

    # Fetch user's monthly budget using username
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM user_budgets WHERE username=%s AND month=%s AND year=%s", (username, month, year))
    budget = cur.fetchone()
    cur.close()
    db.close()

    starting_amount = budget['starting_amount'] if budget else None

    # Filter expenses for current month
    month_exps = [e for e in expenses if e['date_time'].month == month and e['date_time'].year == year]
    total_spent = sum(e['amount'] for e in month_exps)
    balance = starting_amount - total_spent if starting_amount is not None else None

    # Alerts based on balance
    alert_message = None
    alert_type = None
    if balance is not None:
        if balance <= 100:
            alert_message = "Balance below ₹100! Take backup from friends/family."
            alert_type = "danger"
        elif balance <= 500:
            alert_message = "Only ₹500 left! Keep money reserved for emergencies."
            alert_type = "warning"
        elif balance <= 1000:
            alert_message = "Less than ₹1000 left, spend wisely."
            alert_type = "info"

    # --- Monthly Pie Chart ---
    category_totals = {}
    for e in month_exps:
        cat = e['category'] or 'Other'
        category_totals[cat] = category_totals.get(cat, 0) + float(e['amount'])
    cats = list(category_totals.keys())
    amts = list(category_totals.values())
    month_chart = ""
    if cats and amts:
        fig, ax = plt.subplots()
        colors = ['#10b981','#6366f1','#f472b6','#f59e42','#4ade80','#818cf8','#fde68a','#ff80b5']
        patches, texts, autotexts = ax.pie(amts, labels=cats, autopct="%.1f%%", startangle=140, colors=colors[:len(cats)], pctdistance=0.85)
        centre_circle = plt.Circle((0,0),0.65,fc='white')
        fig.gca().add_artist(centre_circle)
        [t.set_fontsize(13) for t in texts]
        for at in autotexts:
            at.set_color('#524a4e')
            at.set_fontsize(11)
        ax.set_title("Monthly Expenses by Category", size=15)
        fig.set_facecolor('#faf6f4')
        plt.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.2)
        buf.seek(0)
        month_chart = base64.b64encode(buf.getvalue()).decode()
        plt.close(fig)

    # --- Weekly Polar Chart ---
    week_start = now - datetime.timedelta(days=now.weekday())
    week_exps = [e for e in expenses if week_start.date() <= e['date_time'].date() < (week_start.date() + datetime.timedelta(days=7))]
    week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    values = []
    for wd in week_days:
        wd_num = week_days.index(wd) + 1
        wd_total = sum(e['amount'] for e in week_exps if e['date_time'].isoweekday() == wd_num)
        values.append(wd_total)
    week_chart = ""
    if any(v > 0 for v in values):
        theta = np.linspace(0, 2 * np.pi, 7, endpoint=False)
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
        values_closed = values + [values[0]]
        theta_closed = np.append(theta, theta[0])
        ax.plot(theta_closed, values_closed, color='#6366f1', linewidth=3, marker='o')
        ax.fill(theta_closed, values_closed, color='#c7d2fe', alpha=0.5)
        ax.set_xticks(theta)
        ax.set_xticklabels(week_days)
        ax.set_yticklabels([])
        ax.set_title("Weekly Expense (Polar Chart)", size=15, va="bottom")
        fig.set_facecolor('#faf6f4')
        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.15)
        buf.seek(0)
        week_chart = base64.b64encode(buf.getvalue()).decode()
        plt.close(fig)

    return render_template('dashboard.html',
                           user_name=session['user_name'],
                           starting_amount=starting_amount,
                           balance=balance,
                           alert_message=alert_message,
                           alert_type=alert_type,
                           total_spent=total_spent,
                           total_count=len(expenses),
                           max_expense=max((e['amount'] for e in expenses), default=0),
                           month_chart=month_chart,
                           week_chart=week_chart,
                           expenses=expenses)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    if 'user_name' not in session:
        flash("Login required.", "error")
        return redirect(url_for('login'))
    db = get_db()
    cur = db.cursor()
    dt = request.form['date_time']
    cur.execute("""
        INSERT INTO expenses (username, date_time, amount, category, with_whom, purpose)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        session['user_name'],
        dt,
        request.form['amount'],
        request.form['category'],
        request.form.get('with_whom',''),
        request.form['purpose']
    ))
    db.commit()
    cur.close()
    db.close()
    flash("Expense Added!", "success")
    return redirect(url_for('dashboard'))

@app.route('/set_budget', methods=['GET', 'POST'])
def set_budget():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    username = session['user_name']
    now = datetime.datetime.now()
    month = now.month
    year = now.year

    if request.method == 'POST':
        starting_amount = float(request.form['starting_amount'])
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id FROM user_budgets WHERE username=%s AND month=%s AND year=%s", (username, month, year))
        existing = cur.fetchone()
        if existing:
            cur.execute("UPDATE user_budgets SET starting_amount=%s WHERE id=%s", (starting_amount, existing[0]))
        else:
            cur.execute("INSERT INTO user_budgets (username, starting_amount, month, year) VALUES (%s, %s, %s, %s)", (username, starting_amount, month, year))
        db.commit()
        cur.close()
        db.close()
        flash("Monthly budget set successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('set_budget.html')

if __name__ == "__main__":
    app.run(debug=True)
