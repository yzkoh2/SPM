def get_status_update_email(task_title, old_status, new_status, changed_by_name, deadline_str, description, is_subtask=False):
    #Generate email template for status update notifications
    task_type = "Subtask" if is_subtask else "Task"
    subject = f"{task_type} Status Updated: {task_title}"
    
    status_colors = {
        'Unassigned': '#94A3B8',
        'Ongoing': '#3B82F6',
        'Under Review': '#F59E0B',
        'Completed': '#10B981'
    }
    
    status_icons = {
        'Unassigned': '📋',
        'Ongoing': '🔄',
        'Under Review': '👀',
        'Completed': '✅'
    }
    
    old_color = status_colors.get(old_status, '#6B7280')
    new_color = status_colors.get(new_status, '#6B7280')
    new_icon = status_icons.get(new_status, '📌')
    
    #Truncate long descriptions
    display_description = description
    if len(description) > 200:
        display_description = description[:197] + "..."
    
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 40px 20px;">
        <table role="presentation" style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 0;">
                    <!-- Main Container -->
                    <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #FFFFFF; border-radius: 16px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); overflow: hidden;">
                        
                        <!-- Header with Gradient -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 32px; text-align: center;">
                                <div style="font-size: 48px; margin-bottom: 12px;">{new_icon}</div>
                                <h1 style="margin: 0; color: #FFFFFF; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">
                                    Status Update
                                </h1>
                                <p style="margin: 8px 0 0 0; color: rgba(255, 255, 255, 0.9); font-size: 14px; font-weight: 500;">
                                    {task_type} • Updated by {changed_by_name}
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px 32px;">
                                
                                <!-- Task Title -->
                                <div style="margin-bottom: 28px;">
                                    <h2 style="margin: 0 0 4px 0; color: #1e293b; font-size: 24px; font-weight: 700; line-height: 1.3;">
                                        {task_title}
                                    </h2>
                                    <div style="height: 3px; width: 60px; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 2px; margin-top: 12px;"></div>
                                </div>
                                
                                <!-- Status Change Card -->
                                <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding: 24px; border-radius: 12px; margin-bottom: 28px; border: 2px solid #e2e8f0;">
                                    <p style="margin: 0 0 16px 0; color: #64748b; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                        Status Transition
                                    </p>
                                    <table role="presentation" style="width: 100%;">
                                        <tr>
                                            <td style="text-align: center; vertical-align: middle;">
                                                <div style="display: inline-block; padding: 10px 20px; background-color: {old_color}; color: white; border-radius: 8px; font-weight: 600; font-size: 14px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);">
                                                    {old_status}
                                                </div>
                                            </td>
                                            <td style="width: 60px; text-align: center; vertical-align: middle;">
                                                <div style="color: #667eea; font-size: 24px; font-weight: 700;">→</div>
                                            </td>
                                            <td style="text-align: center; vertical-align: middle;">
                                                <div style="display: inline-block; padding: 10px 20px; background-color: {new_color}; color: white; border-radius: 8px; font-weight: 600; font-size: 14px; box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2); transform: scale(1.05);">
                                                    {new_status}
                                                </div>
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                                
                                <!-- Description -->
                                <div style="background-color: #fefce8; border-left: 4px solid #facc15; padding: 16px 20px; border-radius: 8px; margin-bottom: 24px;">
                                    <p style="margin: 0 0 6px 0; color: #854d0e; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                                        📝 Description
                                    </p>
                                    <p style="margin: 0; color: #713f12; font-size: 14px; line-height: 1.6;">
                                        {display_description}
                                    </p>
                                </div>
                                
                                <!-- Details Grid -->
                                <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                    <tr>
                                        <td style="padding: 16px 0; border-top: 2px solid #f1f5f9;">
                                            <table role="presentation" style="width: 100%;">
                                                <tr>
                                                    <td style="width: 40px; vertical-align: top;">
                                                        <div style="font-size: 20px;">👤</div>
                                                    </td>
                                                    <td style="vertical-align: top;">
                                                        <p style="margin: 0 0 2px 0; color: #64748b; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                                            Changed By
                                                        </p>
                                                        <p style="margin: 0; color: #1e293b; font-size: 15px; font-weight: 600;">
                                                            {changed_by_name}
                                                        </p>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 16px 0; border-top: 2px solid #f1f5f9;">
                                            <table role="presentation" style="width: 100%;">
                                                <tr>
                                                    <td style="width: 40px; vertical-align: top;">
                                                        <div style="font-size: 20px;">📅</div>
                                                    </td>
                                                    <td style="vertical-align: top;">
                                                        <p style="margin: 0 0 2px 0; color: #64748b; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                                            Deadline
                                                        </p>
                                                        <p style="margin: 0; color: #1e293b; font-size: 15px; font-weight: 600;">
                                                            {deadline_str}
                                                        </p>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                                
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="padding: 24px 32px; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-top: 2px solid #e2e8f0;">
                                <table role="presentation" style="width: 100%;">
                                    <tr>
                                        <td style="text-align: center;">
                                            <p style="margin: 0; color: #64748b; font-size: 12px; line-height: 1.6;">
                                                <strong style="color: #475569;">Task Management System</strong><br>
                                                This is an automated notification. Please do not reply to this email.
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    return subject, body_html

