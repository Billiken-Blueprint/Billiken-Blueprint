import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
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
      minor: body.minor,
      completed_course_ids: body.completedCourseIds,
      degree_ids: []
    }), {
      headers: {'Content-Type': 'application/json'}
    });
  }
}

export interface UpdateUserInfoBody {
  name: string;
  graduationYear: number;
  major: string;
  minor: string | null | undefined;
  completedCourseIds: number[];
}

export interface UserInfo {
  name: string;
  graduationYear: number;
  major: string;
  minor: string | null | undefined;
  completedCourses: Course[]
}
