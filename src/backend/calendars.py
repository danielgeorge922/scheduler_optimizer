import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ocr import process_screenshot  # Import the function to process the screenshot

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=62502)  # Ensure this port matches your redirect URI
            with open("token.json", "w") as token:
                token.write(creds.to_json())
    service = build("calendar", "v3", credentials=creds)
    return service


def create_event(service, calendar_id, event_details):
    event = {
        'summary': event_details['summary'],
        'location': event_details.get('location', ''),
        'description': event_details.get('description', ''),
        'start': {
            'dateTime': event_details['start'],
            'timeZone': 'America/New_York',  # Update the timezone as needed
        },
        'end': {
            'dateTime': event_details['end'],
            'timeZone': 'America/New_York',  # Update the timezone as needed
        },
        'recurrence': event_details.get('recurrence', []),
        'attendees': event_details.get('attendees', []),
    }
    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f'Event created: {event.get("htmlLink")}')
    print(f'Event details: {event}')


def list_events(service, calendar_id='primary'):
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    events_result = service.events().list(
        calendarId=calendar_id, timeMin=now, maxResults=100, singleEvents=True, orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])
    return events


def delete_events(service, calendar_id='primary', summary=None):
    events = list_events(service, calendar_id)
    for event in events:
        if summary is None or event['summary'] == summary:
            try:
                service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
                print(f"Deleted event: {event['summary']}")
            except HttpError as error:
                print(f"An error occurred: {error}")


def add_events_to_calendar(schedule, service, calendar_id='primary'):
    for class_id, details in schedule.items():
        for time in details['times']:
            for day, time_range in time.items():
                start_time_str, end_time_str = time_range.split(' - ')
                start_time = datetime.datetime.strptime(start_time_str, '%I:%M %p')
                end_time = datetime.datetime.strptime(end_time_str, '%I:%M %p')

                # Assuming classes start on the next Monday
                today = datetime.datetime.now()
                days_ahead = (day_to_num(day) - today.weekday() + 7) % 7
                class_start_date = today + datetime.timedelta(days=days_ahead)

                start_datetime = class_start_date.replace(hour=start_time.hour, minute=start_time.minute)
                end_datetime = class_start_date.replace(hour=end_time.hour, minute=end_time.minute)

                event_details = {
                    'summary': details['title'],
                    'start': start_datetime.isoformat(),
                    'end': end_datetime.isoformat(),
                    'recurrence': [
                        f'RRULE:FREQ=WEEKLY;BYDAY={day_to_rrule_day(day)}'
                    ]
                }
                create_event(service, calendar_id, event_details)

        if details['exam']['date']:
            exam_start_datetime = datetime.datetime.strptime(details['exam']['date'] + ' ' + details['exam']['start'],
                                                             '%m/%d/%Y %I:%M %p')
            exam_end_datetime = datetime.datetime.strptime(details['exam']['date'] + ' ' + details['exam']['end'],
                                                           '%m/%d/%Y %I:%M %p')
            exam_event_details = {
                'summary': f"{details['title']} - Final Exam",
                'start': exam_start_datetime.isoformat(),
                'end': exam_end_datetime.isoformat()
            }
            create_event(service, calendar_id, exam_event_details)


# Helper function to convert day character to weekday number
def day_to_num(day):
    return {'M': 0, 'T': 1, 'W': 2, 'R': 3, 'F': 4, 'S': 5, 'U': 6}[day]


# Helper function to convert day character to RRULE format
def day_to_rrule_day(day):
    return {'M': 'MO', 'T': 'TU', 'W': 'WE', 'R': 'TH', 'F': 'FR', 'S': 'SA', 'U': 'SU'}[day]


def main():
    service = get_calendar_service()

    # Uncomment the next line if you want to delete all events before adding new ones
    delete_events(service)  # Optionally specify a summary to delete specific events

    image_path = r'C:\Users\danie\OneDrive\Pictures\Screenshots\Screenshot 2024-07-22 233852.png'
    schedule = process_screenshot(image_path)

    # Print the schedule for verification
    print("\nExtracted Schedule:")
    print(schedule)

    add_events_to_calendar(schedule, service)


if __name__ == '__main__':
    main()
