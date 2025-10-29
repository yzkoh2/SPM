from ..routes import task_bp 
from . import generator_service as generator
from flask import make_response, jsonify, request
from datetime import datetime

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

@task_bp.route('/reports/project/<int:project_id>', methods=['GET'])
def get_project_report(project_id):
    """
    Generates a PDF report for a specific project.
    The user_id must be passed as a query parameter.
    e.g., GET /reports/project/1?user_id=123
    """
    
    # --- 1. Get user_id from query parameter ---
    # This is required for authorization in your generator service
    user_id_str = request.args.get('user_id')
    if not user_id_str:
        return jsonify({"error": "Missing 'user_id' query parameter"}), 400
        
    try:
        user_id = int(user_id_str)
    except ValueError:
        return jsonify({"error": "'user_id' must be an integer"}), 400

    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    start_date = None
    end_date = None

    try:
        if start_date_str:
            # Add time component to start of the day
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
        if end_date_str:
            # Add time component to end of the day
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            
        if start_date and end_date and start_date > end_date:
             return jsonify({"error": "start_date cannot be after end_date"}), 400

    except ValueError:
        return jsonify({"error": "Date format must be YYYY-MM-DD"}), 400

    # --- 2. Call Generator Service ---
    try:
        # Call the correct function from your generator
        pdf_data, error = generator.generate_project_pdf_report(
            project_id=project_id, 
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Check if the generator itself had an error
        if error:
            print(f"Report generation failed with error: {error}")
            # pdf_data might contain an HTML error page, but we'll return JSON
            return jsonify({"error": f"Report could not be generated: {error}"}), 500

        # Check if data is missing (should be caught by 'error' but as a safeguard)
        if not pdf_data:
             return jsonify({"error": "Report generation resulted in empty data."}), 500

        # --- 4. Create and send the file response ---
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=project_{project_id}_report.pdf'
        
        return response

    except Exception as e:
        print(f"Unhandled error in get_project_report: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500