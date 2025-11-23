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
  rmpRating?: number | null;
  rmpNumRatings?: number | null;
  rmpUrl?: string | null;
  department?: string | null;
}

export interface RmpReview {
  id: number;
  type: 'rmp' | 'billiken_blueprint';
  instructorId: number;
  course?: string | null;
  courseCode?: string | null;
  courseName?: string | null;
  courseId?: number | null;
  quality: number;
  difficulty?: number | null;
  comment: string;
  wouldTakeAgain?: boolean | null;
  grade?: string | null;
  attendance?: string | null;
  tags?: string[];
  reviewDate: string | null;
  canDelete?: boolean;
}
