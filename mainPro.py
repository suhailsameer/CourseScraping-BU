from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig, Controller
from pydantic import SecretStr, BaseModel
from typing import List
import os
import csv
import asyncio
import getpass
from dotenv import load_dotenv
load_dotenv()

username = input("Enter your username: ")
password = getpass.getpass("Enter your password: ")
api_key = os.getenv("GEMINI_API_KEY")

class Course(BaseModel):
    course_code: str
    course_name: str
    credits: int
    instructor: List[str]
    room: str
    days: str
    start_time: str
    end_time: str
    max_enroll: str
    total_enroll: str

class Courses(BaseModel):
    courses: List[Course]

controller = Controller(output_model=Courses)

task = f"""
    ### Step 1: Navigate to Website
    Open "https://cudportal.cud.ac.ae/student/login.asp" in a web browser.
    ### Step 2: Enter Credentials
    Enter the following credentials:
    - Username: {username}
    - Password: {password}
    ### Step 3: Login
    Click the "Login" button.
    ### Step 4: Access Courses
    Click on the "Course Offerings" tab.
    ### Step 5: Filter Courses
    Filter the courses by selecting the "Show Filter" option.
    Select SEAST from the division dropdown
    Click the "Apply Filter" button.
    ### Step 6: Obtain Courses
    Only Obtain the following information for each course the first page (Make sure its in JSON format):
    - Course Code
    - Course Name
    - Credits
    - Instructor
    - Room
    - Days
    - Start Time
    - End Time
    - Max Enroll
    - Total Enroll
    ### Step 7: Return Courses
    Return the obtained information.
    ```
"""

def save_to_file(data,filename="courses.csv"):
    header = ["Course Code", "Course Name", "Credits", "Instructor", "Room", "Days", "Start Time", "End Time", "Max Enroll", "Total Enroll"]
    with open(filename, "w") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for course in data:
            writer.writerow([
                course.course_code,
                course.course_name,
                course.credits,
                ', '.join(course.instructor),
                course.room,
                course.days,
                course.start_time,
                course.end_time,
                course.max_enroll,
                course.total_enroll
            ])
    print(f"Data saved to {filename}")


# Initialize the model
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(os.getenv('GEMINI_API_KEY')))
browser = Browser()
async def main():
    agent = Agent(
        task=task,
        llm=llm,
        use_vision=False,
        controller=controller,
    )
    results = await agent.run()
    #print(results.final_result())
    data = results.final_result()
    if data:
        parsed: Courses = Courses.model_validate_json(data)
        for course in parsed.courses:
            print("\n----------------------------")
            print(f"Course Code: {course.course_code}")
            print(f"Course Name: {course.course_name}")
            print(f"Credits: {course.credits}")
            print(f"Instructor: {', '.join(course.instructor)}")
            print(f"Room: {course.room}")
            print(f"Days: {course.days}")
            print(f"Start Time: {course.start_time}")
            print(f"End Time: {course.end_time}")
            print(f"Max Enroll: {course.max_enroll}")
            print(f"Total Enroll: {course.total_enroll}")
            print("----------------------------")     
        save_to_file(parsed.courses)
    input("Press Enter to continue...")
    await browser.close()

asyncio.run(main())
