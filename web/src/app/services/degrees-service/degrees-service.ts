import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class DegreesService {
  private http = inject(HttpClient);

  getDegrees() {
    return this.http.get<Degree[]>('/api/degrees');
  }
}

export interface Degree {
  major: string;
  degreeType: string;
  college: string;
}
