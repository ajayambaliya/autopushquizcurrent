import mysql.connector
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
import random
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get database credentials and FCM topic from .env
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
FCM_NOTIFICATION_TOPIC = os.getenv("FCM_NOTIFICATION_TOPIC")

# Initialize Firebase with service account credentials
cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_PATH)
firebase_admin.initialize_app(cred)

# Database connection
try:
    db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = db.cursor()

    # SQL query to get the latest post from category_id = 10
    query = """
        SELECT news_title, news_description
        FROM tbl_news
        WHERE cat_id = 10
        ORDER BY news_date DESC
        LIMIT 1
    """
    cursor.execute(query)
    latest_post = cursor.fetchone()

    if latest_post:
        original_title, description = latest_post

        # List of catchy title templates with transformation indicators
        catchy_templates = [
            ("🔥 {title} 🚀 Quiz Time! 🎉", lambda x: x),
            ("🌟 {title} Alert! 🔔 Let's Quiz! 🎯", lambda x: x.upper()),
            ("🎊 {title} Challenge! ⚡ Test Your Skills! 🌈", lambda x: x.capitalize()),
            ("💥 {title} Quiz of the Day! 🎮 Time to Shine! ✨", lambda x: x.upper()),
            ("🏆 {title} Quiz Time! 🕒 Get Ready! 🎆", lambda x: x.capitalize())
        ]

        # Randomly select a catchy template and its transformation function
        selected_template, transform_func = random.choice(catchy_templates)
        transformed_title = transform_func(original_title)
        catchy_title = selected_template.format(title=transformed_title)

        # Truncate description for notification body
        notification_body = description[:100] + "..." if len(description) > 100 else description

        # Create a detailed notification payload using the latest FCM techniques
        message = messaging.Message(
            notification=messaging.Notification(
                title=catchy_title,
                body=notification_body
            ),
            android=messaging.AndroidConfig(
                priority="high",  # Ensures high priority for Android devices
                notification=messaging.AndroidNotification(
                    title=catchy_title,
                    body=notification_body,
                    icon="ic_notification",  # Replace with your app's notification icon if available
                    sound="default",  # Play default notification sound
                    click_action="FCM_PLUGIN_ACTIVITY"  # Opens app on click
                )
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        alert=messaging.ApsAlert(
                            title=catchy_title,
                            body=notification_body
                        ),
                        sound="default"  # Play default notification sound on iOS
                    )
                )
            ),
            topic=FCM_NOTIFICATION_TOPIC  # Use topic from .env
        )

        # Send the notification
        try:
            response = messaging.send(message)
            print(f"Successfully sent message: {response}")
            print(f"Notification title: {catchy_title}")
            print(f"Sent to topic: {FCM_NOTIFICATION_TOPIC}")
        except Exception as e:
            print(f"Error sending message: {e}")
    else:
        print("No posts found for category_id 10.")

except mysql.connector.Error as db_err:
    print(f"Database connection error: {db_err}")

finally:
    # Close database connection
    if 'cursor' in locals():
        cursor.close()
    if 'db' in locals() and db.is_connected():
        db.close()
