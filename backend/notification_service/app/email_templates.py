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
    #Generate email template for deadline reminder notifications
    task_type = "Subtask" if is_subtask else "Task"
    
    #Urgency configuration based on days remaining
    if days_before == 7:
        urgency_color = '#3B82F6'  #Blue
        urgency_bg = '#EFF6FF'
        urgency_icon = '📌'
        urgency_text = 'UPCOMING'
        urgency_gradient = 'linear-gradient(135deg, #60A5FA, #3B82F6)'
        border_color = '#DBEAFE'
    elif days_before == 3:
        urgency_color = '#F59E0B'  #Orange
        urgency_bg = '#FFFBEB'
        urgency_icon = '⚠️'
        urgency_text = 'IMPORTANT'
        urgency_gradient = 'linear-gradient(135deg, #FBBF24, #F59E0B)'
        border_color = '#FEF3C7'
    else:  # 1 day
        urgency_color = '#EF4444'  #Red
        urgency_bg = '#FEF2F2'
        urgency_icon = '🚨'
        urgency_text = 'URGENT'
        urgency_gradient = 'linear-gradient(135deg, #F87171, #EF4444)'
        border_color = '#FEE2E2'
    
    subject = f"{urgency_icon} Reminder: {task_title} - Due in {days_before} day{'s' if days_before > 1 else ''}!"
    
    #Truncate description
    display_description = description[:197] + "..." if len(description) > 200 else description
    
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, {urgency_bg} 0%, #FFFFFF 100%); min-height: 100vh; padding: 40px 20px;">
        <table role="presentation" style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 0;">
                    
                    <!-- Main Container -->
                    <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #FFFFFF; border-radius: 16px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); overflow: hidden; border: 4px solid {border_color};">
                        
                        <!-- Urgency Top Strip -->
                        <tr>
                            <td style="height: 8px; background: {urgency_gradient};"></td>
                        </tr>
                        
                        <!-- Header -->
                        <tr>
                            <td style="background: {urgency_gradient}; padding: 48px 32px; text-align: center; position: relative;">
                                
                                <!-- Decorative circles -->
                                <div style="position: absolute; top: 20px; left: 20px; width: 80px; height: 80px; background: rgba(255,255,255,0.15); border-radius: 50%;"></div>
                                <div style="position: absolute; bottom: 20px; right: 20px; width: 60px; height: 60px; background: rgba(255,255,255,0.15); border-radius: 50%;"></div>
                                
                                <!-- Icon -->
                                <div style="position: relative; z-index: 10; font-size: 64px; margin-bottom: 16px; filter: drop-shadow(0 6px 16px rgba(0,0,0,0.3));">
                                    {urgency_icon}
                                </div>
                                
                                <h1 style="position: relative; z-index: 10; margin: 0; color: #FFFFFF; font-size: 32px; font-weight: 800; letter-spacing: -1px; text-shadow: 0 4px 16px rgba(0,0,0,0.2);">
                                    Deadline Reminder
                                </h1>
                                <p style="position: relative; z-index: 10; margin: 12px 0 0 0; color: rgba(255, 255, 255, 0.95); font-size: 18px; font-weight: 700;">
                                    Due in {days_before} day{'s' if days_before > 1 else ''}!
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px 32px;">
                                
                                <!-- Urgency Badge -->
                                <div style="text-align: center; margin-bottom: 32px;">
                                    <div style="display: inline-block; background: {urgency_gradient}; padding: 12px 32px; border-radius: 12px; box-shadow: 0 8px 24px {urgency_color}40;">
                                        <span style="color: white; font-size: 14px; font-weight: 800; text-transform: uppercase; letter-spacing: 1.5px; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                                            {urgency_text}
                                        </span>
                                    </div>
                                </div>
                                
                                <!-- Task Info -->
                                <div style="margin-bottom: 28px;">
                                    <div style="display: inline-block; background: linear-gradient(135deg, #667eea, #764ba2); padding: 6px 14px; border-radius: 6px; margin-bottom: 12px;">
                                        <span style="color: white; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px;">
                                            {task_type}
                                        </span>
                                    </div>
                                    <h2 style="margin: 0 0 4px 0; color: #1e293b; font-size: 24px; font-weight: 700; line-height: 1.3;">
                                        {task_title}
                                    </h2>
                                    <div style="height: 3px; width: 60px; background: {urgency_gradient}; border-radius: 2px; margin-top: 12px;"></div>
                                </div>
                                
                                <!-- Countdown Box -->
                                <div style="background: linear-gradient(135deg, {urgency_bg} 0%, #FFFFFF 100%); border-radius: 16px; padding: 32px; margin-bottom: 28px; border: 3px solid {border_color}; box-shadow: 0 8px 24px {urgency_color}15; text-align: center;">
                                    <p style="margin: 0 0 16px 0; color: #64748b; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                                        ⏰ Deadline
                                    </p>
                                    <div style="background: {urgency_gradient}; padding: 20px 32px; border-radius: 12px; display: inline-block; box-shadow: 0 10px 30px {urgency_color}40;">
                                        <p style="margin: 0; color: white; font-size: 20px; font-weight: 800; text-shadow: 0 2px 8px rgba(0,0,0,0.3);">
                                            {deadline_str}
                                        </p>
                                    </div>
                                </div>
                                
                                <!-- Current Status -->
                                <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-left: 4px solid #64748b; padding: 16px 20px; border-radius: 8px; margin-bottom: 24px;">
                                    <table role="presentation" style="width: 100%;">
                                        <tr>
                                            <td style="width: 40px; vertical-align: top;">
                                                <div style="font-size: 20px;">📊</div>
                                            </td>
                                            <td style="vertical-align: top;">
                                                <p style="margin: 0 0 4px 0; color: #64748b; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                                    Current Status
                                                </p>
                                                <p style="margin: 0; color: #1e293b; font-size: 15px; font-weight: 600;">
                                                    {task_status}
                                                </p>
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
                                                This is an automated deadline reminder. Please do not reply to this email.
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