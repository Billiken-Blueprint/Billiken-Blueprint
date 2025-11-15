import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class InstructorsService {
  private http = inject(HttpClient);

  getInstructors() {
    return this.http.get<Instructor[]>('/api/instructors');
  }
}

export interface Instructor {
  id: number;
  name: string;
}
