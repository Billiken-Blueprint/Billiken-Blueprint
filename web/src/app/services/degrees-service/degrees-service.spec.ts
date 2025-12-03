import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideZonelessChangeDetection } from '@angular/core';

import { DegreesService } from './degrees-service';

describe('DegreesService', () => {
  let service: DegreesService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [],
      providers: [provideZonelessChangeDetection(), provideHttpClient(), provideHttpClientTesting()]});
    service = TestBed.inject(DegreesService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
