import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map } from 'rxjs/operators';
import { forkJoin } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CoursesService {
  private http = inject(HttpClient);

  getCourses() {
    return this.http.get<GetCoursesResponse>('/api/courses');
  }

  search(query: string) {
    return this.http.get<{
      ids: number[][];
      documents: string[][];
      metadatas: {
        course_int: number;
        course_number: string;
        course_id: number;
        major_code: string;
        course_code: string
      }[][]
    }>(`/api/courses/search?query=${query}`)
      .pipe(map((response) => {
        const descriptions = response.documents[0];
        const meta = response.metadatas[0];
        return descriptions.map((description, index) => {
          return {
            id: meta[index].course_id,
            description,
            courseCode: meta[index].course_code
          };
        });
      }));
  }

  addDesiredCourses(courseIds: number[]) {
    const requests = courseIds.map(id =>
      this.http.post('/api/student/desired_courses', { course_id: id })
    );
    return forkJoin(requests);
  }

  removeDesiredCourse(courseId: number) {
    return this.http.delete(`/api/student/desired_courses/${courseId}`);
  }
}

export interface Course {
  id: number;
  courseCode: string;
}

export interface SearchCourse {
  id: number;
  description: string;
  courseCode: string;
}

export type GetCoursesResponse = Course[];
