import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class CoursesService {
  private http = inject(HttpClient);

  getCourses() {
    return this.http.get<GetCoursesResponse>('/api/courses');
  }
}

export interface Course {
  id: number;
  courseCode: string;
}

export type GetCoursesResponse = Course[];
