import { ComponentFixture, TestBed } from '@angular/core/testing';
import { QuestionnairePage } from './questionnaire';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { provideZonelessChangeDetection } from '@angular/core';

describe('QuestionnairePage Time Conversion', () => {
    let component: QuestionnairePage;
    let fixture: ComponentFixture<QuestionnairePage>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [QuestionnairePage],
            providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting(), provideZonelessChangeDetection()]
        }).compileComponents();

        fixture = TestBed.createComponent(QuestionnairePage);
        component = fixture.componentInstance;
    });

    describe('convertTimeToHHMM', () => {
        it('should convert HH:MM format to HHMM format', () => {
            expect(component.convertTimeToHHMM('09:00')).toBe('0900');
            expect(component.convertTimeToHHMM('17:30')).toBe('1730');
            expect(component.convertTimeToHHMM('12:45')).toBe('1245');
        });

        it('should handle early morning times', () => {
            expect(component.convertTimeToHHMM('08:00')).toBe('0800');
            expect(component.convertTimeToHHMM('07:15')).toBe('0715');
        });

        it('should handle afternoon times', () => {
            expect(component.convertTimeToHHMM('13:00')).toBe('1300');
            expect(component.convertTimeToHHMM('16:45')).toBe('1645');
            expect(component.convertTimeToHHMM('23:59')).toBe('2359');
        });

        it('should return default time when input is empty', () => {
            expect(component.convertTimeToHHMM('')).toBe('0900');
        });

        it('should return default time when input is null or undefined', () => {
            expect(component.convertTimeToHHMM(null as any)).toBe('0900');
            expect(component.convertTimeToHHMM(undefined as any)).toBe('0900');
        });

        it('should handle times with leading zeros', () => {
            expect(component.convertTimeToHHMM('00:00')).toBe('0000');
            expect(component.convertTimeToHHMM('01:30')).toBe('0130');
            expect(component.convertTimeToHHMM('09:05')).toBe('0905');
        });
    });
});
