from datetime import datetime
from .models import db, Project, ProjectCollaboratorLink
from sqlalchemy import or_

class ProjectService:
    """Service class for project-related business logic"""
    
    @staticmethod
    def create_project(name, owner_id, description=None, deadline=None):
        """
        Create a new project
        
        Args:
            name (str): Project name
            owner_id (int): User ID of the project owner
            description (str, optional): Project description
            deadline (str or datetime, optional): Project deadline
            
        Returns:
            Project: Created project object
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        if not name or not name.strip():
            raise ValueError("Project name cannot be empty")
        
        if not owner_id:
            raise ValueError("Owner ID is required")
        
        # Parse deadline if provided as string
        deadline_dt = None
        if deadline:
            if isinstance(deadline, str):
                try:
                    deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                except ValueError:
                    raise ValueError("Invalid deadline format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
            else:
                deadline_dt = deadline
        
        # Create project
        project = Project(
            name=name.strip(),
            description=description.strip() if description else None,
            deadline=deadline_dt,
            owner_id=owner_id
        )
        
        db.session.add(project)
        db.session.commit()
        
        return project
    
    @staticmethod
    def update_project(project_id, user_id, name=None, description=None, deadline=None):
        """
        Update project details (only owner can update)
        
        Args:
            project_id (int): Project ID to update
            user_id (int): User ID attempting the update
            name (str, optional): New project name
            description (str, optional): New project description
            deadline (str or datetime, optional): New project deadline
            
        Returns:
            Project: Updated project object
            
        Raises:
            ValueError: If project not found
            PermissionError: If user is not the project owner
        """
        project = Project.query.get(project_id)
        
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # Check if user is the owner
        if project.owner_id != user_id:
            raise PermissionError("Only the project owner can update project details")
        
        # Update fields if provided
        if name is not None:
            if not name.strip():
                raise ValueError("Project name cannot be empty")
            project.name = name.strip()
        
        if description is not None:
            project.description = description.strip() if description else None
        
        if deadline is not None:
            if isinstance(deadline, str):
                try:
                    project.deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                except ValueError:
                    raise ValueError("Invalid deadline format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
            else:
                project.deadline = deadline
        
        db.session.commit()
        
        return project
    
    @staticmethod
    def get_project_by_id(project_id):
        """
        Get a project by ID
        
        Args:
            project_id (int): Project ID
            
        Returns:
            Project: Project object
            
        Raises:
            ValueError: If project not found
        """
        project = Project.query.get(project_id)
        
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        return project
    
    @staticmethod
    def get_user_projects(user_id, role_filter=None):
        """
        Get all projects a user is involved in
        
        Args:
            user_id (int): User ID
            role_filter (str, optional): Filter by role ('owner' or 'collaborator')
            
        Returns:
            list: List of project dictionaries with role information
        """
        projects_data = []
        
        if role_filter == 'owner':
            # Get only projects owned by user
            owned_projects = Project.query.filter_by(owner_id=user_id).all()
            for project in owned_projects:
                project_dict = project.to_dict()
                project_dict['user_role'] = 'owner'
                projects_data.append(project_dict)
        
        elif role_filter == 'collaborator':
            # Get only projects where user is a collaborator
            collaborations = ProjectCollaboratorLink.query.filter_by(user_id=user_id).all()
            for collab in collaborations:
                project_dict = collab.project.to_dict()
                project_dict['user_role'] = collab.role or 'collaborator'
                projects_data.append(project_dict)
        
        else:
            # Get all projects (owned + collaborating)
            # First, get owned projects
            owned_projects = Project.query.filter_by(owner_id=user_id).all()
            for project in owned_projects:
                project_dict = project.to_dict()
                project_dict['user_role'] = 'owner'
                projects_data.append(project_dict)
            
            # Then, get projects where user is a collaborator
            collaborations = ProjectCollaboratorLink.query.filter_by(user_id=user_id).all()
            for collab in collaborations:
                project_dict = collab.project.to_dict()
                project_dict['user_role'] = collab.role or 'collaborator'
                projects_data.append(project_dict)
        
        return projects_data
    
    @staticmethod
    def delete_project(project_id, user_id):
        """
        Delete a project (only owner can delete)
        
        Args:
            project_id (int): Project ID to delete
            user_id (int): User ID attempting the deletion
            
        Raises:
            ValueError: If project not found
            PermissionError: If user is not the project owner
        """
        project = Project.query.get(project_id)
        
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # Check if user is the owner
        if project.owner_id != user_id:
            raise PermissionError("Only the project owner can delete the project")
        
        # Delete project (cascade will handle related records)
        db.session.delete(project)
        db.session.commit()