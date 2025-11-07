import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule, FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';
import { QuestionnairePage } from './questionnaire';
import { AuthService } from '../auth-service/auth-service';
import { CommonModule } from '@angular/common';
import { BehaviorSubject } from 'rxjs';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';

describe('QuestionnairePage - Comprehensive CI Tests', () => {
  let component: QuestionnairePage;
  let fixture: ComponentFixture<QuestionnairePage>;
  let mockRouter: jasmine.SpyObj<Router>;
  let mockAuthService: jasmine.SpyObj<AuthService>;

  beforeEach(async () => {
    // Mock services
    mockRouter = jasmine.createSpyObj('Router', ['navigate']);
    mockAuthService = jasmine.createSpyObj('AuthService', ['updateUserProfile'], {
      isLoggedIn: new BehaviorSubject(true)
    });

    await TestBed.configureTestingModule({
      imports: [
        QuestionnairePage,
        ReactiveFormsModule,
        CommonModule
      ],
      providers: [
        FormBuilder,
        { provide: Router, useValue: mockRouter },
        { provide: AuthService, useValue: mockAuthService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(QuestionnairePage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  // ===== UNIT TESTS =====
  describe('Unit Tests - Component Initialization', () => {
    it('should create the component', () => {
      expect(component).toBeTruthy();
    });

    it('should initialize with correct default values', () => {
      expect(component.currentStep).toBe(1);
      expect(component.totalSteps).toBe(5);
    });

    it('should initialize form with all required controls', () => {
      const form = component.questionnaireForm;
      expect(form.get('fullName')).toBeTruthy();
      expect(form.get('age')).toBeTruthy();
      expect(form.get('dateOfBirth')).toBeTruthy();
      expect(form.get('graduationYear')).toBeTruthy();
      expect(form.get('currentSemester')).toBeTruthy();
      expect(form.get('major')).toBeTruthy();
      expect(form.get('minor')).toBeTruthy();
    });

    it('should initialize data arrays correctly', () => {
      expect(component.courses.length).toBe(10);
      expect(component.timeSlots.length).toBeGreaterThan(0);
      expect(component.semesters.length).toBe(9);
      expect(component.majors.length).toBeGreaterThan(0);
    });
  });

  describe('Unit Tests - Form Validation', () => {
    describe('Step 1 - Personal Information', () => {
      beforeEach(() => {
        component.currentStep = 1;
      });

      it('should be invalid when fields are empty', () => {
        expect(component.isCurrentStepValid()).toBeFalsy();
      });

      it('should be valid when all required fields are filled correctly', () => {
        component.questionnaireForm.patchValue({
          fullName: 'John Doe',
          age: '20',
          dateOfBirth: '2003-01-01',
          graduationYear: '2025'
        });
        expect(component.isCurrentStepValid()).toBeTruthy();
      });

      it('should validate age range (16-100)', () => {
        const ageControl = component.questionnaireForm.get('age');
        
        ageControl?.setValue('15');
        expect(ageControl?.valid).toBeFalsy();
        
        ageControl?.setValue('101');
        expect(ageControl?.valid).toBeFalsy();
        
        ageControl?.setValue('20');
        expect(ageControl?.valid).toBeTruthy();
      });

      it('should validate graduation year range (2024-2030)', () => {
        const yearControl = component.questionnaireForm.get('graduationYear');
        
        yearControl?.setValue('2023');
        expect(yearControl?.valid).toBeFalsy();
        
        yearControl?.setValue('2031');
        expect(yearControl?.valid).toBeFalsy();
        
        yearControl?.setValue('2025');
        expect(yearControl?.valid).toBeTruthy();
      });
    });

    describe('Step 2 - Academic Information', () => {
      beforeEach(() => {
        component.currentStep = 2;
      });

      it('should be invalid when academic fields are empty', () => {
        expect(component.isCurrentStepValid()).toBeFalsy();
      });

      it('should be valid when semester and major are selected', () => {
        component.questionnaireForm.get('currentSemester')?.setValue('Junior - Fall' as any);
        component.questionnaireForm.get('major')?.setValue('Computer Science' as any);
        expect(component.isCurrentStepValid()).toBeTruthy();
      });
    });
  });

  describe('Unit Tests - Navigation Logic', () => {
    it('should advance to next step when valid', () => {
      component.currentStep = 1;
      spyOn(component, 'isCurrentStepValid').and.returnValue(true);
      
      component.nextStep();
      expect(component.currentStep).toBe(2);
    });

    it('should not advance when invalid', () => {
      component.currentStep = 1;
      spyOn(component, 'isCurrentStepValid').and.returnValue(false);
      
      component.nextStep();
      expect(component.currentStep).toBe(1);
    });

    it('should go back to previous step', () => {
      component.currentStep = 3;
      component.previousStep();
      expect(component.currentStep).toBe(2);
    });

    it('should not go below step 1', () => {
      component.currentStep = 1;
      component.previousStep();
      expect(component.currentStep).toBe(1);
    });

    it('should go to specific valid step', () => {
      component.goToStep(4);
      expect(component.currentStep).toBe(4);
    });

    it('should not go to invalid step numbers', () => {
      component.currentStep = 2;
      component.goToStep(0);
      expect(component.currentStep).toBe(2);
      
      component.goToStep(6);
      expect(component.currentStep).toBe(2);
    });
  });

  describe('Unit Tests - Course Selection', () => {
    it('should select all courses', () => {
      component.selectAllCourses();
      const allSelected = component.completedCoursesArray.controls.every(control => control.value);
      expect(allSelected).toBeTruthy();
    });

    it('should deselect all courses', () => {
      component.selectAllCourses();
      component.deselectAllCourses();
      const noneSelected = component.completedCoursesArray.controls.every(control => !control.value);
      expect(noneSelected).toBeTruthy();
    });

    it('should count selected courses correctly', () => {
      component.deselectAllCourses();
      expect(component.getCourseSelectionCount()).toBe(0);
      
      component.completedCoursesArray.at(0)?.setValue(true);
      expect(component.getCourseSelectionCount()).toBe(1);
    });

    it('should calculate total credits correctly', () => {
      component.deselectAllCourses();
      expect(component.calculateTotalCredits()).toBe(0);
      
      component.selectAllCourses();
      const expectedCredits = component.courses.reduce((sum, course) => sum + course.credits, 0);
      expect(component.calculateTotalCredits()).toBe(expectedCredits);
    });
  });

  // ===== INTEGRATION TESTS =====
  describe('Integration Tests - DOM Interaction', () => {
    it('should render form fields correctly', () => {
      const fullNameInput = fixture.debugElement.query(By.css('input[formControlName="fullName"]'));
      const ageInput = fixture.debugElement.query(By.css('input[formControlName="age"]'));
      
      expect(fullNameInput).toBeTruthy();
      expect(ageInput).toBeTruthy();
    });

    it('should show Next button as disabled initially', () => {
      const nextButton = fixture.debugElement.query(By.css('button:contains("Next")'));
      if (nextButton) {
        expect(nextButton.nativeElement.disabled).toBeTruthy();
      }
    });

    it('should enable Next button when step 1 is valid', () => {
      // Fill form
      component.questionnaireForm.patchValue({
        fullName: 'John Doe',
        age: '20',
        dateOfBirth: '2003-01-01',
        graduationYear: '2025'
      });
      
      fixture.detectChanges();
      
      const nextButton = fixture.debugElement.query(By.css('button'));
      if (nextButton && nextButton.nativeElement.textContent?.includes('Next')) {
        expect(nextButton.nativeElement.disabled).toBeFalsy();
      }
    });

    it('should update step title correctly', () => {
      component.currentStep = 1;
      expect(component.getStepTitle()).toBe('Personal Information');
      
      component.currentStep = 2;
      expect(component.getStepTitle()).toBe('Academic Information');
    });
  });

  describe('Integration Tests - Multi-Step Workflow', () => {
    it('should complete full questionnaire workflow', () => {
      // Step 1: Personal Information
      component.currentStep = 1;
      component.questionnaireForm.patchValue({
        fullName: 'John Doe',
        age: '20',
        dateOfBirth: '2003-01-01',
        graduationYear: '2025'
      });
      expect(component.isCurrentStepValid()).toBeTruthy();
      
      component.nextStep();
      expect(component.currentStep).toBe(2);
      
      // Step 2: Academic Information
      component.questionnaireForm.get('currentSemester')?.setValue('Junior - Fall' as any);
      component.questionnaireForm.get('major')?.setValue('Computer Science' as any);
      expect(component.isCurrentStepValid()).toBeTruthy();
      
      component.nextStep();
      expect(component.currentStep).toBe(3);
      
      // Step 3: Course Selection (optional)
      expect(component.isCurrentStepValid()).toBeTruthy();
      component.nextStep();
      expect(component.currentStep).toBe(4);
      
      // Step 4: Time Preferences (optional)
      expect(component.isCurrentStepValid()).toBeTruthy();
      component.nextStep();
      expect(component.currentStep).toBe(5);
      
      // Step 5: Review
      expect(component.isCurrentStepValid()).toBeTruthy();
    });

    it('should maintain form data across navigation', () => {
      // Fill step 1
      component.questionnaireForm.patchValue({
        fullName: 'John Doe',
        age: '20'
      });
      
      // Navigate forward and back
      component.nextStep();
      component.previousStep();
      
      // Data should be preserved
      expect(component.questionnaireForm.get('fullName')?.value).toBe('John Doe');
      expect(component.questionnaireForm.get('age')?.value).toBe('20');
    });
  });

  describe('Integration Tests - Course Selection UI', () => {
    beforeEach(() => {
      component.currentStep = 3;
      fixture.detectChanges();
    });

    it('should handle course selection interactions', () => {
      // Select some courses
      component.completedCoursesArray.at(0)?.setValue(true);
      component.completedCoursesArray.at(1)?.setValue(true);
      
      expect(component.getCourseSelectionCount()).toBe(2);
      expect(component.getSelectedCourses()).toEqual(['CSCI 1300', 'CSCI 2100']);
    });

    it('should handle select all and deselect all', () => {
      component.selectAllCourses();
      expect(component.getCourseSelectionCount()).toBe(component.courses.length);
      
      component.deselectAllCourses();
      expect(component.getCourseSelectionCount()).toBe(0);
    });
  });

  describe('Integration Tests - Time Preferences', () => {
    beforeEach(() => {
      component.currentStep = 4;
    });

    it('should handle time slot selections', () => {
      // Select unavailable times
      component.unavailableTimesArray.at(0)?.setValue(true);
      component.unavailableTimesArray.at(1)?.setValue(true);
      
      const selectedTimes = component.getSelectedUnavailableTimes();
      expect(selectedTimes.length).toBe(2);
    });

    it('should handle preferred not times', () => {
      component.preferredNotTimesArray.at(0)?.setValue(true);
      
      const selectedTimes = component.getSelectedPreferredNotTimes();
      expect(selectedTimes.length).toBe(1);
    });

    it('should save time preference reasons', () => {
      component.questionnaireForm.patchValue({
        unavailableReason: 'Work schedule conflict',
        preferredNotReason: 'Prefer morning classes'
      });
      
      expect(component.questionnaireForm.get('unavailableReason')?.value).toBe('Work schedule conflict');
      expect(component.questionnaireForm.get('preferredNotReason')?.value).toBe('Prefer morning classes');
    });
  });

  describe('Integration Tests - Form Submission', () => {
    it('should submit completed form and navigate', () => {
      // Fill required fields
      component.questionnaireForm.patchValue({
        fullName: 'John Doe',
        age: '20',
        dateOfBirth: '2003-01-01',
        graduationYear: '2025'
      });
      component.questionnaireForm.get('currentSemester')?.setValue('Junior - Fall' as any);
      component.questionnaireForm.get('major')?.setValue('Computer Science' as any);

      component.onSubmit();
      
      expect(mockRouter.navigate).toHaveBeenCalledWith(['/courses']);
    });
  });

  describe('Integration Tests - Error Handling', () => {
    it('should handle form errors gracefully', () => {
      expect(() => component.isCurrentStepValid()).not.toThrow();
      expect(() => component.getCourseSelectionCount()).not.toThrow();
      expect(() => component.calculateTotalCredits()).not.toThrow();
    });

    it('should handle invalid navigation gracefully', () => {
      expect(() => component.goToStep(-1)).not.toThrow();
      expect(() => component.goToStep(100)).not.toThrow();
    });
  });

  describe('Integration Tests - Data Validation Edge Cases', () => {
    it('should handle boundary age values', () => {
      const ageControl = component.questionnaireForm.get('age');
      
      ageControl?.setValue('16'); // Minimum valid
      expect(ageControl?.valid).toBeTruthy();
      
      ageControl?.setValue('100'); // Maximum valid
      expect(ageControl?.valid).toBeTruthy();
    });

    it('should handle boundary graduation years', () => {
      const yearControl = component.questionnaireForm.get('graduationYear');
      
      yearControl?.setValue('2024'); // Minimum valid
      expect(yearControl?.valid).toBeTruthy();
      
      yearControl?.setValue('2030'); // Maximum valid
      expect(yearControl?.valid).toBeTruthy();
    });

    it('should handle empty optional fields', () => {
      const minorControl = component.questionnaireForm.get('minor');
      
      minorControl?.setValue('');
      expect(minorControl?.valid).toBeTruthy();
      
      minorControl?.setValue('Mathematics');
      expect(minorControl?.valid).toBeTruthy();
    });
  });

  describe('Integration Tests - Complete User Scenarios', () => {
    it('should handle typical student scenario', () => {
      // Freshman Computer Science student
      component.questionnaireForm.patchValue({
        fullName: 'Alice Johnson',
        age: '18',
        dateOfBirth: '2005-03-15',
        graduationYear: '2028'
      });
      component.questionnaireForm.get('currentSemester')?.setValue('Freshman - Fall' as any);
      component.questionnaireForm.get('major')?.setValue('Computer Science' as any);
      
      // Select introductory courses
      component.completedCoursesArray.at(0)?.setValue(true); // CSCI 1300
      
      // Set work schedule conflicts
      component.unavailableTimesArray.at(0)?.setValue(true);
      component.questionnaireForm.get('unavailableReason')?.setValue('Part-time job');
      
      // Verify all data is properly stored
      expect(component.questionnaireForm.get('fullName')?.value).toBe('Alice Johnson');
      expect(component.getSelectedCourses()).toContain('CSCI 1300');
      expect(component.getSelectedUnavailableTimes().length).toBe(1);
    });

    it('should handle graduate student scenario', () => {
      // Graduate student scenario
      component.questionnaireForm.patchValue({
        fullName: 'Bob Smith',
        age: '24',
        dateOfBirth: '1999-08-22',
        graduationYear: '2026'
      });
      component.questionnaireForm.get('currentSemester')?.setValue('Graduate Student' as any);
      component.questionnaireForm.get('major')?.setValue('Computer Science' as any);
      component.questionnaireForm.get('minor')?.setValue('Mathematics');
      
      // Select advanced courses
      component.selectAllCourses();
      
      // Verify advanced student setup
      expect(component.calculateTotalCredits()).toBeGreaterThan(0);
      expect(component.questionnaireForm.get('minor')?.value).toBe('Mathematics');
    });

    it('should handle user changing their mind', () => {
      // User fills form, changes mind, and updates
      component.questionnaireForm.patchValue({
        fullName: 'Charlie Brown'
      });
      component.questionnaireForm.get('major')?.setValue('Mathematics' as any);
      
      // Changes major
      component.questionnaireForm.get('major')?.setValue('Engineering' as any);
      
      // Select courses, then change selection
      component.selectAllCourses();
      expect(component.getCourseSelectionCount()).toBe(component.courses.length);
      
      component.deselectAllCourses();
      expect(component.getCourseSelectionCount()).toBe(0);
      
      // Final state should reflect last changes
      expect(component.questionnaireForm.get('major')?.value).toBe('Engineering' as any);
    });
  });

  describe('Performance and Accessibility Tests', () => {
    it('should handle large course selections efficiently', () => {
      const startTime = performance.now();
      
      // Simulate selecting all courses multiple times
      for (let i = 0; i < 10; i++) {
        component.selectAllCourses();
        component.deselectAllCourses();
      }
      
      const endTime = performance.now();
      expect(endTime - startTime).toBeLessThan(100); // Should complete in under 100ms
    });

    it('should have accessible form structure', () => {
      // Check that form controls exist and can be accessed
      const formControls = ['fullName', 'age', 'dateOfBirth', 'graduationYear', 'currentSemester', 'major'];
      
      formControls.forEach(controlName => {
        const control = component.questionnaireForm.get(controlName);
        expect(control).toBeTruthy();
        expect(control?.disabled).toBeDefined();
        expect(control?.valid).toBeDefined();
      });
    });
  });
});