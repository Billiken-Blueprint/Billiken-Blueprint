import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {switchMap} from 'rxjs/operators';
import {Course} from '../courses-service/courses-service';

@Injectable({
  providedIn: 'root'
})
export class UserInfoService {
  private http = inject(HttpClient);

  getUserInfo() {
    return this.http.get<GetUserInfoResponse>('/api/user_info');
  }

  updateUserInfo(body: UpdateUserInfoBody) {
    return this.http.post<UserInfo>('/api/user_info', JSON.stringify({
      name: body.name,
      graduation_year: body.graduationYear,
      completed_course_ids: body.completedCourseIds,
      degree_ids: [],
      major_code: body.majorCode,
      degree_type: body.degreeType,
      college: body.college
    }), {
      headers: {'Content-Type': 'application/json'}
    });
  }

  updateSavedCourses(savedCourseCodes: string[]) {
    // Get current user info first, then update with saved courses
    return this.getUserInfo().pipe(
    );
  }
}

export interface UpdateUserInfoBody {
  name: string;
  graduationYear: number;
  majorCode: string;
  degreeType: string;
  college: string;
  completedCourseIds: number[];
}

export interface UserInfo {
  name: string;
  graduationYear: number;
  majorCode: string;
  degreeType: string;
  college: string;
  completedCourseIds: number[];
}

export interface GetUserInfoResponse extends UserInfo {
  savedCourseCodes: string[];
}
