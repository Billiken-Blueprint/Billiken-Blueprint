import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SchedulingService, AutogenerateScheduleResponse } from '../services/scheduling-service/scheduling-service';
import { ChatbotService } from '../services/chatbot-service/chatbot-service';

interface ScheduleBlock {
  type: 'section' | 'unavailable' | 'avoid';
  title?: string;
  courseCode?: string;
  instructors?: string[];
  startTime: string;
  endTime: string;
  leftPercent: number;
  widthPercent: number;
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
  chatbotService = inject(ChatbotService);

  days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  times = ['8am', '9am', '10am', '11am', '12pm', '1pm', '2pm', '3pm', '4pm', '5pm'];

  // Data for the horizontal timeline
  scheduleCourses = signal<ScheduleBlock[][]>(Array(5).fill(null).map(() => []));
  scheduleSections = signal<Array<{ id: number; courseCode: string; title: string; requirementLabels: string[] }>>([]);
  minTimePercent = signal<number>(0);
  maxTimePercent = signal<number>(100);
  discardedSectionIds = signal<number[]>([]);

  // Time percentages for the timeline header
  timePercentages: number[] = [];

  private schedulingService = inject(SchedulingService);

  ngOnInit() {
    this.calculateTimePercentages();
    this.loadSchedule();
  }

  loadSchedule() {
    this.schedulingService.autoGenerateSchedule(this.discardedSectionIds()).subscribe({
      next: (response) => {
        this.processScheduleData(response);
      },
      error: (err) => {
        console.error('Failed to load schedule', err);
      }
    });
  }

  regenerateSchedule() {
    this.loadSchedule();
  }

  discardSection(sectionId: number) {
    this.discardedSectionIds.update(ids => [...ids, sectionId]);
    this.loadSchedule();
  }

  private processScheduleData(data: AutogenerateScheduleResponse): void {
    const schedule: ScheduleBlock[][] = Array(5).fill(null).map(() => []);
    const sections: Array<{ id: number; courseCode: string; title: string; requirementLabels: string[] }> = [];
    let minTime = Infinity;
    let maxTime = -Infinity;

    if (data.discardedSectionIds) {
      this.discardedSectionIds.set(data.discardedSectionIds);
    }

    // Helper to process time range
    const processTime = (startTime: string, endTime: string) => {
      const start = this.timeToPercent(startTime);
      const end = this.timeToPercent(endTime);
      minTime = Math.min(minTime, start);
      maxTime = Math.max(maxTime, end);
      return { start, end };
    };

    // 1. Sections
    data.sections.forEach((section) => {
      sections.push({
        id: section.id || 0,
        courseCode: section.courseCode,
        title: section.title,
        requirementLabels: section.requirementLabels || []
      });

      section.meetingTimes.forEach((meeting) => {
        processTime(meeting.startTime, meeting.endTime);
      });
    });

    // 2. Unavailability
    data.unavailabilityTimes?.forEach((time) => {
      processTime(time.start, time.end);
    });

    // 3. Avoid
    data.avoidTimes?.forEach((time) => {
      processTime(time.start, time.end);
    });

    // Enforce default range (8am - 5pm)
    const defaultMin = this.timeToPercent('0800');
    const defaultMax = this.timeToPercent('1700');

    if (minTime === Infinity) minTime = defaultMin;
    else minTime = Math.min(minTime, defaultMin);

    if (maxTime === -Infinity) maxTime = defaultMax;
    else maxTime = Math.max(maxTime, defaultMax);

    // Buffer range slightly
    const buffer = (60 / 1440) * 100; // 1 hour buffer
    minTime = Math.max(0, minTime - buffer);
    maxTime = Math.min(100, maxTime + buffer);

    this.minTimePercent.set(minTime);
    this.maxTimePercent.set(maxTime);

    // Recalculate header percentages based on new range
    this.calculateTimePercentages();

    // Second pass: build schedule
    const timeRange = maxTime - minTime;

    const createBlock = (type: 'section' | 'unavailable' | 'avoid', startTime: string, endTime: string, extra?: any): ScheduleBlock => {
      const startPercent = this.timeToPercent(startTime);
      const endPercent = this.timeToPercent(endTime);
      const leftPercent = ((startPercent - minTime) / timeRange) * 100;
      const widthPercent = ((endPercent - startPercent) / timeRange) * 100;

      return {
        type,
        startTime,
        endTime,
        leftPercent,
        widthPercent,
        ...extra
      };
    };

    data.sections.forEach((section) => {
      section.meetingTimes.forEach((meeting) => {
        if (meeting.day >= 0 && meeting.day < 5) {
          schedule[meeting.day].push(createBlock('section', meeting.startTime, meeting.endTime, {
            courseCode: section.courseCode,
            title: section.title,
            instructors: section.instructorNames
          }));
        }
      });
    });

    data.unavailabilityTimes?.forEach((time) => {
      if (time.day >= 0 && time.day < 5) {
        schedule[time.day].push(createBlock('unavailable', time.start, time.end, { title: 'Busy' }));
      }
    });

    data.avoidTimes?.forEach((time) => {
      if (time.day >= 0 && time.day < 5) {
        schedule[time.day].push(createBlock('avoid', time.start, time.end, { title: 'Avoid' }));
      }
    });

    this.scheduleCourses.set(schedule);
    this.scheduleSections.set(sections);
  }

  timeToPercent(timeStr: string): number {
    if (!timeStr) {
      console.warn('timeToPercent received empty time string');
      return 0;
    }
    const hours = parseInt(timeStr.substring(0, 2), 10);
    const mins = parseInt(timeStr.substring(2, 4), 10);
    const totalMinutes = hours * 60 + mins;
    return (totalMinutes / 1440) * 100;
  }

  calculateTimePercentages() {
    this.timePercentages = this.times.map(time => {
      const match = time.match(/(\d+)(am|pm)/);
      if (!match) return 0;
      let hours = parseInt(match[1], 10);
      const isPm = match[2] === 'pm';
      if (hours === 12) hours = isPm ? 12 : 0;
      else if (isPm) hours += 12;
      const timeStr = `${String(hours).padStart(2, '0')}00`;
      return this.timeToPercent(timeStr);
    });
  }

  formatTime(timeStr: string): string {
    if (!timeStr) return '';
    let hours = parseInt(timeStr.substring(0, 2), 10);
    const mins = timeStr.substring(2, 4);
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    if (hours === 0) hours = 12;
    return `${hours}:${mins} ${ampm}`;
  }
}
