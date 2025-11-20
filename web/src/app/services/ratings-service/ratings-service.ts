import {inject, Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {CreateRatingPage} from '../../ratings-page/create-rating-page/create-rating-page';

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
    return this.http.post('/api/ratings', JSON.stringify({
      instructor_id: body.instructorId,
      course_id: body.courseId,
      rating: body.rating,
      description: body.description,
    }), {
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
  id: number;
  instructorId: number | null;
  courseId: number | null;
  rating: number;
  canEdit: boolean;
  description: string;
}
