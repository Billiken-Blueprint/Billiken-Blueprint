import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';

import { CreateRatingPage } from './create-rating-page';

describe('CreateRatingPage', () => {
  let component: CreateRatingPage;
  let fixture: ComponentFixture<CreateRatingPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreateRatingPage],
      providers: [provideZonelessChangeDetection(), provideRouter([]), provideHttpClient(), provideHttpClientTesting()]
    })
      .compileComponents();

    fixture = TestBed.createComponent(CreateRatingPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
