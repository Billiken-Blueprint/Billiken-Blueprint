import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

interface TimeSlot {
  time: string;
  courses: CourseOnSchedule[];
}

interface CourseOnSchedule {
  code: string;
  name: string;
  instructor: string;
  location: string;
  credits: number;
  startTime: string;
  endTime: string;
  day: string;
  color: string;
}

@Component({
  selector: 'app-schedule',
  imports: [CommonModule],
  templateUrl: './schedule-page.html',
  styleUrl: './schedule-page.css',
  host: {
    class: 'block w-full h-full flex-grow flex flex-col'
  }
})
export class SchedulePage implements OnInit {
  semester = 'Spring 2026';
  totalCredits = 15;
  
  daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  timeSlots = [
    '8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM'
  ];

  courses: CourseOnSchedule[] = [];
  private colorClasses = [
    'from-blue-500/40 to-blue-600/20 border-blue-400/50',
    'from-purple-500/40 to-purple-600/20 border-purple-400/50',
    'from-cyan-500/40 to-cyan-600/20 border-cyan-400/50',
    'from-pink-500/40 to-pink-600/20 border-pink-400/50',
    'from-indigo-500/40 to-indigo-600/20 border-indigo-400/50',
    'from-amber-500/40 to-amber-600/20 border-amber-400/50',
    'from-emerald-500/40 to-emerald-600/20 border-emerald-400/50',
    'from-rose-500/40 to-rose-600/20 border-rose-400/50',
  ];

  ngOnInit() {
    this.courses = this.generateSchedule();
  }

  getCoursesForDayAndTime(day: string, hour: string): CourseOnSchedule[] {
    return this.courses.filter(course => 
      course.day === day && course.startTime === hour
    );
  }

  private getRandomColor(): string {
    return this.colorClasses[Math.floor(Math.random() * this.colorClasses.length)];
  }

  private getRandomTime(): string {
    const times = ['8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM'];
    return times[Math.floor(Math.random() * times.length)];
  }

  private getRandomDays(): string[] {
    const dayCombinations = [
      ['Monday', 'Wednesday', 'Friday'],
      ['Tuesday', 'Thursday'],
      ['Monday', 'Wednesday'],
      ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
      ['Tuesday', 'Wednesday', 'Thursday'],
    ];
    return dayCombinations[Math.floor(Math.random() * dayCombinations.length)];
  }

  private generateSchedule(): CourseOnSchedule[] {
    const allCourses = [
      { code: 'CS 3000', name: 'Algorithms', credits: 3 },
      { code: 'CS 3500', name: 'Web Development', credits: 3 },
      { code: 'CS 4000', name: 'Database Systems', credits: 3 },
      { code: 'CS 4200', name: 'Software Engineering', credits: 3 },
      { code: 'MATH 2100', name: 'Linear Algebra', credits: 4 },
      { code: 'MATH 2500', name: 'Probability & Statistics', credits: 4 },
      { code: 'ENG 2200', name: 'Literature and Composition', credits: 3 },
      { code: 'PHYS 2050', name: 'Physics II', credits: 2 },
      { code: 'CHEM 1030', name: 'Chemistry I', credits: 4 },
      { code: 'BIOL 1040', name: 'Biology I', credits: 3 },
    ];

    const instructors = [
      'Dr. Sarah Johnson',
      'Prof. Michael Chen',
      'Dr. Emily Rodriguez',
      'Prof. James Wilson',
      'Dr. David Kumar',
      'Prof. Lisa Anderson',
      'Dr. Robert Martinez',
      'Prof. Jennifer Taylor',
    ];

    const locations = [
      'Science Building 201',
      'Science Building 310',
      'Math Building 105',
      'Tech Center 301',
      'Humanities 220',
      'Engineering Building 150',
      'Life Sciences 250',
      'Chemistry Lab 301',
    ];

    // Randomly select 5 courses for the schedule
    const selectedCourses = [];
    const shuffled = allCourses.sort(() => Math.random() - 0.5);
    for (let i = 0; i < 5; i++) {
      selectedCourses.push({
        ...shuffled[i],
        instructor: instructors[Math.floor(Math.random() * instructors.length)],
        location: locations[Math.floor(Math.random() * locations.length)],
        startTime: this.getRandomTime(),
        days: this.getRandomDays(),
        color: this.getRandomColor()
      });
    }

    // Create schedule entries for each day/time combination
    const schedule: CourseOnSchedule[] = [];
    selectedCourses.forEach(course => {
      course.days.forEach(day => {
        schedule.push({
          code: course.code,
          name: course.name,
          instructor: course.instructor,
          location: course.location,
          credits: course.credits,
          startTime: course.startTime,
          endTime: this.addMinutes(course.startTime, 90),
          day: day,
          color: course.color
        });
      });
    });

    return schedule;
  }

  private addMinutes(time: string, minutes: number): string {
    const [timePart, period] = time.split(' ');
    const [hours, mins] = timePart.split(':').map(Number);
    let totalMinutes = hours * 60 + (mins || 0) + minutes;
    
    let newHours = Math.floor(totalMinutes / 60) % 12;
    if (newHours === 0) newHours = 12;
    const newMins = totalMinutes % 60;
    
    const newPeriod = totalMinutes >= 12 * 60 ? 'PM' : 'AM';
    return `${newHours}:${newMins === 0 ? '00' : newMins} ${newPeriod}`;
  }

  regenerateSchedule() {
    // Regenerate a completely new schedule with different courses, times, instructors, and locations
    this.courses = this.generateSchedule();
    console.log('Schedule regenerated with', this.courses.length, 'course sessions');
  }
}
