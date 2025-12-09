import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DegreeRequirementsPage } from './degree-requirements-page';
import { SchedulingService, GraduationRequirement } from '../services/scheduling-service/scheduling-service';
import { of } from 'rxjs';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { provideZonelessChangeDetection } from '@angular/core';

describe('DegreeRequirementsPage', () => {
    let component: DegreeRequirementsPage;
    let fixture: ComponentFixture<DegreeRequirementsPage>;
    let schedulingServiceSpy: jasmine.SpyObj<SchedulingService>;

    const mockRequirements: GraduationRequirement[] = [
        { label: 'Core', needed: 3, satisfyingCourseCodes: ['CS 1010'] },
        { label: 'Math', needed: 4, satisfyingCourseCodes: ['MATH 1010'] }
    ];

    beforeEach(async () => {
        schedulingServiceSpy = jasmine.createSpyObj('SchedulingService', ['getRequirements']);
        schedulingServiceSpy.getRequirements.and.returnValue(of(mockRequirements));

        await TestBed.configureTestingModule({
            imports: [DegreeRequirementsPage],
            providers: [
                provideHttpClient(),
                provideHttpClientTesting(),
                provideRouter([]),
                provideZonelessChangeDetection(),
                { provide: SchedulingService, useValue: schedulingServiceSpy }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(DegreeRequirementsPage);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should display requirements from service', () => {
        const listItems = component.requirements();
        expect(listItems.length).toBe(2);
        expect(listItems[0].label).toBe('Core');
        expect(listItems[1].label).toBe('Math');
    });

    it('should toggle expansion', () => {
        const req = component.requirements()[0];
        expect(req.expanded).toBeFalse();
        component.toggleCategory(req);
        expect(req.expanded).toBeTrue();
    });
});
