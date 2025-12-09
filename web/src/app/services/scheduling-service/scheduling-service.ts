import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class SchedulingService {
  private http = inject(HttpClient);

  getRequirements() {
    return this.http.get<GraduationRequirement[]>('/api/degree-requirements');
  }

  autoGenerateSchedule() {
    return this.http.get<AutogenerateScheduleResponse>('api/degree-requirements/autogenerate-schedule')
  }
}

export interface GraduationRequirement {
  label: string;
  needed: number;
  satisfyingCourseCodes: string[];
  satisfyingCourseIds: number[];
}

export interface AutogenerateScheduleResponse {
  sections: {
    id: number | null | undefined;
    crn: string;
    instructorNames: string[];
    campusCode: string;
    description: string;
    title: string;
    courseCode: string;
    semester: string;
    requirementLabels: string[];
    meetingTimes: {
      day: number;
      startTime: string;
      endTime: string;
    }[]
  }[];
  unavailabilityTimes: {
    day: number;
    start: string;
    end: string;
  }[];
  avoidTimes: {
    day: number;
    start: string;
    end: string;
  }[];
}
