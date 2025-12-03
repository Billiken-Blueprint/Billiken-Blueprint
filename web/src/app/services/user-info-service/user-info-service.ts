import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class UserInfoService {
  private http = inject(HttpClient);

  getUserInfo() {
    return this.http.get<GetUserInfoResponse>('/api/user_info');
  }

  setUserInfo(body: SetUserInfoBody) {
    return this.http.post('/api/user_info', JSON.stringify({
      name: body.name,
      graduation_year: body.graduationYear,
      completed_course_ids: body.completedCourseIds,
      unavailability_times: body.unavailabilityTimes,
      avoid_times: body.avoidTimes,
      degree_id: body.degreeId
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
  }

  updateSavedCourses(savedCourseCodes: string[]) {
    // Get current user info first, then update with saved courses
    return this.getUserInfo().pipe(
    );
  }
}


export interface TimeSlot {
  day: number;
  start: string;
  end: string;
}

export interface SetUserInfoBody {
  name: string;
  graduationYear: number;
  completedCourseIds: number[];
  unavailabilityTimes: TimeSlot[];
  avoidTimes: TimeSlot[];
  degreeId: number;
}

export interface GetUserInfoResponse {
  name: string;
  completedCourseIds: number[];
  unavailabilityTimes: TimeSlot[];
  avoidTimes: TimeSlot[];
  savedCourseCodes: string[];
  graduationYear: number;
  degreeId: number;
}

