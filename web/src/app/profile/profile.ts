import {Component, inject, OnInit} from '@angular/core';
import {AuthService} from '../auth-service/auth-service';
import {FormBuilder, ReactiveFormsModule, Validators, FormArray, FormControl} from '@angular/forms';
import {CommonModule} from '@angular/common';
import {Router} from '@angular/router';

interface Course {
  code: string;
  name: string;
  credits: number;
}

interface TimeSlot {
  time: string;
  label: string;
}

interface UserProfile {
  fullName?: string;
  age?: number;
  dateOfBirth?: Date;
  graduationYear?: number;
  currentSemester?: string;
  major?: string;
  minor?: string;
  completedCourses?: string[];
  totalCredits?: number;
  unavailableTimes?: string[];
  unavailableReason?: string;
  preferredNotTimes?: string[];
  preferredNotReason?: string;
  questionnaireCompleted?: boolean;
}

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule
  ],
  templateUrl: './profile.html',
  styleUrl: './profile.css'
})
export class ProfilePage implements OnInit {
  userProfile: UserProfile = {};
  isEditing = false;
  courses: Course[] = [
    {code: 'CSCI 1300', name: 'Introduction to Object-Oriented Programming', credits: 4},
    {code: 'CSCI 2100', name: 'Data Structures', credits: 4},
    {code: 'CSCI 2300', name: 'Object-Oriented Software Design', credits: 3},
    {code: 'CSCI 2500', name: 'Computer Organization and Systems', credits: 3},
    {code: 'CSCI 2510', name: 'Principles of Computing Systems', credits: 3},
    {code: 'CSCI 3100', name: 'Algorithms', credits: 3},
    {code: 'CSCI 3200', name: 'Programming Languages', credits: 3},
    {code: 'CSCI 3300', name: 'Software Engineering', credits: 3},
    {code: 'CSCI 4961', name: 'Capstone Project I', credits: 2},
    {code: 'CSCI 4962', name: 'Capstone Project II', credits: 2}
  ];
  timeSlots: TimeSlot[] = [
    {time: '8:00-9:00', label: '8:00 AM - 9:00 AM'},
    {time: '9:00-10:00', label: '9:00 AM - 10:00 AM'},
    {time: '10:00-11:00', label: '10:00 AM - 11:00 AM'},
    {time: '11:00-12:00', label: '11:00 AM - 12:00 PM'},
    {time: '12:00-13:00', label: '12:00 PM - 1:00 PM'},
    {time: '13:00-14:00', label: '1:00 PM - 2:00 PM'},
    {time: '14:00-15:00', label: '2:00 PM - 3:00 PM'},
    {time: '15:00-16:00', label: '3:00 PM - 4:00 PM'},
    {time: '16:00-17:00', label: '4:00 PM - 5:00 PM'},
    {time: '17:00-18:00', label: '5:00 PM - 6:00 PM'},
    {time: '18:00-19:00', label: '6:00 PM - 7:00 PM'},
    {time: '19:00-20:00', label: '7:00 PM - 8:00 PM'},
    {time: '20:00-21:00', label: '8:00 PM - 9:00 PM'}
  ];
  majors = [
    'Computer Science',
    'Mathematics',
    'Engineering',
    'Business',
    'Biology',
    'Chemistry',
    'Physics',
    'English',
    'History',
    'Psychology',
    'Other'
  ];
  minors = [
    'None',
    'Computer Science',
    'Mathematics',
    'Business',
    'Biology',
    'Chemistry',
    'Physics',
    'English',
    'History',
    'Psychology',
    'Other'
  ];
  semesters = [
    'Freshman - Fall',
    'Freshman - Spring',
    'Sophomore - Fall',
    'Sophomore - Spring',
    'Junior - Fall',
    'Junior - Spring',
    'Senior - Fall',
    'Senior - Spring',
    'Graduate Student'
  ];
  private formBuilder = inject(FormBuilder);
  profileForm = this.formBuilder.group({
    fullName: ['', Validators.required],
    age: ['', [Validators.required, Validators.min(16), Validators.max(100)]],
    dateOfBirth: ['', Validators.required],
    graduationYear: ['', [Validators.required, Validators.min(2024), Validators.max(2030)]],
    currentSemester: ['', Validators.required],
    major: ['', Validators.required],
    minor: [''],
    completedCourses: this.formBuilder.array([]),
    unavailableTimes: this.formBuilder.array([]),
    unavailableReason: [''],
    preferredNotTimes: this.formBuilder.array([]),
    preferredNotReason: ['']
  });
  private authService = inject(AuthService);
  private router = inject(Router);

  constructor() {
    // Initialize course checkboxes
    this.courses.forEach(() => {
      this.completedCoursesArray.push(new FormControl(false));
    });

    // Initialize time slot checkboxes
    this.timeSlots.forEach(() => {
      this.unavailableTimesArray.push(new FormControl(false));
      this.preferredNotTimesArray.push(new FormControl(false));
    });
  }

  get completedCoursesArray() {
    return this.profileForm.get('completedCourses') as FormArray;
  }

  get unavailableTimesArray() {
    return this.profileForm.get('unavailableTimes') as FormArray;
  }

  get preferredNotTimesArray() {
    return this.profileForm.get('preferredNotTimes') as FormArray;
  }

