import os
import base64
import io
from flask import (
    Flask, render_template, request, redirect, url_for, flash, session, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user, login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp # For 2FA
import qrcode # For 2FA QR codes

# --- Configuration ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'db.sqlite3')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) # Crucial for session security
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Database Setup ---
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False) # Store hash, not plain password
    cash = db.Column(db.Float, default=0.0)
    symbol = db.Column(db.String(10))
    stock_count = db.Column(db.Integer, default=0)
    portfolio_value = db.Column(db.Float, default=0.0)
    level = db.Column(db.Integer, default=1)
    user_tier = db.Column(db.String(50), default="Bronze")
    otp_secret = db.Column(db.String(16), unique=True) # 2FA secret key
    is_2fa_enabled = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        # Hash the password for security
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # Check hashed password
        return check_password_hash(self.password_hash, password)

    def get_totp_uri(self):
        # Generate URI for authenticator apps
        return pyotp.totp.TOTP(self.otp_secret).provisioning_uri(
            name=self.username, issuer_name="YourAppName" # Customize app name
        )

    def verify_totp(self, token):
        # Verify the 2FA code
        return pyotp.TOTP(self.otp_secret).verify(token)

    # Required by Flask-Login
    def get_id(self):
        return str(self.id)

# --- Login Manager Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index' # Redirect to index if login required
login_manager.login_message = "로그인이 필요한 서비스입니다."
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    # Load user from database for session management
    return User.query.get(int(user_id))

# --- Routes ---
@app.route('/')
def index():
    # Main page showing login/register options if not logged in
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    # Handle registration form submission from the modal
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    terms_accepted = request.form.get('terms_accepted')

    if not all([username, password, confirm_password]):
        flash('모든 필수 항목을 입력해주세요.', 'danger')
        return redirect(url_for('index'))

    if password != confirm_password:
        flash('비밀번호가 일치하지 않습니다.', 'warning')
        return redirect(url_for('index'))

    if not terms_accepted:
        flash('이용약관 및 개인정보처리방침에 동의해야 합니다.', 'warning')
        return redirect(url_for('index'))

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash('이미 사용 중인 사용자 이름입니다.', 'warning')
        return redirect(url_for('index'))

    # Create new user
    new_user = User(username=username)
    new_user.set_password(password) # Hash the password
    # Set initial values (optional, can be done later)
    new_user.cash = 1500000 # Example initial cash
    new_user.portfolio_value = new_user.cash
    new_user.level = 1
    new_user.user_tier = "Bronze"
    # Generate a unique OTP secret for 2FA setup later
    new_user.otp_secret = pyotp.random_base32()

    try:
        db.session.add(new_user)
        db.session.commit()
        flash(f'{username}님, 회원가입 성공! 로그인해주세요.', 'success')
        # Optional: Log the user in directly or redirect to 2FA setup
        # login_user(new_user)
        # return redirect(url_for('setup_2fa'))
        return redirect(url_for('index')) # Redirect to login after registration
    except Exception as e:
        db.session.rollback()
        flash(f'회원가입 중 오류 발생: {e}', 'danger')
        return redirect(url_for('index'))


@app.route('/login', methods=['POST'])
def login():
    # Handle login form submission from the modal
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False # Optional "remember me"

    if not username or not password:
        flash('아이디와 비밀번호를 모두 입력해주세요.', 'warning')
        return redirect(url_for('index'))

    user = User.query.filter_by(username=username).first()

    # Check if user exists and password is correct
    if not user or not user.check_password(password):
        flash('사용자 이름 또는 비밀번호가 잘못되었습니다.', 'danger')
        return redirect(url_for('index'))

    # --- 2FA Check ---
    if user.is_2fa_enabled:
        # Store user ID in session to verify 2FA on the next step
        session['user_id_awaiting_2fa'] = user.id
        session['remember_me_awaiting_2fa'] = remember
        flash('2단계 인증 코드를 입력해주세요.', 'info')
        return redirect(url_for('verify_2fa'))
    else:
        # Log in user directly if 2FA is not enabled
        login_user(user, remember=remember)
        flash(f'{user.username}님, 로그인 성공!', 'success')
        return redirect(url_for('dashboard'))


