import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideZonelessChangeDetection } from '@angular/core';

import { InstructorsService } from './instructors-service';

describe('InstructorsService', () => {
  let service: InstructorsService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [],
      providers: [provideZonelessChangeDetection(), provideHttpClient(), provideHttpClientTesting()]});
    service = TestBed.inject(InstructorsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
