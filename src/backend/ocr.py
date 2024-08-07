from PIL import Image
import pytesseract
import re

# Ensure pytesseract can find the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update the path as needed

def process_screenshot(image_path):
    # Load image and perform OCR
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    print("Extracted Text:\n", text)  # Debugging: Print the extracted text

    # Initialize patterns to extract class details
    class_pattern = re.compile(r'([A-Z]+\d+)\s-\s(.+)')
    time_pattern = re.compile(
        r'([MTWRF])\s\|\sPeriods?\s[\d-]+\s\((\d{1,2}:\d{2}\s[APM]{2})\s-\s(\d{1,2}:\d{2}\s[APM]{2})\)')
    exam_pattern = re.compile(
        r'(\d{1,2}/\d{1,2}/\d{4})\s@\s(\d{1,2}:\d{2}\s[APM]{2})\s-\s(\d{1,2}:\d{2}\s[APM]{2})')

    classes = {}
    current_class_id = None
    current_class_title = None
    current_class_times = []
    current_exam_date = None
    current_exam_start = None
    current_exam_end = None
    exam_next_line = False

    lines = text.split('\n')
    for line in lines:
        line = line.strip()  # Trim whitespace
        # Debugging: Print each line being processed
        print("Processing line:", line)

        # Check for final exam trigger
        if exam_next_line:
            exam_match = exam_pattern.match(line)
            if exam_match:
                current_exam_date, current_exam_start, current_exam_end = exam_match.groups()
            exam_next_line = False
            continue

        if line.lower() == 'final exam':
            exam_next_line = True
            continue

        # Check for class ID and title
        class_match = class_pattern.match(line)
        if class_match:
            if current_class_id:
                classes[current_class_id] = {
                    'title': current_class_title,
                    'times': current_class_times,
                    'exam': {
                        'date': current_exam_date,
                        'start': current_exam_start,
                        'end': current_exam_end
                    }
                }
            current_class_id = class_match.group(1)
            current_class_title = class_match.group(2).strip()
            current_class_times = []
            current_exam_date = None
            current_exam_start = None
            current_exam_end = None
            continue

        # Check for class times
        time_match = time_pattern.findall(line)
        if time_match:
            for day, start, end in time_match:
                current_class_times.append({day: f"{start} - {end}"})
            continue

    # Add the last class to the dictionary
    if current_class_id:
        classes[current_class_id] = {
            'title': current_class_title,
            'times': current_class_times,
            'exam': {
                'date': current_exam_date,
                'start': current_exam_start,
                'end': current_exam_end
            }
        }

    return classes

def main(image_path):
    # Process the image and extract schedule data
    schedule = process_screenshot(image_path)

    # Print parsed schedule data in a readable format
    for class_id, details in schedule.items():
        print(f"Class ID: {class_id}")
        print(f"Title: {details['title']}")
        print("Class Times:")
        for time in details['times']:
            for day, t in time.items():
                print(f"  {day}: {t}")
        if details['exam']['date']:
            print(f"Final Exam: {details['exam']['date']} from {details['exam']['start']} to {details['exam']['end']}")
        else:
            print("Final Exam: None")
        print()

    # Print the entire dictionary structure
    print("\nDictionary Structure:\n")
    print(schedule)

if __name__ == '__main__':
    image_path = r'C:\Users\danie\OneDrive\Pictures\Screenshots\Screenshot 2024-07-22 233852.png'
    main(image_path)
