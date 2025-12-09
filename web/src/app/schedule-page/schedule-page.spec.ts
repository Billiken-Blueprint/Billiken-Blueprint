import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SchedulePage } from './schedule-page';
import { SchedulingService, AutogenerateScheduleResponse } from '../services/scheduling-service/scheduling-service';
import { ChatbotService } from '../services/chatbot-service/chatbot-service';
import { of, throwError } from 'rxjs';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideZonelessChangeDetection } from '@angular/core';

describe('SchedulePage', () => {
    let component: SchedulePage;
    let fixture: ComponentFixture<SchedulePage>;
    let schedulingServiceSpy: jasmine.SpyObj<SchedulingService>;

    const mockScheduleResponse: AutogenerateScheduleResponse = {
        sections: [
            {
                id: 1,
                crn: '12345',
                instructorNames: ['Dr. Smith'],
                campusCode: 'STL',
                description: 'Intro to CS',
                title: 'Intro CS',
                courseCode: 'CS 1010',
                semester: 'Spring 2026',
                requirementLabels: ['Core'],
                meetingTimes: [
                    { day: 0, startTime: '0900', endTime: '0950' }, // Monday 9:00 AM - 9:50 AM
                    { day: 2, startTime: '0900', endTime: '0950' }  // Wednesday 9:00 AM - 9:50 AM
                ]
            }
        ],
        unavailabilityTimes: [
            { day: 1, start: '1200', end: '1300' } // Tuesday 12pm - 1pm
        ],
        avoidTimes: [
            { day: 4, start: '1600', end: '1700' } // Friday 4pm - 5pm
        ]
    };

    beforeEach(async () => {
        schedulingServiceSpy = jasmine.createSpyObj('SchedulingService', ['autoGenerateSchedule']);
        schedulingServiceSpy.autoGenerateSchedule.and.returnValue(of(mockScheduleResponse));

        await TestBed.configureTestingModule({
            imports: [SchedulePage],
            providers: [
                provideHttpClient(),
                provideHttpClientTesting(),
                provideZonelessChangeDetection(),
                { provide: SchedulingService, useValue: schedulingServiceSpy },
                { provide: ChatbotService, useValue: { open: jasmine.createSpy('open') } }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(SchedulePage);
        component = fixture.componentInstance;
        fixture.detectChanges(); // triggers ngOnInit -> loadSchedule
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should load schedule on init', () => {
        expect(schedulingServiceSpy.autoGenerateSchedule).toHaveBeenCalled();
    });

    it('should process schedule data and update scheduleCourses signal', () => {
        // Check Section
        const mondayCourses = component.scheduleCourses()[0];
        expect(mondayCourses.length).toBe(1);
        expect(mondayCourses[0].type).toBe('section');
        expect(mondayCourses[0].courseCode).toBe('CS 1010');

        // Check Unavailable
        const tuesdayCourses = component.scheduleCourses()[1];
        expect(tuesdayCourses.length).toBe(1);
        expect(tuesdayCourses[0].type).toBe('unavailable');

        // Check Avoid
        const fridayCourses = component.scheduleCourses()[4];
        expect(fridayCourses.length).toBe(1);
        expect(fridayCourses[0].type).toBe('avoid');

        const sections = component.scheduleSections();
        expect(sections.length).toBe(1);
        expect(sections[0].courseCode).toBe('CS 1010');
        expect(sections[0].requirementLabels).toEqual(['Core']);
    });

    it('should calculate time percentages accurately', () => {
        // 9:00 = (9*60)/1440 * 100 = 37.5%
        const percent = component.timeToPercent('0900');
        expect(percent).toBeCloseTo(37.5);
    });

    it('should format time string correctly', () => {
        expect(component.formatTime('1330')).toBe('1:30 PM');
        expect(component.formatTime('0905')).toBe('9:05 AM');
    });
});
