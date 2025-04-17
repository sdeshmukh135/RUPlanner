import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def parse_date(date_str):
    """Parse a date string like 'Tue, September 3, 2024' into 'YYYY-MM-DD' format."""
    return datetime.strptime(date_str, "%a, %B %d, %Y").strftime("%Y-%m-%d")

def parse_recess(recess_str):
    """Parse a recess string like 'Thu, November 28 to Sun, December 1, 2024' into start and end dates."""
    parts = recess_str.split("to")
    if len(parts) != 2:
        raise ValueError(f"Invalid recess format: {recess_str}")
    start_str, end_str = [part.strip() for part in parts]
    end_date = datetime.strptime(end_str, "%a, %B %d, %Y")
    start_date = datetime.strptime(f"{start_str}, {end_date.year}", "%a, %B %d, %Y")
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

def process_semester(rows, academic_years, i, semester_key, start_key, end_key, recess_info=None):
    """Helper to process a semester's data from table rows."""
    # Find the start row for the semester
    start_row = next(r for r in rows if r.find("td").find("strong", string=start_key))
    start_index = rows.index(start_row)
    
    # For semesters ending with "Regular Classes End", find the next occurrence after the start row
    if end_key == "Regular Classes End":
        end_row = next((r for r in rows[start_index + 1:] if r.find("td").find("strong", string=end_key)), None)
        if end_row is None:
            raise ValueError(f"No 'Regular Classes End' row found after '{start_key}' for {semester_key}")
    else:
        # For other semesters (e.g., Winter, Summer), use the first matching row
        end_row = next(r for r in rows if r.find("td").find("strong", string=end_key))
    
    # Extract start and end dates from the appropriate columns
    start_str = start_row.find_all("td")[i + 1].text.strip()
    end_str = end_row.find_all("td")[i + 1].text.strip()
    if not (start_str and end_str):
        return None
    
    # Initialize data dictionary
    data = {"start": parse_date(start_str), "end": parse_date(end_str), "recesses": []}
    
    # Handle Thanksgiving Recess for Fall semester
    if recess_info and recess_info["name"] == "Thanksgiving Recess":
        recess_row = next(r for r in rows if r.find("td").find("strong", string=recess_info["name"]))
        recess_str = recess_row.find_all("td")[i + 1].text.strip()
        if recess_str:
            recess_start, recess_end = parse_recess(recess_str)
            data["recesses"].append({"name": recess_info["name"], "start": recess_start, "end": recess_end})
    
    # Handle Spring Recess for Spring semester
    elif recess_info and recess_info["name"] == "Spring Recess Begins":
        recess_start_row = next(r for r in rows if r.find("td").find("strong", string="Spring Recess Begins"))
        recess_end_row = next(r for r in rows if r.find("td").find("strong", string="Spring Recess Ends"))
        recess_start_str = recess_start_row.find_all("td")[i + 1].text.strip()
        recess_end_str = recess_end_row.find_all("td")[i + 1].text.strip()
        if recess_start_str and recess_end_str:
            data["recesses"].append({
                "name": "Spring Recess",
                "start": parse_date(recess_start_str),
                "end": parse_date(recess_end_str)
            })
    
    return data

def scrape_academic_calendar(log=False):
    url = "https://scheduling.rutgers.edu/scheduling/academic-calendar"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to load page: {response.status_code}")
    
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="pretty-table responsive-enabled")
    if not table:
        raise ValueError("Academic calendar table not found.")
    
    rows = table.find("tbody").find_all("tr")
    academic_years = [th.text.strip() for th in table.find("thead").find("tr").find_all("th")[1:]]
    
    calendar_data = {}
    semester_configs = [
        ("Fall {}", "Fall Semester Begins", "Regular Classes End", {"name": "Thanksgiving Recess"}),
        ("Winter {}", "Winter Session Begins", "Winter Session Ends", None),
        ("Spring {}", "Spring Semester Begins", "Regular Classes End", {"name": "Spring Recess Begins"}),
        ("Summer {}", "Summer Session Begins", "Summer Session Ends", None)
    ]
    
    for i, year in enumerate(academic_years):
        fall_year, spring_year = map(int, year.split("-"))
        for name_template, start_key, end_key, recess_info in semester_configs:
            year_to_use = fall_year if "Fall" in name_template else spring_year
            semester_key = name_template.format(year_to_use)
            data = process_semester(rows, academic_years, i, semester_key, start_key, end_key, recess_info)
            if data:
                calendar_data[semester_key] = data
    
    with open("academic_calendar.json", "w") as f:
        json.dump(calendar_data, f, indent=2)
    if log: print("Data successfully written to academic_calendar.json")

def main():
    scrape_academic_calendar(log=True)

if __name__ == "__main__":
    main()