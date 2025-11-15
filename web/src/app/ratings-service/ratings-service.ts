import {inject, Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {CreateRatingPage} from '../ratings-page/create-rating-page/create-rating-page';

@Injectable({
  providedIn: 'root'
})
export class RatingsService {
  private http = inject(HttpClient);

  getRatings(instructorId: string | null | undefined, courseId: string | null | undefined) {
    let params = new HttpParams()
    if (instructorId) {
      params = params.set('instructor_id', instructorId);
    }
    if (courseId) {
      params = params.set('course_id', courseId);
    }
    return this.http.get<Rating[]>('/api/ratings', {params: params});
  }

  createRating(body: CreateRatingBody) {
    const payload: any = {
      rating: body.rating,
      description: body.description,
    };
    
    // Only include instructor_id if it's provided and convert to number
    if (body.instructorId !== null && body.instructorId !== undefined && body.instructorId !== '') {
      const instructorIdNum = parseInt(body.instructorId, 10);
      if (!isNaN(instructorIdNum)) {
        payload.instructor_id = instructorIdNum;
      }
    }
    
    // Only include course_id if it's provided and convert to number
    if (body.courseId !== null && body.courseId !== undefined && body.courseId !== '') {
      const courseIdNum = parseInt(body.courseId, 10);
      if (!isNaN(courseIdNum)) {
        payload.course_id = courseIdNum;
      }
    }
    
    return this.http.post('/api/ratings', JSON.stringify(payload), {
      headers: {'Content-Type': 'application/json'}
    })
  }
}

export interface CreateRatingBody {
  instructorId: string | null | undefined;
  courseId: string | null | undefined;
  rating: number;
  description: string;
}

export interface Rating {
  id: number | null;
  instructorId: number | null;
  courseId: number | null;
  rating: number;
  canEdit: boolean;
  description: string;
  instructorName?: string;
  courseCode?: string;
  courseName?: string;
  createdAt?: string;
  isRmpRating?: boolean;
  rmpUrl?: string;
  rmpNumRatings?: number;
}
