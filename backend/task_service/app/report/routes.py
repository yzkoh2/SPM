from fileinput import filename
from ..routes import task_bp 
from . import generator_service as generator
from flask import make_response, jsonify, request
from datetime import datetime
import pytz

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
    end_datetime_str = None
    timezone_str = None

    data = request.get_json()
    if data:
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        end_datetime_str = data.get('end_datetime')  # ISO format datetime if provided
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

        # Check if end_datetime is provided (current datetime for "today")
        if end_datetime_str:
            # Parse ISO datetime string (from JavaScript toISOString(), already in UTC)
            # Format: 2025-11-03T08:30:45.123Z
            end_datetime = datetime.fromisoformat(end_datetime_str.replace('Z', '+00:00'))
            # Already in UTC, just ensure it's timezone-aware
            utc_end_date = end_datetime.astimezone(pytz.utc)
            print(f"DEBUG: Using current datetime - end_datetime_str: {end_datetime_str}, utc_end_date: {utc_end_date}")
        elif end_date_str:
            # Use end of day (23:59:59) in user's timezone
            naive_end = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            # Localize it to the user's timezone
            user_end_date = user_tz.localize(naive_end)
            # Convert to UTC
            utc_end_date = user_end_date.astimezone(pytz.utc)
            print(f"DEBUG: Using end of day - end_date_str: {end_date_str}, utc_end_date: {utc_end_date}")

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

    # --- 2. Get Dates and Timezone from JSON Request Body ---
    start_date_str = None
    end_date_str = None
    end_datetime_str = None
    timezone_str = None

    data = request.get_json()
    if data:
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        end_datetime_str = data.get('end_datetime')  # ISO format datetime if provided
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

        # Check if end_datetime is provided (current datetime for "today")
        if end_datetime_str:
            # Parse ISO datetime string (from JavaScript toISOString(), already in UTC)
            # Format: 2025-11-03T08:30:45.123Z
            end_datetime = datetime.fromisoformat(end_datetime_str.replace('Z', '+00:00'))
            # Already in UTC, just ensure it's timezone-aware
            utc_end_date = end_datetime.astimezone(pytz.utc)
            print(f"DEBUG: Using current datetime - end_datetime_str: {end_datetime_str}, utc_end_date: {utc_end_date}")
        elif end_date_str:
            # Use end of day (23:59:59) in user's timezone
            naive_end = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            user_end_date = user_tz.localize(naive_end)
            utc_end_date = user_end_date.astimezone(pytz.utc)
            print(f"DEBUG: Using end of day - end_date_str: {end_date_str}, utc_end_date: {utc_end_date}")

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

@task_bp.route('/reports/history/<int:user_id>', methods=['GET'])
def retrieve_all_reports(user_id):
    """
    Retrieves all report metadata for a specific user.
    """
    try:
        # This list is NOW a list of JSON-ready dicts, enriched with names
        reports_json_list, error = generator.get_all_reports_for_user(user_id)
        
        if error:
            return jsonify({"error": error}), 500
        
        # We don't need to call .to_json() anymore, just return the list
        return jsonify(reports_json_list), 200
        
    except Exception as e:
        print(f"Unhandled error in retrieve_all_reports: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500

@task_bp.route('/reports/retrieve/<int:report_id>', methods=['GET'])
def retrieve_report(report_id):
    """
    Retrieves a specific report file by its ID.
    """
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing 'user_id' query parameter"}), 400
    
    try:
        presigned_url, error = generator.get_report_by_id(report_id, user_id)
        
        if error:
            return jsonify({"error": error}), 500
        if not presigned_url:
            return jsonify({"error": "Report file is empty or could not be retrieved."}), 404

        return jsonify({"url": presigned_url}), 200

    except Exception as e:
        print(f"Unhandled error in retrieve_report: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500

@task_bp.route('/reports/delete/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    """
    Deletes a specific report by its ID.
    """
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing 'user_id' query parameter"}), 400
    try:
        success, error = generator.delete_report_by_id(report_id, user_id)
        
        if error:
            return jsonify({"error": error}), 500
        if not success:
            return jsonify({"error": "Report could not be deleted."}), 404

        return jsonify({"message": "Report deleted successfully."}), 200

    except Exception as e:
        print(f"Unhandled error in delete_report: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500