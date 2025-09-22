from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, CleanTrack, ComplaintUpdate, Admin, ContactMessage
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'cleantrack@123' 
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cleantrack.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/complaint_submission", methods=["GET", "POST"])
def submission():
    if 'user_id' not in session:
        flash('Please login to submit a complaint', 'warning')
        return redirect(url_for('login'))
    if request.method == "POST":
        user = User.query.get(session['user_id'])
        submission = CleanTrack(
            email_id = request.form["email_id"],
            name = request.form["name"],
            address = request.form["address"],
            description = request.form["description"],
            user_id = user.id
        )
        db.session.add(submission)
        db.session.commit()
        flash('Complaint submitted successfully!', 'success')
        return redirect(url_for('dashboard'))  
    return render_template('submission_form.html')

@app.route('/waste_warrior')
def waste_warrior():
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('login'))
    complaints = CleanTrack.query.order_by(CleanTrack.date_listed.desc()).all()
    return render_template('waste_warrior.html', complaints=complaints)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            if user.is_admin:
                return redirect(url_for('waste_warrior'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    page = request.args.get('page', 1, type=int)  
    per_page = 5  
    total_complaints = CleanTrack.query.count()
    resolved_complaints = CleanTrack.query.filter_by(status='Resolved').count()
    in_progress = CleanTrack.query.filter_by(status='In Progress').count()
    pending_complaints = total_complaints - resolved_complaints - in_progress
    complaints = CleanTrack.query.order_by(
        CleanTrack.date_listed.desc()
    ).paginate(page=page, per_page=per_page)
    
    return render_template('dashboard.html',
        total_complaints=total_complaints,
        resolved_complaints=resolved_complaints,
        in_progress=in_progress,
        pending_complaints=pending_complaints,
        complaints=complaints.items,
        page=page,
        total_pages=complaints.pages
    )

@app.route('/admin/dashboard')
def admin_dashboard():
    user = get_current_user()
    if not user or not user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('login'))
    
    complaints = CleanTrack.query.all()
    return render_template('waste_warrior.html', complaints=complaints)

@app.route('/admin/update/<int:complaint_id>', methods=['POST'])
def update_complaint(complaint_id):
    admin = get_current_user()
    if not admin or not admin.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('login'))
    
    complaint = CleanTrack.query.get_or_404(complaint_id)
    update = ComplaintUpdate(
        complaint_id=complaint.id,
        admin_id=admin.id,
        status_change=request.form['status'],
        update_text=request.form['remark']
        )
    complaint.status = request.form['status']
    
    db.session.add(update)
    db.session.commit()
    flash('Complaint updated!', 'success')
    return redirect(url_for('waste_warrior'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

def create_admin():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='rifasaudagar@gmail.com').first():
            admin = User(
                email='rifasaudagar@gmail.com',
                is_admin=True
            )
            admin.set_password('Rifa1234')
            db.session.add(admin)
            db.session.commit()
            print('Admin user created!')
            
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        message = request.form.get("message")

        if not name or not phone or not email or not message:
            flash("All fields are required!", "error")
            return redirect(url_for("contact"))

        new_msg = ContactMessage(
            name=name,
            phone=phone,
            email=email,
            message=message
        )
        db.session.add(new_msg)
        db.session.commit()

        flash("✅ Your message has been sent successfully!", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(host='0.0.0.0', port=5000, debug=True)