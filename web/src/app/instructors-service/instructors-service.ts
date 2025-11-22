import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class InstructorsService {
  private http = inject(HttpClient);

  getInstructors() {
    return this.http.get<Instructor[]>('/api/instructors');
  }

  getInstructorReviews(instructorId: number): Observable<RmpReview[]> {
    return this.http.get<RmpReview[]>(`/api/instructors/${instructorId}/reviews`);
  }
}

export interface Instructor {
  id: number;
  name: string;
}

export interface RmpReview {
  id: number;
  instructorId: number;
  course: string | null;
  quality: number;
  difficulty: number | null;
  comment: string;
  wouldTakeAgain: boolean | null;
  grade: string | null;
  attendance: string | null;
  tags: string[];
  reviewDate: string | null;
}
