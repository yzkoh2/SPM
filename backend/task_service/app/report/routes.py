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

    # --- 2. RBAC Authorization - Check if user is owner or collaborator ---
    from app import models
    try:
        project = models.Project.query.get(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404

        # Get project collaborators (including owner)
        project_owner_id = project.owner_id
        project_collaborator_ids = project.collaborator_ids()  # Returns list of collaborator IDs

        # Check if requesting user is owner or collaborator
        is_owner = (user_id == project_owner_id)
        is_collaborator = (user_id in project_collaborator_ids)

        if not (is_owner or is_collaborator):
            return jsonify({"error": "Unauthorized: Only project owner and collaborators can generate project reports"}), 403

        print(f"User {user_id} authorized to generate report for project {project_id} (Owner: {is_owner}, Collaborator: {is_collaborator})")

    except Exception as e:
        print(f"Error checking project authorization: {e}")
        return jsonify({"error": "Authorization check failed"}), 500

    # --- 3. Get Dates and Timezone from JSON Request Body ---
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

    # --- 4. Parse Dates and Convert to UTC for Querying ---
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


    # --- 5. Call Generator Service ---
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

        # --- 6. Create and send the file response ---
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=project_{project_id}_report.pdf'
        
        return response

    except Exception as e:
        print(f"Unhandled error in get_project_report: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500


@task_bp.route('/reports/individual/<int:user_id>', methods=['POST'])
def get_individual_report(user_id):
    """
    Generates a PDF report for an individual user's task performance.
    user_id in URL is the target user whose report is being generated.
    requesting_user_id must be in query params (for authorization).
    start_date, end_date (in user's timezone), and timezone are in the JSON body.
    """

    # --- 1. Get requesting_user_id from query parameter (for authorization) ---
    requesting_user_id_str = request.args.get('requesting_user_id')
    if not requesting_user_id_str:
        return jsonify({"error": "Missing 'requesting_user_id' query parameter"}), 400
    try:
        requesting_user_id = int(requesting_user_id_str)
    except ValueError:
        return jsonify({"error": "'requesting_user_id' must be an integer"}), 400

    # --- 2. RBAC Authorization ---
    # Fetch requesting user details
    requesting_user = generator._fetch_user_details(requesting_user_id)
    if "Not Found" in requesting_user['name'] or "Service Down" in requesting_user['name']:
        return jsonify({"error": "Could not verify requesting user"}), 403

    requesting_user_role = requesting_user['role']

    # Authorization logic based on role
    if requesting_user_role == 'Staff':
        # Staff can only generate their own report
        if requesting_user_id != user_id:
            return jsonify({"error": "Unauthorized: Staff can only generate their own reports"}), 403

    elif requesting_user_role == 'Manager':
        # Manager can generate reports for their team members
        if requesting_user_id != user_id:  # If not generating own report
            # Fetch requesting user's full details to get team_id
            import requests
            try:
                user_service_url = current_app.config.get('USER_SERVICE_URL', 'http://spm_user_service:6000')
                req_user_response = requests.get(f"{user_service_url}/user/{requesting_user_id}", timeout=5)
                target_user_response = requests.get(f"{user_service_url}/user/{user_id}", timeout=5)

                if req_user_response.status_code != 200 or target_user_response.status_code != 200:
                    return jsonify({"error": "Could not verify user relationships"}), 403

                req_user_data = req_user_response.json()
                target_user_data = target_user_response.json()

                # Check if target user is in the same team
                if req_user_data.get('team_id') != target_user_data.get('team_id'):
                    return jsonify({"error": "Unauthorized: Managers can only generate reports for their team members"}), 403
            except Exception as e:
                print(f"Error verifying team membership: {e}")
                return jsonify({"error": "Authorization check failed"}), 500

    elif requesting_user_role == 'Director':
        # Director can generate reports for their department members
        if requesting_user_id != user_id:  # If not generating own report
            import requests
            try:
                user_service_url = current_app.config.get('USER_SERVICE_URL', 'http://spm_user_service:6000')
                req_user_response = requests.get(f"{user_service_url}/user/{requesting_user_id}", timeout=5)
                target_user_response = requests.get(f"{user_service_url}/user/{user_id}", timeout=5)

                if req_user_response.status_code != 200 or target_user_response.status_code != 200:
                    return jsonify({"error": "Could not verify user relationships"}), 403

                req_user_data = req_user_response.json()
                target_user_data = target_user_response.json()

                # Check if target user is in the same department
                if req_user_data.get('department_id') != target_user_data.get('department_id'):
                    return jsonify({"error": "Unauthorized: Directors can only generate reports for their department members"}), 403
            except Exception as e:
                print(f"Error verifying department membership: {e}")
                return jsonify({"error": "Authorization check failed"}), 500

    elif requesting_user_role in ['HR', 'Senior Management']:
        # HR and Senior Management can generate reports for anyone - no additional checks needed
        pass

    else:
        # Unknown role - deny access
        return jsonify({"error": f"Unauthorized: Unknown role '{requesting_user_role}'"}), 403

    # --- 3. Get Dates and Timezone from JSON Request Body ---
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
        timezone_str = "UTC"

    try:
        if start_date_str:
            naive_start = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            user_start_date = user_tz.localize(naive_start)
            utc_start_date = user_start_date.astimezone(pytz.utc)

        if end_date_str:
            naive_end = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            user_end_date = user_tz.localize(naive_end)
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
        print(f"DEBUG: routes.py - Calculated utc_start_date: {utc_start_date}")
        print(f"DEBUG: routes.py - Calculated utc_end_date: {utc_end_date}")
        print(f"DEBUG: routes.py - Passing timezone_str: {timezone_str}")

        pdf_data, error = generator.generate_individual_pdf_report(
            target_user_id=user_id,
            requesting_user_id=requesting_user_id,
            start_date=utc_start_date,
            end_date=utc_end_date,
            timezone_str=timezone_str
        )

        if error:
            print(f"Report generation failed with error: {error}")
            return jsonify({"error": f"Report could not be generated: {error}"}), 500
        if not pdf_data:
             return jsonify({"error": "Report generation resulted in empty data."}), 500

        # --- 5. Create and send the file response ---
        # Get user details for filename
        from app import service as task_service
        user_cache = {}
        if user_id not in user_cache:
            user_cache[user_id] = generator._fetch_user_details(user_id)
        user_name_clean = user_cache[user_id]['name'].replace(' ', '')
        report_date = datetime.now(pytz.timezone(timezone_str)).strftime('%d%m%Y')

        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={user_name_clean}IndividualTaskPerformanceReport_{report_date}.pdf'

        return response

    except Exception as e:
        print(f"Unhandled error in get_individual_report: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500