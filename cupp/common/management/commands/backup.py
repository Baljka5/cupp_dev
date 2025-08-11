import os
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

sender_email = "noreply@cumongol.mn"
to_emails = ["baljinnyam.ye@cumongol.mn", "enkhbayar.e@cumongol.mn"]
cc_emails = ["tserenjagzan.g@cumongol.mn", "uuganbayar.n@cumongol.mn", "temuul.b@cumongol.mn", "turmunkh@cumongol.mn", "bolor-erdene.n@cumongol.mn"]
smtp_server = "smtp.office365.com"
smtp_port = 587
smtp_username = "noreply@cumongol.mn"
smtp_password = "Gol71747"

mysql_user = "root"
mysql_password = "CE@dmin22"
mysql_database = "ebarimt3_db"

backup_base_path = "/mnt/NAS/10.10.90.231"
log_file = "/var/log/ebarimt_db_backup.log"
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
backup_path = os.path.join(backup_base_path, f"{mysql_database}_{timestamp}")


def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = ", ".join(to_emails)
        msg["Cc"] = ", ".join(cc_emails)
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        all_recipients = to_emails + cc_emails

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, all_recipients, msg.as_string())

        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


def take_backup():
    try:
        os.makedirs(backup_path, exist_ok=True)

        sql_file_path = os.path.join(backup_path, f"{mysql_database}.sql")
        command = (
            f"mysqldump -u{mysql_user} -p'{mysql_password}' {mysql_database} "
            f"--result-file={sql_file_path} >> {log_file} 2>&1"
        )
        subprocess.run(command, shell=True, check=True)

        if not os.path.exists(sql_file_path) or os.path.getsize(sql_file_path) == 0:
            raise Exception("Backup file is empty. Dump may have failed silently.")

        subject = "Ebarimt Backup Successful"
        body = (
            f"Ebarimt DB backup completed successfully.\n\n"
            f"Database: {mysql_database}\n"
            f"Backup file: {sql_file_path}\n"
            f"Log file: {log_file}"
        )
        send_email(subject, body)

    except Exception as e:
        subject = "Ebarimt Backup Failed"
        body = (
            f"Ebarimt DB backup failed.\n\n"
            f"Database: {mysql_database}\n"
            f"Error: {str(e)}\n"
            f"Check log file: {log_file}"
        )
        send_email(subject, body)


if __name__ == "__main__":
    take_backup()
