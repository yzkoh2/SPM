from ..routes import task_bp 
from . import generator_service as generator
from flask import make_response, jsonify, request
from datetime import datetime
import pytz

@task_bp.route('/reports/team/<int:team_id>', methods=['GET'])
def get_team_report(team_id):
    """
    Generates a PDF report for a specific team.
    """
    try:
        # Call your generator function to get the raw PDF data
        pdf_data = generator.get_project_by_id(team_id)

        # Create a Flask response to send the file
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=team_{team_id}_report.pdf'
        
        return response

    except Exception as e:
        print(f"Error generating report: {e}")
        return jsonify({"error": "Could not generate report"}), 500

@task_bp.route('/reports/project/<int:project_id>', methods=['POST'])
def get_project_report(project_id):
    """
    Generates a PDF report for a specific project.
    user_id must be in query params.
    start_date, end_date (in user's timezone), and timezone are in the JSON body.
    """
    
    # --- 1. Get user_id from query parameter ---
    user_id_str = request.args.get('user_id')
    if not user_id_str:
        return jsonify({"error": "Missing 'user_id' query parameter"}), 400
    try:
        user_id = int(user_id_str) # Corrected variable name
    except ValueError:
        return jsonify({"error": "'user_id' must be an integer"}), 400

    
    # --- 2. Get Dates and Timezone from JSON Request Body ---
    start_date_str = None
    end_date_str = None
    timezone_str = None 
    
    data = request.get_json()
    if data:
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        timezone_str = data.get('timezone') 
    
    # Default to UTC if no timezone is provided
    if not timezone_str:
        timezone_str = "UTC"

    # --- 3. Parse Dates and Convert to UTC for Querying ---
    utc_start_date = None
    utc_end_date = None
    try:
        # Get the timezone object
        user_tz = pytz.timezone(timezone_str)
    except pytz.exceptions.UnknownTimeZoneError:
        print(f"Unknown timezone '{timezone_str}' received in request. Defaulting to UTC.")
        user_tz = pytz.utc
        timezone_str = "UTC" # Correct the string if it was invalid

    try:
        if start_date_str:
            # Create a naive datetime first
            naive_start = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            # Localize it to the user's timezone
            user_start_date = user_tz.localize(naive_start)
            # Convert to UTC
            utc_start_date = user_start_date.astimezone(pytz.utc)

        if end_date_str:
            # Create a naive datetime first
            naive_end = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
             # Localize it to the user's timezone
            user_end_date = user_tz.localize(naive_end)
            # Convert to UTC
            utc_end_date = user_end_date.astimezone(pytz.utc)
            
        # Basic validation
        if utc_start_date and utc_end_date and utc_start_date > utc_end_date:
             return jsonify({"error": "start_date cannot be after end_date"}), 400
        if (utc_start_date and not utc_end_date) or (utc_end_date and not utc_start_date):
            return jsonify({"error": "Both 'start_date' and 'end_date' must be provided together"}), 400

    except ValueError:
        return jsonify({"error": "Date format must be YYYY-MM-DD"}), 400
    except pytz.exceptions.AmbiguousTimeError:
         return jsonify({"error": f"Ambiguous timestamp provided near DST change in {timezone_str}. Please clarify."}), 400
    except pytz.exceptions.NonExistentTimeError:
        return jsonify({"error": f"Non-existent timestamp provided near DST change in {timezone_str}. Please use a valid time."}), 400


    # --- 4. Call Generator Service ---
    try:
        # Pass the UTC datetimes for filtering, and the timezone string for display
        print(f"DEBUG: routes.py - Calculated utc_start_date: {utc_start_date}")
        print(f"DEBUG: routes.py - Calculated utc_end_date: {utc_end_date}")
        print(f"DEBUG: routes.py - Passing timezone_str: {timezone_str}")
        # Call generator...
        pdf_data, error = generator.generate_project_pdf_report(
            project_id=project_id, 
            user_id=user_id,
            # Use the UTC datetimes here
            start_date=utc_start_date, 
            end_date=utc_end_date,   
            # Keep passing the original timezone string for display formatting
            timezone_str=timezone_str  
        )
        
        if error:
            print(f"Report generation failed with error: {error}")
            return jsonify({"error": f"Report could not be generated: {error}"}), 500
        if not pdf_data:
             return jsonify({"error": "Report generation resulted in empty data."}), 500

        # --- 5. Create and send the file response ---
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=project_{project_id}_report.pdf'
        
        return response

    except Exception as e:
        print(f"Unhandled error in get_project_report: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500