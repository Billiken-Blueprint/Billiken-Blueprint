import { Component, inject, input, output, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CoursesService, SearchCourse } from '../../services/courses-service/courses-service';
import { finalize } from 'rxjs/operators';

@Component({
    selector: 'app-chatbot-drawer',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './chatbot-drawer.html',
    host: {
        class: 'fixed inset-0 pointer-events-none z-[100000] overflow-hidden'
    }
})
export class ChatbotDrawerComponent {
    isOpen = input.required<boolean>();
    close = output<void>();

    private coursesService = inject(CoursesService);

    query = signal("");
    isLoading = signal(false);
    messages = signal<{ text: string, sender: 'user' | 'bot' }[]>([
        { text: "What are your interests or career goals?", sender: 'bot' }
    ]);

    suggestedCourses = signal<SearchCourse[]>([]);

    search() {
        if (!this.query().trim() || this.isLoading()) return;

        const userQuery = this.query();
        this.messages.update(msgs => [...msgs, { text: userQuery, sender: 'user' }]);
        this.query.set("");

        this.isLoading.set(true);
        this.coursesService.search(userQuery)
            .pipe(finalize(() => this.isLoading.set(false)))
            .subscribe({
                next: (courses) => {
                    this.suggestedCourses.set(courses);
                    this.messages.update(msgs => [...msgs, { text: `I found ${courses.length} courses that match your interests.`, sender: 'bot' }]);
                },
                error: (err) => {
                    console.error(err);
                    this.messages.update(msgs => [...msgs, { text: "Sorry, I encountered an error searching for courses.", sender: 'bot' }]);
                }
            });
    }

    removeCourse(courseId: number) {
        this.suggestedCourses.update(courses => courses.filter(c => c.id !== courseId));
    }

    isAddingToRoadmap = signal(false);

    addToRoadmap() {
        if (this.suggestedCourses().length === 0 || this.isAddingToRoadmap()) return;

        this.isAddingToRoadmap.set(true);
        const courseIds = this.suggestedCourses().map(c => c.id);

        this.coursesService.addDesiredCourses(courseIds)
            .pipe(finalize(() => this.isAddingToRoadmap.set(false)))
            .subscribe({
                next: () => {
                    this.messages.update(msgs => [...msgs, { text: "Courses successfully added to your roadmap!", sender: 'bot' }]);
                    this.suggestedCourses.set([]);
                },
                error: (err) => {
                    console.error(err);
                    this.messages.update(msgs => [...msgs, { text: "Failed to add courses to roadmap. Please try again.", sender: 'bot' }]);
                }
            });
    }

    onClose() {
        this.close.emit();
    }
}
