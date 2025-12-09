import { Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-chatbot-drawer',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './chatbot-drawer.html',
    host: {
        class: 'fixed inset-0 pointer-events-none z-[100000] overflow-hidden'
    }
})
export class ChatbotDrawerComponent {
    isOpen = input.required<boolean>();
    close = output<void>();

    onClose() {
        this.close.emit();
    }
}
