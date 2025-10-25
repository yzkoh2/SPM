from ..routes import task_bp 
from . import generator_service as generator
from flask import make_response, jsonify, request

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

# You can add more report routes here...
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

    # --- 2. Call Generator Service ---
    try:
        # Call the correct function from your generator
        pdf_data = generator.generate_project_pdf_report(
            project_id=project_id, 
            user_id=user_id
        )
        
        # Check if generator failed (e.g., auth error, project not found)
        if pdf_data is None:
            return jsonify({"error": "Report could not be generated. Check permissions or project ID."}), 404

        # --- 3. Create and send the file response ---
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=project_{project_id}_report.pdf'
        
        return response

    except Exception as e:
        print(f"Unhandled error in get_project_report: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500