def get_deadline_reminder_email(task_title, days_before, deadline_str, description, task_status, is_subtask=False):
    #Generate modern email template for deadline reminder notifications
    task_type = "Subtask" if is_subtask else "Task"
    
    #Color scheme based on days remaining
    if days_before == 7:
        #Calm Purple/Indigo theme for 7 days
        primary_color = '#6366f1' 
        secondary_color = '#8b5cf6'  
        bg_color = '#f5f3ff'
        light_bg = '#ede9fe'
        icon = '📅'
        urgency_badge = 'In 7 Days'
        message = 'You have a full week to prepare!'
    elif days_before == 3:
        # Warm Amber theme for 3 days
        primary_color = '#f59e0b'  
        secondary_color = '#f97316' 
        bg_color = '#fffbeb'
        light_bg = '#fef3c7'
        icon = '⏰'
        urgency_badge = 'In 3 Days'
        message = 'The deadline is approaching. Stay on track!'
    else:  
        # Vibrant Red theme for 1 day
        primary_color = '#ef4444' 
        secondary_color = '#ec4899' 
        bg_color = '#fef2f2'
        light_bg = '#fee2e2'
        icon = '🔔'
        urgency_badge = 'Final Day'
        message = 'This task is due tomorrow. Time to wrap it up!'
    
    #Truncate description
    display_description = description[:180] + "..." if len(description) > 180 else description
    
    subject = f"{icon} Reminder: {task_title} - Due in {days_before} day{'s' if days_before > 1 else ''}"
    
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f3f4f6; padding: 40px 20px;">
        
        <table role="presentation" style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.08);">
            
            <!-- Header with gradient -->
            <tr>
                <td style="background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%); padding: 50px 40px 30px 40px; text-align: center; position: relative;">
                    
                    <!-- Solid background overlay for better text contrast -->
                    <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.15);"></div>
                    
                    <!-- Decorative elements -->
                    <div style="position: absolute; top: -30px; right: -30px; width: 150px; height: 150px; background: rgba(255,255,255,0.1); border-radius: 50%; opacity: 0.4; z-index: 1;"></div>
                    <div style="position: absolute; bottom: -20px; left: -20px; width: 100px; height: 100px; background: rgba(255,255,255,0.1); border-radius: 50%; opacity: 0.4; z-index: 1;"></div>
                    
                    <div style="position: relative; z-index: 2;">
                        <div style="font-size: 60px; margin-bottom: 8px; line-height: 1; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));">
                            {icon}
                        </div>
                        <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: -0.5px; text-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.4);">
                            Deadline Reminder
                        </h1>
                        <p style="margin: 10px 0 0 0; color: #ffffff; font-size: 16px; font-weight: 500; text-shadow: 0 1px 4px rgba(0,0,0,0.3);">
                            {message}
                        </p>
                    </div>
                </td>
            </tr>
            
            <!-- Content -->
            <tr>
                <td style="padding: 30px 40px 40px 40px;">
                    
                    <!-- Urgency Badge -->
                    <div style="text-align: center; margin-bottom: 35px;">
                        <div style="display: inline-block; background: {bg_color}; border: 2px solid {primary_color}; padding: 12px 30px; border-radius: 25px;">
                            <span style="color: {primary_color}; font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
                                {urgency_badge}
                            </span>
                        </div>
                    </div>
                    
                    <!-- Task Card -->
                    <div style="background: {light_bg}; border-left: 5px solid {primary_color}; border-radius: 12px; padding: 25px; margin-bottom: 30px;">
                        
                        <!-- Task Type Badge -->
                        <div style="margin-bottom: 12px;">
                            <span style="display: inline-block; background: {primary_color}; color: #ffffff; padding: 6px 14px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                                {task_type}
                            </span>
                        </div>
                        
                        <!-- Task Title -->
                        <h2 style="margin: 0 0 15px 0; color: #111827; font-size: 22px; font-weight: 700; line-height: 1.3;">
                            {task_title}
                        </h2>
                        
                        <!-- Description -->
                        <p style="margin: 0; color: #374151; font-size: 15px; line-height: 1.6;">
                            {display_description}
                        </p>
                    </div>
                    
                    <!-- Deadline Info Box -->
                    <div style="background: #ffffff; border: 2px solid {light_bg}; border-radius: 12px; padding: 25px; margin-bottom: 30px;">
                        <table role="presentation" style="width: 100%;">
                            <tr>
                                <td style="width: 50%; padding-right: 15px; border-right: 2px solid {light_bg};">
                                    <p style="margin: 0 0 8px 0; color: #6b7280; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                        Deadline
                                    </p>
                                    <p style="margin: 0; color: #111827; font-size: 16px; font-weight: 700;">
                                        {deadline_str}
                                    </p>
                                </td>
                                <td style="width: 50%; padding-left: 15px;">
                                    <p style="margin: 0 0 8px 0; color: #6b7280; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                        Status
                                    </p>
                                    <p style="margin: 0; color: #111827; font-size: 16px; font-weight: 700;">
                                        {task_status}
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </div>
                    
                    <!-- CTA Section -->
                    <div style="text-align: center; margin-bottom: 20px;">
                        <p style="margin: 0 0 20px 0; color: #374151; font-size: 14px;">
                            Ready to make progress on this task?
                        </p>
                        <a href="#" style="display: inline-block; background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%); color: #ffffff; text-decoration: none; padding: 14px 35px; border-radius: 10px; font-weight: 600; font-size: 15px; box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);">
                            View Task Details
                        </a>
                    </div>
                    
                    <!-- Tips Section -->
                    <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 20px; margin-top: 30px;">
                        <p style="margin: 0 0 10px 0; color: #111827; font-size: 13px; font-weight: 600;">
                            💡 Quick Tips:
                        </p>
                        <ul style="margin: 0; padding-left: 20px; color: #374151; font-size: 13px; line-height: 1.8;">
                            <li>Break down the task into smaller steps</li>
                            <li>Set aside dedicated time to work on it</li>
                            <li>Communicate with your team if you need help</li>
                        </ul>
                    </div>
                    
                </td>
            </tr>
            
            <!-- Footer -->
            <tr>
                <td style="background: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb;">
                    <p style="margin: 0 0 8px 0; color: #111827; font-size: 14px; font-weight: 600;">
                        Task Management System
                    </p>
                    <p style="margin: 0; color: #6b7280; font-size: 12px; line-height: 1.6;">
                        This is an automated reminder. Please do not reply to this email.
                    </p>
                </td>
            </tr>
            
        </table>
        
    </body>
    </html>
    """
    
    return subject, body_html