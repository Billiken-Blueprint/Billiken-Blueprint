import { Component, inject, OnInit, signal } from '@angular/core';
import { GraduationRequirement, SchedulingService, AutogenerateScheduleResponse } from '../services/scheduling-service/scheduling-service';
import { CommonModule } from '@angular/common';
import { Button } from 'primeng/button';

interface ScheduleSlot {
  courseCode?: string;
  title?: string;
  instructors?: string[];
  startTime?: string;
  endTime?: string;
  rowSpan?: number;
}

interface ScheduleCourse {
  courseCode: string;
  title: string;
  instructors: string[];
  startTime: string;
  endTime: string;
  leftPercent: number;
  widthPercent: number;
}

@Component({
  selector: 'app-scheduling-page',
  imports: [CommonModule, Button],
  templateUrl: './scheduling-page.html',
  styleUrl: './scheduling-page.css',
  host: {
    class: 'flex-grow flex flex-col'
  }
})
export class SchedulingPage implements OnInit {
  gradReqs = signal<GraduationRequirement[]>([]);
  showRequirements = signal<boolean>(false);
  showSchedule = signal<boolean>(false);
  expandedRequirements = signal<Set<number>>(new Set());
  expandedClasses = signal<Set<string>>(new Set());
  scheduleData = signal<AutogenerateScheduleResponse | null>(null);
  scheduleCourses = signal<ScheduleCourse[][]>(Array(5).fill(null).map(() => []));
  scheduleSections = signal<Array<{ courseCode: string; title: string; requirementLabels: string[] }>>([]);
  minTimePercent = signal<number>(this.timeToPercent('0600')); // 6am
  maxTimePercent = signal<number>(this.timeToPercent('1900')); // 7pm
  private schedulingService = inject(SchedulingService);

  days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  times = ['12am', '1am', '2am', '3am', '4am', '5am', '6am', '7am', '8am', '9am', '10am', '11am', '12pm', '1pm', '2pm', '3pm', '4pm', '5pm', '6pm', '7pm', '8pm', '9pm', '10pm', '11pm'];

  // Pre-computed time percentages for template use
  timePercentages = this.times.map(time => {
    const match = time.match(/(\d+)(am|pm)/);
    if (!match) return 0;
    let hours = parseInt(match[1], 10);
    const isPm = match[2] === 'pm';
    if (hours === 12) hours = isPm ? 12 : 0;
    else if (isPm) hours += 12;
    const timeStr = `${String(hours).padStart(2, '0')}00`;
    return this.timeToPercent(timeStr);
  });

  ngOnInit(): void {
    this.schedulingService.getRequirements().subscribe(x => {
      this.gradReqs.set(x);
    });
  }

  toggleShowRequirements(): void {
    this.showRequirements.update(v => !v);
  }

  toggleShowSchedule(): void {
    this.showSchedule.update(v => !v);
  }

  autogenerateSchedule(): void {
    this.schedulingService.autoGenerateSchedule().subscribe(
      (response) => {
        this.scheduleData.set(response);
        this.buildScheduleGrid(response);
        console.log('After build - min:', this.minTimePercent(), 'max:', this.maxTimePercent());
        console.log('Courses:', this.scheduleCourses());
      },
      (error) => {
        console.error('Error autogenerating schedule:', error);
      }
    );
  }

  private buildScheduleGrid(data: AutogenerateScheduleResponse): void {
    // Initialize schedule for each day
    const schedule: ScheduleCourse[][] = Array(5).fill(null).map(() => []);
    const sections: Array<{ courseCode: string; title: string; requirementLabels: string[] }> = [];
    let minTime = Infinity;
    let maxTime = -Infinity;

    // First pass: find min/max times from actual courses
    data.sections.forEach((section) => {
      section.meetingTimes.forEach((meeting) => {
        const startPercent = this.timeToPercent(meeting.startTime);
        const endPercent = this.timeToPercent(meeting.endTime);
        minTime = Math.min(minTime, startPercent);
        maxTime = Math.max(maxTime, endPercent);
      });
    });

    // Apply defaults if no courses found
    if (minTime === Infinity) minTime = this.timeToPercent('0600'); // Default 6am
    if (maxTime === -Infinity) maxTime = this.timeToPercent('1900'); // Default 7pm

    // Expand by 2 hours on both sides (120 minutes = 8.33% of 1440)
    const twoHoursPercent = (120 / 1440) * 100;
    minTime = Math.max(0, minTime - twoHoursPercent);
    maxTime = Math.min(100, maxTime + twoHoursPercent);

    // Second pass: build schedule with adjusted positions
    const timeRange = maxTime - minTime;
    data.sections.forEach((section) => {
      // Collect section info
      sections.push({
        courseCode: section.courseCode,
        title: section.title,
        requirementLabels: section.requirementLabels || []
      });

      section.meetingTimes.forEach((meeting) => {
        const dayIndex = meeting.day;
        if (dayIndex >= 0 && dayIndex < 5) {
          const startPercent = this.timeToPercent(meeting.startTime);
          const endPercent = this.timeToPercent(meeting.endTime);

          // Calculate adjusted percentages relative to the visible range (0-100)
          const adjustedLeftPercent = ((startPercent - minTime) / timeRange) * 100;
          const adjustedWidthPercent = ((endPercent - startPercent) / timeRange) * 100;

          schedule[dayIndex].push({
            courseCode: section.courseCode,
            title: section.title,
            instructors: section.instructorNames,
            startTime: meeting.startTime,
            endTime: meeting.endTime,
            leftPercent: adjustedLeftPercent,
            widthPercent: adjustedWidthPercent
          });
        }
      });
    });

    this.minTimePercent.set(minTime);
    this.maxTimePercent.set(maxTime);
    this.scheduleCourses.set(schedule);
    this.scheduleSections.set(sections);
  }

  timeToPercent(timeStr: string): number {
    // Convert "0845" to percentage of day (0-100)
    const hours = parseInt(timeStr.substring(0, 2), 10);
    const mins = parseInt(timeStr.substring(2, 4), 10);
    const totalMinutes = hours * 60 + mins;
    return (totalMinutes / 1440) * 100; // 1440 minutes in a day
  }

  formatTime(timeStr: string | undefined): string {
    if (!timeStr) return '';
    // Format "0845" to "8:45 AM" or "1735" to "5:35 PM"
    const hours = parseInt(timeStr.substring(0, 2), 10);
    const mins = timeStr.substring(2, 4);
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours > 12 ? hours - 12 : (hours === 0 ? 12 : hours);
    return `${displayHours}:${mins} ${ampm}`;
  }

  toggleRequirement(index: number): void {
    const updated = new Set(this.expandedRequirements());
    if (updated.has(index)) {
      updated.delete(index);
    } else {
      updated.add(index);
    }
    this.expandedRequirements.set(updated);
  }

  isRequirementExpanded(index: number): boolean {
    return this.expandedRequirements().has(index);
  }

  toggleClass(coursCode: string): void {
    const updated = new Set(this.expandedClasses());
    if (updated.has(coursCode)) {
      updated.delete(coursCode);
    } else {
      updated.add(coursCode);
    }
    this.expandedClasses.set(updated);
  }

  isClassExpanded(coursCode: string): boolean {
    return this.expandedClasses().has(coursCode);
  }
}
