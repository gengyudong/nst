import json
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

# ---------- CONFIGURATION ----------
FLASHCARDS_FILE = 'flashcards.json'
USER_EMAIL = 'your_email@gmail.com'
SMTP_USER = 'your_email@gmail.com'
SMTP_PASSWORD = 'your_password'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
# -----------------------------------

def load_flashcards(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Flashcards file not found.")
        return {}

def save_flashcards(filepath, flashcards):
    with open(filepath, 'w') as f:
        json.dump(flashcards, f, indent=4, default=str)

def initialize_flashcards(filepath):
    flashcards = load_flashcards(filepath)
    today_str = datetime.today().strftime('%Y-%m-%d')
    # Add metadata to each flashcard if not already present
    for key, card in flashcards.items():
        if 'repetition' not in card:
            card['repetition'] = 0
        if 'interval' not in card:
            card['interval'] = 0
        if 'ef' not in card:
            card['ef'] = 2.5
        if 'last_review_date' not in card:
            card['last_review_date'] = ""
        if 'next_review_date' not in card:
            card['next_review_date'] = today_str
    save_flashcards(filepath, flashcards)
    return flashcards

def update_flashcard(card, quality, review_date):
    """Apply SM-2 algorithm updates to a flashcard based on review quality."""
    review_date_dt = review_date
    if quality < 3:
        card['repetition'] = 0
        card['interval'] = 1
    else:
        card['repetition'] += 1
        if card['repetition'] == 1:
            card['interval'] = 1
        elif card['repetition'] == 2:
            card['interval'] = 6
        else:
            card['interval'] = int(card['interval'] * card['ef'])
        # Update easiness factor
        card['ef'] = card['ef'] + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if card['ef'] < 1.3:
            card['ef'] = 1.3
    card['last_review_date'] = review_date_dt.strftime('%Y-%m-%d')
    next_review_date = review_date_dt + timedelta(days=card['interval'])
    card['next_review_date'] = next_review_date.strftime('%Y-%m-%d')
    return card

def run_quiz(flashcards):
    today = datetime.today()
    updated = False
    for key, card in flashcards.items():
        next_review_date = datetime.strptime(card['next_review_date'], '%Y-%m-%d')
        if next_review_date <= today:
            print("\n---")
            print(f"Concept: {card['concept']}")
            input("Press Enter to reveal the explanation...")
            print(f"Explanation: {card['explanation']}")
            
            # Get quality feedback from user
            while True:
                try:
                    quality = int(input("Rate your recall (0-5): "))
                    if quality < 0 or quality > 5:
                        raise ValueError
                    break
                except ValueError:
                    print("Please enter a valid number between 0 and 5.")
            
            # Update the flashcard metadata
            card = update_flashcard(card, quality, today)
            flashcards[key] = card
            print(f"Next review on: {card['next_review_date']} (Interval: {card['interval']} days, EF: {round(card['ef'], 2)})")
            updated = True
    return flashcards, updated

def send_email_notification(to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = to_email

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Notification email sent!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_and_notify(flashcards):
    today = datetime.today()
    due_cards = [card for card in flashcards.values() 
                 if datetime.strptime(card['next_review_date'], '%Y-%m-%d') <= today]
    if due_cards:
        subject = "Flashcard Review Reminder"
        body = f"You have {len(due_cards)} flashcards due for review today. Please complete your review session."
        send_email_notification(USER_EMAIL, subject, body)
    else:
        print("No flashcards are due for review today.")

def main():
    flashcards = initialize_flashcards(FLASHCARDS_FILE)
    flashcards, updated = run_quiz(flashcards)
    if updated:
        save_flashcards(FLASHCARDS_FILE, flashcards)
    # Optionally, trigger an email notification at the end of the session or schedule this separately
    check_and_notify(flashcards)

if __name__ == '__main__':
    main()
