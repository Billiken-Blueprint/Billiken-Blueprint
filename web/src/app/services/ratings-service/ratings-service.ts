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
    
    // Include instructor_name if provided (for creating new instructors)
    if (body.instructorName !== null && body.instructorName !== undefined && body.instructorName.trim() !== '') {
      payload.instructor_name = body.instructorName.trim();
    }
    
    // Include instructor_department if provided (for creating new instructors)
    if (body.instructorDepartment !== null && body.instructorDepartment !== undefined && body.instructorDepartment.trim() !== '') {
      payload.instructor_department = body.instructorDepartment.trim();
    }
    
    // Only include course_id if it's provided and convert to number
    if (body.courseId !== null && body.courseId !== undefined && body.courseId !== '') {
      const courseIdNum = parseInt(body.courseId, 10);
      if (!isNaN(courseIdNum)) {
        payload.course_id = courseIdNum;
      }
    }
    
    // Include additional fields if provided
    if (body.difficulty !== null && body.difficulty !== undefined) {
      payload.difficulty = body.difficulty;
    }
    if (body.wouldTakeAgain !== null && body.wouldTakeAgain !== undefined) {
      payload.would_take_again = body.wouldTakeAgain;
    }
    if (body.grade !== null && body.grade !== undefined && body.grade !== '') {
      payload.grade = body.grade;
    }
    if (body.attendance !== null && body.attendance !== undefined && body.attendance !== '') {
      payload.attendance = body.attendance;
    }
    
    return this.http.post<CreateRatingResponse>('/api/ratings', JSON.stringify(payload), {
      headers: {'Content-Type': 'application/json'}
    })
  }

  updateRating(ratingId: number, body: CreateRatingBody) {
    const payload: any = {
      rating: body.rating,
      description: body.description,
    };
    
    if (body.instructorId !== null && body.instructorId !== undefined && body.instructorId !== '') {
      const instructorIdNum = parseInt(body.instructorId, 10);
      if (!isNaN(instructorIdNum)) {
        payload.instructor_id = instructorIdNum;
      }
    }
    
    if (body.courseId !== null && body.courseId !== undefined && body.courseId !== '') {
      const courseIdNum = parseInt(body.courseId, 10);
      if (!isNaN(courseIdNum)) {
        payload.course_id = courseIdNum;
      }
    }
    
    // Include additional fields if provided
    if (body.difficulty !== null && body.difficulty !== undefined) {
      payload.difficulty = body.difficulty;
    }
    if (body.wouldTakeAgain !== null && body.wouldTakeAgain !== undefined) {
      payload.would_take_again = body.wouldTakeAgain;
    }
    if (body.grade !== null && body.grade !== undefined && body.grade !== '') {
      payload.grade = body.grade;
    }
    if (body.attendance !== null && body.attendance !== undefined && body.attendance !== '') {
      payload.attendance = body.attendance;
    }
    
    return this.http.put(`/api/ratings/${ratingId}`, JSON.stringify(payload), {
      headers: {'Content-Type': 'application/json'}
    });
  }

  deleteRating(ratingId: number) {
    return this.http.delete(`/api/ratings/${ratingId}`);
  }
}

export interface CreateRatingBody {
  instructorId?: string | null | undefined;
  instructorName?: string | null | undefined;
  instructorDepartment?: string | null | undefined;
  courseId: string | null | undefined;
  rating: number;
  description: string;
  difficulty?: number | null;
  wouldTakeAgain?: boolean | null;
  grade?: string | null;
  attendance?: string | null;
}

export interface CreateRatingResponse {
  id: number;
  instructorId: number | null;
  courseId: number | null;
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
  difficulty?: number | null;
  wouldTakeAgain?: boolean | null;
  grade?: string | null;
  attendance?: string | null;
}
