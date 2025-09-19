from app import create_app

# Create the Flask application instance using the app factory function.
# This 'app' variable is what Gunicorn looks for.
app = create_app()

if __name__ == '__main__':
    # This block runs ONLY when you execute `python run.py` directly.
    # It starts the Flask development server, which is used for local testing.
    # The 'debug=True' flag enables features like auto-reloading and an interactive debugger.
    app.run(debug=True, host='0.0.0.0', port=6000)