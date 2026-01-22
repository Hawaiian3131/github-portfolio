"""
Scheduled Automation for File Organizer
Automatically run file organization on a schedule
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import subprocess


class ScheduledOrganizer:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.schedule_config = self.script_dir / "schedule_config.json"
        
    def create_schedule(self, frequency="daily", time="09:00", enable_email=False, email_address=""):
        """
        Create a Windows scheduled task
        
        Args:
            frequency: "daily", "weekly", "monthly"
            time: Time to run (HH:MM format)
            enable_email: Send email notifications
            email_address: Email to send notifications to
        """
        
        # Save configuration
        config = {
            "frequency": frequency,
            "time": time,
            "enable_email": enable_email,
            "email_address": email_address,
            "last_run": None
        }
        
        with open(self.schedule_config, 'w') as f:
            json.dump(config, f, indent=4)
        
        # Create batch file to run organizer
        batch_file = self.script_dir / "run_organizer_scheduled.bat"
        python_exe = sys.executable
        organizer_script = self.script_dir / "organizer.py"
        
        batch_content = f'''@echo off
cd /d "{self.script_dir}"
"{python_exe}" "{organizer_script}"
pause
'''
        
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        
        # Create Windows Task Scheduler task
        task_name = "FileOrganizerAutomatic"
        
        # Build schedule trigger based on frequency
        if frequency == "daily":
            schedule_cmd = f'/SC DAILY /ST {time}'
        elif frequency == "weekly":
            schedule_cmd = f'/SC WEEKLY /D MON /ST {time}'
        elif frequency == "monthly":
            schedule_cmd = f'/SC MONTHLY /D 1 /ST {time}'
        else:
            schedule_cmd = f'/SC DAILY /ST {time}'
        
        # PowerShell command to create scheduled task
        ps_command = f'''
$action = New-ScheduledTaskAction -Execute "{batch_file}"
$trigger = New-ScheduledTaskTrigger -{frequency.capitalize()} -At {time}
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "{task_name}" -Action $action -Trigger $trigger -Settings $settings -Description "AI File Organizer - Automatic file organization" -Force
'''
        
        try:
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return True, f"Scheduled task created: {frequency} at {time}"
            else:
                return False, f"Error: {result.stderr}"
        except Exception as e:
            return False, f"Error creating schedule: {str(e)}"
    
    def remove_schedule(self):
        """Remove the scheduled task"""
        task_name = "FileOrganizerAutomatic"
        
        try:
            result = subprocess.run(
                ["schtasks", "/Delete", "/TN", task_name, "/F"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return True, "Scheduled task removed"
            else:
                return False, "No scheduled task found"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def check_schedule(self):
        """Check if a schedule exists"""
        task_name = "FileOrganizerAutomatic"
        
        try:
            result = subprocess.run(
                ["schtasks", "/Query", "/TN", task_name],
                capture_output=True,
                text=True
            )
            
            return result.returncode == 0
        except:
            return False
    
    def get_schedule_info(self):
        """Get current schedule configuration"""
        if self.schedule_config.exists():
            with open(self.schedule_config, 'r') as f:
                return json.load(f)
        return None


def send_email_notification(stats, email_address):
    """
    Send email notification about organization
    Note: Requires email configuration
    """
    # This is a placeholder - would need SMTP configuration
    # For now, just log the attempt
    print(f"Would send email to {email_address}")
    print(f"Files organized: {stats.get('Files Moved', 0)}")
    print(f"Duplicates found: {stats.get('Duplicates Found', 0)}")
