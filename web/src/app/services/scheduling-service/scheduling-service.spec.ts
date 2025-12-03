import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideZonelessChangeDetection } from '@angular/core';

import { SchedulingService } from './scheduling-service';

describe('SchedulingService', () => {
  let service: SchedulingService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [],
      providers: [provideZonelessChangeDetection(), provideHttpClient(), provideHttpClientTesting()]
    });
    service = TestBed.inject(SchedulingService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
