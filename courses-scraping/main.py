from courses_scraping.api.get_courses import get_courses, Semesters

result = get_courses('csci', Semesters.SPRING)

print(result)
