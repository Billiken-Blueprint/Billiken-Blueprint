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
    return this.http.get<UserInfo>('/api/user_info');
  }

  updateUserInfo(body: UpdateUserInfoBody) {
    return this.http.post<UserInfo>('/api/user_info', JSON.stringify({
      name: body.name,
      graduation_year: body.graduationYear,
      major: body.major,
      completed_course_ids: body.completedCourseIds,
      saved_course_codes: body.savedCourseCodes || [],
      degree_ids: []
    }), {
      headers: {'Content-Type': 'application/json'}
    });
  }

  updateSavedCourses(savedCourseCodes: string[]) {
    // Get current user info first, then update with saved courses
    return this.getUserInfo().pipe(
      switchMap((userInfo) => {
        return this.updateUserInfo({
          name: userInfo.name,
          graduationYear: userInfo.graduationYear,
          major: userInfo.major,
          completedCourseIds: userInfo.completedCourseIds || [],
          savedCourseCodes: savedCourseCodes
        });
      })
    );
  }
}

export interface UpdateUserInfoBody {
  name: string;
  graduationYear: number;
  major: string;
  completedCourseIds: number[];
  savedCourseCodes?: string[];
}

export interface UserInfo {
  name: string;
  graduationYear: number;
  major: string;
  minor: string | null | undefined;
  completedCourses?: Course[];
  completedCourseIds?: number[];
  savedCourseCodes?: string[];
}