@app.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    # Handle 2FA code verification after username/password check
    user_id = session.get('user_id_awaiting_2fa')
    if not user_id:
        # If session variable is missing, redirect to login
        flash("인증 세션이 만료되었습니다. 다시 로그인해주세요.", "warning")
        return redirect(url_for('index'))

    user = User.query.get(user_id)
    if not user:
        flash("사용자 정보를 찾을 수 없습니다.", "danger")
        session.pop('user_id_awaiting_2fa', None) # Clean up session
        return redirect(url_for('index'))

    if request.method == 'POST':
        token = request.form.get('otp_token')
        if not token:
            flash("2단계 인증 코드를 입력해주세요.", "warning")
            return render_template('verify_2fa.html')

        if user.verify_totp(token):
            # 2FA code is correct, log the user in
            remember = session.get('remember_me_awaiting_2fa', False)
            login_user(user, remember=remember)
            # Clear temporary session variables
            session.pop('user_id_awaiting_2fa', None)
            session.pop('remember_me_awaiting_2fa', None)
            flash(f'{user.username}님, 로그인 성공!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('잘못된 2단계 인증 코드입니다.', 'danger')
            return render_template('verify_2fa.html') # Show form again

    # Show the 2FA verification form on GET request
    return render_template('verify_2fa.html')


@app.route('/logout')
@login_required # Ensure user is logged in to logout
def logout():
    # Log the user out
    logout_user()
    flash('로그아웃 되었습니다.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required # Protect this route
def dashboard():
    # Show user dashboard after successful login
    # Data is accessed via current_user proxy from Flask-Login
    return render_template('dashboard.html', user=current_user)


@app.route('/setup_2fa', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    # Handle 2FA setup process
    if current_user.is_2fa_enabled:
        flash("2단계 인증이 이미 활성화되어 있습니다.", "info")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # Verify the token entered by the user to confirm setup
        token = request.form.get('otp_token')
        secret = session.get('otp_secret_for_setup') # Get secret stored temporarily

        if not token or not secret:
             flash("인증 코드를 입력해주세요.", "warning")
             # Regenerate QR code data if needed or redirect
             return redirect(url_for('setup_2fa')) # Re-render the setup page


        # Use the stored secret to verify
        totp = pyotp.TOTP(secret)
        if totp.verify(token):
            # Verification successful, enable 2FA for the user
            user = User.query.get(current_user.id)
            user.is_2fa_enabled = True
            # user.otp_secret is already set during registration or GET request below
            db.session.commit()
            session.pop('otp_secret_for_setup', None) # Clean up temporary secret
            flash('2단계 인증 설정이 완료되었습니다!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('잘못된 인증 코드입니다. 다시 시도해주세요.', 'danger')
            # Re-render the setup page with the same QR code/secret
            return redirect(url_for('setup_2fa'))

    # --- GET Request Logic ---
    # Generate QR code for the user's secret
    # Ensure the user has an OTP secret (should be generated at registration)
    if not current_user.otp_secret:
        current_user.otp_secret = pyotp.random_base32()
        db.session.commit() # Save the newly generated secret immediately

    # Store the secret in the session temporarily for verification on POST
    session['otp_secret_for_setup'] = current_user.otp_secret

    # Generate TOTP URI and QR Code
    uri = current_user.get_totp_uri()
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    qr_code_data = base64.b64encode(buf.getvalue()).decode('ascii')

    return render_template('setup_2fa.html', qr_code_data=qr_code_data, secret=current_user.otp_secret)

# --- Helper to create DB ---
def create_db():
    """Creates database tables if they don't exist."""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created (if they didn't exist).")

# --- Run the App ---
if __name__ == '__main__':
    if not os.path.exists(DATABASE_PATH):
        create_db()
    app.run(debug=True) # Enable debug mode for development