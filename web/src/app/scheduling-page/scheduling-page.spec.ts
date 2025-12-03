import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { of } from 'rxjs';
import { SchedulingService } from '../services/scheduling-service/scheduling-service';
import { SchedulingPage } from './scheduling-page';

describe('SchedulingPage', () => {
  let component: SchedulingPage;
  let fixture: ComponentFixture<SchedulingPage>;

  beforeEach(async () => {
    const schedulingServiceMock = {
      getRequirements: () => of([]),
      autoGenerateSchedule: () => of({ sections: [], requirementsCovered: 0 })
    };

    await TestBed.configureTestingModule({
      imports: [SchedulingPage],
      providers: [
        provideZonelessChangeDetection(),
        { provide: SchedulingService, useValue: schedulingServiceMock }
      ]
    })
      .compileComponents();

    fixture = TestBed.createComponent(SchedulingPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
