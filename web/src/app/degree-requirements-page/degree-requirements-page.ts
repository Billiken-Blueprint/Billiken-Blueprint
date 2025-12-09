import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

interface Course {
  code: string;
  name: string;
  credits: number;
}

@Component({
  selector: 'app-degree-requirements',
  imports: [CommonModule],
  templateUrl: './degree-requirements-page.html',
  styleUrl: './degree-requirements-page.css',
  host: {
    class: 'block w-full h-full flex-grow flex flex-col'
  }
})
export class DegreeRequirementsPage {
  private router = new Router();

  degreeInfo = {
    name: 'Computer Science (B.S.)',
    totalCredits: 120,
  };

  requirements: Course[] = [
    // Core Computer Science
    { code: 'CS 1000', name: 'Introduction to Computer Science', credits: 3 },
    { code: 'CS 2000', name: 'Data Structures', credits: 3 },
    { code: 'CS 2500', name: 'Discrete Mathematics', credits: 3 },
    { code: 'CS 3000', name: 'Algorithms', credits: 3 },
    { code: 'CS 3100', name: 'Operating Systems', credits: 3 },
    { code: 'CS 4000', name: 'Database Systems', credits: 3 },
    { code: 'CS 4200', name: 'Software Engineering', credits: 3 },
    { code: 'CS 4500', name: 'Artificial Intelligence', credits: 3 },
    { code: 'CS 4800', name: 'Computer Networks', credits: 3 },
    { code: 'CS 4900', name: 'Capstone Project', credits: 3 },
    
    // Mathematics
    { code: 'MATH 1010', name: 'Calculus I', credits: 4 },
    { code: 'MATH 1020', name: 'Calculus II', credits: 4 },
    { code: 'MATH 2100', name: 'Linear Algebra', credits: 4 },
    { code: 'MATH 2500', name: 'Probability & Statistics', credits: 4 },
    
    // General Education
    { code: 'ENG 1000', name: 'English Composition I', credits: 3 },
    { code: 'ENG 1100', name: 'English Composition II', credits: 3 },
    { code: 'PHYS 1050', name: 'Physics I', credits: 4 },
    { code: 'PHYS 1060', name: 'Physics II', credits: 4 },
    { code: 'CHEM 1030', name: 'Chemistry I', credits: 4 },
    { code: 'BIOL 1040', name: 'Biology I', credits: 3 },
    { code: 'HIST 2000', name: 'World History', credits: 3 },
    { code: 'PSYC 1500', name: 'General Psychology', credits: 3 },
    { code: 'ECON 1100', name: 'Microeconomics', credits: 3 },
    { code: 'PHLY 2000', name: 'Philosophy & Ethics', credits: 3 },
    { code: 'COM 1200', name: 'Intro to Communication', credits: 3 },
    
    // Electives
    { code: 'CS 3500', name: 'Web Development', credits: 3 },
    { code: 'CS 3600', name: 'Mobile Development', credits: 3 },
    { code: 'ENTR 2000', name: 'Entrepreneurship Basics', credits: 3 },
    { code: 'BUS 2100', name: 'Business Management', credits: 3 },
    { code: 'CS 3800', name: 'Machine Learning', credits: 3 },
    { code: 'CS 3900', name: 'Cybersecurity', credits: 3 },
  ];

  navigateToSchedule() {
    this.router.navigate(['/schedule']);
  }
}