  ngOnInit() {
    this.loadProfile();
  }

  loadProfile() {
    /*
    this.authService.getProfile().subscribe({
      next: (profile) => {
        this.userProfile = profile;
        this.populateForm();
      },
      error: (error) => {
        console.error('Error loading profile:', error);
        // If no profile exists, redirect to questionnaire
        if (error.status === 404) {
          this.router.navigate(['/questionnaire']);
        }
      }
    });
     */
  }

  populateForm() {
    if (this.userProfile) {
      this.profileForm.patchValue({
        fullName: this.userProfile.fullName,
        age: this.userProfile.age?.toString(),
        dateOfBirth: this.userProfile.dateOfBirth ? this.userProfile.dateOfBirth.toISOString().split('T')[0] : '',
        graduationYear: this.userProfile.graduationYear?.toString(),
        currentSemester: this.userProfile.currentSemester,
        major: this.userProfile.major,
        minor: this.userProfile.minor,
        unavailableReason: this.userProfile.unavailableReason,
        preferredNotReason: this.userProfile.preferredNotReason
      });

      // Set completed courses
      if (this.userProfile.completedCourses) {
        this.courses.forEach((course, index) => {
          const isCompleted = this.userProfile.completedCourses?.includes(course.code);
          this.completedCoursesArray.at(index).setValue(isCompleted);
        });
      }

      // Set unavailable times
      if (this.userProfile.unavailableTimes) {
        this.timeSlots.forEach((timeSlot, index) => {
          const isUnavailable = this.userProfile.unavailableTimes?.includes(timeSlot.time);
          this.unavailableTimesArray.at(index).setValue(isUnavailable);
        });
      }

      // Set preferred not times
      if (this.userProfile.preferredNotTimes) {
        this.timeSlots.forEach((timeSlot, index) => {
          const isPreferredNot = this.userProfile.preferredNotTimes?.includes(timeSlot.time);
          this.preferredNotTimesArray.at(index).setValue(isPreferredNot);
        });
      }
    }
  }

  calculateTotalCredits(): number {
    let totalCredits = 0;
    this.completedCoursesArray.controls.forEach((control: any, index: number) => {
      if (control.value) {
        totalCredits += this.courses[index].credits;
      }
    });
    return totalCredits;
  }

  getSelectedCourses(): string[] {
    const selectedCourses: string[] = [];
    this.completedCoursesArray.controls.forEach((control: any, index: number) => {
      if (control.value) {
        selectedCourses.push(this.courses[index].code);
      }
    });
    return selectedCourses;
  }

  getSelectedUnavailableTimes(): string[] {
    const selectedTimes: string[] = [];
    this.unavailableTimesArray.controls.forEach((control: any, index: number) => {
      if (control.value) {
        selectedTimes.push(this.timeSlots[index].time);
      }
    });
    return selectedTimes;
  }

  getSelectedPreferredNotTimes(): string[] {
    const selectedTimes: string[] = [];
    this.preferredNotTimesArray.controls.forEach((control: any, index: number) => {
      if (control.value) {
        selectedTimes.push(this.timeSlots[index].time);
      }
    });
    return selectedTimes;
  }

  getCompletedCoursesDisplay(): string[] {
    if (!this.userProfile.completedCourses) return [];
    return this.userProfile.completedCourses.map(courseCode => {
      const course = this.courses.find(c => c.code === courseCode);
      return course ? `${course.code} - ${course.name} (${course.credits} credits)` : courseCode;
    });
  }

  getTimeSlotDisplay(times: string[]): string[] {
    if (!times) return [];
    return times.map(time => {
      const timeSlot = this.timeSlots.find(ts => ts.time === time);
      return timeSlot ? timeSlot.label : time;
    });
  }

  enableEdit() {
    this.isEditing = true;
  }

  cancelEdit() {
    this.isEditing = false;
    this.populateForm(); // Reset form to original values
  }

  saveProfile() {
    if (this.profileForm.valid) {
      const formValue = this.profileForm.value;

      const updatedProfile = {
        fullName: formValue.fullName || '',
        age: parseInt(formValue.age || '0'),
        dateOfBirth: formValue.dateOfBirth ? new Date(formValue.dateOfBirth) : undefined,
        graduationYear: parseInt(formValue.graduationYear || '0'),
        currentSemester: formValue.currentSemester || '',
        major: formValue.major || '',
        minor: formValue.minor || '',
        completedCourses: this.getSelectedCourses(),
        totalCredits: this.calculateTotalCredits(),
        unavailableTimes: this.getSelectedUnavailableTimes(),
        unavailableReason: formValue.unavailableReason || '',
        preferredNotTimes: this.getSelectedPreferredNotTimes(),
        preferredNotReason: formValue.preferredNotReason || '',
        questionnaireCompleted: true
      };

      /*
      this.authService.updateProfile(updatedProfile).subscribe({
        next: (profile) => {
          this.userProfile = profile;
          this.isEditing = false;
        },
        error: (error) => {
          console.error('Error updating profile:', error);
        }
      });
       */
    }
  }

  selectAllCourses() {
    this.completedCoursesArray.controls.forEach(control => {
      control.setValue(true);
    });
  }

  deselectAllCourses() {
    this.completedCoursesArray.controls.forEach(control => {
      control.setValue(false);
    });
  }
}
