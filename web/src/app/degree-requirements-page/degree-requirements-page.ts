import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { GraduationRequirement, SchedulingService } from '../services/scheduling-service/scheduling-service';

interface RequirementViewModel extends GraduationRequirement {
  expanded: boolean;
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
export class DegreeRequirementsPage implements OnInit {
  private router = inject(Router);
  private schedulingService = inject(SchedulingService);

  degreeInfo = {
    name: 'Computer Science (B.A.)',
    totalCredits: 120,
  };

  requirements = signal<RequirementViewModel[]>([]);

  ngOnInit() {
    this.schedulingService.getRequirements().subscribe(reqs => {
      this.requirements.set(reqs.map(r => ({ ...r, expanded: false })));
    });
  }

  toggleCategory(req: RequirementViewModel) {
    req.expanded = !req.expanded;
  }

  navigateToSchedule() {
    this.router.navigate(['/schedule']);
  }
}
