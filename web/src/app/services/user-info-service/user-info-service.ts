import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Course} from '../courses-service/courses-service';
import {Degree} from '../degrees-service/degrees-service';

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
      major: {
        major: body.major.major,
        degree_type: body.major.degreeType,
        college: body.major.college
      },
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
  major: Degree;
  completedCourseIds: number[];
}

export interface UserInfo {
  email: string;
  name: string;
  graduationYear: number;
  major: Degree;
  completedCourseIds: number[]
}
