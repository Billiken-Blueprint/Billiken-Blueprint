import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class CoursesService {
  private http = inject(HttpClient);

  getCourses() {
    return this.http.get<Course[]>('/api/courses');
  }
}

export interface Course {
  id: number;
  courseCode: string;
  title: string;
}
