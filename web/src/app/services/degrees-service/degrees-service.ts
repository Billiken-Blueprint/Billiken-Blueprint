import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class DegreesService {
  private http = inject(HttpClient);

  getDegrees() {
    return this.http.get<GetDegreesResponse>('/api/degrees');
  }
}

export interface Degree {
  id: number | null;
  name: string;
  major: string;
  degreeType: string;
  college: string;
}

export type GetDegreesResponse = Degree[];
